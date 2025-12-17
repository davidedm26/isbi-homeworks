# Avvio del Progetto Streamlit

Per avviare il progetto Streamlit, segui questi passaggi:

1. **Crea e attiva un ambiente virtuale (opzionale ma consigliato)**  
    È consigliato utilizzare un ambiente virtuale per isolare le dipendenze del progetto.  
    Su Windows:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    ```
    Su macOS/Linux:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2. **Installa le dipendenze**  
    Assicurati di avere Python installato. Poi, installa Streamlit e le altre dipendenze:
    ```bash
    pip install -r requirements.txt
    ```

3. **Avvia l'applicazione**  
    Esegui il comando:
    ```bash
    streamlit run nome_file_app.py
    ```
    Sostituisci `nome_file_app.py` con il nome del file principale dell'app Streamlit.

4. **Accedi all'app**  
    Dopo l'avvio, Streamlit aprirà automaticamente il browser all'indirizzo [http://localhost:8501](http://localhost:8501).

---

**Nota:** Se hai bisogno di ulteriori dettagli, consulta la documentazione ufficiale di [Streamlit](https://docs.streamlit.io/).