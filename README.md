# Bedriftsoppslag | Frontend
## Søk opp bedrifter og hent ut e-post, organisasjonsinformasjon og mer!
[http://bedriftsoppslag.no](http://www.bedriftsoppslag.no/) Nettsiden er ikke tilgjengelig hele tiden.
Når den er oppe så bruker jeg Gunicorn og NGINX for hosting på lokal server.

Bedriftsoppslag startet med OrgOppslag; en egen modul for henting av data fra brønnøysundsregisteret og google søk. Fra disse kildene <br>
hentes diverse nøkkelinformasjon om bedriften (adresse, org. nr, ansatte og mer), fra google brukes webscraping for å hente ut relevante <br>
søkeresultater. På disse sidene brukes filtrering for å se etter epost-adresser.

Python Flask, Flask Restful, HTML / CSS er byggeklossene i dette prosjektet.
Dette prosjektet ga innsyn i hvordan en dynamisk nettside kan laged ved bruk av Python. Det er bruk av databaser og egen API server (https://github.com/FFaanes/bedriftsoppslag_api).
Jeg deler gjerne innsyn og tar gjennomgang av prosjektet om dette ønskes!<br>
PS! Nettsiden kan brukes uten at API server kjøres, den vil bruke backup løsning og derfor ikke ha: caching, søkehistorikk osv..<br>
Admin siden bruker API server for data, og vil derfor ikke fungere når kun frontend server brukes. <br>
<br>
Ta kontakt via mail: frankfaanes@hotmail.com
