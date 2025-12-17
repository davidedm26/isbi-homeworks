import streamlit as st
import pandas as pd
import pickle # Mantenuto per completezza

# --- CONFIGURAZIONE E CARICAMENTO DATI ---
DATA_PATH = 'dataset/cleaned_data.csv' 

@st.cache_data
def load_data():
    """
    Carica il dataset già pulito dal file CSV.
    Include la conversione dei tipi di dato.
    """
    try:
        # Carica il CSV
        df = pd.read_csv(DATA_PATH)
        
        # L'unica trasformazione necessaria è la conversione del timestamp
        df['date_time'] = pd.to_datetime(df['date_time'])
        
        # Ordiniamo per sicurezza cronologica
        df = df.sort_values('date_time')
        
        # Conversione dei tipi per le colonne già presenti nel CSV, assicurando siano interi
        # Questo previene problemi di float in analisi (es. 9.0 anziché 9)
        if 'day_of_week' in df.columns:
            df['day_of_week'] = df['day_of_week'].astype('Int64') # Int64 gestisce i NaN se presenti
        if 'month' in df.columns:
            df['month'] = df['month'].astype('Int64')
        if 'hour' in df.columns:
            df['hour'] = df['hour'].astype('Int64')
        if 'year' in df.columns:
             df['year'] = df['year'].astype('Int64')
        
        return df

    except FileNotFoundError:
        st.error(f"⚠️ Errore: File non trovato in '{DATA_PATH}'. Controlla il nome e la cartella.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Errore nel caricamento: {e}")
        return pd.DataFrame()
# --------------------------------------------------------


# Configurazione della pagina (deve essere la prima istruzione)
st.set_page_config(
    page_title="Dashboard Traffico I-94",
    page_icon="🚦",
    layout="wide"
)


# --- TITOLO E INTRODUZIONE ---
st.title("🚦 Dashboard Traffico I-94 — Home")

st.markdown("""
<div style='font-size:1.2em'>
Benvenuto nella dashboard interattiva per l'analisi e la previsione del traffico sulla <b>Interstate 94</b> (Minneapolis - St. Paul)!<br>
<br>
<span style='font-size:1.1em'>
🔍 <b>Analisi & KPI</b>: Esplora indicatori chiave, pattern orari, trend stagionali e l'impatto di meteo e festività.<br>
🔮 <b>Previsione</b>: Simula il traffico futuro con modelli avanzati, scegliendo orizzonti e strategie meteo.<br>
</span>
</div>
""", unsafe_allow_html=True)

with st.container():
    st.info("""
    👈 **Usa il menu laterale** per navigare tra le sezioni principali:
    
    - 🏆 **Analisi & KPI**: cruscotto con grafici, heatmap, confronto tra giornate e meteo.
    - 🔮 **Previsione**: ottieni previsioni sulle condizioni di traffico delle prossime ore o dei prossimi giorni.
    """, icon="📊")
    st.markdown("")
    st.markdown("""
    **📦 Dataset:** Dati orari di traffico, meteo e festività dal tratto urbano della I-94 (2012-2018).
    """)
    st.markdown("**🔗 Fonte dati:**")
    st.code("https://archive.ics.uci.edu/ml/datasets/Metro+Interstate+Traffic+Volume", language=None)

# --- CARICAMENTO DATI PER LA HOME ---
# La funzione load_data ora è definita in questo stesso file
df = load_data()


if not df.empty:
    st.markdown("---")
    st.subheader("🗺️ Area Geografica e Periodo Dati")

    col_map, col_info = st.columns([3, 2])

    with col_map:
        map_data = pd.DataFrame({
            'lat': [44.96],
            'lon': [-93.20]
        })
        st.map(map_data, zoom=10, width='stretch')
        st.caption("<b>Interstate 94</b> tra Minneapolis e Saint Paul, MN (USA)", unsafe_allow_html=True)

    with col_info:
        st.markdown("#### 📅 Periodo di osservazione")
        st.write("Dati orari dal sensore urbano della I-94.")
        start_date = df['date_time'].min().strftime('%d/%m/%Y')
        end_date = df['date_time'].max().strftime('%d/%m/%Y')
        total_obs = df.shape[0]
        st.metric(label="📅 Data Inizio Rilevamenti", value=start_date)
        st.metric(label="📅 Data Fine Rilevamenti", value=end_date)
        st.metric(label="📊 Totale Ore Rilevate", value=f"{total_obs:,}")
        

else:
    st.warning("Caricamento dati in corso... controlla che il file sia nella cartella 'data'.")