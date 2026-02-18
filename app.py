import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Traitement Excel SBA", page_icon="📊")

# Dictionnaire de mapping pour Classification et Famille
MAPPING_DICT = {
    'internet': 'Infrastructure',
    'electricité': 'Frais de fonctionnement',
    'eau': 'Frais de fonctionnement',
    'assainissement': 'Infrastructure',
    'déchets': 'Infrastructure',
    'pépites': 'Projets',
    'défraiements': 'Defraiements',
    'defraiement': 'Defraiements',
    'chef': 'Defraiements',
    'loyer': 'Frais de fonctionnement',
    'nutrition': 'Santé',
    'médicaments': 'Santé',
    'médical': 'Santé',
    'rugby': 'Rugby',
    'tournois': 'Rugby',
    'fournitures': 'Education',
    'fourniture': 'Education',
    'transport': 'Frais de fonctionnement',
    'bac': 'Education',
    'imprévus': 'Dépenses exceptionnelles',
    'couture': 'Santé',
    'scolaire': 'Education',
    'scolaires': 'Education',
    'assurances': 'Frais de fonctionnement',
    'équipement': 'Frais de fonctionnement',
    'equipement': 'Frais de fonctionnement',
    'entretien': 'Frais de fonctionnement',
    'repas': 'Santé',
    'goûters': 'Santé',
    'gouter': 'Santé',
    'maintenance': 'Frais de fonctionnement',
    'carburant': 'Frais de fonctionnement',
    'communication': 'Infrastructure',
    'communications': 'Infrastructure',
    'connexion': 'Infrastructure',
    'caisse': 'Dépenses exceptionnelles',
    'Icam': 'Education',
    'ESS-UCAC': 'Education',
    'voiture': 'Infrastructure',
    'ecole': 'Education',
    'particulier': 'Dépenses exceptionnelles',
    'particuliers': 'Dépenses exceptionnelles',
}

def get_classification(type_text):
    """
    Cherche dans le dictionnaire de mapping pour trouver la classification.
    Retourne (classification, found) où found indique si un match a été trouvé.
    """
    type_lower = type_text.lower().strip()
    
    # Chercher une correspondance exacte ou partielle
    for key, value in MAPPING_DICT.items():
        if key in type_lower:
            return value, True
    
    # Aucune correspondance trouvée
    return "Aucune info", False

st.title("📊 Traitement des Décharges Excel")
st.write("Upload un ou plusieurs fichiers Excel et télécharge le résultat combiné.")

# Upload de plusieurs fichiers
uploaded_files = st.file_uploader(
    "Dépose tes fichiers Excel ici (tu peux en sélectionner plusieurs)", 
    type=['xlsx', 'xls'],
    accept_multiple_files=True
)

