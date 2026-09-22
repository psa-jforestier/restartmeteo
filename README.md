
# reSTARtMETEO
Faire revivre nos stations météo StarMétéo.

## Avant propos

Ce projet a pour but de faire revivre les stations personelles de prévision météo (_personal weather station_) qui utilisaient le service StarMétéo. Ces stations étaient principalement vendu par La Crosse Technologies entre 2005 et 2025. Le service a été brutalement interrompu en juin 2026, rendant ces stations inutilisables.

A titre expérimentale, il est possible de refaire fonctionner ces équipements, en utilisant un Raspberry Pi.

## Comment ca marche ?
Le protocole utilisé par les stations StarMétéo a fait l'objet d'une phase d’ingénierie inverse, dont vous pouvez voir l'historique sur le [forum Tetrahub.net](https://forum.tetrahub.net/decodage-meteo/meteofrance-pocsag-t5935.html) (inscription obligatoire, ou alors utilisez la version dans le cache de Google).
Grace a cette analyse, une très grande partie du protocole a été compris, et a été ré-implémenté dans ce projet.
D'ailleurs, ce projet utilise des morceaux entier d'autres projets qui ont vu le jour sur ce forum.

Pour en savoir plus sur le protocole StarMétéo, consulter le fichier [protocole.md](protocole.md).

### Matériel nécessaire

Vous devez posséder un Raspberry Pi 3B minimum, ainsi qu'un bout de fil electrique de 18cm qui devra être connecté sur un des ports GPIO du Raspberry.

### Logiciels
Vous devez avoir les programmes installées suivants sur votre Raspberry Pi :
- [RPITX](https://github.com/F5OEO/rpitx) : permet d'émettre des ondes radios à partir de votre Raspberry, sans matériel supplémentaire à part un bout de fil de cuivre.
- [RFTOOLS](https://github.com/jfdelnero/rf-tools) : utilisé pour encoder les messages de prévisions au format StarMétéo

Ces deux programmes doivent être compilés sur votre Raspberry. Si vous ne savez pas comment faire une version compilée des outils indispensables de RPITX et RFTOOLS sont disponibles dans le répertoire [bin](bin/).

- Python 3 : normalement déja installé et disponible.

## Installation
Connectez vous en SSH sur votre Raspberry. Clonez le repository reSTARtMETEO :

    cd ~/ # par defaut, on va cloner dans le home mais ca peut etre n'importe où
    git clone https://github.com/psa-jforestier/restartmeteo/

Éditez le fichier `cronmeteo.config.sh`et modifier les variables suivantes :
- STARMETEO_AREA : numéro du département où recevoir les prévisions (par défaut, 75 pour le département de Paris)
- STARMETEO_LATLONG : la latitude et la longitude de l'endroit ou vous souhaitez recevoir les prévisions (oui, c'est redondant avec le numéro du département, c'est comme ca). Format : 48.8529,2.3445 (latitude - virgule - longitude)

Afin de tester l'installation, lancer le script `cronmeteo.sh`:

    cd ~/restartmeteo
    /crontmeteo.sh
    == FORECAST ==
		==  2026-09-22
		    T min : +11 | T max : +24
		    Day   : clear sky        | Night : clear sky          | Rain : 0
		    Night : clear sky        | Morning : clear sky        | Afternoon : clear sky        | Evening : clear sky
		(...)
		Time sync on Tue 22 Sep 22:05:10 CEST 2026
		curtime=25176D:o 68FK  8B7-G6kEVm?!I0
		forecast=25176D:1+!.460 &     4F4 &    "4V0s&0," M4V8!&0$  '

Si vous avez une erreur, rendez-vous en bas de cette page dans la section "Problèmes connus".

Créer une tâche planifiée sur votre Raspberry, qui doit déclencher toutes les heures a 1 minute, le script `cronmeteo.sh` . Avec une crontab, la syntaxe est :

    1 * * * * cd /home/user/restartmeteo && ./cronmeteo.sh >> /home/user/restartmeteo/cronmeteo.log 2>&1

Vous devez adapter le chemin  `/home/user`en fonction de l'endroit où vous avez installé reSTARtMETEO.

Retirez les piles de votre station et remettez les, ou effectuez un RESET / RAZ.
Au bout d'une heure maximum, votre station devrait se mettre à l'heure et les prévisions devraient s'afficher.

## Problèmes connus
- lors de l'execution de `cronmeteo.sh`
