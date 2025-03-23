Šis web servisas pritaiko MongoDB duomenų bazę, kad galima būtų valdyti klientų, automobilių ir kelionių duomenis. 
Suteikiama galimybė registruoti klientus, jų automobilius ir keliones, sekti kelionių koordinates, apskaičiuoti atstumą ar trukmę. 
Programa taip pat pritaiko funkcijas duomenų gavimui, šalinimui ir visos duomenų bazės ištrynimui.

## **Programos paleidimas**

Vienas iš būdų paleisti programą naudojant Docker Desktop:

* Atsisiųskite ir susidiekite Docker Desktop
  
* Pasileiskite Docker konteinerį: docker run -p 27017:27017 -d mongo
  
Programos veikimui testuoti galima naudoti Postman.

## **Operacijos klientams**

/klientas (PUT) – registruoja naują klientą pagal pateiktus duomenis (vardas, pavardė, gimimo data, el. paštas).

/klientas/<El_pastas> (DELETE) – ištrina klientą pagal el. paštą, pašalina ir su juo susijusius automobilius bei keliones.

/klientas/<El_pastas> (GET) – grąžina kliento informaciją pagal jo el. paštą.

## **Operacijos automobiliams**

/klientas/<El_pastas>/auto (PUT) – registruoja automobilį klientui pagal pateiktus duomenis (valstybinis numeris, gamintojas, modelis, metai, VIN).

/klientas/<El_pastas>/auto/<valstybinis_numeris> (DELETE) – ištrina automobilį pagal valstybinį numerį ir pašalina su juo susijusias keliones.

/klientas/<El_pastas>/auto (GET) – grąžina visus kliento automobilius pagal jo el. paštą.

## **Operacijos kelionėms**

/klientas/<El_pastas>/auto/<valstybinis_numeris>/kelione (PUT) – registruoja kelionę su nurodytu automobiliu ir kliento el. paštu, įrašo išvykimo ir atvykimo taškus.

/kelione/<keliones_id>/koordinate (POST) – registruoja kelionės koordinates (lat, lon) tam tikrai kelionei pagal jos ID.

/kelione/<keliones_id>/pabaiga (POST) – baigia kelionę, apskaičiuoja atstumą ir kelionės trukmę bei žymi ją kaip baigtą.

/kelione/<keliones_id> (DELETE) – ištrina kelionę pagal jos ID.

/kelione/<keliones_id>/papildoma (GET) – grąžina papildomą kelionės informaciją pagal jos ID.

## **Operacijos statistikų gavimui**

/kelione/<keliones_id> (GET) – grąžina kelionės metrikas, tokias kaip bendras atstumas ir kelionės trukmė.

/auto/<car_id> (GET) – grąžina su automobiliu susijusias keliones, jų bendrą atstumą ir trukmę.


## **Papildomos operacijos**

/panaikinti (DELETE) – ištrina visus duomenis iš visų kolekcijų (klientų, automobilių, kelionių).
