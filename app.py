import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Traitement Excel SBA", page_icon="📊")

# Dictionnaire de mapping pour Famille
MAPPING_DICT = {
    'internet': 'Infrastructure',
    'electricité': 'Frais de fonctionnement',
    'eau': 'Frais de fonctionnement',
    'assainissement': 'Infrastructure',
    'déchets': 'Infrastructure',
    'pépites': 'Projets',
    'pepites': 'Projets',
    'défraiements': 'Defraiements',
    'défraiement' :'Defraiements',
    'defraiements' : 'Defraiements',
    'defraiement': 'Defraiements',
    'chef': 'Defraiements',
    'loyer': 'Frais de fonctionnement',
    'nutrition': 'Santé',
    'médicaments': 'Santé',
    'médical': 'Santé',
    'rugby': 'Rugby',
    'etudiants' : 'Education',
    'étudiants' : 'Education', 
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
    'icam': 'Education',
    'ess-ucac': 'Education',
    'voiture': 'Infrastructure',
    'ecole': 'Education',
    'particulier': 'Dépenses exceptionnelles',
    'particuliers': 'Dépenses exceptionnelles',
}


CLASSIFICATION_DICT = {
    'bac' : 'Education',
    'rugby' : 'Rugby',
    'eau' : 'Infrastructures',
    'Médical' : 'Santé/Genre',
    'transport' : 'Infrastructures',
    'chef de centre' : 'Education',
    'imprévus' : 'Imprévus',
    'internet' : 'Infrastructures',
    'enseignant' : 'Education',
    'nutrition' : 'Santé/Genre',
    'loyer' : 'Infrastructures',
    'scolaires' : 'Education',
    'couture' : 'Santé/Genre',
    'administratif' : 'Infrastructures',
    'electricité' : 'Infrastructures', 
    'pépites' : 'Pépites'
}


def get_famille(type_text):
    type_lower = type_text.lower().strip()
    for key, value in MAPPING_DICT.items():
        if key in type_lower:
            return value, True
    return "Aucune info", False


def get_classification(type_text):
    type_lower = type_text.lower().strip()
    for key, value in CLASSIFICATION_DICT.items():
        if key in type_lower:
            return value, True
    return "Aucune info", False


st.title("📊 Traitement des Décharges Excel")
st.write("Upload un ou plusieurs fichiers Excel et télécharge le résultat combiné.")

uploaded_files = st.file_uploader(
    "Dépose tes fichiers Excel ici (tu peux en sélectionner plusieurs)", 
    type=['xlsx', 'xls'],
    accept_multiple_files=True
)