if uploaded_files:
    # Afficher le nombre de fichiers uploadés
    st.success(f"✅ {len(uploaded_files)} fichier(s) chargé(s)")
    
    # Liste pour stocker tous les DataFrames traités
    all_dataframes = []
    
    # Fonction de traitement (pour éviter la répétition)
    def process_file(uploaded_file):
        """Traite un fichier Excel et retourne le DataFrame résultant"""
        try:
            # Extraction des infos depuis le nom de fichier
            nom = uploaded_file.name.split('.')[0]
            parts = nom.split('_')
            
            # Gestion du nom du centre (peut contenir des underscores)
            date = parts[0]
            centre = '_'.join(parts[2:])  # Prend tout après "Décharge_"
            
            mois_dict = {
                '01': 'Janvier', '02': 'Février', '03': 'Mars', '04': 'Avril',
                '05': 'Mai', '06': 'Juin', '07': 'Juillet', '08': 'Août',
                '09': 'Septembre', '10': 'Octobre', '11': 'Novembre', '12': 'Décembre'
            }
            
            mois = mois_dict[date.split('-')[0]]
            annee = date.split('-')[1]
            supp = f'01-{date.split("-")[0]}-{date.split("-")[1]}'
            
            # Lire sans header pour gérer tous les formats
            df = pd.read_excel(uploaded_file, header=None)
            
            # Fonction pour retirer les deux-points et espaces
            def remove_colon(string):
                string = str(string).strip()
                if string.endswith(':'):
                    return string[:-1].strip()
                return string
            
            # Trouver où commencent les vraies données (première ligne avec ":")
            start_row = None
            data_col = None
            amount_col = None
            
            for i in range(min(50, len(df))):
                for j in range(len(df.columns)):
                    val = df.iloc[i, j]
                    if pd.notna(val) and isinstance(val, str):
                        # Chercher une catégorie (se termine par : et pas "Tel" ou "Période")
                        if ':' in val and not val.startswith('Tel') and 'Période' not in val:
                            start_row = i
                            data_col = j
                            # Colonne des montants = même colonne que la catégorie
                            amount_col = j
                            break
                if start_row is not None:
                    break
            
            if start_row is None:
                raise ValueError(f"Impossible de trouver le début des données dans {uploaded_file.name}")
            
            # Extraction des données
            ListeType = []
            ListeFamille = []
            ListeClass = []
            ListeDescription = []
            ListeDecharge = []
            unfound_items = []  # Pour tracker les items sans correspondance
            
            i = start_row
            while i < len(df):
                row = df.iloc[i]
                val = row[data_col]
                
                # Vérifier si c'est une catégorie (se termine par :)
                if pd.notna(val) and isinstance(val, str) and ':' in val:
                    # C'est une catégorie
                    INFO = remove_colon(val)
                    i += 1
                    
                    # Lire les montants jusqu'à la prochaine catégorie ou ligne vide
                    while i < len(df):
                        row = df.iloc[i]
                        
                        # Vérifier si ligne vide (toutes les colonnes sont NaN)
                        if row.isna().all():
                            i += 1
                            break
                        
                        # Vérifier si nouvelle catégorie
                        val_check = row[data_col]
                        if pd.notna(val_check) and isinstance(val_check, str) and ':' in val_check:
                            # C'est une nouvelle catégorie, on sort de la boucle interne
                            break
                        
                        # Vérifier si c'est un montant (nombre)
                        montant = row[amount_col]
                        if pd.notna(montant) and (isinstance(montant, (int, float)) or str(montant).replace(' ', '').isdigit()):
                            # Chercher une description dans les autres colonnes
                            description = None
                            for col in range(len(df.columns)):
                                if col != amount_col:
                                    desc_val = row[col]
                                    if pd.notna(desc_val) and isinstance(desc_val, str) and desc_val.strip() and not ':' in desc_val:
                                        description = remove_colon(desc_val)
                                        break
                            
                            if description is None:
                                description = INFO  # Utiliser la catégorie comme description
                            
                            # Utiliser le mapping pour Classification et Famille
                            classification, found = get_classification(INFO)
                            
                            # Tracker les items non trouvés
                            if not found and INFO not in unfound_items:
                                unfound_items.append(INFO)
                            
                            ListeType.append(INFO)
                            ListeFamille.append(classification)  # Utiliser la classification mappée
                            ListeClass.append(classification)    # Utiliser la classification mappée
                            ListeDescription.append(description)
                            ListeDecharge.append(montant)
                        
                        i += 1
                        
                        # Vérifier si on atteint une ligne "TOTAL"
                        for col in range(len(df.columns)):
                            check_val = row[col]
                            if pd.notna(check_val) and isinstance(check_val, str):
                                upper_val = check_val.upper()
                                if 'TOTAL' in upper_val or 'SBA' in upper_val:
                                    i = len(df)  # Sortir de toutes les boucles
                                    break
                        
                        if i >= len(df):
                            break
                else:
                    i += 1
                
                # Sécurité : vérifier les lignes TOTAL
                if i < len(df):
                    for col in range(len(df.columns)):
                        check_val = df.iloc[i, col] if i < len(df) else None
                        if pd.notna(check_val) and isinstance(check_val, str):
                            upper_val = str(check_val).upper()
                            if 'TOTAL' in upper_val or 'SBA' in upper_val:
                                i = len(df)
                                break
            
            if len(ListeDecharge) == 0:
                raise ValueError(f"Aucune donnée extraite dans {uploaded_file.name}")
            
            # Création du DataFrame pour ce fichier
            df_result = pd.DataFrame({
                'Pays': ['Cameroun'] * len(ListeFamille),
                'Centre': [centre] * len(ListeFamille),
                'Type': ListeType,
                'Famille': ListeFamille,
                'Classification': ListeClass,
                'Description': ListeDescription,
                'Date': [supp] * len(ListeFamille),
                'Mois': [mois] * len(ListeFamille),
                'Annee': [annee] * len(ListeFamille),
                'Ref': [date] * len(ListeFamille),
                'Decharge': ListeDecharge
            })
            
            return {
                'success': True,
                'filename': uploaded_file.name,
                'centre': centre,
                'mois': mois,
                'annee': annee,
                'lignes': len(df_result),
                'dataframe': df_result,
                'unfound_items': unfound_items  # Ajouter la liste des items non trouvés
            }
            
        except Exception as e:
            return {
                'success': False,
                'filename': uploaded_file.name,
                'error': str(e)
            }
    
    # Traiter tous les fichiers
    with st.spinner('Traitement en cours...'):
        results = []
        for uploaded_file in uploaded_files:
            result = process_file(uploaded_file)
            results.append(result)
            
            if result['success']:
                all_dataframes.append(result['dataframe'])
    
    # Afficher un résumé du traitement
    st.subheader("📋 Résumé du traitement")
    
    success_count = sum(1 for r in results if r['success'])
    error_count = len(results) - success_count
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("✅ Fichiers traités avec succès", success_count)
    with col2:
        st.metric("❌ Fichiers en erreur", error_count)
    
    # Détails par fichier
    for result in results:
        if result['success']:
            st.success(f"✓ **{result['filename']}** : {result['centre']} - {result['mois']} {result['annee']} ({result['lignes']} lignes)")
        else:
            st.error(f"✗ **{result['filename']}** : {result['error']}")
    
    # Afficher les warnings pour les items non trouvés dans le mapping
    all_unfound = []
    for result in results:
        if result['success'] and result.get('unfound_items'):
            all_unfound.extend(result['unfound_items'])
    
    # Dédupliquer et afficher
    unique_unfound = list(set(all_unfound))
    if unique_unfound:
        st.warning(f"⚠️ **Info** : Certains types n'ont pas de classification définie et ont été marqués comme 'Aucune info' : {', '.join(unique_unfound)}")
    
    # Si au moins un fichier a été traité avec succès
    if all_dataframes:
        # Combiner tous les DataFrames
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        st.success(f"✨ Traitement terminé ! **{len(combined_df)} lignes au total** dans {len(all_dataframes)} fichier(s).")
        
        # Aperçu du résultat combiné
        st.subheader("📊 Aperçu du résultat combiné")
        
        # Statistiques par centre
        st.write("**Répartition par centre :**")
        centre_stats = combined_df.groupby('Centre').agg({
            'Decharge': ['count', 'sum']
        }).round(0)
        centre_stats.columns = ['Nombre de lignes', 'Total décharge']
        st.dataframe(centre_stats)
        
        # Aperçu des premières lignes
        st.write("**Premières lignes du fichier combiné :**")
        st.dataframe(combined_df.head(15))
        
        # Conversion en Excel pour téléchargement
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            combined_df.to_excel(writer, index=False, sheet_name='Decharges')
        excel_data = output.getvalue()
        
        # Nom du fichier de sortie
        if len(all_dataframes) == 1:
            # Un seul fichier : utiliser le nom original
            result = results[0]
            output_filename = f'Decharges_{result["centre"]}_{result["mois"]}_{result["annee"]}.xlsx'
        else:
            # Plusieurs fichiers : nom générique
            output_filename = f'Decharges_Combines_{len(all_dataframes)}_centres.xlsx'
        
        # Bouton de téléchargement
        st.download_button(
            label=f"⬇️ Télécharger le fichier combiné ({len(all_dataframes)} centre(s))",
            data=excel_data,
            file_name=output_filename,
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        st.error("❌ Aucun fichier n'a pu être traité avec succès.")

else:
    st.info("👆 Upload un ou plusieurs fichiers Excel pour commencer")
    st.markdown("""
    ### 💡 Comment ça marche :
    
    1. **Clique sur "Browse files"** ou glisse-dépose tes fichiers
    2. **Tu peux sélectionner plusieurs fichiers** en une fois (Ctrl+clic ou Cmd+clic)
    3. Le traitement combine automatiquement tous les centres en un seul fichier
    
    ### 📝 Format attendu des fichiers :
    - Nom : `MM-JJ_xxx_Centre.xlsx` (exemple: `01-26_Décharge_Bafia.xlsx`)
    - Le fichier doit contenir les colonnes de données standard
    
    ### ✨ Nouveauté :
    - Upload **plusieurs fichiers** à la fois
    - Obtiens **un seul Excel** avec tous les centres combinés
    """)
