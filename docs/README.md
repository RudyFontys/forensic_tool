# Forensic Syslog Tool – fase 1

Deze versie vervangt de tijdelijke CLI door een Tkinter-GUI en past objectgeoriënteerde verantwoordelijkheden toe.

## Starten

Open een terminal in deze map en voer uit:

```bash
python main.py
```

De applicatie gebruikt standaard `forensic.db` in de projectmap. Bij de eerste start worden de tabellen en indexen automatisch aangemaakt. Met **Bladeren** selecteer je een logbestand. Een server override is optioneel; zonder override wordt de servernaam uit iedere syslogregel gebruikt.

## Klassen en verantwoordelijkheden

- `DatabaseManager`: verbindingen, transacties en schema-initialisatie.
- `SyslogParser`: omzetting van een tekstregel naar een logobject.
- `IpChecker`: vinden en valideren van een IPv4-adres.
- `LogImporter`: coördinatie van lezen, parseren en opslaan.
- `ForensicToolApp`: alleen de gebruikersinterface en gebruikersinteractie.
- `ParsedLogEntry` en `ImportResult`: vaste datamodellen voor gegevensuitwisseling.

Deze verdeling voorkomt herhaalde code (DRY) en sluit aan bij het Single Responsibility Principle. `main.py` is de composition root: daar worden de objecten één keer samengesteld.

## Tests uitvoeren

Installeer pytest en voer de tests uit:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

Er zijn bewust drie tests:

1. **Parsertest** – controleert een representatieve geldige syslogregel en de vier belangrijke velden. Dit is kernlogica met veel kans op formaatfouten.
2. **IP-test** – controleert dat een ongeldig IPv4-adres wordt afgewezen en een later geldig adres wel wordt gevonden. Alleen een regex zou `999.999.999.999` ten onrechte accepteren.
3. **Importtest** – integratietest met een tijdelijke SQLite-database. Deze test controleert aantallen, server override, koppeling tussen `logs` en `servers`, en opslag van het IP-adres.

### Vuistregels voor wat wel en niet wordt getest

Wel automatisch testen:

- logica met duidelijke invoer en verwachte uitvoer;
- foutgevoelige parsing en validatie;
- databasegedrag in een geïsoleerde tijdelijke database;
- eigen code en de samenwerking tussen eigen klassen.

Niet in deze fase automatisch testen:

- of Tkinter-knoppen er visueel goed uitzien;
- het standaardgedrag van `filedialog`, `messagebox`, SQLite of Tkinter zelf;
- private hulpmethoden rechtstreeks, wanneer hetzelfde gedrag via een publieke methode getest wordt;
- toekomstige query-, anomaly- en trusted-IP-functionaliteit die nog niet is geïmplementeerd.

## Handmatige GUI-test

1. Start `python main.py`.
2. Selecteer `voorbeeld_syslog.log`.
3. Laat de server override leeg en importeer.
4. Controleer dat 3 regels slagen en 1 regel mislukt.
5. Herhaal met een server override, bijvoorbeeld `server-lab-01`.
6. Controleer dat het uitvoervenster kan scrollen en dat **Uitvoer wissen** werkt.

## Opmerking bij klassiek syslog

Een klassiek syslogtijdstip zoals `Mar 15 08:32:03` bevat geen jaar. De parser gebruikt daarom het huidige jaar. Voor forensisch bewijs kan in een latere fase een importdialoog worden toegevoegd waarin de onderzoeker expliciet het jaar opgeeft.
