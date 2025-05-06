import streamlit as st
import pandas as pd
import os
import zipfile
import tempfile
from docxtpl import DocxTemplate
import unicodedata

st.set_page_config(page_title="Generatore Certificati DOCX", layout="centered")
st.title("📄 Generatore massivo di certificati - compatibile con Excel con spazi")

# Funzione per "pulire" i nomi delle colonne
def normalizza_nome(nome):
    # Rimuove accenti e caratteri speciali, spazi e li trasforma in PascalCase
    nome = unicodedata.normalize('NFKD', nome).encode('ASCII', 'ignore').decode('utf-8')
    return ''.join([word.capitalize() for word in nome.replace("-", " ").split()])

# Upload file
excel_file = st.file_uploader("📥 Carica il file Excel (.xlsx)", type=["xlsx"])
word_template = st.file_uploader("📄 Carica il template Word (.docx)", type=["docx"])

if excel_file and word_template:
    df_raw = pd.read_excel(excel_file)
    
    # Mappa colonne originali -> normalizzate
    originali = df_raw.columns
    colonne_pulite = [normalizza_nome(col) for col in originali]
    mappa_colonne = dict(zip(colonne_pulite, originali))
    
    # Ricrea il DataFrame con colonne pulite
    df = df_raw.rename(columns={v: k for k, v in mappa_colonne.items()})
    
    st.success("Excel caricato. Colonne usabili (formato pulito):")
    st.write(list(df.columns))

    # Campo per rinominare i file
    filename_field = st.selectbox("📝 Seleziona il campo da usare per rinominare i file", df.columns)

    if st.button("🚀 Genera certificati"):
        with st.spinner("Creazione documenti in corso..."):
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "certificati_word.zip")
            docx_files = []

            for _, row in df.iterrows():
                context = row.to_dict()
                doc = DocxTemplate(word_template)
                doc.render(context)

                filename = str(row[filename_field]).strip().replace(" ", "_")
                filepath = os.path.join(temp_dir, f"{filename}.docx")
                doc.save(filepath)
                docx_files.append(filepath)

            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in docx_files:
                    zipf.write(file, arcname=os.path.basename(file))

            st.success("✅ Tutti i file Word sono stati creati.")
            with open(zip_path, "rb") as f:
                st.download_button("⬇️ Scarica ZIP", f, file_name="certificati_word.zip")
