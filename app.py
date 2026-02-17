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
        centre = nom.split('_')[2]
        date = nom.split('_')[0]
        
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
            df = pd.read_excel(uploaded_file)
            df.columns = ['1', '2', '3', '4', '5', '6']
            df.drop(columns=['2', '4', '5', '6'], inplace=True)
            
            # Suppression des lignes vides au début
            i = 0
            while str(df.loc[i]['3']) == 'nan':
                df.drop(index=i, inplace=True)
                i += 1
            
            df.reset_index(drop=True, inplace=True)
            
            # Fonction pour retirer les deux-points
            def remove_colon(string):
                if string.endswith(':'):
                    return string[:-1]
                return string
            
            # Extraction des données
            ListeType = []
            ListeFamille = []
            ListeClass = []
            ListeDescription = []
            ListeDecharge = []
            
            j = 0
            while j < len(df):
                INFO = remove_colon(str(df.loc[j]['1']))
                j += 1
                while not df.loc[j].isna().all():
                    ListeType.append(INFO)
                    ListeFamille.append(INFO)
                    ListeClass.append(INFO)
                    DESCR = remove_colon(str(df.loc[j]['3']))
                    MONTANT = df.loc[j]['1']
                    ListeDescription.append(DESCR)
                    ListeDecharge.append(MONTANT)
                    j += 1
                j += 1
                if str(df.loc[j]['3']).upper() in ('TOTAL', 'TOTAL A PAYER', 'SBA', 'TOTAL ' + centre.upper(), 'TOTAL DECHARGE ' + centre.upper()):
                    break
            
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

else:
    st.info("👆 Upload un fichier Excel pour commencer")
    st.markdown("""
    ### Format attendu du fichier :
    - Nom : `MM-JJ_xxx_Centre.xlsx` (exemple: `01-26_Décharge_Bafia.xlsx`)
    - Le fichier doit contenir les colonnes de données standard
    """)
