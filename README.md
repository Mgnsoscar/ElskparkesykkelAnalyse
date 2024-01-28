# Analyseverktøy for el-sparkesykler og t-bane

All kode som leser, sorterer og analyserer data fra elsparkesykler, t-bane og vær ligger 
i scriptet dataAnalyse.py. Her er alt av utregninger gjort, og generelt alt som er
relevant for selve analysen.

I scriptet programGUI.py ligger det grafiske brukergrensesnittet som kan brukes
for å få enkel tilgang til all dataen som dataAnalyse.py har.
Med dette programmet kan man enkelt skrive inn tidsperioden en ønsker og se på, og lage 
grafer utifra hvilke parametre man ønsker. I tilegg vil programmet regne ut div. gjennomsnittsverdier
og korrelasjonskoeffisienter i tidsrommet og vise dette i et tekstfelt. Programmet lar også
brukeren lage excelark av dataen i det ønskede tidsrommet.

programGUI.py arver en del klasser fra customQtWidgets.py som er 
spesialtilpassede klasser jeg har laget basert på de vanlige PyQt5 widgetene. Disse klassene gjør PyQt5
veldig mye raskere og enklere å bruke.

Om en skulle øsnke å bruke dette programmet med et annet datasett trengs det kun noen små endringer på koden
gitt at dataen kommer på samme format. I tilegg til at inputfilnavnene må endres er det også noen
steder i koden som definerer året som 2022, og hvis man vil se på et annet år så må dette endres. Det er ikke mange
steder, og det burde ikke ta lang tid. Hvis man vil se på data fra en t-banestasjon som ikke er en endestasjon
er det litt mer som må endres, for da kan man ikke lenger dele opp i avganger og ankomster slik jeg har gjort her.
Dette burde heller ikke være så veldig komplisert, men det tar kanskje litt lenger tid.

Filene med rådata er ikke lagt ved ettersom disse inneholder offentlig utilgjengelig informasjon.
