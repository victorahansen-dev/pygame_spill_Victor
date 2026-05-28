Logg

07.04.2026:
- laget en bakgrunn til spillet, må nå lage objekter som karakter kan gå på for selve "platformer" følelsen, i tillegg til design.
- Settet inn første frame av karakter.

17.04.2026
- settet lava på bunn av spillvinduet.
- legget til sprite, kan gå høyre, venstre og hoppe.
- legget til kollisjon på bunn av spillvindu.

30.04.2026
- settet a & d for høyre og venstre for bevegelse.

02.05.2026
- settet opp animasjon for venstre

12.05.2026
- legget til kollisjon og oppdatert sprite animasjon

19.05.2026
- laget første lvl til spillet.

22.05.2026
- legget til fiender og mulighet til å dø hvis man treffer fiende eller lava.

23.05.2026
- legget til "restart" knapp for når man dør.

26.05.2026
- lagd ny sprite med ordentlig animasjon.
- karakter blir borte når man dør.
- legget til tekst som viser fps.
- kan også nå bruke "R" knappen til å starte på nytt etter man dør.

28.05.2026
- laget dør og mulighet til å vinne.
- legget til text pop-up for når man dør og vinner.
- laget start meny.

- Endret world_data til level_data som inneholder en liste med nivåer
- Lagt til level-variabel som holder styr på hvilket nivå spilleren er på
- Lagt til reset_level()-funksjon som tømmer alle sprite-grupper og laster inn nytt nivå
- Lagt til next_level()-funksjon som går videre til neste nivå når spilleren vinner
- Lagt til restart_current()-funksjon som starter gjeldende nivå på nytt
- Vinnerskjermen går nå videre til neste nivå istedenfor å starte på nytt
- R-tasten fungerer nå både etter død og etter å ha vunnet

- Lagt til sand
- Designet nivå 2 med sand-tema og annerledes layout
- To fiender plassert på plattformer i nivå 2
