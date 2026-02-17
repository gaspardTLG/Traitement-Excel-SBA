# 📊 Application de Traitement Excel SBA

Application Streamlit pour traiter automatiquement les fichiers de décharges Excel.

## 🚀 Déploiement sur Streamlit Cloud (GRATUIT)

### Étape 1 : Créer un compte GitHub
1. Va sur https://github.com
2. Crée un compte gratuit si tu n'en as pas

### Étape 2 : Créer un nouveau repository
1. Clique sur le "+" en haut à droite → "New repository"
2. Nom : `traitement-excel-sba` (ou ce que tu veux)
3. Mets-le en **Public**
4. Clique sur "Create repository"

### Étape 3 : Upload les fichiers
1. Sur la page du repository, clique sur "uploading an existing file"
2. Glisse-dépose ces 3 fichiers :
   - `app.py`
   - `requirements.txt`
   - `README.md` (optionnel)
3. Clique sur "Commit changes"

### Étape 4 : Déployer sur Streamlit Cloud
1. Va sur https://streamlit.io/cloud
2. Connecte-toi avec ton compte GitHub
3. Clique sur "New app"
4. Sélectionne :
   - Repository : `ton-nom/traitement-excel-sba`
   - Branch : `main`
   - Main file path : `app.py`
5. Clique sur "Deploy!"

### Étape 5 : Partager le lien
Après 2-3 minutes, ton app sera en ligne ! Tu auras une URL du type :
```
https://ton-app.streamlit.app
```

Donne cette URL à la personne. Elle pourra :
1. Ouvrir le lien dans son navigateur
2. Déposer son fichier Excel
3. Télécharger le résultat

## 🖥️ Test en local (sur ton Mac)

Si tu veux tester avant de déployer :

```bash
# Installe streamlit
pip install streamlit pandas openpyxl

# Lance l'app
streamlit run app.py
```

Ça ouvrira automatiquement ton navigateur sur `http://localhost:8501`

## 📝 Format du fichier attendu

Le fichier Excel doit être nommé : `MM-JJ_xxx_Centre.xlsx`

Exemple : `01-26_Décharge_Bafia.xlsx`

## ❓ Problèmes courants

**L'app crash au déploiement**
- Vérifie que `requirements.txt` est bien présent
- Vérifie qu'il n'y a pas de typo dans les noms de fichiers

**Erreur lors du traitement**
- Vérifie que le nom du fichier respecte le format `MM-JJ_xxx_Centre.xlsx`
- Vérifie que les colonnes du fichier Excel sont correctes
