# Information System & Business Intelligence – #1 Project
Care studentesse e cari student del corso di Information Systems & Business Intelligence,  
questo è il vostro primo progetto sul tema **Business Process Management** con Bonita. Useremo tre contesti reali della giustizia digitale (progetti europei DEUCE, IDEA e CREA3) come contest operativo per costruire tre diversi processi BPMN. L’obiettivo principale è che impariate a modellare in Bonita: attori, attività, flussi e semplici decisioni.
## Contest
## DATI I SEGUENTI PROGETTI EUROPEI
• **DEUCE** è un progetto europeo che si occupa di **digitalizzare le procedure per il recupero dei crediti pecuniari non contestati** all’interno dell’Unione Europea. L’idea di fondo è che, quando un creditore vuole recuperare un credito (ad esempio una fattura non pagata) in un contesto transfrontaliero, la procedura sia spesso lenta, frammentata e ancora molto legata alla carta o a pratiche manuali.
L’UE ha già creato strumenti giuridici specifici come l’**Ingiunzione di Pagamento Europea (EPO)** e il **Titolo Esecutivo Europeo (EEO)** per semplificare e armonizzare queste procedure; DEUCE si inserisce qui, cercando di trasformare questi strumenti in **workflow digitali chiari, tracciabili e interoperabili** tra i diversi sistemi nazionali. Il progetto si appoggia ai risultati di progetti precedenti (SCAN, EFFORTS, SCAN II) e dialoga con l’infrastruttura **e-CODEX** e con l’Agenzia **EU-LISA**, che gestisce i grandi sistemi informatici europei per la cooperazione giudiziaria.
• **IDEA** lavora sul tema della **giustizia predittiva e della digitalizzazione nel diritto del lavoro**. Il progetto parte da una domanda molto attuale: come usare **AI, big data e predictive analytics** per migliorare l’accesso alla giustizia, senza mettere a rischio lo stato di diritto e i diritti fondamentali?  
Il focus è sulle **controversie di lavoro** (licenziamenti, salari, condizioni di lavoro). L’obiettivo è sviluppare:
-   una **procedura di tribunale digitalizzata**,
-   una **piattaforma online** che guidi il cittadino in un vero e proprio *“Digital Journey”* dalla percezione dell’ingiustizia fino alla scelta del percorso:
    -   negoziazione assistita / automatizzata,
    -   mediazione online,
    -   oppure ricorso al tribunale del lavoro.
• **CREA3** si occupa di **giustizia predittiva e digitalizzazione nel diritto di famiglia** (separazioni, divisione dei beni, eredità, ecc.), in contesti sia nazionali che transfrontalieri. È la naturale continuazione di due progetti precedenti (CREA e CREA2) che già avevano sviluppato strumenti digitali per la risoluzione dei conflitti familiari.
Il cuore del progetto è la creazione di una **piattaforma digitale basata su algoritmi “equitativi”** (in particolare strumenti di teoria dei giochi e text mining) che:
-   aiuti le parti a trovare soluzioni sulla **divisione dei beni** in modo più rapido, economico e meno conflittuale rispetto al processo tradizionale;
-   supporti giudici, avvocati, notai, mediatori e cittadini nella gestione dei casi, fornendo **suggerimenti basati su casi simili** e strumenti per simulare diversi scenari di accordo;
-   integri **comunicazione elettronica, firme digitali, videoconferenza** e un’interfaccia conversazionale (chatbot).
## Contest 1 – Mediazione familiare con assistenza e consenso (CREA3)
*Percorso di mediazione familiare semplificato.*  
**Scenario:** una persona richiede una mediazione, indicando se ha bisogno di assistenza speciale. Lo staff verifica se l’altra parte è d’accordo a partecipare; se c’è consenso, il mediatore fissa la sessione.  
Cosa fare in Bonita:  
\- create un processo con tre lane: Richiedente, Staff, Mediatore;  
\- definite una prima attività “Richiedi mediazione” (Richiedente), con nome, contatti, dati dell’altra parte e un campo sì/no per il bisogno di assistenza;  
\- inserite un gateway esclusivo che, se è richiesta assistenza, manda il flusso a “Registra bisogni di assistenza” (Staff), altrimenti salta direttamente allo step successivo;  
\- definite una attività “Verifica consenso altra parte” (Staff), in cui viene registrato se l’altra parte accetta (sì/no);  
\- inserite un secondo gateway esclusivo: se non c’è consenso, il processo termina con “Mediazione non possibile”; se c’è consenso, il flusso va a “Pianifica sessione di mediazione” (Mediatore), dove vengono scelti data, ora e modalità dell’incontro (online o in presenza), per poi terminare con “Mediazione programmata”.  
**Risultato atteso:** eseguendo il processo dovete poter simulare sia casi in cui la mediazione procede (con sessione programmata) sia casi in cui si ferma per mancanza di consenso.
