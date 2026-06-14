# Use cases - Sysloganalyse-applicatie

**Opleiding:** Fontys Master Docent ICT  
**Auteur:** Rudy Bouland  
**Versie:** 1.0  
**Datum:** 11-06-2026

## Inhoud

1. [Use case 1 - Syslogbestand importeren](#use-case-1---syslogbestand-importeren)
2. [Use case 2 - Importresultaat controleren](#use-case-2---importresultaat-controleren)

---

# Use case 1 - Syslogbestand importeren

## Overzicht

| Onderdeel | Beschrijving |
|---|---|
| **Naam** | Syslogbestand importeren |
| **Primaire actor** | Forensisch onderzoeker |
| **Doel** | Syslogregels vanuit een bestand opslaan in de SQLite-database |
| **Aanleiding** | De onderzoeker wil een syslogbestand van een Linux-server onderzoeken |
| **Voorwaarden** | De applicatie is gestart en het syslogbestand is beschikbaar |
| **Resultaat** | Geldige logregels zijn opgeslagen in de tabellen `servers` en `logs` |

## Normaal verloop

1. De forensisch onderzoeker start de applicatie met:

   ```bash
   python main.py
   ```

2. De applicatie maakt verbinding met `forensic.db`.
3. De applicatie controleert of de tabellen `servers` en `logs` bestaan.
4. De onderzoeker klikt in de GUI op **Bestand kiezen**.
5. De onderzoeker selecteert een syslogbestand.
6. De onderzoeker kan eventueel een servernaam invullen.
7. De onderzoeker klikt op **Importeren**.
8. De GUI roept de methode `import_file()` van de klasse `LogImporter` aan.
9. `LogImporter` leest het bestand regel voor regel.
10. Iedere regel wordt door `SyslogParser` verwerkt.
11. `IpChecker` zoekt naar een IP-adres in de melding.
12. De server wordt opgezocht of toegevoegd in de tabel `servers`.
13. De logregel wordt toegevoegd aan de tabel `logs`.
14. Na afloop toont de GUI hoeveel regels succesvol en niet succesvol zijn geïmporteerd.

## Alternatieve situaties

### A1 - Er is geen bestand geselecteerd

1. De onderzoeker klikt op **Importeren** zonder een bestand te selecteren.
2. De applicatie toont een foutmelding.
3. Er worden geen gegevens geïmporteerd.

### A2 - Een regel heeft geen geldig syslogformaat

1. `SyslogParser` kan de regel niet verwerken.
2. De regel wordt niet opgeslagen.
3. De teller voor mislukte regels wordt met één verhoogd.
4. De import van de overige regels gaat verder.

### A3 - Er is geen servernaam ingevuld

1. De onderzoeker laat het serverveld leeg.
2. De applicatie gebruikt de servernaam uit de syslogregel.

### A4 - Er is wel een servernaam ingevuld

1. De onderzoeker vult bijvoorbeeld `webserver-01` in.
2. Deze servernaam vervangt de servernaam uit alle regels van het gekozen bestand.
3. Alle geïmporteerde regels worden aan `webserver-01` gekoppeld.

## Nacondities

Na een succesvolle import:

- staat de server in de tabel `servers`;
- staan de geldige logregels in de tabel `logs`;
- zijn de logregels via `server_id` aan de server gekoppeld;
- is een gevonden IP-adres opgeslagen;
- zijn ongeldige regels niet opgeslagen;
- ziet de gebruiker het aantal geslaagde en mislukte regels.

## Betrokken classes

| Class | Verantwoordelijkheid |
|---|---|
| `ForensicApp` | Bestand selecteren en de import starten |
| `LogImporter` | Het bestand regel voor regel verwerken |
| `SyslogParser` | Een syslogregel opdelen in velden |
| `IpChecker` | Een IP-adres uit de melding halen |
| `Database` | Verbinding maken en gegevens opslaan |

---

# Use case 2 - Importresultaat controleren

## Overzicht

| Onderdeel | Beschrijving |
|---|---|
| **Naam** | Importresultaat controleren |
| **Primaire actor** | Forensisch onderzoeker |
| **Doel** | Controleren of het syslogbestand correct is verwerkt |
| **Aanleiding** | De import van een syslogbestand is afgerond |
| **Voorwaarden** | De onderzoeker heeft een import uitgevoerd |
| **Resultaat** | De onderzoeker weet hoeveel regels zijn geïmporteerd en hoeveel regels zijn mislukt |

## Normaal verloop

1. De onderzoeker importeert een syslogbestand.
2. `LogImporter` houdt tijdens de import twee tellers bij:

   ```python
   imported_count = 0
   failed_count = 0
   ```

3. Bij iedere succesvol opgeslagen regel wordt `imported_count` verhoogd:

   ```python
   imported_count += 1
   ```

4. Wanneer een regel niet kan worden geparsed of opgeslagen, wordt `failed_count` verhoogd:

   ```python
   failed_count += 1
   ```

5. Na het verwerken van het bestand geeft `LogImporter` beide waarden terug:

   ```python
   return imported_count, failed_count
   ```

6. De GUI ontvangt de resultaten:

   ```python
   imported, failed = self.importer.import_file(
       filepath,
       server_name
   )
   ```

7. De GUI toont het resultaat aan de onderzoeker, bijvoorbeeld:

   ```text
   Geïmporteerde regels: 120
   Mislukte regels: 3
   ```

8. De onderzoeker beoordeelt of het resultaat aannemelijk is.

## Alternatieve situaties

### B1 - Alle regels zijn geldig

De GUI toont bijvoorbeeld:

```text
Geïmporteerde regels: 120
Mislukte regels: 0
```

De onderzoeker weet dat alle niet-lege regels zijn verwerkt.

### B2 - Een deel van de regels is ongeldig

De GUI toont bijvoorbeeld:

```text
Geïmporteerde regels: 117
Mislukte regels: 3
```

De onderzoeker weet dat drie regels niet voldeden aan het ondersteunde syslogformaat of niet konden worden opgeslagen.

### B3 - Geen enkele regel kan worden geïmporteerd

De GUI toont bijvoorbeeld:

```text
Geïmporteerde regels: 0
Mislukte regels: 120
```

De onderzoeker kan hieruit afleiden dat het bestand waarschijnlijk een niet-ondersteund formaat heeft.

### B4 - Er ontstaat een bestands- of databasefout

1. De importer geeft een fout door aan de GUI.
2. De GUI toont een foutmelding.
3. De applicatie wordt niet onverwacht afgesloten.
4. De onderzoeker kan een ander bestand kiezen of het probleem oplossen.

## Nacondities

Na deze use case:

- weet de onderzoeker of de import succesvol was;
- weet de onderzoeker hoeveel regels niet verwerkt konden worden;
- kan de onderzoeker besluiten het bestand opnieuw te controleren;
- kan de onderzoeker de database controleren voordat een verdere analyse wordt uitgevoerd.

## Waarom deze use case belangrijk is

Bij forensisch onderzoek is betrouwbaarheid belangrijk. De applicatie moet daarom niet alleen gegevens importeren, maar ook duidelijk melden of er gegevens zijn overgeslagen.

Wanneer de applicatie bijvoorbeeld alleen "import voltooid" zou tonen, weet de onderzoeker niet of alle regels zijn opgeslagen. Met de twee tellers is het importproces beter controleerbaar.

## Vervolg

Een volgende belangrijke use case voor een latere versie zou zijn: **geïmporteerde sysloggegevens doorzoeken met een query**. Die hoort nog niet bij de huidige code.
