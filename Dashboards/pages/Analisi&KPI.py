import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pickle # Mantenuto per completezza

# --- CONFIGURAZIONE E CARICAMENTO DATI  ---
DATA_PATH = 'dataset/cleaned_data.csv' 

@st.cache_data
def load_data():
    """
    Carica il dataset già pulito.
    """
    try:
        # Carica il CSV
        df = pd.read_csv(DATA_PATH)
        
        # L'unica trasformazione necessaria è la conversione del timestamp
        df['date_time'] = pd.to_datetime(df['date_time'])
        
        # Ordiniamo per sicurezza cronologica
        df = df.sort_values('date_time')

        # Conversione dei tipi per le colonne già presenti nel CSV
        df['day_of_week'] = df['day_of_week'].astype(int)
        df['month'] = df['month'].astype(int)
        df['hour'] = df['hour'].astype(int)

        # Tronca tutte le colonne float a due cifre decimali
        float_cols = df.select_dtypes(include=['float', 'float64', 'float32']).columns
        df[float_cols] = df[float_cols].apply(lambda x: x.round(2))

        return df

    except FileNotFoundError:
        st.error(f"⚠️ Errore: File non trovato in '{DATA_PATH}'. Controlla il nome e la cartella.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Errore nel caricamento: {e}")
        return pd.DataFrame()
# --------------------------------------------------------


# Configurazione pagina
st.set_page_config(page_title="Analisi & KPI", page_icon="🔍", layout="wide")

st.title("🔍 Analisi Prestazioni e Pattern di Traffico")


