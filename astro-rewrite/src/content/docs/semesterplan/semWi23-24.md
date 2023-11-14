---
title: Autonome Systeme - Winter Semester 23/24
description: Martin Sulzmann
---



## Evaluation

-   Klausur, 60min, ohne Hilfsmittel

-   Bonuspunkte (10% extra) bei Bearbeitung Online Tests

    -   Lineare Bonuspunkte Verteilung (100% Online Tests = 10% extra,
        50% Online Tests = 5% extra)
    -   Pro Test zwei Versuche jeweils 90min
    -   Durchführungstermine beachten

## Vorlesungsunterlagen

-   [Overview](./overview.html)
-   [Concurrency in Go](./lec-concurrency-go.html)
    -   Go multi-threading, Kanal-basierte Kommunikation
    -   Synchrone versus Asynchrone Kommunikation
    -   Kanäle von Kanälen
    -   Nichtdeterministische Auswahl (“select”)
    -   Was alles schief gehen kann
    -   Weitere Aufgaben und Zusammenfassung
-   Dynamic data race prediction
    -   [Overview](./lec-data-race-overview.html)
    -   [Happens-before Methode](./lec-hb-vc.html)
    -   [Lockset Methode](./lec-lockset.html)
-   [Deadlock Analyse](./lec-deadlock.html)
-   [Concurrency models](./lec-concurrency-models.html)
    -   mutex
    -   fork/join
    -   barrier
    -   wait/notify
    -   actors
    -   futures und Zusammenfassung
    -   [Mehr zu futures und promises](./lec-futures.html)
-   [Weitere Beispiele](./weitereBeispiele.html)
-   [Go - kurz und knapp](./lec-go-compact.html)

[GitHub Order mit markdown und Programmen aus der
Vorlesung](https://github.com/sulzmann/AutonomeSysteme/tree/master/WiSe23-24)

# Semesterablauf

-   Vorlesung, E301, Donnerstags 11:30-13:00 und auf
    [zoom](https://h-ka-de.zoom-x.de/j/4837536496?pwd=dnlrTmVhWXlYOTFNMEhnYVNtRTJwZz09)

-   Tutorium, E301, Donnerstags 13:00-14:00

Wöchentlicher Ablauf.

-   W1, 25.09-01.10
    -   Intro
    -   Go multi-threading, Kanal-basierte Kommunikation
-   W2, 02.10-08.10 (03.10 public holiday)
    -   Kanal-basierte Kommunikation
    -   Mutex und Semaphore
-   W3, 09.10-15.10
    -   Fork/Join, Barrier
    -   Kanäle von Kanälen
    -   Nichtdeterministische Auswahl (“select”)
-   W4, 16.10-22.10
    -   Wiederholung: select, “publish-subscribe” Beispiel
    -   Was alles schief gehen kann
    -   Deadlock, Starvation, Livelock
    -   Problem der speisenden Philosophen
    -   Kein Tutorium diese Woche
    -   Ab 13:00 “Vorlesungsbesuch High Speed Karlsruhe”
-   W5, 23.10-29.10
    -   Wiederholung (Fehlerszenarien, Programmspuren)
    -   Dynamische Data Race Erkennung (Overview)
-   W6, 30.10-05.11 (01.11 public holiday)
    -   Keine Vorlesung aber Tutorium
-   W7, 06.11-12.11
    -   Dynamische Data Race Erkennung
        -   Program, Lock Semantics, Last Writer Condition
        -   Lamport’s Happpes-before Relation
        -   Mengen-basierte Darstellung (“set-based data race
            predictor”)
-   W8, 13.11-19.11
    -   Dynamische Data Race Erkennung
-   W9, 20.11-26.11
    -   Dynamische Data Race Erkennung
-   W10, 27.11-03.12
    -   Deadlock Analyse
-   W11, 04.12-10.12
    -   Concurrency models
-   W12, 11.12-17.12
    -   Concurrency models
-   W13, 28.12-24.12
    -   Concurrency models
-   Winter break
-   W14, 08.01-14.01
    -   TBA
-   W15, 15.01-21.01
    -   Klausurvorbereitung
