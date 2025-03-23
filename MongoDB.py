from flask import Flask, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
import random
from datetime import datetime
import uuid
import math

def create_app():
    app = Flask(__name__)
    client = MongoClient("mongodb://localhost:27017/")
    db = client['gps']
    clients_collection = db['clients']
    auto_collection = db['auro']
    trips_collection = db['trips']
    

    # Registruoti klientą
    @app.route('/klientas', methods=['PUT'])
    def put_client():
        data = request.get_json()
        name = data.get('Vardas')
        surname = data.get('Pavarde')
        dob = data.get('Gimimo_data')
        email = data.get('El_pastas')

        if name == None or surname == None or dob == None or email == None:
            return {"message": "Nėra įvestas vardas, pavardė, gimimo data ar el. paštas"}, 400
        
        if clients_collection.find_one({'_id': email}) != None:
            return {"message": "Toks el. paštas jau egzistuoja"}, 402
                
        client = {
            '_id': email,
            'Vardas': name,
            'Pavarde': surname,
            'Gimimo_data': dob,
        }
        clients_collection.insert_one(client)

        return {"message": "Registracija sėkminga"}, 201
    
    # Ištrinti klientą pagal el. paštą
    @app.route('/klientas/<El_pastas>', methods=['DELETE'])
    def delete_client(El_pastas):
        client = clients_collection.find_one({'_id': El_pastas})
        if client != None:
            cars = list(auto_collection.find({'Klientas': El_pastas}))
            car_ids = [car['_id'] for car in cars]

            clients_collection.delete_one({'_id': El_pastas})
            auto_collection.delete_many({'Klientas': El_pastas})
            trips_collection.delete_many({'Automobilis': {'$in': car_ids}})
            return {"message": "Panaikinimas sėkmingas"}, 204
        return {"message": "Klientas nerastas"}, 404
    

    # Gauti kliento informaciją pagal el. paštą
    @app.route('/klientas/<El_pastas>', methods=['GET'])
    def get_client(El_pastas):
        client = clients_collection.find_one({'_id': El_pastas})
        if client != None:
            return {"Vardas": client['Vardas'], "Pavarde": client['Pavarde'], "Gimimo_data": client['Gimimo_data'], "El_pastas": client['_id']}, 200
        return {"message": "Klientas nerastas"}, 404
    

    # Registruoti automobilį
    @app.route('/klientas/<El_pastas>/auto', methods=['PUT'])
    def put_auto(El_pastas):
        data = request.get_json()
        numeris = data.get('Valstybinis_numeris')
        gamintojas = data.get('Gamintojas')
        modelis = data.get('Modelis')
        metai = data.get('Metai')
        VIN = data.get('VIN')

        if numeris == None or gamintojas == None or modelis == None or metai == None:
            return {"message": "Nėra įvestas valstybinis numeris, gamintojas, modelis ar metai"}, 400
        
        if auto_collection.find_one({'_id': numeris}) != None:
            return {"message": "Toks automobilis jau egzistuoja"}, 402

        auto = {
            '_id': numeris,
            'VIN': VIN,
            'Gamintojas': gamintojas,
            'Modelis': modelis,
            'Metai': metai,
            'Klientas': El_pastas
        }
        auto_collection.insert_one(auto)

        return {"message": "Automobilio registracija sėkminga"}, 201
    

    # Ištrinti automobilį pagal valstybinį numerį
    @app.route('/klientas/<El_pastas>/auto/<valstybinis_numeris>', methods=['DELETE'])
    def delete_auto(El_pastas, valstybinis_numeris):
        auto = auto_collection.find_one({'_id': valstybinis_numeris})
        if auto != None:
            auto_collection.delete_one({'_id': valstybinis_numeris})
            trips_collection.delete_many({'Automobilis': valstybinis_numeris})
            return {"message": "Automobilis panaikintas"}, 204
        return {"message": "Automobilis nerastas"}, 404
    

    # Gauti visus kliento automobilius pagal el. paštą
    @app.route('/klientas/<El_pastas>/auto', methods=['GET'])
    def get_autos(El_pastas):
        autos = list(auto_collection.find({'Klientas': El_pastas}))
        if autos != None:
            return autos, 200
        return {"message": "Automobilių nerasta"}, 404
    

    # Registruoti kelionę
    @app.route('/klientas/<El_pastas>/auto/<valstybinis_numeris>/kelione', methods=['PUT'])
    def put_trip(El_pastas, valstybinis_numeris):
        data = request.get_json()
        isvykimo_taskas = data.get('Isvykimo_taskas')
        atvykimo_taskas = data.get('Atvykimo_taskas')
        keliones_id = str(uuid.uuid4())
        
        if isvykimo_taskas == None or atvykimo_taskas == None:
            return {"message": "Nėra įvesta isvykimo taskas ar atvykimo taskas"}, 400

        if clients_collection.find_one({'_id': El_pastas}) == None:
            return {"message": "Klientas nerastas"}, 404
        
        if auto_collection.find_one({'_id': valstybinis_numeris}) == None:
            return {"message": "Automobilis nerastas"}, 404

        trip = {
            '_id': keliones_id,
            'Isvykimo_taskas': isvykimo_taskas,
            'Atvykimo_taskas': atvykimo_taskas,
            'Automobilis': valstybinis_numeris,
            'Koordinačių_įrašai': [],
            'Keliones_pradzia': datetime.now(),
            'Keliones_pabaiga': False
        }
        trips_collection.insert_one(trip)

        return {"message": "Kelionė sėkmingai pradėta", "Kelionės ID": keliones_id}, 201
    
    


    # Registruoti kelionės koordinates
    @app.route('/kelione/<keliones_id>/koordinate', methods=['POST'])
    def put_coordinates(keliones_id):
        data = request.get_json()
        lat = data.get('lat')
        lon = data.get('lon')
        trip = trips_collection.find_one({'_id': keliones_id, 'Keliones_pabaiga': False})
        if trip == None:
            return {"message": "Kelionė nerasta arba baigta"}, 404
        
        if lat == None or lon == None:
            return {"message": "Nepateikta koordinatė"}, 400
        
        koordinates = {
            'lat': lat,
            'lon': lon
        }
        trips_collection.update_one({'_id': keliones_id}, {'$push': {'Koordinačių_įrašai': koordinates}})
        
        return {"message": "Koordinatės sėkmingai užregistruotos"}, 201


    # Baigti kelionę
    @app.route('/kelione/<keliones_id>/pabaiga', methods=['POST'])
    def end_trip(keliones_id):

        trip = trips_collection.find_one({'_id': keliones_id, 'Keliones_pabaiga': False})
        if trip == None:
            return {"message": "Kelionė nerasta arba baigta"}, 404
        pabaigos_laikas = datetime.now()

        pipeline = [
        {"$match": {"_id": keliones_id, "Keliones_pabaiga": False}},
        {"$set": {
            "distances": {
                "$map": {
                    "input": {"$range": [1, {"$size": "$Koordinačių_įrašai"}]},
                    "as": "idx",
                    "in": {
                        "$sqrt": {
                            "$add": [
                                {"$pow": [
                                    {"$subtract": [
                                        {"$arrayElemAt": ["$Koordinačių_įrašai.lat", "$$idx"]},
                                        {"$arrayElemAt": ["$Koordinačių_įrašai.lat", {"$subtract": ["$$idx", 1]}]}
                                    ]}, 2
                                ]},
                                {"$pow": [
                                    {"$subtract": [
                                        {"$arrayElemAt": ["$Koordinačių_įrašai.lon", "$$idx"]},
                                        {"$arrayElemAt": ["$Koordinačių_įrašai.lon", {"$subtract": ["$$idx", 1]}]}
                                    ]}, 2]}
                            ]}}}}
        }},
        {"$set": {
            "total_distance": {"$sum": "$distances"}
        }},
        {"$set": {
            "keliones_trukme": {"$divide": [
                {"$subtract": [pabaigos_laikas, "$Keliones_pradzia"]},
                1000  
            ]}
        }},
        {"$project": {
            "_id": 0,
            "total_distance": 1,
            "keliones_trukme": 1
        }}
    ]

        result = list(trips_collection.aggregate(pipeline))
        if result == []:
            return {"message": "Kelionė nerasta arba..."}, 404

        total_distance = result[0]['total_distance']
        trip_duration = result[0]['keliones_trukme']

        trips_collection.update_one(
            {'_id': keliones_id},
            {'$set': {
                'Keliones_pabaiga': True,
                'Keliones_pabaigos_laikas': pabaigos_laikas,
                'Keliones_trukme': trip_duration,
                'Atstumas': total_distance
            }}
        )

        return {"message": "Kelionė baigta"}, 200

    
    # Panaikinti kelionę pagal kelionės ID
    @app.route('/kelione/<keliones_id>', methods=['DELETE'])
    def delete_trip(keliones_id):
        trip = trips_collection.find_one({'_id': keliones_id})
        if trip != None:
            trips_collection.delete_one({'_id': keliones_id})
            return {"message": "Kelionė panaikinta"}, 204
        return {"message": "Kelionė nerasta"}, 404

    # Gauti kelionės informaciją pagal kelionės ID
    @app.route('/kelione/<keliones_id>/papildoma', methods=['GET'])
    def get_trip(keliones_id):
        trip = trips_collection.find_one({'_id': keliones_id})
        if trip != None:
            return trip, 200
        return {"message": "Kelionė nerasta"}, 404
    

    # Gauli keliones metrikas pagal keliones ID
    @app.route('/kelione/<keliones_id>', methods=['GET'])
    def get_trip_details(keliones_id):
        trip = trips_collection.find_one({"_id": keliones_id})
        if trip == None:
            return {"message": "Kelionė nerasta"}, 404
    
        return {
            "trip_id": keliones_id,
            "total_distance_m": trip['Atstumas'],
            "trip_duration_s": trip['Keliones_trukme']
        }, 200
   
    
    # Gauti automobilio kelionių informaciją pagal kelionės ID
    @app.route('/auto/<car_id>', methods=['GET'])
    def get_car_summary(car_id):        
        pipeline = [
            {"$match": {"Automobilis": car_id}},  
            {"$group": {
                "_id": "$Automobilis",
                "total_distance": {"$sum": "$Atstumas"},
                "total_duration": {"$sum": "$Keliones_trukme"}
            }},
            {"$project": {
                "_id": 0,
                "car_id": "$_id",
                "total_distance_m": "$total_distance",
                "total_duration_s": "$total_duration"
            }}
        ]

        car = auto_collection.find_one({"_id": car_id})
        if car == None:
            return {"message": "Automobilis nerastas"}, 404
        
        result = list(trips_collection.aggregate(pipeline))
        
        if not result:
            return {
                "car_id": car_id,
                "total_distance_m": 0,
                "total_duration_s": 0
            }, 200

        return result[0], 200


    # Panaikinti visa duomenu baze
    @app.route('/panaikinti', methods=['DELETE'])
    def delete_all():
        clients_collection.delete_many({})
        auto_collection.delete_many({})
        trips_collection.delete_many({})
        return {"message": "Visi duomenys panaikinti"}, 204

    return app