if uploaded_files:
    st.success(f"✅ {len(uploaded_files)} fichier(s) chargé(s)")
    
    all_dataframes = []
    
    def process_file(uploaded_file):
        """Traite un fichier Excel et retourne le DataFrame résultant"""
        try:
            nom = uploaded_file.name.split('.')[0]
            parts = nom.split('_')
            pays = "Cameroun"
            date = parts[0]
            centre = '_'.join(parts[2:])
            centre = centre.replace("-"," ").replace("_"," ")
            if centre.lower() == "mali":
                pays = "Mali"
            
            mois = int(date.split('-')[0])
            annee = int("20" + date.split('-')[1])
            date = str(mois) + "-" + str(annee)
            
            df = pd.read_excel(uploaded_file, header=None)
            
            def remove_colon(string):
                string = str(string).strip()
                if string.endswith(':'):
                    return string[:-1].strip()
                return string
            
            start_row = None
            data_col = None
            amount_col = None
            
            for i in range(min(50, len(df))):
                for j in range(len(df.columns)):
                    val = df.iloc[i, j]
                    if pd.notna(val) and isinstance(val, str):
                        if ':' in val and not val.startswith('Tel') and 'Période' not in val:
                            start_row = i
                            data_col = j
                            amount_col = j
                            break
                if start_row is not None:
                    break
            
            if start_row is None:
                raise ValueError(f"Impossible de trouver le début des données dans {uploaded_file.name}")
            
            ListeType = []
            ListeFamille = []
            ListeClassification = []
            ListeDescription = []
            ListeDecharge = []
            unfound_famille = []
            unfound_classification = []
            
            i = start_row
            while i < len(df):
                row = df.iloc[i]
                val = row[data_col]
                
                if pd.notna(val) and isinstance(val, str) and ':' in val:
                    INFO = remove_colon(val)
                    i += 1
                    
                    while i < len(df):
                        row = df.iloc[i]
                        
                        if row.isna().all():
                            i += 1
                            break
                        
                        val_check = row[data_col]
                        if pd.notna(val_check) and isinstance(val_check, str) and ':' in val_check:
                            break
                        
                        montant = row[amount_col]
                        if pd.notna(montant) and (isinstance(montant, (int, float)) or str(montant).replace(' ', '').isdigit()):
                            description = None
                            for col in range(len(df.columns)):
                                if col != amount_col:
                                    desc_val = row[col]
                                    if pd.notna(desc_val) and isinstance(desc_val, str) and desc_val.strip() and ':' not in desc_val:
                                        description = remove_colon(desc_val)
                                        break
                            
                            if description is None:
                                description = INFO
                            
                            famille, found_f = get_famille(INFO)
                            if not found_f and INFO not in unfound_famille:
                                unfound_famille.append(INFO)

                            classification, found_c = get_classification(INFO)
                            if not found_c and INFO not in unfound_classification:
                                unfound_classification.append(INFO)
                            
                            ListeType.append(INFO)
                            ListeFamille.append(famille)
                            ListeClassification.append(classification)
                            ListeDescription.append(description)
                            ListeDecharge.append(montant)
                        
                        i += 1
                        
                        for col in range(len(df.columns)):
                            check_val = row[col]
                            if pd.notna(check_val) and isinstance(check_val, str):
                                upper_val = check_val.upper()
                                if 'TOTAL' in upper_val:
                                    if 'DECHARGE' in upper_val or centre.upper() in upper_val:
                                        i = len(df)  
                                        break
                        
                        if i >= len(df):
                            break
                else:
                    i += 1
                
                if i < len(df):
                    for col in range(len(df.columns)):
                        check_val = df.iloc[i, col] if i < len(df) else None
                        if pd.notna(check_val) and isinstance(check_val, str):
                            upper_val = str(check_val).upper()
                            if 'TOTAL' in upper_val:
                                if 'DECHARGE' in upper_val or centre.upper() in upper_val:
                                    i = len(df)
                                    break
            
            if len(ListeDecharge) == 0:
                raise ValueError(f"Aucune donnée extraite dans {uploaded_file.name}")
            
            df_result = pd.DataFrame({
                'Pays':           [pays]  * len(ListeFamille),
                'Centre':         [centre] * len(ListeFamille),
                'Type':           ListeType,
                'Famille':        ListeFamille,
                'Classification': ListeClassification,   # ← nouvelle colonne
                'Description':    ListeDescription,
                'Mois':           [mois]  * len(ListeFamille),
                'Annee':          [annee] * len(ListeFamille),
                'Ref':            [date]  * len(ListeFamille),
                'Decharge':       ListeDecharge
            })
            
            return {
                'success': True,
                'filename': uploaded_file.name,
                'centre': centre,
                'mois': mois,
                'annee': annee,
                'lignes': len(df_result),
                'dataframe': df_result,
                'unfound_famille': unfound_famille,
                'unfound_classification': unfound_classification,
            }
            
        except Exception as e:
            return {
                'success': False,
                'filename': uploaded_file.name,
                'error': str(e)
            }
    
    with st.spinner('Traitement en cours...'):
        results = []
        for uploaded_file in uploaded_files:
            result = process_file(uploaded_file)
            results.append(result)
            if result['success']:
                all_dataframes.append(result['dataframe'])
    
    st.subheader("📋 Résumé du traitement")
    
    success_count = sum(1 for r in results if r['success'])
    error_count = len(results) - success_count
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("✅ Fichiers traités avec succès", success_count)
    with col2:
        st.metric("❌ Fichiers en erreur", error_count)
    
    for result in results:
        if result['success']:
            st.success(f"✓ **{result['filename']}** : {result['centre']} - {result['mois']} {result['annee']} ({result['lignes']} lignes)")
        else:
            st.error(f"✗ **{result['filename']}** : {result['error']}")
    
    # Warnings Famille
    all_unfound_f = []
    for result in results:
        if result['success'] and result.get('unfound_famille'):
            all_unfound_f.extend(result['unfound_famille'])
    unique_unfound_f = list(set(all_unfound_f))
    if unique_unfound_f:
        st.warning(f"⚠️ **Famille non trouvée** : {', '.join(unique_unfound_f)}")

    # Warnings Classification
    all_unfound_c = []
    for result in results:
        if result['success'] and result.get('unfound_classification'):
            all_unfound_c.extend(result['unfound_classification'])
    unique_unfound_c = list(set(all_unfound_c))
    if unique_unfound_c:
        st.info(f"ℹ️ **Classification non trouvée** (CLASSIFICATION_DICT vide ou clé manquante) : {', '.join(unique_unfound_c)}")
    
    if all_dataframes:
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        
        st.success(f"✨ Traitement terminé ! **{len(combined_df)} lignes au total** dans {len(all_dataframes)} fichier(s).")
        
        st.subheader("📊 Aperçu du résultat combiné")
        
        st.write("**Répartition par centre :**")
        centre_stats = combined_df.groupby('Centre').agg({
            'Decharge': ['count', 'sum']
        }).round(0)
        centre_stats.columns = ['Nombre de lignes', 'Total décharge']
        st.dataframe(centre_stats)
        
        st.write("**Premières lignes du fichier combiné :**")
        st.dataframe(combined_df.head(15))
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            combined_df.to_excel(writer, index=False, sheet_name='Decharges')
        excel_data = output.getvalue()
        
        if len(all_dataframes) == 1:
            result = results[0]
            output_filename = f'Decharges_{result["centre"]}_{result["mois"]}_{result["annee"]}.xlsx'
        else:
            output_filename = f'Decharges_Combines_{len(all_dataframes)}_centres.xlsx'
        
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
