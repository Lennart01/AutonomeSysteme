---
title: Autonome Systeme - Sommer Semester 24
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

-   [Overview](./../../overview/overview)
-   [Concurrency in Go](./../../teil_1/lec-concurrency-go)
    -   Go multi-threading, Kanal-basierte Kommunikation
    -   Synchrone versus Asynchrone Kommunikation
    -   Kanäle von Kanälen
    -   Nichtdeterministische Auswahl (“select”)
    -   Was alles schief gehen kann
    -   Weitere Aufgaben und Zusammenfassung
-   Dynamic data race prediction
    -   [Overview](./../../teil_2/lec-data-race-overview)
    -   [Happens-before Methode](./../../teil_2/lec-hb-vc)
    -   [TSan and examples](./../../teil_2/lec-data-race-examples)
    -   [Lockset Methode](./../../teil_2/lec-lockset)
    -   [Summary](./../../teil_2/lec-data-race-summary)
-   [Deadlock Analyse](./../../teil_2/lec-deadlock)
-   [Concurrency models](./../../teil_1/lec-concurrency-models)
    -   mutex
    -   fork/join
    -   barrier
    -   wait/notify
    -   actors
    -   futures und Zusammenfassung
    -   [Mehr zu futures und promises](./../../teil_1/lec-futures)
-   [Weitere Beispiele](./../../teil_2/weiterebeispiele)
-   [Go - kurz und knapp](./../../teil_1/lec-go-compact)

## Semesterablauf

-   Vorlesung, E302, Donnerstags 09:50-11:20 und auf
    [zoom](https://h-ka-de.zoom-x.de/j/4837536496?pwd=dnlrTmVhWXlYOTFNMEhnYVNtRTJwZz09)

Wöchentlicher Ablauf.

-   W1, 18.03-24.03
    -   Intro
    -   Go multi-threading, Kanal-basierte Kommunikation
-   W2, 25.03-31.03 (Freitag Vorlesungsfrei)
    -   Kanal-basierte Kommunikation
    -   Mutex und Semaphore
-   W3, 01.04-07.04 (Montag + Dienstag Vorlesungsfrei)
    -   Keine Vorlesung
-   W4, 08.04-14.04
    -   Fork/Join, Barrier
    -   Kanäle von Kanälen
    -   Nichtdeterministische Auswahl (“select”)
-   W5, 15.04-21.04
    -   Was alles schief gehen kann
        -   Fehlerszenarien
        -   Programmspuren
-   W6, 22.04-28.04
    -   Dynamische Data Race Erkennung (Overview)
-   W7, 29.04-05.05 (Mittwoch Vorlesungsfrei)
    -   Dynamische Data Race Erkennung
        -   Program, Lock Semantics, Last Writer Condition
        -   Lamport’s Happpes-before Relation
        -   Mengen-basierte Darstellung (“set-based data race
            predictor”)
    -   Events sets vs Vector clocks
-   W8, 06.05-12.05 (Donnerstag Vorlesungsfrei)
    -   Keine Vorlesung
-   W9, 13.05-19.05
    -   Dynamische Data Race Erkennung
        -   Lockset Methode
    -   go-race
-   Pfingstwoche Vorlesungsfrei, 20.05-26.05
-   W10, 27.05-02.06 (Donnerstag Vorlesungsfrei)
    -   Keine Vorlesung
-   W11, 03.06-09.06
    -   Deadlock Analyse
-   W12, 10.06-16.06
    -   General purpose versus domain specific languages
    -   Concurrency models (mutex, fork/join, barrier, wait/notify,
        futures)
-   W13, 17.06-23.06
    -   Concurrency models (more on futures)
-   W14, 24.06-30.06
    -   TBA
-   W15, 01.07-07.07
    -   Klausurinfo:
        -   Schriftlich, ohne Hilfsmittel
        -   Teil der Modulklausur Autonome Systeme + Rechner Architektur
            (120min insgesamt)
        -   Themen siehe oben
