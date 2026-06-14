# Master Piece: projectidee en volledige userstory

**Opleiding:** Fontys Master Docent ICT  
**Auteur:** Rudy Bouland  
**Datum:** 01-04-2026  

## Projectidee

Het idee is om een forensische applicatie te maken waarmee syslogbestanden van Linux-servers kunnen worden geïmporteerd in een SQLite-database en vervolgens kunnen worden onderzocht.

Er is een importmodule nodig waarmee syslogbestanden van verschillende servers via een grafische gebruikersinterface kunnen worden geïmporteerd. Voor het uitlezen en opsplitsen van syslogregels kan reguliere-expressieparsing worden gebruikt.

De geïmporteerde sysloggegevens worden via een SQL-tabel aan de juiste server gekoppeld. Daardoor kan de forensisch onderzoeker een specifieke server selecteren en de bijbehorende loggegevens bekijken.

In de syslogtabel worden de volgende velden opgeslagen:

- datum en tijd;
- server;
- service;
- melding.

De gebruiker kan selecties uitvoeren met:

- een handmatig ingevoerde SQL-query;
- een vooraf gemaakte en opgeslagen query.

Een handmatig ingevoerde query moet eerst kunnen worden getest. Daarna kan de query, samen met een beschrijving, in een aparte tabel worden opgeslagen. Opgeslagen queries moeten opnieuw kunnen worden uitgevoerd en indien nodig kunnen worden verwijderd. Ook geïmporteerde sysloggegevens die niet meer nodig zijn, moeten kunnen worden verwijderd.

De applicatie moet ondersteuning bieden voor het onderzoeken van verdachte gebeurtenissen, zoals:

- meerdere mislukte inlogpogingen kort na elkaar;
- inlogpogingen buiten werktijden;
- verbindingen vanaf IP-adressen buiten Nederland of Europa;
- activiteiten rondom een opgegeven bestandsnaam.

