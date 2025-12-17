Project Work #2 – Sistemi Informativi & Business Intelligence
(corso: Sistemi Informativi & Business Intelligence – Analisi di Serie Storiche)

Questo project-work si focalizza sulla analisi delle serie storiche sulla base di diversi domini ed applicazioni reali (energia, mobilità, ambiente, clima, ecc.). Per ogni dataset sono riportati:
• una breve descrizione dei dati
• i comandi per il download (wget) e un link alla versione mirror su Kaggle
• una descrizione della struttura dei dati e delle variabili principali
• la definizione della/e variabile/i target
• una lista di compiti suggeriti, lasciando libertà sulla scelta dei modelli statistici o di machine learning.

Compito generale dello studente:
1. Caricare e pulire il dataset scelto (concordato\assegnato dal docente);
2. Effettuare un’analisi esplorativa della serie storica (grafici, trend, stagionalità, correlazioni, qualità dei dati);
3. Eseguire l’opportuno preprocessing e costruire uno o più modelli predittivi per la serie storica (modelli a scelta dello studente);
N.B. specifici dataset potrebbero prevedere particolari modelli da utilizzare.
4. Valutare le prestazioni dei modelli con metriche adeguate (es. MAE, RMSE) e confronto con baseline semplici;
N.B. Instanziare una baseline semplice e valutare le performance di modelli più performanti
5. Presentare un breve report (Slides) che colleghi i risultati a un contesto decisionale o di supporto alle decisioni.

Dataset 1 – Metro Interstate Traffic Volume
Dominio: Trasporti / Traffico
Download
Sorgente originale (wget):
wget -O metro_interstate_traffic_volume.zip "https://archive.ics.uci.edu/static/public/492/metro%2Binterstate%2Btraffic%2Bvolume.zip"
unzip metro_interstate_traffic_volume.zip
Mirror Kaggle:
https://www.kaggle.com/datasets/pooriamst/metro-interstate-traffic-volume
Descrizione dei dati
Serie storica oraria del volume di traffico (numero di auto all’ora) su un tratto dell’autostrada Interstate 94 tra Minneapolis e Saint Paul (USA). Ogni osservazione include il volume di traffico e diverse informazioni meteo e di calendario (festività, ora del giorno, ecc.). È adatto per esercizi di previsione a breve termine e analisi di pattern giornalieri/settimanali.
Struttura dei dati
•	Orizzonte temporale: circa 2012–2018
•	Frequenza: 1 osservazione all’ora
•	Dimensione: ~48.000 righe
•	Colonne principali: date_time (timestamp), traffic_volume (auto/ora), temperatura, rain_1h, snow_1h, clouds_all, holiday, descrizione meteo
Variabile/i target
Target principale: traffic_volume – numero di veicoli che transitano nel tratto nell’ora considerata.
Compiti suggeriti
1.	Compito A – Previsione del traffico a breve termine
Obiettivo: prevedere il valore futuro di traffic_volume (ad esempio l’ora successiva) utilizzando informazioni storiche sul traffico, sulle condizioni meteo e sul calendario.

Indicazioni operative:
• Creare un indice temporale a partire da date_time e ordinare i dati;
• Costruire variabili temporali (ora del giorno, giorno della settimana, festivo/non festivo);
• Creare una o più variabili di ritardo (lag) di traffic_volume (es. ultimo valore, ultime 24 ore);
• Scegliere uno o più modelli di previsione (es. modello di regressione o modello per serie storiche) e confrontarli con baseline semplici (ad esempio “stesso valore dell’ora precedente”);
• Valutare le prestazioni con metriche appropriate e commentare i risultati.
2.	Compito B – Analisi di pattern giornalieri e settimanali
Obiettivo: analizzare il comportamento del traffico nel corso della giornata e della Settimana e mensilità.
Creare delle KPIs per il dominio di interesse.

Indicazioni operative:
• Calcolare e rappresentare graficamente la media di traffic_volume per ora del giorno, separando giorni feriali e weekend;
• Analizzare l’effetto di condizioni meteo estreme (pioggia/neve) sui volumi;
• Discutere come queste informazioni potrebbero essere utilizzate per la pianificazione dei trasporti.


Project Work #3 – Cruscotto interattivo & Predizioni con Streamlit
(corso: Sistemi Informativi & Business Intelligence – Analisi di Serie Storiche)

In questo terzo project work si chiede di riprendere il lavoro svolto nel Project Work #2 (analisi di una serie storica reale e costruzione di un modello predittivo) trasformandolo in una applicazione interattiva sviluppata con Streamlit.
L’obiettivo è realizzare un cruscotto (dashboard) web che permetta a un utente non tecnico di:
1.	Esplorare i dati: vedere la serie storica principale, capire il dominio applicativo (energia, traffico, mobilità, ecc.), avere una breve descrizione del dataset e del significato della variabile target.
2.	Osservare risultati e indicatori: visualizzare alcuni grafici significativi (ad esempio andamento nel tempo, stagionalità, confronti con variabili meteo o di calendario) e pochi KPI sintetici, come ad esempio il valore medio e massimo del target, e una misura dell’errore del modello sui dati di test. Non è importante il tipo specifico di modello utilizzato, ma che ci sia un chiaro collegamento tra analisi, visualizzazioni e interpretazione.
3.	Utilizzare il modello predittivo come artefatto: integrare nella dashboard il modello costruito nel Project Work #2 (o una sua versione semplificata) in modo che l’utente possa fornire alcuni input tramite un semplice form (per esempio data/ora, condizioni meteo ipotetiche, valori recenti del target o di altre variabili) e ottenere una previsione della variabile target. La previsione deve essere mostrata in modo chiaro, ad esempio come valore numerico e, se possibile, inserita in un piccolo grafico accanto agli ultimi dati osservati.
Tutto il lavoro deve essere svolto in Python con Streamlit, organizzando l’applicazione in modo semplice e leggibile (ad esempio con una pagina o una navigazione a sezioni: descrizione dati, analisi/KPI, predizioni). Il risultato finale è un piccolo sistema informativo interattivo: non solo un modello addestrato, ma un artefatto utilizzabile, che combina dati, visualizzazioni, indicatori e capacità predittiva in un’unica interfaccia.

