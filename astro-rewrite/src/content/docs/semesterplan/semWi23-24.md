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

[GitHub Order mit markdown und Programmen aus der
Vorlesung](https://github.com/sulzmann/AutonomeSysteme/tree/master/WiSe23-24)

## Semesterablauf

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
    -   Events sets vs Vector clocks
-   W9, 20.11-26.11
    -   Dynamische Data Race Erkennung
    -   lockset, go-race
-   W10, 27.11-03.12
    -   Deadlock Analyse
-   W11, 04.12-10.12
    -   Keine Vorlesung und kein Tutorium
-   W12, 11.12-17.12
    -   General purpose versus domain specific languages
    -   Concurrency models (mutex, fork/join, barrier, wait/notify,
        futures)
-   W13, 28.12-24.12
    -   Concurrency models (more on futures)
-   Winter break
-   W14, 08.01-14.01
    -   [Some fun stuff](./../../teil_2/lec-fun-stuff)
-   W15, 15.01-21.01
    -   Klausurinfo:
        -   Schriftlich, ohne Hilfsmittel
        -   Teil der Modulklausur Autonome Systeme + Rechner Architektur
            (120min insgesamt)
        -   Themen siehe oben
