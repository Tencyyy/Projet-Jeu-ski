Projet du groupe 1 - Jeux olympiques d'hiver 2026

Contexte:

Jeu de ski type "runner": on descend la piste, on doit passer entre des portes
(couloirs d'obstacles) pour marquer des points. Si on rate le couloir, c'est game over.


Objectifs simples:
- Avoir un jeu qui se lance sans erreur.
- Pouvoir jouer: bouger, eviter les obstacles, gagner des points.
- Avoir un menu, une pause, et un ecran de fin.
- Avoir au moins une image de depart et, si possible, un son.

Prochain objectif (adapte):
1) Version complete (dossier `game/` + lanceur `winter_runner.py`)
- Gameplay: runner de ski avec obstacles, portes de sapins a traverser, bonus, drone et yeti.
- Score + niveaux + vitesse qui augmente.
- Ecrans: splash, menu, jeu, pause, game over, saisie de prenom + classement.
- Audio: musiques + effets.
- Assets: images/sons dans `assets/` charges par `game/assets.py`.

Equipe (4 personnes) et repartition:
1) Personne A (gameplay):
   - Deplacements du joueur.
   - Regles de collision (perdre si pas dans le couloir).
   - Score (points quand on passe un couloir).
2) Personne B (obstacles/level):
   - Apparition des lignes d'obstacles.
   - Taille du couloir et vitesse.
   - Variations simples (couloir pas toujours au meme endroit).
3) Personne C (interface):
   - Menu de depart.
   - Ecran pause et ecran game over.
   - Affichage du score.
4) Personne D (assets):
   - Image de depart (fond menu).
   - Sons si possible (facultatif).
   - Organisation du dossier assets.

Plan sur 4 jours (adapte, jour 1 deja fait):
Jour 1 - Fait:
- Projet lance, pygame OK, base comprise.
- Repartition A/B/C/D et checklist.
- Gameplay de base: couloirs + score + game over + pause.

Jour 2 - Gameplay avance:
- Ajouter un yeti qui poursuit (simple: il se rapproche si on rate des couloirs).
- Ajouter des obstacles differents (roches).
- Remplacer le bonhomme par un skieur (image).
- Tester les vitesses et difficulte.

Jour 3 - Assets et decor:
- Trouver de meilleurs assets (arbres, roches, skieur, yeti).
- Remplacer les lignes par un decor (neige qui tombe ou sol neigeux).
- Ajouter sapins de Noel sur les cotes.
- Verifier que tout s'affiche sans lag.

Jour 4 - Esthetisme + finitions:
- Focus sur le visuel (background, couleurs, animations simples).
- Ajouter un classement + saisie de prenom (si possible).
- Musique/sons legers.
- Tests finaux et corrections.

Regles de travail pour debutants:
- Toujours tester souvent (petites modifications).
- Si un bug apparait, revenir a la derniere version qui marchait.
- Garder le code simple, pas besoin de fonctions compliquees.
- Communiquer: chacun dit ce qu'il a fait en fin de journee.

Lancer:
  python main.py

Touches:
- ENTREE: demarrer / revenir au menu
- Fleches: bouger
- P: pause
- R: rejouer (apres game over)
- ECHAP: quitter
