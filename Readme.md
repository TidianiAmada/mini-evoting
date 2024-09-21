
# Application de Vote Électronique (Ranked voting method)

## Description
Cette application de vote électronique permet aux électeurs de classer les candidats par ordre de préférence lors d'une élection. Elle est conçue en utilisant **Flask** (framework web Python), **SQLAlchemy** pour la gestion de la base de données MySQL, et le système de vote par classement pour déterminer le gagnant.

### Fonctionnalités principales
- Gestion des élections par les organisateurs
- Inscription des électeurs et des candidats
- Processus de vote sécurisé avec classement de préférence (1er et 2ème choix)
- Calcul des résultats selon la méthode de vote par classement (redistribution des voix si aucun candidat n'obtient la majorité absolue au premier tour)
- Affichage des résultats des élections en temps réel une fois les votes clôturés

## Technologies utilisées
- **Python 3.x**
- **Flask** : Framework web léger
- **SQLAlchemy** : ORM pour l'interaction avec la base de données MySQL
- **MySQL** : Base de données relationnelle
- **Jinja2** : Moteur de template pour le rendu des pages HTML
- **HTML/CSS** : Pour l'interface utilisateur

## Prérequis
Avant de commencer, assurez-vous d'avoir les éléments suivants installés sur votre machine :

- Python 3.x
- MySQL
- Pip (gestionnaire de paquets Python)
- Virtualenv (pour créer un environnement virtuel)

## Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/votre-utilisateur/vote-electronique.git
   cd vote-electronique
   ```

2. Créez et activez un environnement virtuel :
   ```bash
   python -m venv venv
   source venv/bin/activate  # Pour Linux/Mac
   venv\Scripts\activate  # Pour Windows
   ```

3. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

4. Configurez la base de données MySQL :
   - Créez une base de données MySQL pour l'application.
   - Mettez à jour la configuration de la base de données dans le fichier `config.py` avec vos informations MySQL.

5. Initialisez la base de données :
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

6. Démarrez le serveur Flask :
   ```bash
   flask run
   ```

L'application sera accessible à l'adresse `http://127.0.0.1:5000/`.

## Utilisation

### 1. Planification de l'élection
- Un **Organisateur** peut créer une élection en spécifiant le titre, la date et l'heure, les candidats et les modalités.
- Chaque **Candidat** peut être enregistré avec un nom, une photo et une profession.

### 2. Inscription des électeurs
- L'**Organisateur** inscrit les électeurs en fournissant leur numéro d'électeur (CNE) et leur nom.

### 3. Processus de vote
- Un **Électeur** peut se connecter à la plateforme avec son identifiant sécurisé.
- L'électeur sélectionne un premier et un second choix parmi les candidats proposés.
- Une fois le vote soumis, il est enregistré et comptabilisé.

### 4. Calcul des résultats
- Les votes de premier choix sont comptés.
- Si aucun candidat n'obtient la majorité absolue, les votes du candidat ayant le moins de voix sont redistribués en fonction du second choix.
- Le processus continue jusqu'à ce qu'un candidat obtienne la majorité.

### 5. Affichage des résultats
- À la fin de l'élection, les résultats sont affichés, montrant le nombre total de voix et le pourcentage obtenu par chaque candidat.

## Arborescence du projet

```
vote-electronique/
│
├── app.py                  # Point d'entrée principal de l'application
├── config.py               # Configuration de la base de données
├── models.py               # Modèles SQLAlchemy pour les tables
├── services.py             # Logique des services de vote et calcul des résultats
├── routes.py               # Définition des routes Flask
├── templates/
│   ├── base.html           # Template de base
│   ├── login.html          # Page de connexion
│   ├── create_election.html # Page de création d'élection
│   ├── vote.html           # Page de vote
│   └── results.html        # Page d'affichage des résultats
├── static/
│   └── styles.css          # Feuilles de style CSS
├── migrations/             # Gestion des migrations de base de données
└── README.md               # Ce fichier
```

## Sécurité
- Les mots de passe des organisateurs sont **hachés** avant d'être stockés dans la base de données pour assurer la sécurité des données.
- Chaque utilisateur (organisateur et électeur) se connecte via une session sécurisée.

## Contribution
Les contributions sont les bienvenues ! Si vous souhaitez ajouter des fonctionnalités ou améliorer le code existant, n'hésitez pas à créer une branche et à soumettre une pull request.

## Licence
Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

Avec ce fichier `README.md`, vos utilisateurs ou collaborateurs comprendront rapidement l'objectif de l'application et comment l'utiliser et la déployer.