Voor vertrouwde IP-adressen is een importfunctie nodig. Daarmee kunnen bijvoorbeeld Nederlandse IP-bereiken worden geïmporteerd vanaf een externe gegevensbron, zoals [IP2Location — Netherlands IP Address Ranges](https://lite.ip2location.com/netherlands-ip-address-ranges).

De resultaten moeten in een scrollbaar venster worden weergegeven. De gebruiker moet daarbij een begin- en eindtijd kunnen selecteren om de onderzochte tijdsperiode te beperken.

Voor de grafische gebruikersinterface wordt Tkinter gebruikt.

### Optionele functionaliteiten

- exporteren van resultaten naar CSV;
- snelle filters via knoppen, zoals **Failed logins** en **Sudo usage**;
- rollen en rechten, bijvoorbeeld **admin** en **analyst**;
- eenvoudige anomaliedetectie met Python.

---

# Userstories volgens Atlassian

De onderstaande uitwerking bevat epics, userstories en acceptatiecriteria.

## EPIC 1 — Syslog Import & Data Management

### Beschrijving

Als forensisch onderzoeker wil ik syslogbestanden kunnen importeren en beheren, zodat ik loggegevens van meerdere Linux-servers centraal kan analyseren.

### Userstory 1.1 — Importeren van syslogbestanden

**Als** forensisch onderzoeker  
**wil ik** syslogbestanden via een GUI kunnen importeren  
**zodat ik** loggegevens van verschillende servers in één database kan analyseren.

#### Acceptatiecriteria

- De gebruiker kan één of meerdere syslogbestanden selecteren.
- Per bestand kan een servernaam worden toegewezen.
- De gegevens worden opgeslagen in een SQLite-database.
- De volgende velden worden correct geparsed:
  - datum en tijd;
  - server;
  - service;
  - melding.
- Foutieve regels worden gelogd en niet geïmporteerd.

### Userstory 1.2 — Logs aan servers koppelen

**Als** forensisch onderzoeker  
**wil ik** logs aan specifieke servers kunnen koppelen  
**zodat ik** analyses per server kan uitvoeren.

#### Acceptatiecriteria

- Elke server wordt opgeslagen in een aparte tabel.
- Logs bevatten een foreign key naar de bijbehorende server.
- De GUI toont een lijst met beschikbare servers.
- Filters per server werken correct.

### Userstory 1.3 — Geïmporteerde logs verwijderen

**Als** forensisch onderzoeker  
**wil ik** geïmporteerde syslogdatasets kunnen verwijderen  
**zodat ik** irrelevante gegevens kan opschonen.

#### Acceptatiecriteria

- De gebruiker kan logs per server of per bestand verwijderen.
- Voor het verwijderen wordt om bevestiging gevraagd.
- De gegevens worden permanent uit de database verwijderd.

---

## EPIC 2 — Query- en analysefunctionaliteit

### Beschrijving

Als forensisch onderzoeker wil ik loggegevens met queries kunnen analyseren, zodat ik verdachte activiteiten kan detecteren.

### Userstory 2.1 — Handmatige SQL-queries uitvoeren

**Als** gebruiker  
**wil ik** handmatig SQL-queries kunnen invoeren  
**zodat ik** flexibel analyses kan uitvoeren.

#### Acceptatiecriteria

- De GUI bevat een invoerveld voor SQL-queries.
- De resultaten worden in een tabel weergegeven.
- Fouten in een query leveren een duidelijke foutmelding op.

### Userstory 2.2 — Queries opslaan

**Als** gebruiker  
**wil ik** queries met een beschrijving kunnen opslaan  
**zodat ik** ze later opnieuw kan gebruiken.

#### Acceptatiecriteria

- De query en bijbehorende beschrijving worden in de database opgeslagen.
- Een query kan vóór het opslaan worden getest.
- De GUI toont een lijst met opgeslagen queries.

### Userstory 2.3 — Opgeslagen queries uitvoeren

**Als** gebruiker  
**wil ik** opgeslagen queries kunnen selecteren en uitvoeren  
**zodat ik** analyses snel kan herhalen.

#### Acceptatiecriteria

- De GUI bevat een keuzelijst of lijst met opgeslagen queries.
- Het selecteren van een query voert deze direct uit.
- De resultaten worden weergegeven.

### Userstory 2.4 — Opgeslagen queries verwijderen

**Als** gebruiker  
**wil ik** opgeslagen queries kunnen verwijderen  
**zodat ik** de lijst overzichtelijk kan houden.

#### Acceptatiecriteria

- Een query kan worden geselecteerd en verwijderd.
- Voor het verwijderen wordt om bevestiging gevraagd.

---

## EPIC 3 — Detectie van verdachte activiteiten

### Beschrijving

Als forensisch onderzoeker wil ik verdachte patronen kunnen herkennen, zodat ik mogelijke beveiligingsincidenten kan identificeren.

### Userstory 3.1 — Mislukte loginpogingen detecteren

**Als** gebruiker  
**wil ik** mislukte loginpogingen kunnen analyseren  
**zodat ik** brute-forceaanvallen kan detecteren.

#### Acceptatiecriteria

- Een query detecteert meerdere mislukte loginpogingen.
- Het tijdsinterval is instelbaar.
- Het resultaat toont het IP-adres, het tijdstip en de frequentie.

### Userstory 3.2 — Activiteiten buiten werktijden detecteren

**Als** gebruiker  
**wil ik** loginactiviteiten buiten werktijden kunnen bekijken  
**zodat ik** verdachte activiteiten kan herkennen.

#### Acceptatiecriteria

- De werktijden zijn configureerbaar.
- De resultaten tonen alleen gebeurtenissen buiten de ingestelde tijdsperiode.

### Userstory 3.3 — Detectie op basis van IP-locatie

**Als** gebruiker  
**wil ik** IP-adressen op herkomst kunnen controleren  
**zodat ik** buitenlandse of verdachte toegang kan detecteren.

#### Acceptatiecriteria

- IP-bereiken, zoals Nederlandse IP-bereiken, kunnen worden geïmporteerd.
- IP-adressen worden vergeleken met de opgeslagen bereiken.
- Het resultaat toont niet-vertrouwde IP-adressen.

### Userstory 3.4 — Zoeken op bestandsnaam

**Als** gebruiker  
**wil ik** in de logs naar specifieke bestandsnamen kunnen zoeken  
**zodat ik** verdachte bestandsactiviteiten kan vinden.

#### Acceptatiecriteria

- De GUI bevat een zoekveld voor een bestandsnaam.
- De resultaten tonen de relevante logregels.

---

## EPIC 4 — GUI en visualisatie

### Beschrijving

Als gebruiker wil ik een overzichtelijke GUI, zodat ik analyses efficiënt kan uitvoeren.

### Userstory 4.1 — Resultaten weergeven

**Als** gebruiker  
**wil ik** resultaten in een scrollbare tabel kunnen bekijken  
**zodat ik** grote datasets kan analyseren.

#### Acceptatiecriteria

- De resultatenweergave is scrollbaar.
- De tabel bevat minimaal de kolommen:
  - tijd;
  - server;
  - service;
  - melding.
- De gebruiker kan de resultaten op kolommen sorteren.

### Userstory 4.2 — Filteren op tijdslijn

**Als** gebruiker  
**wil ik** resultaten op tijd kunnen filteren  
**zodat ik** specifieke perioden kan analyseren.

#### Acceptatiecriteria

- Een begin- en eindtijd zijn instelbaar.
- Het filter wordt op het queryresultaat toegepast.

---

## EPIC 5 — Optionele geavanceerde functionaliteiten

> Deze epic bevat stretch goals.

### Beschrijving

Als forensisch onderzoeker wil ik extra analysemogelijkheden en gebruiksgemak, zodat ik efficiënter en diepgaander onderzoek kan uitvoeren.

### Userstory 5.1 — Resultaten naar CSV exporteren

**Als** gebruiker  
**wil ik** queryresultaten naar CSV kunnen exporteren  
**zodat ik** gegevens extern kan analyseren of rapporteren.

#### Acceptatiecriteria

- De GUI bevat een exportknop.
- De resultaten worden als `.csv`-bestand opgeslagen.
- De bestandsnaam is configureerbaar.
- Het CSV-bestand bevat alle zichtbare resultaatkolommen.
- Exporteren werkt ook met gefilterde datasets.

### Userstory 5.2 — Snelle filters via GUI-knoppen

**Als** gebruiker  
**wil ik** vooraf gedefinieerde filters via knoppen kunnen toepassen  
**zodat ik** veelvoorkomende analyses snel kan uitvoeren.

#### Acceptatiecriteria

- De GUI bevat knoppen voor bijvoorbeeld:
  - **Failed logins**;
  - **Sudo usage**;
  - **Authentication events**.
- Het aanklikken van een knop voert de bijbehorende query uit.
- De resultaten worden direct weergegeven.
- Nieuwe filters en knoppen kunnen later worden toegevoegd.

### Userstory 5.3 — Rollen- en rechtenbeheer

**Als** beheerder  
**wil ik** rollen aan gebruikers kunnen toewijzen  
**zodat ik** de toegang tot functionaliteiten kan beheren.

#### Acceptatiecriteria

- Er zijn minimaal de rollen **admin** en **analyst**.
- Een admin kan:
  - logs importeren en verwijderen;
  - queries opslaan en verwijderen.
- Een analyst kan:
  - queries uitvoeren;
  - resultaten bekijken.
- Authenticatie vindt plaats via een eenvoudige login met gebruikersnaam en wachtwoord.
- Rollen worden in de database opgeslagen.

### Userstory 5.4 — Eenvoudige anomaliedetectie

**Als** gebruiker  
**wil ik** afwijkend gedrag automatisch kunnen laten detecteren  
**zodat ik** verdachte patronen sneller kan identificeren.

#### Acceptatiecriteria

- De applicatie detecteert bijvoorbeeld:
  - een plotselinge toename van mislukte loginpogingen;
  - activiteiten op afwijkende tijdstippen;
  - onbekende IP-adressen.
- Verdachte resultaten worden visueel gemarkeerd, bijvoorbeeld met een highlight in de GUI.
- De analyse kan handmatig worden gestart.
- De detectie gebruikt Python-logica, zoals statistiek of eenvoudige drempelwaarden.

---

# MoSCoW-prioritering

## Must-have — MVP

- importfunctionaliteit;
- queryfunctionaliteit;
- grafische gebruikersinterface;
- basisfiltering.

## Should-have

- IP-analyse;
- tijdslijnfiltering.

## Could-have

- exporteren naar CSV;
- snelle filters;
- rollen- en rechtenbeheer;
- anomaliedetectie.

---

# Bibliografie

- Python Software Foundation. (2026). *ipaddress — IPv4/IPv6 manipulation library*. [Python-documentatie](https://docs.python.org/3/library/ipaddress.html)
- Python Software Foundation. (2026). *re — Regular expression operations*. [Python-documentatie](https://docs.python.org/3/library/re.html)
- Python Software Foundation. (2026). *tkinter — Python interface to Tcl/Tk*. [Python-documentatie](https://docs.python.org/3/library/tkinter.html)
