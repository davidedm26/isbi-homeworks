import streamlit as st
import pandas as pd
import numpy as np
import pickle
import altair as alt
import datetime
from datetime import datetime, timedelta

# --- 1. CONFIGURAZIONE ---
st.set_page_config(page_title="Traffic AI Forecast", page_icon="🚦", layout="wide")

st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        background-color: #FF4B4B;
        color: white;
        font-size: 18px;
        font-weight: bold;
        padding: 10px;
        border-radius: 8px;
        border: none;
    }
    div[data-testid="stMetricValue"] {
        font-size: 60px;
        font-weight: bold;
        color: #333;
    }
</style>
""", unsafe_allow_html=True)

MODEL_PATH = 'models/rf_pipeline.pkl'

DATA_PATH = 'dataset/cleaned_data.csv'

@st.cache_resource
def load_model():
    try:
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        st.error(f"Errore caricamento modello: {e}")
        return None

def estimate_background_lags(hour):
    """Restituisce una stima automatica basata sull'ora"""
    if 0 <= hour <= 5: return 500.0
    elif 6 <= hour <= 9: return 4500.0
    elif 10 <= hour <= 15: return 3500.0
    elif 16 <= hour <= 19: return 5000.0
    else: return 2000.0


@st.cache_data
def load_cleaned_data(path=DATA_PATH):
    try:
        df = pd.read_csv(path, parse_dates=['date_time'])
        return df
    except Exception as e:
        st.error(f"Impossibile leggere {path}: {e}")
        return None


def holiday_for_date(df, dt):
    # Cerca nel dataset una festività per la data specificata
    day = dt.normalize()
    mask = df['date_time'].dt.normalize() == day
    if mask.any():
        vals = df.loc[mask, 'holiday'].unique()
        vals = [v for v in vals if str(v).lower() not in ('none', 'nan', 'nan.0')]
        return vals[0] if len(vals) > 0 else None
    return None


def choose_weather_from_last12(combined_df, ref_dt):
    # prende le ultime 12 righe antecedenti a ref_dt (escluse)
    cutoff = ref_dt - pd.Timedelta(hours=12)
    sel = combined_df[(combined_df['date_time'] > cutoff) & (combined_df['date_time'] < ref_dt)]
    if sel.empty:
        return None, None, np.nan, 0.0, 0.0, 0.0
    main = sel['weather_main'].mode()
    desc = sel['weather_description'].mode()
    clouds = sel['clouds_all'].median()
    temp = sel['temp'].iloc[-1] if 'temp' in sel.columns else sel['temp'].mean()
    rain = sel['rain_1h'].max() if 'rain_1h' in sel.columns else 0.0
    snow = sel['snow_1h'].max() if 'snow_1h' in sel.columns else 0.0
    return (main.iloc[0] if not main.empty else None,
            desc.iloc[0] if not desc.empty else None,
            temp,
            rain,
            snow,
            clouds)


def build_feature_row(dt, holiday, is_weekend, weather_main, weather_desc, temp, rain, snow, clouds, lag_1, lag_24, lag_168):
    return {
        'date_time': dt,
        'holiday': holiday,
        'temp': float(temp),
        'rain_1h': float(rain),
        'snow_1h': float(snow),
        'clouds_all': float(clouds),
        'weather_main': weather_main,
        'weather_description': weather_desc,
        'hour': float(dt.hour),
        'day_of_week': float(dt.weekday()),
        'month': float(dt.month),
        'year': float(dt.year),
        'is_weekend': bool(is_weekend),
        'lag_1': float(lag_1),
        'lag_24': float(lag_24),
        'lag_168': float(lag_168)
    }


