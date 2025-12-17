# Project Work #2 – Sistemi Informativi & Business Intelligence  
(corso: Sistemi Informativi & Business Intelligence – Analisi di Serie Storiche)
Questo project-work si focalizza sulla analisi delle serie storiche sulla base di diversi domini ed applicazioni reali (energia, mobilità, ambiente, clima, ecc.). Per ogni dataset sono riportati:  
• una breve descrizione dei dati  
• i comandi per il download (wget) e un link alla versione mirror su Kaggle  
• una descrizione della struttura dei dati e delle variabili principali  
• la definizione della/e variabile/i target  
• una lista di compiti suggeriti, lasciando libertà sulla scelta dei modelli statistici o di machine learning.  
Compito generale dello studente:  
1\. Caricare e pulire il dataset scelto (concordato\\assegnato dal docente);  
2\. Effettuare un’analisi esplorativa della serie storica (grafici, trend, stagionalità, correlazioni, qualità dei dati);  
3\. Eseguire l’opportuno preprocessing e costruire uno o più modelli predittivi per la serie storica (modelli a scelta dello studente);  
N.B. specifici dataset potrebbero prevedere particolari modelli da utilizzare.  
4\. Valutare le prestazioni dei modelli con metriche adeguate (es. MAE, RMSE) e confronto con baseline semplici;  
N.B. Instanziare una baseline semplice e valutare le performance di modelli più performanti  
5\. Presentare un breve report (Slides) che colleghi i risultati a un contesto decisionale o di supporto alle decisioni.  
## Dataset 1 – Metro Interstate Traffic Volume
Dominio: Trasporti / Traffico
### Download
Sorgente originale (wget):
wget -O metro\_interstate\_traffic\_volume.zip "https://archive.ics.uci.edu/static/public/492/metro%2Binterstate%2Btraffic%2Bvolume.zip"  
unzip metro\_interstate\_traffic\_volume.zip
Mirror Kaggle:
https://www.kaggle.com/datasets/pooriamst/metro-interstate-traffic-volume
### Descrizione dei dati
Serie storica oraria del volume di traffico (numero di auto all’ora) su un tratto dell’autostrada Interstate 94 tra Minneapolis e Saint Paul (USA). Ogni osservazione include il volume di traffico e diverse informazioni meteo e di calendario (festività, ora del giorno, ecc.). È adatto per esercizi di previsione a breve termine e analisi di pattern giornalieri/settimanali.
### Struttura dei dati
-   Orizzonte temporale: circa 2012–2018
-   Frequenza: 1 osservazione all’ora
-   Dimensione: ~48.000 righe
-   Colonne principali: date\_time (timestamp), traffic\_volume (auto/ora), temperatura, rain\_1h, snow\_1h, clouds\_all, holiday, descrizione meteo
### Variabile/i target
Target principale: traffic\_volume – numero di veicoli che transitano nel tratto nell’ora considerata.
### Compiti suggeriti
1.  Compito A – Previsione del traffico a breve termine
Obiettivo: prevedere il valore futuro di traffic\_volume (ad esempio l’ora successiva) utilizzando informazioni storiche sul traffico, sulle condizioni meteo e sul calendario.  
Indicazioni operative:  
• Creare un indice temporale a partire da date\_time e ordinare i dati;  
• Costruire variabili temporali (ora del giorno, giorno della settimana, festivo/non festivo);  
• Creare una o più variabili di ritardo (lag) di traffic\_volume (es. ultimo valore, ultime 24 ore);  
• Scegliere uno o più modelli di previsione (es. modello di regressione o modello per serie storiche) e confrontarli con baseline semplici (ad esempio “stesso valore dell’ora precedente”);  
• Valutare le prestazioni con metriche appropriate e commentare i risultati.
1.  Compito B – Analisi di pattern giornalieri e settimanali
Obiettivo: analizzare il comportamento del traffico nel corso della giornata e della Settimana e mensilità.
**Creare delle KPIs per il dominio di interesse.**  
Indicazioni operative:  
• Calcolare e rappresentare graficamente la media di traffic\_volume per ora del giorno, separando giorni feriali e weekend;  
• Analizzare l’effetto di condizioni meteo estreme (pioggia/neve) sui volumi;  
• Discutere come queste informazioni potrebbero essere utilizzate per la pianificazione dei trasporti.