def _apply_plot_style(fig, title=None, x_title=None, y_title=None):
    # Evita titoli/label "undefined" in output (succede quando Plotly riceve None lato JS)
    resolved_title = title
    if resolved_title is None:
        resolved_title = fig.layout.title.text if getattr(fig.layout, "title", None) is not None else ""
    if resolved_title is None:
        resolved_title = ""

    fig.update_layout(
        template="plotly_white",
        title=dict(text=resolved_title, x=0.01, xanchor="left"),
        xaxis_title=x_title or "",
        yaxis_title=y_title or "",
        margin=dict(l=20, r=20, t=60, b=20),
        legend_title_text=None,
        hovermode="x unified",
        font=dict(size=13),
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(0,0,0,0.06)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(0,0,0,0.06)")
    return fig


def summarize_day(day_df: pd.DataFrame) -> dict:
    """Riepilogo giornaliero (una riga) per confronto diretto."""
    if day_df.empty:
        return {}

    # Valori categoriali: prendiamo il più frequente (o il primo non nullo)
    def _mode(series):
        series = series.dropna()
        if series.empty:
            return None
        m = series.mode()
        return m.iloc[0] if not m.empty else series.iloc[0]

    holiday_vals = day_df['holiday'].dropna().astype(str).unique().tolist() if 'holiday' in day_df.columns else []
    holiday_vals = [h for h in holiday_vals if h.lower() not in ("none", "nan", "nan.0")]
    holiday_val = holiday_vals[0] if len(holiday_vals) > 0 else "Nessuna"

    return {
        "📅 Giorno settimana": str(day_df.iloc[0].get('nome_giorno', '')),
        "🗓️ Weekend": bool(day_df.iloc[0].get('is_weekend', False)),
        "🎉 Holiday": holiday_val,
        "🌦️ Meteo (main)": _mode(day_df['weather_main']) if 'weather_main' in day_df.columns else None,
        "🌫️ Meteo (desc)": _mode(day_df['weather_description']) if 'weather_description' in day_df.columns else None,
        "🌡️ Temp media (°C)": float(day_df['temp'].mean()) if 'temp' in day_df.columns else None,
        "☁️ Clouds mediana (%)": float(day_df['clouds_all'].median()) if 'clouds_all' in day_df.columns else None,
        "🌧️ Pioggia tot (mm)": float(day_df['rain_1h'].sum()) if 'rain_1h' in day_df.columns else None,
        "❄️ Neve tot (mm)": float(day_df['snow_1h'].sum()) if 'snow_1h' in day_df.columns else None,
        "🚗 Traffico totale": float(day_df['traffic_volume'].sum()) if 'traffic_volume' in day_df.columns else None,
        "🚀 Traffico max": float(day_df['traffic_volume'].max()) if 'traffic_volume' in day_df.columns else None,
        "📈 Traffico medio": float(day_df['traffic_volume'].mean()) if 'traffic_volume' in day_df.columns else None,
    }

# 1. Caricamento Dati
df = load_data()

if not df.empty:
    
    # --- SEZIONE 1: KPI SINTETICI ---
    st.subheader("📊 1. Indicatori Chiave (KPIs)")
    
    avg_traffic = round(df['traffic_volume'].mean(), 2)
    max_traffic = round(df['traffic_volume'].max(), 2)
    min_dt = df['date_time'].min()
    max_dt = df['date_time'].max()
    n_rows = len(df)
    
    # Non è più necessario creare 'hour' qui, usiamo 'traffic_volume'
    busy_hours = df[df['traffic_volume'] > 5000].shape[0] 
    
    # INSERISCI QUI I TUOI VALORI REALI
    mae_model = 150  # esempio: MAE modello
    mae_baseline = 500  # esempio: MAE baseline ora precedente
    
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Traffico medio", f"{avg_traffic:.2f}", help="veicoli/ora medi")
    kpi2.metric("Picco massimo", f"{max_traffic:.2f}", help="numero massimo rilevato di veicoli/ora")
    kpi3.metric("MAE baseline", f"{mae_baseline:.0f}", help="Modello Baseline Traffico ora precedente", delta_color="normal")
    kpi4.metric("MAE modello", f"{mae_model:.0f}", delta=f"{mae_model - mae_baseline:+.0f}", help="Errore medio assoluto del nostro modello RandomForest", delta_color="inverse")
    
    kpi5.metric("Ore congestionate", f"{busy_hours:,}", help="Ora in cui si registrano più di 5.000 veicoli", delta_color="inverse")

    st.caption(f"Periodo dati: {min_dt:%Y-%m-%d} → {max_dt:%Y-%m-%d} • Righe: {n_rows:,}")

    st.markdown("---")

    # --- SEZIONE 2: ANALISI DETTAGLIATA ---
    st.subheader("🧭 2. Esplorazione dei Pattern")

    st.markdown("""
    🚦 In questa sezione analizziamo i **trend temporali** ed **ambientali** del traffico.
    🧩 Usa le schede sottostanti per navigare tra le diverse prospettive:
    """)
    
    # Feature Engineering per i nomi testuali (non sono presenti nel CSV come stringhe)
    day_map = {0: 'Lunedì', 1: 'Martedì', 2: 'Mercoledì', 3: 'Giovedì', 4: 'Venerdì', 5: 'Sabato', 6: 'Domenica'}
    # Utilizzo la colonna 'day_of_week' già presente nel CSV
    df['nome_giorno'] = df['day_of_week'].map(day_map) 
    
    month_map = {1: 'Gen', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'Mag', 6: 'Giu', 7: 'Lug', 8: 'Ago', 9: 'Set', 10: 'Ott', 11: 'Nov', 12: 'Dic'}
    # Utilizzo la colonna 'month' già presente nel CSV
    df['nome_mese'] = df['month'].map(month_map) 

    # 'is_weekend' è già presente, usiamo solo 'tipo_giorno' per il raggruppamento
    df['tipo_giorno'] = df['is_weekend'].apply(lambda x: 'Weekend' if x else 'Feriale')

    # --- TABS ---
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["⏱️ Pattern Orari", "📈 Serie temporale", "📅 Trend Stagionali", "🆚 Confronto Diretto", "🌧️ Traffico & Meteo"])
    
    # --- TAB 1: Pattern Orari ---
    with tab1:
        st.markdown("**🕒 Profilo orario: Feriali vs Weekend**")
        # 'hour' è già disponibile dal CSV
        daily_trend = df.groupby(['hour', 'tipo_giorno'])['traffic_volume'].mean().round(2).reset_index()
        fig_daily = px.line(daily_trend, x='hour', y='traffic_volume', color='tipo_giorno',
                            title='Traffico medio per ora', markers=True,
                            color_discrete_map={'Feriale': '#1f77b4', 'Weekend': '#ff7f0e'})
        fig_daily.update_xaxes(dtick=1)
        _apply_plot_style(fig_daily, title="Traffico medio per ora", x_title="Ora del giorno", y_title="Traffico medio (veicoli/ora)")
        st.plotly_chart(fig_daily, width='stretch')

        #st.markdown("**📦 Distribuzione del traffico per ora (boxplot)**")
        fig_box = px.box(df, x='hour', y='traffic_volume', points=False)
        fig_box.update_xaxes(dtick=1)
        _apply_plot_style(fig_box, title="📦 Distribuzione del traffico per ora", x_title="Ora del giorno", y_title="Traffico (veicoli/ora)")
        st.plotly_chart(fig_box, width='stretch')

    # --- TAB 2: Serie temporale (demo) ---
    with tab2:

        # --- Selettore intervallo data per "tornare indietro nel tempo" ---
        daily_series = df.set_index('date_time')['traffic_volume'].resample('D').mean().round(2).reset_index()
        min_date = daily_series['date_time'].min().date()
        max_date = daily_series['date_time'].max().date()
        default_end = max_date
        default_start = max(max_date - pd.Timedelta(days=29), min_date)

        # Slider solo per andare indietro (non avanti oltre la data massima)
        #st.markdown("**📆 Traffico nel tempo (media giornaliera)**")
        date_range = st.slider(
            "Seleziona intervallo di date",
            min_value=min_date,
            max_value=max_date,
            value=(default_start, default_end),
            format="YYYY-MM-DD",
            step=pd.Timedelta(days=1)
        )
        # Filtro dati in base all'intervallo selezionato
        mask = (daily_series['date_time'].dt.date >= date_range[0]) & (daily_series['date_time'].dt.date <= date_range[1])
        filtered_series = daily_series[mask]
        fig_ts = px.line(filtered_series, x='date_time', y='traffic_volume')
        _apply_plot_style(fig_ts, title="📅 Traffico nel tempo (media giornaliera)", x_title="Data", y_title="Traffico medio giornaliero (veicoli/ora)")
        st.plotly_chart(fig_ts, width='stretch')

        #st.markdown("**🧊 Matrice ora × giorno della settimana (media)**")
        pivot = df.pivot_table(index='day_of_week', columns='hour', values='traffic_volume', aggfunc='mean').round(2)
        # Ordine al contrario (Domenica → Lunedì)
        pivot = pivot.reindex([6, 5, 4, 3, 2, 1, 0])
        # Heatmap senza colorbar (l'informazione principale è nei valori/hover)
        y_labels = [day_map[i] for i in pivot.index]
        fig_heat = go.Figure(
            data=go.Heatmap(
                z=pivot.values,
                x=pivot.columns,
                y=y_labels,
                showscale=False,
                colorscale="Blues",
                hovertemplate="Giorno: %{y}<br>Ora: %{x}<br>Traffico medio: %{z:.0f}<extra></extra>",
            )
        )
        _apply_plot_style(fig_heat, title="🧊 Matrice ora × giorno (media)", x_title="Ora del giorno", y_title="Giorno della settimana")
        fig_heat.update_layout(
            yaxis=dict(categoryorder="array", categoryarray=y_labels),
            xaxis=dict(dtick=1)
        )
        st.plotly_chart(fig_heat, width='stretch')

    # --- TAB 3: Trend Stagionali ---
    with tab3:
        col_week, col_month = st.columns(2)

        # Settimanale
        with col_week:
            #st.markdown("**📅 Media per giorno della settimana**")
            ordine_giorni = ['Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato', 'Domenica']
            weekly_trend = df.groupby('nome_giorno')['traffic_volume'].mean().round(2).reindex(ordine_giorni).reset_index()
            fig_week = px.bar(weekly_trend, x='nome_giorno', y='traffic_volume', text_auto='.0f')
            fig_week.update_traces(marker_opacity=0.85)
            _apply_plot_style(fig_week, title="📅 Media per giorno della settimana", x_title="Giorno", y_title="Traffico medio (veicoli/ora)")
            st.plotly_chart(fig_week, width='stretch')

        # Mensile
        with col_month:
            #st.markdown("**🗓️ Stagionalità mensile**")
            ordine_mesi = ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic']
            monthly_trend = df.groupby('nome_mese')['traffic_volume'].mean().round(2).reindex(ordine_mesi).reset_index()
            fig_month = px.line(monthly_trend, x='nome_mese', y='traffic_volume', markers=True)
            _apply_plot_style(fig_month, title="📅 Stagionalità mensile", x_title="Mese", y_title="Traffico medio (veicoli/ora)")
            st.plotly_chart(fig_month, width='stretch')

        # Annuale
        st.markdown("---")
        yearly_trend = df.groupby('year')['traffic_volume'].mean().round(2).reset_index()
        fig_year = px.bar(yearly_trend, x='year', y='traffic_volume', text_auto='.0f')
        fig_year.update_xaxes(type='category')
        _apply_plot_style(fig_year, title="Trend annuale", x_title="Anno", y_title="Traffico medio (veicoli/ora)")
        st.plotly_chart(fig_year, width='stretch')

    # --- TAB 4: CONFRONTO DIRETTO ---
    with tab4:
        st.subheader("🆚 Confronto tra Giorni")
        st.markdown("📌 Metti a confronto due date specifiche per analizzare differenze di traffico e contesto (meteo/weekend/holiday).")
        
        # Assicuriamoci che 'date_time' sia solo la data per i selettori
        min_date = df['date_time'].min().date()
        max_date = df['date_time'].max().date()

        col_in1, col_in2 = st.columns(2)
        
        # Imposta i valori di default per essere sicuri che ci siano dati (se possibile)
        default_date1 = pd.to_datetime("2016-10-05").date() if pd.to_datetime("2016-10-05").date() >= min_date and pd.to_datetime("2016-10-05").date() <= max_date else min_date
        default_date2 = pd.to_datetime("2016-10-06").date() if pd.to_datetime("2016-10-06").date() >= min_date and pd.to_datetime("2016-10-06").date() <= max_date else min_date

        def _clamp_date(value):
            if value is None:
                return min_date
            if value < min_date:
                return min_date
            if value > max_date:
                return max_date
            return value

        # In Streamlit: se usi `key=...`, evita di passare anche `value=...`.
        st.session_state.setdefault('cmp_date1', default_date1)
        st.session_state.setdefault('cmp_date2', default_date2)
        st.session_state['cmp_date1'] = _clamp_date(st.session_state.get('cmp_date1'))
        st.session_state['cmp_date2'] = _clamp_date(st.session_state.get('cmp_date2'))

        with col_in1:
            date1 = st.date_input("📅 Data 1 (Baseline)", min_value=min_date, max_value=max_date, key='cmp_date1')
        with col_in2:
            date2 = st.date_input("📅 Data 2 (Confronto)", min_value=min_date, max_value=max_date, key='cmp_date2')
        
        # Estrai i dati
        d1_data = df[df['date_time'].dt.date == date1].copy()
        d2_data = df[df['date_time'].dt.date == date2].copy()
        
        # Tronca anche i dati estratti per confronto diretto
        for _df in [d1_data, d2_data]:
            float_cols = _df.select_dtypes(include=['float', 'float64', 'float32']).columns
            _df[float_cols] = _df[float_cols].apply(lambda x: x.round(2))

        if not d1_data.empty and not d2_data.empty:
            # Calcolo Differenza Totale
            vol1 = round(d1_data['traffic_volume'].sum(), 2)
            vol2 = round(d2_data['traffic_volume'].sum(), 2)
            diff = round(vol2 - vol1, 2)
            diff_perc = round((diff / vol1) * 100, 2) if vol1 > 0 else 0
            
            # Recuperiamo il nome del giorno della settimana dalle colonne già mappate
            day1_name = d1_data.iloc[0]['nome_giorno'] if not d1_data.empty else "N/A"
            day2_name = d2_data.iloc[0]['nome_giorno'] if not d2_data.empty else "N/A"
            
            st.metric(label=f"📉 Differenza Totale ({date2} vs {date1})", 
                      value=f"{diff:+.2f} veicoli", 
                      delta=f"{diff_perc:+.2f}%")
            
            # Grafico Sovrapposto
            fig_comp = go.Figure()
            # 'hour' è già disponibile dal CSV
            fig_comp.add_trace(go.Scatter(x=d1_data['hour'], y=d1_data['traffic_volume'], 
                                           mode='lines+markers', name=f"{date1} ({day1_name})",
                                           line=dict(width=3)))
            fig_comp.add_trace(go.Scatter(x=d2_data['hour'], y=d2_data['traffic_volume'], 
                                           mode='lines+markers', name=f"{date2} ({day2_name})",
                                           line=dict(width=3, dash='dot')))

            _apply_plot_style(fig_comp, title="📊 Confronto orario diretto", x_title="Ora del giorno", y_title="Traffico (veicoli/ora)")
            fig_comp.update_xaxes(dtick=1)
            st.plotly_chart(fig_comp, width='stretch')

            st.markdown("---")
            st.markdown("**🧾 Contesto delle due giornate**")
            summary_1 = summarize_day(d1_data)
            summary_2 = summarize_day(d2_data)
            # Arrotonda tutti i valori float del summary a 2 decimali
            for s in (summary_1, summary_2):
                for k, v in s.items():
                    if isinstance(v, float):
                        s[k] = round(v, 2)
            summary_df = pd.DataFrame({"📅"+str(date1): summary_1, "📅"+str(date2): summary_2})
            # Arrow/pyarrow può fallire con colonne `object` miste (es. bool + string).
            summary_df = summary_df.map(lambda v: "" if pd.isna(v) else str(v))
            st.dataframe(summary_df, width='stretch')

            st.markdown("**🌦️ Meteo orario (overview)**")
            meteo_cols = [c for c in ['hour', 'temp', 'rain_1h', 'snow_1h', 'clouds_all', 'weather_main', 'weather_description'] if c in df.columns]
            mcol1, mcol2 = st.columns(2)
            with mcol1:
                st.caption(f"📅 {date1}")
                st.dataframe(d1_data[meteo_cols].sort_values('hour'), width='stretch', height=280)
            with mcol2:
                st.caption(f"📅 {date2}")
                st.dataframe(d2_data[meteo_cols].sort_values('hour'), width='stretch', height=280)
            
        else:
            st.warning("⚠️ Dati non disponibili per una o entrambe le date selezionate.")
    
    # --- TAB 5: Traffico & Meteo ---
    with tab5:
        st.subheader("🌦️ 5. Relazione tra Traffico e Meteo")
        st.markdown("""
        Questa sezione esamina come le **diverse condizioni meteorologiche** e i **fattori ambientali** (come temperatura, pioggia, neve e nuvolosità) influenzano il volume di traffico.
        """)
    # 5.1 Grafico traffico per tipo di meteo (weather_main)
        st.markdown("**1. Traffico Medio per Categoria Meteo Principale**")
        # Escludiamo i valori nulli o vuoti per l'analisi
        weather_traffic = df[df['weather_main'].notna() & (df['weather_main'] != '')].groupby('weather_main')['traffic_volume'].agg(['mean', 'median', 'count']).sort_values('mean', ascending=False).reset_index()
        weather_traffic.columns = ['Condizione Meteo', 'Traffico Medio', 'Traffico Mediano', 'Conteggio Ore']
        
        # Rimuoviamo le categorie con pochissimi campioni per evitare outlier (es. meno di 100 ore)
        MIN_SAMPLES = 100
        weather_traffic_filtered = weather_traffic[weather_traffic['Conteggio Ore'] >= MIN_SAMPLES]
        
        if not weather_traffic_filtered.empty:
            fig_weather_bar = px.bar(weather_traffic_filtered, x='Condizione Meteo', y='Traffico Medio', 
                                    text_auto='.0f',
                                    title=f"Traffico Medio per tipo di Meteo (min. {MIN_SAMPLES} campioni)")
            fig_weather_bar.update_traces(marker_color='#2ca02c', opacity=0.85)
            _apply_plot_style(fig_weather_bar, x_title="Condizione Meteo", y_title="Traffico Medio (veicoli/ora)")
            st.plotly_chart(fig_weather_bar, width='stretch')
            
            # Mostra la tabella di supporto
            st.caption("Dati sottostanti (inclusa la conta dei campioni):")
            st.dataframe(weather_traffic.set_index('Condizione Meteo'), width='stretch')
            
        else:
            st.warning(f"⚠️ Non ci sono abbastanza campioni (min. {MIN_SAMPLES}) per visualizzare le categorie meteo.")
            
        st.markdown("---")

        # 5.2 Correlazione con i fattori numerici (Temperatura, Pioggia, Neve, Nuvolosità)
        st.markdown("**2. Relazione con i Fattori Numerici (Temperatura, Pioggia, Neve, Nuvolosità)**")
        
        # --- Temperatura ---
        temp_bins = pd.cut(df['temp'], bins=10, duplicates='drop')
        temp_traffic = df.groupby(temp_bins, observed=True)['traffic_volume'].mean().round(2).reset_index()
        temp_traffic['temp_range'] = temp_traffic['temp'].astype(str)
        
        fig_temp = px.bar(temp_traffic, x='temp_range', y='traffic_volume', 
                        title='Traffico Medio per intervallo di Temperatura',
                        text_auto='.0f')
        fig_temp.update_traces(marker_color='#d62728', opacity=0.85)
        _apply_plot_style(fig_temp, x_title="Intervallo di Temperatura (°C)", y_title="Traffico Medio (veicoli/ora)")
        st.plotly_chart(fig_temp, width='stretch')
        

        col_rain, col_snow = st.columns(2)
        
        # --- Grafico Pioggia (rain_1h) ---
        with col_rain:
            st.caption("💧 Pioggia (Rain_1h) vs Traffico")
            # Pioggia: Raggruppiamo i valori di pioggia > 0.05 per analizzare l'effetto delle piogge vere
            rain_groups = df['rain_1h'].apply(lambda x: 'Zero/Minima' if x < 0.05 else ('Leggera' if x < 1.0 else 'Forte'))
            # Assicuriamoci che l'ordine sia logico (Zero, Leggera, Forte)
            if 'Leggera' in rain_groups.unique():
                rain_traffic = df.groupby(rain_groups, observed=True)['traffic_volume'].mean().round(2).reset_index()
                rain_traffic[rain_groups.name] = pd.Categorical(rain_traffic[rain_groups.name], categories=['Zero/Minima', 'Leggera', 'Forte'], ordered=True)
                rain_traffic = rain_traffic.sort_values(rain_groups.name)
            else:
                # Caso fallback se 'Leggera' non c'è
                rain_traffic = df.groupby(rain_groups, observed=True)['traffic_volume'].mean().round(2).reset_index().sort_values('traffic_volume', ascending=False)
            
            fig_rain = px.bar(rain_traffic, x=rain_groups.name, y='traffic_volume', 
                            title='Traffico Medio per Intensità di Pioggia',
                            text_auto='.0f')
            fig_rain.update_traces(marker_color='#17becf', opacity=0.85)
            _apply_plot_style(fig_rain, x_title="Intensità di Pioggia (mm/h)", y_title="Traffico Medio")
            st.plotly_chart(fig_rain, width='stretch')

        # --- Grafico Neve (snow_1h) (AGGIUNTO) ---
        with col_snow:
            st.caption("❄️ Neve (Snow_1h) vs Traffico")
            
            # Filtriamo le ore dove c'è stata neve (snow_1h > 0)
            df_snow = df[df['snow_1h'] > 0].copy()
            
            # Se ci sono dati di neve, analizziamo
            if not df_snow.empty:
                # Raggruppiamo i valori di neve > 0
                snow_groups = df['snow_1h'].apply(lambda x: 'Zero' if x == 0 else ('Leggera' if x < 0.05 else 'Forte'))
                
                # Calcolo dei valori medi
                snow_traffic = df.groupby(snow_groups, observed=True)['traffic_volume'].mean().round(2).reset_index()
                # Ordine logico
                snow_traffic[snow_groups.name] = pd.Categorical(snow_traffic[snow_groups.name], categories=['Zero', 'Leggera', 'Forte'], ordered=True)
                snow_traffic = snow_traffic.sort_values(snow_groups.name)

                fig_snow = px.bar(snow_traffic, x=snow_groups.name, y='traffic_volume', 
                                title='Traffico Medio per Intensità di Neve',
                                text_auto='.0f')
                fig_snow.update_traces(marker_color='#8c564b', opacity=0.85)
                _apply_plot_style(fig_snow, x_title="Intensità di Neve (mm/h)", y_title="Traffico Medio")
                st.plotly_chart(fig_snow, width='stretch')
            else:
                st.warning("Nessuna precipitazione nevosa registrata nel dataset.")


        # --- Nuvolosità (Aggiustata per usare la colonna intera) ---
        st.markdown("---")
        st.caption("☁️ Nuvolosità (Clouds_all) vs Traffico")
        
        # Nuvolosità: Creazione di bin per la percentuale di copertura nuvolosa
        cloud_bins = pd.cut(df['clouds_all'], bins=[0, 20, 80, 101], labels=['0-20% (Sereno)', '21-80% (Variabile)', '81-100% (Coperto)'], right=False)
        cloud_traffic = df.groupby(cloud_bins, observed=True)['traffic_volume'].mean().round(2).reset_index()
        
        fig_clouds = px.bar(cloud_traffic, x='clouds_all', y='traffic_volume', 
                            title='Traffico Medio per Fascia di Nuvolosità',
                            text_auto='.0f')
        fig_clouds.update_traces(marker_color='#7f7f7f', opacity=0.85)
        _apply_plot_style(fig_clouds, x_title="Copertura Nuvolosa (%)", y_title="Traffico Medio")
        st.plotly_chart(fig_clouds, width='stretch')

else:
    st.error("❌ Errore nel caricamento dei dati.")