def render_history_forecast_chart(chart_placeholder, hist_plot_df, preds_df_state):
    """Renderizza (e aggiorna) il grafico persistente storico + previsto."""
    hist_plot_df = hist_plot_df[['date_time', 'traffic_volume']].copy()
    hist_plot_df['date_time'] = pd.to_datetime(hist_plot_df['date_time'])

    hist_series = hist_plot_df.copy()
    hist_series['series'] = 'Storico'

    plot_df = hist_series
    forecast_rule_dt = None
    pred_series = None
    pred_line_series = None
    if isinstance(preds_df_state, pd.DataFrame) and not preds_df_state.empty:
        preds_df_state = preds_df_state[['date_time', 'traffic_volume']].copy()
        preds_df_state['date_time'] = pd.to_datetime(preds_df_state['date_time'])
        pred_series = preds_df_state.copy()
        pred_series['series'] = 'Previsto'
        # Punto ponte: include l'ultima ora nota nella serie "Previsto" per evitare il buco
        # (così la linea rossa collega l'ultimo punto storico al primo previsto)
        last_hist_point = hist_series.sort_values('date_time').tail(1).copy()
        last_hist_point['series'] = 'Previsto'
        if not last_hist_point.empty:
            pred_line_series = pd.concat([last_hist_point, pred_series], ignore_index=True)
        else:
            pred_line_series = pred_series.copy()

        plot_df = pd.concat([hist_series, pred_line_series], ignore_index=True)
        # Riga verticale: in corrispondenza dell'ultimo valore noto (fine storico)
        forecast_rule_dt = pd.to_datetime(last_hist_point['date_time'].iloc[0])

    # Dominio X: padding a destra per decentramento a sinistra e per mostrare tutte le previsioni
    if plot_df.empty:
        chart_placeholder.write("Nessun dato da mostrare.")
        return

    x_start_full = plot_df['date_time'].min()
    x_end_raw = plot_df['date_time'].max()
    span = (x_end_raw - x_start_full) if pd.notna(x_start_full) and pd.notna(x_end_raw) else pd.Timedelta(hours=24)
    # padding a destra: serve sia per decentramento sia per garantire visibilità del primo punto previsto
    pad = max(pd.Timedelta(hours=18), span * 0.18)
    x_end = x_end_raw + pad

    # Calcola la finestra visibile iniziale: vogliamo includere molto storico nel dataframe
    # ma zoomare inizialmente solo sulla porzione finale proporzionale all'orizzonte di previsione.
    # Prendiamo la scelta di orizzonte salvata in session_state (se presente).
    fc_choice = st.session_state.get('forecast_choice')
    # mappa scelta -> finestra visibile
    choice_map = {
        'Ora successiva': pd.Timedelta(hours=6),
        'Oggi': pd.Timedelta(hours=24),
        'Oggi e Domani': pd.Timedelta(days=2),
        'Prossimi 3gg': pd.Timedelta(days=3),
        'Prossima settimana': pd.Timedelta(days=7),
        'Prossimo mese': pd.Timedelta(days=30)
    }
    # fallback: se non c'è scelta previsione, usa il range storico selezionato (se presente)
    hist_choice = st.session_state.get('traffic_hist_choice')
    hist_map = {
        '24h': pd.Timedelta(hours=24),
        '3gg': pd.Timedelta(days=3),
        '1sett': pd.Timedelta(days=7),
        '1 mese': pd.Timedelta(days=30),
        '1 anno': pd.Timedelta(days=365)
    }

    if fc_choice in choice_map:
        visible_span = choice_map[fc_choice]
    elif hist_choice in hist_map:
        visible_span = hist_map[hist_choice]
    else:
        visible_span = pd.Timedelta(days=7)

    # Non mostrare più del range totale disponibile
    visible_span = min(visible_span, span)
    x_visible_start = max(x_start_full, x_end_raw - visible_span)

    # Dominio Y: includi sempre lo zero (serve anche per lo shading della singola ora prevista)
    y_min = 0.0
    y_max = float(plot_df['traffic_volume'].max() * 1.05) if not plot_df.empty else 1.0
    y_scale = alt.Scale(domain=[y_min, y_max])

    line_colors = alt.Scale(domain=['Storico', 'Previsto'], range=['gray', '#FF4B4B'])

    hist_area = alt.Chart(hist_plot_df).mark_area(opacity=0.12, color='lightgray').encode(
        x=alt.X('date_time:T', scale=alt.Scale(domain=[x_visible_start, x_end])),
        y=alt.Y('traffic_volume:Q', scale=y_scale)
    )
    lines = alt.Chart(plot_df).mark_line(strokeWidth=2).encode(
        x=alt.X('date_time:T', scale=alt.Scale(domain=[x_visible_start, x_end])),
        y=alt.Y('traffic_volume:Q', scale=y_scale),
        color=alt.Color('series:N', scale=line_colors, legend=alt.Legend(title=None))
    )

    layers = [hist_area]

    # Rosso SOLO area sottesa alle previsioni
    if pred_series is not None and not pred_series.empty:
        # Usa la serie con punto ponte per colorare anche il tratto ultimo noto -> prima previsione
        area_df = pred_line_series if isinstance(pred_line_series, pd.DataFrame) and not pred_line_series.empty else pred_series

        if len(area_df) >= 2:
            forecast_area = alt.Chart(area_df).mark_area(opacity=0.18, color='#FF4B4B').encode(
                x=alt.X('date_time:T', scale=alt.Scale(domain=[x_visible_start, x_end])),
                y=alt.Y('traffic_volume:Q', scale=y_scale)
            )
            layers.append(forecast_area)
        else:
            # Caso 1 sola previsione: l'area non si vede (serve almeno 2 punti).
            # Usa una barra semitrasparente per rendere visibile lo shading della prima ora prevista.
            forecast_bar = alt.Chart(pred_series).mark_bar(opacity=0.18, color='#FF4B4B', size=16).encode(
                x=alt.X('date_time:T', scale=alt.Scale(domain=[x_visible_start, x_end])),
                y=alt.Y('traffic_volume:Q', scale=y_scale),
                y2=alt.value(y_min)
            )
            layers.append(forecast_bar)

    layers.append(lines)

    # Pallino SOLO sull'ultima previsione corrente
    if pred_series is not None and not pred_series.empty:
        last_pred_point = pred_series.sort_values('date_time').tail(1)
        pred_point = alt.Chart(last_pred_point).mark_circle(size=80, color='#FF4B4B').encode(
            x=alt.X('date_time:T', scale=alt.Scale(domain=[x_visible_start, x_end])),
            y=alt.Y('traffic_volume:Q', scale=y_scale),
            tooltip=['date_time:T', 'traffic_volume:Q']
        )
        layers.append(pred_point)

    if forecast_rule_dt is not None:
        rule_df = pd.DataFrame({'date_time': [forecast_rule_dt]})
        rule = alt.Chart(rule_df).mark_rule(color='#FF4B4B', strokeDash=[6, 6]).encode(
            x=alt.X('date_time:T', scale=alt.Scale(domain=[x_visible_start, x_end]))
        )
        layers.append(rule)

    chart_placeholder.altair_chart(alt.layer(*layers).interactive(), width='stretch')

