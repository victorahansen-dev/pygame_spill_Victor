April 2026
07.04.2026: Laget spillets bakgrunn og la inn første bilde (frame) av karakteren. Planlegger plattformer for å skape selve spillfølelsen.

17.04.2026: Implementert lava i bunnen av skjermen og legget til kollisjon. Karakteren kan nå gå til høyre/venstre og hoppe.

30.04.2026: Konfigurert A og D på tastaturet for mer naturlig styring av karakteren.

Mai 2026:
02.05.2026: Satt opp animasjon for når karakteren beveger seg mot venstre.

12.05.2026: Justerte på kollisjonssystemet og oppdaterte karakterens animasjoner.

19.05.2026: Designet og ferdigstilte spillets første nivå (Level 1).

22.05.2026: Lå til fiender. kodet inn mulighet for spiller å kunne dø ("Game Over") hvis man treffer en fiende eller faller i lavaen.

23.05.2026: Implementerte en Restart-knapp på skjermen som dukker opp når man dør.

26.05.2026: Gjort om karakteren med ny sprite og bedre animasjoner. Karakteren forsvinner nå ved død, og man kan bruke R-tasten for å starte på nytt. Lå også til en FPS-teller for å overvåke ytelsen.

28.05.2026: Lå til en dør (mål), tekst-popups for seier og død, og en startmeny.

Større systemoppdateringer (28.05.2026)
Refaktorering av kode (Nivå-system):

Endret spill datastruktur fra world_data til level_data for å kunne lage flere nivåer, og la til en variabel som holder styr på hvilket nivå spilleren er på.

Laget funksjonene reset_level() (tømmer skjermen), next_level() (går til neste nivå ved seier) og restart_current() (starter gjeldende nivå på nytt ved død).

Byttet farge på tekst pop-ups og legget til en ny en i start meny.

Gjorde R-tasten universell, slik at den kan brukes både etter seier og tap.

Nytt innhold - spill (nivå 2, niva 3)
laget et nytt visuelt tema med sand-grafikk i tillegg til å lage et helt nytt oppsett for Nivå 2.
kom opp med et til nytt tema med stein-grafikk med nytt oppsett for nivå 3.

29.05.2026
Laget en pause meny - kan brukes gjennom å trykke ESC knappen
lagde nivå 4, ny tema med metall-grafikk og annerledes oppsett.