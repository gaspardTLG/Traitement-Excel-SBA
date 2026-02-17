import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Traitement Excel SBA", page_icon="📊")

st.title("📊 Traitement des Décharges Excel")
st.write("Upload ton fichier Excel et télécharge le résultat traité.")

# Upload du fichier
uploaded_file = st.file_uploader("Dépose ton fichier Excel ici", type=['xlsx', 'xls'])

if uploaded_file is not None:
    try:
        # Afficher le nom du fichier
        st.success(f"✅ Fichier chargé : {uploaded_file.name}")
        
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
        
        # Afficher les infos extraites
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Centre", centre)
        with col2:
            st.metric("Mois", mois)
        with col3:
            st.metric("Année", annee)
        
        # Traitement du fichier
        with st.spinner('Traitement en cours...'):
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
                raise ValueError("Impossible de trouver le début des données")
            
            st.info(f"🔍 Données détectées à partir de la ligne {start_row + 1}, colonne {data_col}")
            
            # Extraction des données
            ListeType = []
            ListeFamille = []
            ListeClass = []
            ListeDescription = []
            ListeDecharge = []
            
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
                            
                            ListeType.append(INFO)
                            ListeFamille.append(INFO)
                            ListeClass.append(INFO)
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
                raise ValueError("Aucune donnée extraite. Vérifie le format du fichier.")
            
            # Création du nouveau DataFrame
            nouvelles_lignes = pd.DataFrame({
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
            
            st.success(f"✨ Traitement terminé ! {len(nouvelles_lignes)} lignes générées.")
            
            # Aperçu du résultat
            st.subheader("📋 Aperçu du résultat")
            st.dataframe(nouvelles_lignes.head(10))
            
            # Conversion en Excel pour téléchargement
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                nouvelles_lignes.to_excel(writer, index=False)
            excel_data = output.getvalue()
            
            # Bouton de téléchargement
            st.download_button(
                label="⬇️ Télécharger le fichier traité",
                data=excel_data,
                file_name=f'Decharges_{date}_{centre}.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
    
    except Exception as e:
        st.error(f"❌ Erreur lors du traitement : {str(e)}")
        st.write("Vérifie que le format du fichier est correct (nom: MM-JJ_xxx_Centre.xlsx)")
        import traceback
        st.code(traceback.format_exc())

else:
    st.info("👆 Upload un fichier Excel pour commencer")
    st.markdown("""
    ### Format attendu du fichier :
    - Nom : `MM-JJ_xxx_Centre.xlsx` (exemple: `01-26_Décharge_Bafia.xlsx`)
    - Le fichier doit contenir les colonnes de données standard
    """)
