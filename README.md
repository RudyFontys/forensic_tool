# forensic syslogtool met OOP

Deze versie gebruikt objectgeoriënteerd programmeren.

## Klassen en verantwoordelijkheden

- `Database`: maakt verbinding en beheert de tabellen.
- `SyslogParser`: zet één logregel om naar een dictionary.
- `IpChecker`: zoekt een IP-adres in een melding.
- `LogImporter`: leest een bestand en slaat regels op.
- `ForensicApp`: toont de Tkinter-GUI.

Dit past het Single Responsibility Principle eenvoudig toe: iedere klasse heeft één hoofdtaak.

## Waarom toch classes?

Een class groepeert gegevens en functies die bij elkaar horen. Bijvoorbeeld: `Database` onthoudt de naam van het databasebestand in `self.db_name`. De methodes `connect()`, `create_tables()` en `get_or_create_server()` horen allemaal bij databasebeheer.

De losse onderdelen worden in `main.py` aan elkaar gekoppeld:

database = Database("forensic.db")
parser = SyslogParser()
ip_checker = IpChecker()
importer = LogImporter(database, parser, ip_checker)

Hierdoor blijft zichtbaar welk object waarvoor wordt gebruikt.

## Starten

Voer dit uit vanuit de hoofdmap:

python main.py

De database `forensic.db` wordt automatisch gemaakt als deze nog niet bestaat.

## Tests installeren en uitvoeren

python -m pip install -r requirements-dev.txt
python -m pytest

Door `pytest.ini` krijg je automatisch uitgebreide uitvoer met de namen van de tests.

## Onderbouwing van de drie testonderdelen

1. **IP-checker:** controleert invoer met en zonder IP-adres. Parametrisatie voorkomt herhaalde testcode.
2. **Syslog-parser:** controleert de hoofdtaak van de parser en controleert dat ongeldige invoer `None` geeft.
3. **Log-importer:** controleert de volledige keten van bestand naar database. Een tijdelijke database voorkomt wijzigingen in de echte onderzoeksdatabase.

De GUI wordt voorlopig handmatig getest. Een GUI-test vraagt extra technieken voor vensters en muisklikken, terwijl de belangrijkste verwerkingslogica al apart automatisch wordt getest.


Deze 2e versie met GUI importeert alleen syslogregels in ISO-formaat, zoals:

2026-03-15T08:30:00+00:00 server1 sshd[42]: Failed password from 198.51.100.7

Querybeheer, tijdlijnselectie, vertrouwde IP-ranges en anomaliedetectie kunnen later als afzonderlijke stappen worden toegevoegd.
