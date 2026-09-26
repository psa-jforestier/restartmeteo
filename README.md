

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

Vous devez posséder un Raspberry Pi 3B minimum, ainsi qu'un bout de fil electrique de 18cm qui devra être connecté sur un la sortie GPIO 4, c'est à dire sur la broche 7. Voir https://elinux.org/RPi_Low-level_peripherals#General_Purpose_Input.2FOutput_.28GPIO.29.

### Logiciels
Vous devez avoir les programmes installées suivants sur votre Raspberry Pi :
- [RPITX](https://github.com/F5OEO/rpitx) : permet d'émettre des ondes radios à partir de votre Raspberry, sans matériel supplémentaire à part un bout de fil de cuivre.
- [RFTOOLS](https://github.com/jfdelnero/rf-tools) : utilisé pour encoder les messages de prévisions au format StarMétéo

Ces deux programmes doivent être compilés sur votre Raspberry. Si vous ne savez pas comment faire une version compilée des outils indispensables de RPITX et RFTOOLS sont disponibles dans le répertoire [bin](bin/).

- Python 3 : normalement déja installé et disponible.

## Installation
Connectez vous en SSH sur votre Raspberry. Clonez le repository reSTARtMETEO :

    cd ~/ # par defaut, on va cloner dans le home mais ca peut être n'importe où
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

Si vous avez une erreur à l'execution, rendez-vous en bas de cette page dans la section "Problèmes connus". Votre station météo ne va pas forcément ce mettre à jour ni afficher les prévisions, car elle "écoute" ces informations une fois par heure et il faut tomber au bon moment. C'est pour cela que ce script doit être executé à interval régulier.

Créer une tâche planifiée sur votre Raspberry, qui doit déclencher toutes les heures a 1 minute le script `cronmeteo.sh` . Avec une crontab, la syntaxe est :

    1 * * * * cd /home/user/restartmeteo && ./cronmeteo.sh >> /home/user/restartmeteo/cronmeteo.log 2>&1

Vous devez adapter le chemin  `/home/user` en fonction de l'endroit où vous avez installé reSTARtMETEO.

Vous devez purger de temps en temps le fichier de log `/home/user/restartmeteo/cronmeteo.log`.

Retirez les piles de votre station et remettez les, ou effectuez un RESET / RAZ.
Au bout d'une heure maximum, votre station devrait se mettre à l'heure et les prévisions devraient s'afficher.

## Fonctionnement interne

L'utilisation des pipes Unix permet d'enchainer les commandes nécessaires : récupération des prévisions -> encodage au format Starmeteo -> transmission radio.

```
Obtention des previsions sm_forecast.py --+-> encodeur starmeteo --> rpitx "POCSAG" transmitter --> Station météo    
 (en utilisant OpenMeteo                  |
  ou OpenWeatherMap)                      |
                                          |
Synchronisation horaire sm_time.py (wip) -'
```

Tout ce travail, ainsi que des infos de debug, est réalisé par le script `cronmeteo.sh`.

## Services de prevision

Les prévisions de reSTARtMETEO peuvent provenir de n'importe quel service de prévision météo, du moment qu'il supporte les fonctionalités suivantes :
- Geolocation : pouvoir transformer un nom de lieu ("Paris, France"), en coordonées latitude / longitude (48.8534,2.3488)
- Prévisions jour en cours : prévisions (ou historique) du jour en cours, et sur toute la journée, notemment :  température minimum et maximum sur le jour, tendance sur la journée et la nuit (pluie, nuage, soleil) 
- Prévisions 5 journées suivantes, par quart de journée : température minimum et maximum sur le jour, tendance par sur la journée et la nuit (pluie, nuage, soleil), probabilité de pluie.

Les services météo suivants fonctionnent :
- [Open Meteo](https://open-meteo.com/) : gratuit, très bonnes prévisions. C'est le service privilégié à utiliser.
- [Open Weather Map](https://openweathermap.org/) : gratuit, mais nécéssite un enregistrement pour avoir une clé d'API.

Pour changer le service de prévision, modifier le fichier `cronmeteo.config.sh`.

## Mode DEBUG des stations météo

Certaines stations météo La Crosse Technologies (WD9541, WD6006) possède un mode debug. Pour entrer dedans :
- maintenez appuyer la touche SET jusqu'à l'affichage de DEPT
- maintenez appuyer la touche + et la touche SET une seconde, jusqu'à ce que l'afficheur change.

L'afficheur contient alors :
- la date et heure en haut à gauche
- un affichage clignotant entre 00 et 80 en haut à droite (signification iconnue)
- en bas à gauche dans les prévisions J+1, on trouve un indicateur de force de recepetion du signal POCSAG sur 466,205MHz. En cas de reception d'un signal sur cette fréquence, le nombre augmente.
- sur la prévision J+2, on trouve le nombre de paquet POCSAG décodé (même ceux qui ne sont pas destiné à la station, avec un RIC différent de 25176)
- sur la prévision J+3, on trouve un compteur qui semble s'incrémenter à chaque trame POCSAGE de type Tone Only.

En mode debug, la station ne se synchronise pas. Mais quand on sort de ce mode (appui sur la touche SET), la station se remet en mode "écoute" et va recevoir les prochaines prévisions ou synchonisation horaire sans attendre le début de la prochaine heure.

## Reste à faire

Pour l'instant, les alertes météo ne sont pas gérées.

## Problèmes connus
- Aucun !
