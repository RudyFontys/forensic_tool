# Forensic syslogtool – OOP-uitbreiding voor het lezen van de syslog info uit de database

Deze versie bouwt voort op de eerste OOP-versie. 

## De nieuwe features zijn:

- Server kiezen uit een keuzelijst die rechtstreeks uit SQLite wordt gevuld.
- Logregels filteren op server en optioneel op begin- en eindtijd.
- Een handmatige SQL-filtervoorwaarde testen.
- Een geteste filter opslaan met een naam en beschrijving.
- Een opgeslagen query opnieuw kiezen en uitvoeren.
- Opgeslagen query's verwijderen.
- Een server met alle bijbehorende logregels verwijderen.
- Resultaten bekijken in een tabel met verticale en horizontale schuifbalken.

## Klassen en verantwoordelijkheden

- `Database`: verbinding, tabellen, serverlijst en verwijderen van een server.
- `SyslogParser`: zet één syslogregel om naar velden.
- `IpChecker`: zoekt een IP-adres in de melding.
- `LogImporter`: importeert een bestand.
- `QueryManager`: zoekt logs en beheert opgeslagen query's.
- `ForensicApp`: maakt het hoofdvenster en de tabbladen.
- `ImportTab`: gebruikersscherm voor importeren.
- `QueryTab`: gebruikersscherm voor onderzoeken en querybeheer.
- `ManageTab`: gebruikersscherm voor het verwijderen van serverlogs.

Deze indeling volgt het Single Responsibility Principle: iedere klasse heeft één duidelijke hoofdtaak.

## Database-uitbreiding

Naast `servers` en `logs` wordt automatisch deze tabel gemaakt om queries op te kunnen slaan:

CREATE TABLE IF NOT EXISTS saved_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    where_clause TEXT NOT NULL
)

## Werken met handmatige query's

De onderzoeker vult alleen een voorwaarde in die normaal na `WHERE` staat (dat is makkelijker voor de onderzoeker zonder SQL kennis). Voorbeelden:

service = 'sshd'

service = 'sshd' AND message LIKE '%Failed password%'

ip = '198.51.100.7'

De server en tijdsperiode worden via aparte invoervelden toegevoegd. Daardoor hoeft de gebruiker geen volledige `SELECT` met een `JOIN` te schrijven.

Om een query op te slaan:

1. Kies een server of `Alle servers`.
2. Vul eventueel een begin- en eindtijd in.
3. Vul de queryvoorwaarde in.
4. Klik op **Query uitvoeren / testen**.
5. Vul een naam en beschrijving in.
6. Klik op **Geteste query opslaan**.

## Verwijderen van sysloggegevens

Op het tabblad **Beheren** wordt een server gekozen uit de database. Daarna worden de server en alle gekoppelde logregels verwijderd.

Let op: het oorspronkelijke `syslog`-bestand op de schijf wordt niet verwijderd. Alleen de geïmporteerde gegevens in SQLite worden verwijderd. Wanneer meerdere bestanden onder dezelfde servernaam zijn geïmporteerd, worden alle logregels van die server verwijderd.

## Starten

python main.py

## Tests

python -m pip install -r requirements-dev.txt

python -m pytest -v

De -v: Gebruik de verbose-optie om de namen van de uitgevoerde tests te zien

python -m pytest -vv

Voor nog meer details

Met -rA toont pytest een overzicht van alle testresultaten:

python -m pytest -v -rA


De nieuwe tests gebruiken een tijdelijke SQLite-database en wijzigen de echte `forensic.db` niet.