# --- LISTE OPZIONI ---
holiday_options = [
    'Nessuna (Giorno normale)', 
    'Christmas Day', 'Columbus Day', 'Independence Day', 'Labor Day',
    'Martin Luther King Jr Day', 'Memorial Day', 'New Years Day',
    'State Fair', 'Thanksgiving Day', 'Veterans Day', 'Washingtons Birthday'
]

# Mappa Meteo (UI -> Input Modello)
weather_map = {
    'Clear':        {'main': 'Clear',        'desc': 'sky is clear'},
    'Clouds':       {'main': 'Clouds',       'desc': 'scattered clouds'}, 
    'Rain':         {'main': 'Rain',         'desc': 'light rain'},
    'Drizzle':      {'main': 'Drizzle',      'desc': 'drizzle'},
    'Mist':         {'main': 'Mist',         'desc': 'mist'},
    'Haze':         {'main': 'Haze',         'desc': 'haze'},
    'Fog':          {'main': 'Fog',          'desc': 'fog'},
    'Thunderstorm': {'main': 'Thunderstorm', 'desc': 'thunderstorm'},
    'Snow':         {'main': 'Snow',         'desc': 'light snow'},
    'Squall':       {'main': 'Squall',       'desc': 'squalls'}, 
    'Smoke':        {'main': 'Smoke',        'desc': 'smoke'}
}

