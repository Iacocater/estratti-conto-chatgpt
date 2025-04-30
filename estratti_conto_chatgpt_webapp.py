
import streamlit as st
import fitz  # PyMuPDF
import openai
import pandas as pd
import json
from io import BytesIO

# Inserisci qui la tua API Key di OpenAI
import os
openai.api_key = os.getenv("OPENAI_API_KEY")

def estrai_testo_da_pdf(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        return "\n".join([page.get_text() for page in doc])[:3000]

def estrai_dati_chatgpt(testo):
    prompt = f"""
Il seguente testo proviene da un estratto conto assicurativo. Estrai e restituisci questi campi in JSON valido:
- Broker
- Data documento (formato gg/mm/aaaa)
- Premio Lordo Totale (€)
- Provvigioni (€)
- Totale Estratto conto (€)

Restituisci SOLO il JSON, senza spiegazioni.

Testo:
\"\"\"
{testo}
\"\"\"
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return json.loads(response["choices"][0]["message"]["content"])
    except Exception as e:
        st.error(f"Errore API: {e}")
        return None

def main():
    st.set_page_config(page_title="Estrazione Estratti Conto", layout="centered")
    st.title("📄 Estrazione Estratti Conto via ChatGPT")
    st.markdown("Carica uno o più file PDF per estrarre i dati e generare un Excel riepilogativo.")

    uploaded_files = st.file_uploader("Carica i PDF", type="pdf", accept_multiple_files=True)

    if uploaded_files and st.button("Estrai dati e genera Excel"):
        risultati = []
        for file in uploaded_files:
            st.info(f"🧾 Elaborazione: {file.name}")
            testo = estrai_testo_da_pdf(file)
            dati = estrai_dati_chatgpt(testo)
            if dati:
                dati["File"] = file.name
                risultati.append(dati)
            else:
                st.warning(f"Nessun dato estratto da {file.name}")

        if risultati:
            df = pd.DataFrame(risultati)
            excel_file = BytesIO()
            df.to_excel(excel_file, index=False)
            excel_file.seek(0)
            st.success("✅ Excel generato con successo!")
            st.download_button("📥 Scarica Excel", data=excel_file, file_name="estratti_conto_chatgpt.xlsx")
        else:
            st.warning("❌ Nessun dato è stato estratto da nessun file.")

if __name__ == "__main__":
    main()
