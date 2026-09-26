[La meilleure explication du protocol StarMetéo est donnée sur le projet git CelebWeather.](https://github.com/obones/CelebWeather/blob/main/doc/protocol.md)

Et on va pas se mentir, le protocol est hyper tordu, pas logique du tout. Il semble avoir été écrit expres pour être compliqué. Même en tenant compte de l'ancieneté des équipements et des puissances limités des microcontroleurs des années 1990-2000, il aurait pu être plus simple dès la conception :

- Les bits des données sont mélangés, le BCD n'est pas respécté
- checksum incohérents
- encodage "genre de base 64"  (3->s , 32->p) exotique