# --- INTERFACCIA ---
st.title("🚦 AI Traffic Predictor")
st.markdown("---")

pipeline = load_model()

if pipeline is not None:

    # --- SEZIONE: Previsioni iterative a partire dall'ultimo record del dataset ---
    #st.markdown("---")
    st.markdown("### 🔁 Previsioni del traffico")

    cleaned_df = load_cleaned_data()
    if cleaned_df is None:
        st.warning("Dataset non caricato: assicurati che cleaned_data.csv esista nella cartella.")
    else:
        last_dt = cleaned_df['date_time'].max()
        st.write(f"Data ultimi dati storici registrati: {last_dt}")

        next_dt = last_dt + pd.Timedelta(hours=1)

        # Storico sempre visibile (grafico persistente): usiamo session_state per non perdere i punti previsti
        history_windows = {
            '24h': pd.Timedelta(hours=24),
            '3gg': pd.Timedelta(days=3),
            '1sett': pd.Timedelta(days=7),
            '1 mese': pd.Timedelta(days=30),
            '1 anno': pd.Timedelta(days=365)
        }

        if 'traffic_hist_choice' not in st.session_state:
            st.session_state['traffic_hist_choice'] = '24h'
        if 'traffic_preds_df' not in st.session_state:
            st.session_state['traffic_preds_df'] = None
        if 'traffic_generated_full_df' not in st.session_state:
            st.session_state['traffic_generated_full_df'] = None

        # Layout a 2 colonne: controlli a sinistra, grafico a destra (meno scroll)
        left_panel, right_panel = st.columns([1, 2], gap="large")
        with left_panel:
            st.selectbox(
                "Range temporale di osservazione:",
                list(history_windows.keys()),
                key='traffic_hist_choice'
            )

            if st.button("↩️ Reset previsioni"):
                st.session_state['traffic_preds_df'] = None
                st.session_state['traffic_generated_full_df'] = None

            #st.caption("Genera le previsioni: il grafico a destra si aggiorna e si estende.")

            # Form: evita rerun continui mentre cambi controlli
            with st.form("multi_forecast_form", clear_on_submit=False):
                choice = st.radio(
                    "Orizzonte previsioni:",
                    ("Ora successiva", "Oggi", "Oggi e Domani", "Prossimi 3gg", "Prossima settimana", "Prossimo mese"),
                    horizontal=False
                )
                generate = st.form_submit_button("▶️ Genera previsioni")

        hist_choice = st.session_state['traffic_hist_choice']
        delta = history_windows[hist_choice]
        if delta is None:
            hist_df = cleaned_df.copy()
        else:
            hist_df = cleaned_df[cleaned_df['date_time'] >= (last_dt - delta)].copy()

        hist_plot_df = hist_df[['date_time', 'traffic_volume']].copy()
        if hist_plot_df.empty:
            hist_plot_df = pd.DataFrame({'date_time': pd.to_datetime([]), 'traffic_volume': []})

        # Grafico a destra (sempre visibile)
        with right_panel:
            chart_placeholder = st.empty()
            preds_df_state = st.session_state.get('traffic_preds_df')
            render_history_forecast_chart(chart_placeholder, hist_plot_df, preds_df_state)

        if generate:
            # Modalità incrementale: se scegli "Ora successiva", estendi le previsioni già presenti
            incremental = (choice == "Ora successiva")

            existing_full = st.session_state.get('traffic_generated_full_df')
            if incremental and isinstance(existing_full, pd.DataFrame) and not existing_full.empty:
                base_working = pd.concat([cleaned_df, existing_full], ignore_index=True, sort=False)
                base_working = base_working.sort_values('date_time').reset_index(drop=True)
                start_dt = base_working['date_time'].max() + pd.Timedelta(hours=1)
            else:
                # per gli altri orizzonti (o primo run), rigenera da fine dataset e resetta lo stato previsione
                st.session_state['traffic_generated_full_df'] = None
                st.session_state['traffic_preds_df'] = None
                base_working = cleaned_df.copy().sort_values('date_time').reset_index(drop=True)
                start_dt = base_working['date_time'].max() + pd.Timedelta(hours=1)

            # Calcolo ore da prevedere in base alla scelta (a partire da start_dt)
            if choice == "Ora successiva":
                hours_to_forecast = 1
            elif choice == "Oggi":
                end_dt = datetime.combine(start_dt.date(), datetime.max.time()).replace(hour=23, minute=0, second=0, microsecond=0)
                hours_to_forecast = int((end_dt - start_dt) / pd.Timedelta(hours=1)) + 1
                hours_to_forecast = max(1, hours_to_forecast)
            elif choice == "Oggi e Domani":
                end_dt = datetime.combine((start_dt + pd.Timedelta(days=1)).date(), datetime.max.time()).replace(hour=23, minute=0, second=0, microsecond=0)
                hours_to_forecast = int((end_dt - start_dt) / pd.Timedelta(hours=1)) + 1
                hours_to_forecast = max(1, hours_to_forecast)
            elif choice == "Prossimi 3gg":
                hours_to_forecast = 72
            elif choice == "Prossima settimana":
                hours_to_forecast = 168
            elif choice == "Prossimo mese":
                hours_to_forecast = 720
            else:
                hours_to_forecast = 1

            preds = []
            working = base_working.copy()
            newly_generated_rows = []

            # valore iniziale per lag_1 = ultimo traffico del dataset
            last_known_traffic = working['traffic_volume'].iloc[-1]

            current_dt = start_dt
            for i in range(int(hours_to_forecast)):
                # holiday mapping basata sul dataset
                hol = holiday_for_date(working, current_dt)
                is_weekend = current_dt.weekday() >= 5

                # scegli meteo basato sulle ultime 12h
                wm, wd, temp_sel, rain_sel, snow_sel, clouds_sel = choose_weather_from_last12(working, current_dt)
                if wm is None:
                    # fallback: prendi ultimo record
                    last = working.iloc[-1]
                    wm = last['weather_main']
                    wd = last['weather_description']
                    temp_sel = last['temp']
                    rain_sel = last.get('rain_1h', 0.0)
                    snow_sel = last.get('snow_1h', 0.0)
                    clouds_sel = last.get('clouds_all', 0.0)

                # lag_1 è l'ultimo valore noto (predetto o reale)
                lag_1_val = last_known_traffic

                # lag_24 e lag_168: cerchiamo nel working dataframe
                ts_24 = current_dt - pd.Timedelta(hours=24)
                ts_168 = current_dt - pd.Timedelta(hours=168)

                row_24 = working[working['date_time'] == ts_24]
                row_168 = working[working['date_time'] == ts_168]

                lag_24_val = row_24['traffic_volume'].iloc[0] if not row_24.empty else lag_1_val
                lag_168_val = row_168['traffic_volume'].iloc[0] if not row_168.empty else lag_1_val

                feat = build_feature_row(current_dt, hol, is_weekend, wm, wd, temp_sel, rain_sel, snow_sel, clouds_sel, lag_1_val, lag_24_val, lag_168_val)

                # dataframe per il predict (no date_time)
                X = pd.DataFrame([feat])
                X = X.drop(columns=['date_time'])
                # assicurarsi tipi giusti
                X['holiday'] = X['holiday'].astype(object)
                X['weather_main'] = X['weather_main'].astype(object)
                X['weather_description'] = X['weather_description'].astype(object)

                try:
                    yhat = pipeline.predict(X)[0]
                    yhat = int(max(0, yhat))
                except Exception as e:
                    st.error(f"Errore predizione iterativa: {e}")
                    break

                # append ai risultati e al working dataframe (affinché i lag futuri usino le predizioni)
                preds.append({'date_time': current_dt, 'traffic_volume': yhat})

                new_row = {**feat}
                new_row['traffic_volume'] = yhat
                newly_generated_rows.append(new_row)
                working = pd.concat([working, pd.DataFrame([new_row])], ignore_index=True, sort=False)

                # aggiorna last_known_traffic e passo avanti di un'ora
                last_known_traffic = yhat
                current_dt = current_dt + pd.Timedelta(hours=1)

            if len(preds) == 0:
                st.info("Nessuna previsione generata.")
            else:
                df_preds = pd.DataFrame(preds)
                df_preds_display = df_preds.copy()
                df_preds_display['date_time'] = pd.to_datetime(df_preds_display['date_time'])

                # aggiorna lo stato incrementale completo (con feature) per futuri step
                new_full_df = pd.DataFrame(newly_generated_rows)
                if incremental and isinstance(existing_full, pd.DataFrame) and not existing_full.empty:
                    full_df = pd.concat([existing_full, new_full_df], ignore_index=True, sort=False)
                else:
                    full_df = new_full_df
                st.session_state['traffic_generated_full_df'] = full_df

                # Persisti previsioni leggere per il grafico (date_time, traffic_volume)
                prev_preds_df = st.session_state.get('traffic_preds_df')
                if incremental and isinstance(prev_preds_df, pd.DataFrame) and not prev_preds_df.empty:
                    all_preds = pd.concat([prev_preds_df, df_preds_display], ignore_index=True)
                else:
                    all_preds = df_preds_display
                all_preds = all_preds.drop_duplicates(subset=['date_time']).sort_values('date_time').reset_index(drop=True)

                st.session_state['traffic_preds_df'] = all_preds.copy()

                # Aggiorna subito il grafico nello stesso run
                render_history_forecast_chart(chart_placeholder, hist_plot_df, st.session_state['traffic_preds_df'])


        # Mostra SEMPRE le previsioni già generate (non devono sparire cambiando lo storico)
        preds_to_show = st.session_state.get('traffic_preds_df')
        if isinstance(preds_to_show, pd.DataFrame) and not preds_to_show.empty:
            with right_panel:
                st.write("### Previsioni generate")

                metrics_df = preds_to_show
                total_pred = int(metrics_df['traffic_volume'].sum())
                peak_pred = int(metrics_df['traffic_volume'].max())
                avg_pred = int(metrics_df['traffic_volume'].mean())
                mcol1, mcol2, mcol3 = st.columns(3)
                mcol1.metric(label="Totale", value=f"{total_pred}")
                mcol2.metric(label="Picco", value=f"{peak_pred}")
                mcol3.metric(label="Media", value=f"{avg_pred}")

                st.write("Tabella previsioni")
                st.dataframe(preds_to_show, width='stretch', height=260)

    st.markdown("---")
    st.markdown("### 🔁 Fai una Previsione!")

    with st.container():
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 📅 Data e Ora")
            d_date = st.date_input("Giorno", value=datetime.now())
            # Salviamo l'orario in una variabile per calcolare i lag di default
            t_time = st.time_input("Orario", value=datetime.now())
            st.markdown("### 🗓️ Contesto")
            selected_holiday = st.selectbox("Giorno Festivo", holiday_options)
            # is_weekend_input rimosso: ora viene calcolato automaticamente

        with col2:
            st.markdown("### ☁️ Meteo")
            # Temperatura in CELSIUS (come da tuo CSV)
            temp_c = st.slider("Temperatura (°C)", -20, 40, 20) 
            
            weather_ui = st.selectbox("Condizione Cielo", list(weather_map.keys()))
            clouds = st.slider("Copertura Nuvole (%)", 0, 100, 20)

        with col3:
            st.markdown("### ☔ Dettagli")
            rain = st.number_input("Pioggia (mm)", 0.0, 100.0, 0.0, step=0.1)
            snow = st.number_input("Neve (mm)", 0.0, 100.0, 0.0, step=0.1)

    # --- PARTE 2: INPUT AVANZATI (LAG) ---
    st.markdown("---")
    
    # Calcoliamo il valore suggerito in base all'ora scelta sopra
    default_lag_val = float(estimate_background_lags(t_time.hour))
    # Calcolo automatico weekend
    is_weekend_input = (d_date.weekday() >= 5)

    with st.expander("🛠️ Dati Storici Avanzati (Opzionale)"):
        st.info("Questi valori sono stimati automaticamente in base all'ora scelta. Se conosci i dati reali del traffico precedente, puoi modificarli qui.")
        col_lag1, col_lag2, col_lag3 = st.columns(3)
        
        with col_lag1:
            # Lag 1: Il valore di default cambia se l'utente cambia l'orario sopra
            input_lag_1 = st.number_input("Traffico 1 ora fa", value=default_lag_val, step=100.0)
        with col_lag2:
            input_lag_24 = st.number_input("Traffico Ieri (stessa ora)", value=default_lag_val, step=100.0)
        with col_lag3:
            input_lag_168 = st.number_input("Traffico 7gg fa (stessa ora)", value=default_lag_val, step=100.0)

    # --- PARTE 3: BOTTONE E CALCOLO ---
    st.markdown("<br>", unsafe_allow_html=True)
    col_btn_1, col_btn_2, col_btn_3 = st.columns([1, 2, 1])
    with col_btn_2:
        predict_btn = st.button("🔮 CALCOLA TRAFFICO")

    if predict_btn:
        dt = datetime.combine(d_date, t_time)
        
        # 1. Holiday: None se "Nessuna"
        if selected_holiday == 'Nessuna (Giorno normale)':
            final_holiday = None 
        else:
            final_holiday = selected_holiday 
            
        # 2. Meteo
        w_data = weather_map[weather_ui]
        
        # 3. Costruzione Input (Usando i Lag manuali)
        input_data = {
            'holiday': [final_holiday],          
            'temp': [float(temp_c)],             
            'rain_1h': [float(rain)],
            'snow_1h': [float(snow)],
            'clouds_all': [float(clouds)],       
            'weather_main': [w_data['main']],        # Es: "Clouds"
            'weather_description': [w_data['desc']], # Es: "scattered clouds"
            'hour': [float(dt.hour)],            
            'day_of_week': [float(dt.weekday())],
            'month': [float(dt.month)],
            'year': [float(dt.year)],            
            'is_weekend': [is_weekend_input],    # ora calcolato automaticamente
            # QUI usiamo le variabili dell'expander
            'lag_1': [float(input_lag_1)],
            'lag_24': [float(input_lag_24)],
            'lag_168': [float(input_lag_168)]
        }

        df = pd.DataFrame(input_data)
        
        # 4. Gestione Tipi (Anti-Crash)
        df['holiday'] = df['holiday'].astype(object)
        df['weather_main'] = df['weather_main'].astype(object)
        df['weather_description'] = df['weather_description'].astype(object)

        try:
            prediction = pipeline.predict(df)[0]
            prediction = int(max(0, prediction))

            st.markdown("<br>", unsafe_allow_html=True)
            res_col1, res_col2 = st.columns([1, 1])
            
            with res_col1:
                st.metric(label="Veicoli Previsti", value=prediction)
            
            with res_col2:
                st.write("### Livello Congestione")
                if prediction < 1000:
                    st.success("🟢 Traffico Scorrevole")
                    st.progress(prediction / 7000)
                elif prediction < 3500:
                    st.warning("🟡 Traffico Moderato")
                    st.progress(prediction / 7000)
                else:
                    st.error("🔴 Traffico Intenso")
                    st.progress(min(1.0, prediction / 7000))

        except Exception as e:
            st.error(f"Errore tecnico: {e}")
            st.write("Dati passati al modello:", df)