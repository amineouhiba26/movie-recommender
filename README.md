# 🎬 Système de Recommandation de Films - Approche Hybride

## 📖 Description

Ce projet implémente un **système de recommandation de films intelligent** utilisant une approche hybride qui combine deux techniques principales :

1. **Filtrage basé sur le contenu** : Analyse les caractéristiques des films (genres, synopsis, acteurs)
2. **Filtrage collaboratif** : Apprend des préférences d'autres utilisateurs similaires

## 🧠 Comment fonctionne l'approche hybride ?

### 🎯 Le Problème
Les systèmes de recommandation traditionnels ont des limitations :
- **Contenu seul** : Ne connaît pas vos goûts personnels
- **Collaboratif seul** : Problème du "démarrage à froid" (nouveaux utilisateurs)

### 💡 Notre Solution Hybride

Notre système combine intelligemment les deux approches :

#### 1. **Filtrage par Contenu** (70% du score)
- Analyse les **genres, synopsis, acteurs** des films que vous aimez
- Trouve des films avec des caractéristiques similaires
- Utilise la **vectorisation TF-IDF** et la **similarité cosinus**

#### 2. **Filtrage Collaboratif** (30% du score)
- Analyse les notes d'utilisateurs ayant des goûts similaires aux vôtres
- Utilise la **factorisation matricielle (SVD)** pour découvrir des patterns cachés
- Recommande des films aimés par des "utilisateurs jumeaux"

#### 3. **Combinaison Intelligente**
```
Score Final = (0.7 × Score Contenu) + (0.3 × Score Collaboratif)
```

## 🏗️ Architecture du Système

### 📁 Structure du Projet
```
📦 movie-recommender/
├── 🎬 streamlit_app.py          # Interface utilisateur web
├── 🤖 hybrid_recommender.py     # Cœur du système hybride
├── ⭐ user_rating_system.py     # Gestion des notes utilisateurs
├── 🎯 movie_recommender.py      # Recommandations par contenu
├── 🔧 preprocess_movies.py      # Préparation des données
├── 📊 movies_dataset.json       # Base de données des films
├── 💾 user_ratings.db          # Base SQLite des notes
└── 📋 requirements.txt         # Dépendances Python
```

### 🔧 Composants Principaux

#### **HybridRecommendationSystem**
- **Rôle** : Chef d'orchestre qui combine les deux approches
- **Fonctions** :
  - Entraîne les modèles collaboratifs (SVD, similarité utilisateur)
  - Calcule les scores hybrides personnalisés
  - Gère les poids entre contenu et collaboratif

#### **UserRatingSystem**
- **Rôle** : Gère les notes et préférences utilisateurs
- **Fonctionnalités** :
  - Stockage des notes (SQLite)
  - Analyse des préférences par genre
  - Suppression/modification des notes

#### **MovieRecommender**
- **Rôle** : Recommandations basées sur le contenu
- **Méthodes** :
  - Similarité TF-IDF entre films
  - Recherche par titre et genre

## 🚀 Installation et Utilisation

### 1. **Installation**
```bash
git clone https://github.com/amineouhiba26/movie-recommender.git
cd movie-recommender
pip install -r requirements.txt
```

### 2. **Préparation des Données**
```bash
python preprocess_movies.py
```

### 3. **Lancement de l'Application**
```bash
streamlit run streamlit_app.py
```

### 4. **Utilisation**
1. **Recherche** : Trouvez des films similaires par titre ou genre
2. **Notation** : Notez des films pour entraîner le système
3. **Recommandations Hybrides** : Obtenez des suggestions personnalisées

## 🎯 Fonctionnalités

### ✨ Interface Utilisateur
- **Recherche basique** : Par titre ou genre
- **Recommandations hybrides** : Personnalisées selon vos notes
- **Gestion des notes** : Ajout/suppression de vos évaluations
- **Analyse des préférences** : Visualisation de vos goûts par genre

### 🧠 Intelligence Artificielle
- **TF-IDF** : Analyse sémantique des descriptions de films
- **SVD** : Factorisation matricielle pour découvrir des patterns
- **Similarité Cosinus** : Mesure de ressemblance entre films/utilisateurs
- **Apprentissage Adaptatif** : Le système s'améliore avec vos notes

## 🔬 Algorithmes Utilisés

### **1. Vectorisation TF-IDF**
```
TF-IDF = Fréquence du terme × log(Total documents / Documents contenant le terme)
```
- Transforme les textes en vecteurs numériques
- Met l'accent sur les mots rares et significatifs

### **2. Similarité Cosinus**
```
Similarité = (A · B) / (||A|| × ||B||)
```
- Mesure l'angle entre deux vecteurs
- Valeur entre 0 (différent) et 1 (identique)

### **3. Décomposition SVD**
```
Matrice_Utilisateurs_Films = U × Σ × V^T
```
- Réduit la dimensionnalité des données
- Découvre des "genres latents" non évidents

## 📊 Performance

### **Avantages de l'Approche Hybride**
- ✅ **Précision améliorée** : Combine les forces des deux méthodes
- ✅ **Résolution du démarrage à froid** : Recommandations immédiates via contenu
- ✅ **Découverte de nouveaux films** : Grâce au filtrage collaboratif
- ✅ **Apprentissage continu** : S'améliore avec chaque note

### **Métriques**
- **Score de confiance** : Affiché pour chaque recommandation
- **Composantes détaillées** : Contribution contenu vs collaboratif
- **Analyse des préférences** : Évolution de vos goûts par genre

## 🛠️ Technologies

- **Python 3.9+** : Langage principal
- **Streamlit** : Interface web interactive
- **Scikit-learn** : Algorithmes ML (TF-IDF, SVD, Cosinus)
- **Pandas/NumPy** : Manipulation des données
- **SQLite** : Base de données des notes utilisateurs

## 🤝 Contribution

1. Fork du projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit des changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 👨‍💻 Auteur

**Amine Ouhiba** - [GitHub](https://github.com/amineouhiba26)

---

*🎬 "La beauté du cinéma réside dans sa diversité, et notre IA l'a compris !"*
