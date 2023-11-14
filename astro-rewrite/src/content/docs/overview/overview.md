---
title: Autonome Systeme - Um was geht's hier
description: Martin Sulzmann
---



# Gegenstand der Vorlesung

-   Autonome und reaktive Systeme

    -   Betriebssystem, Steuergerät, Smartphone, ...

-   Softwaresysteme in ständiger Interaktion mit Umgebung und ’inneren’
    Komponenten

-   Eigenschaften

    -   Nebenläufigkeit

    -   Nichtdeterminsmus (aka Indeterminismus)

    -   Nichtterminierung

    -   Kommunikation und Synchronization

# Konzepte und Methoden

Modellierung und Spezifikation

Implementierung und Analyse

Verifikation/Validation

Konkret betrachen wir

-   Die Programmiersprache Go

-   Temporale Logik und UPPAAL Modelchecker

-   Programm Analyse (statische und dynamische Analyse Methoden). Ziel
    Nachweis von Eigenschaften.

Mix aus Vorlesung und praktischen Übungen (Labor)

Weiterführende Seminar-/Projektarbeiten, Bachelor/Master,
Drittmittelprojekte, ...

# Die Programmiersprache Go

Nix neues. Altbekanntes und bewährtes in einer C-artigen Sprache
zusammengefasst.

Unser Fokus:

-   Nebenläufigkeit (Concurrency)

-   Kanal-basierte Kommunikation

Lambdas, ..., nebenbei erklärt.

    // Package system!
    package main

    import "fmt"
    import "time"


    // Keyword fuer Funktionen (=> lambdas, kommt spaeter).
    // Deklarationen: Variable erst dann der Typ.
    func snd(ch chan int) {
        x := 0                                // Einfache Typinferenz
        for {                                 // Vereinfachte Sprache, nur for loops
            x++
            ch <- x                           // Sende
            time.Sleep(1 * 1e9)
        }

    }

    func rcv(ch chan int) {
        var x int
        for {
            x = <-ch                          // Empfange
            fmt.Printf("received %d \n", x)

        }
        // Kein Semikolon!
        // Ein Statement pro Zeile. 

    }

    func main() {
        // Kanalbasierte Kommunikation, getypte Kanaele
        var ch chan int = make(chan int)
        go rcv(ch)                            // Leichtgewichtige Threads
        go snd(ch)
        rcv(ch)
        // Automatische Speicherveraltung.
        // Dynamisch angelegter Kanal wird automatisch freigegeben.
        fmt.Printf("Ende")      
    }

Go inspiriert von

-   [Haskell](https://www.haskell.org/)

-   [Concurrent ML](https://en.wikipedia.org/wiki/Concurrent_ML)

# Deadlock (Verklemmung)

    package main

    import "fmt"

    func snd(ch chan int) {
        var x int = 0
        x++
        ch <- x
    }

    func rcv(ch chan int) {
        var x int
        x = <-ch
        fmt.Printf("received %d \n", x)

    }

    func main() {
        var ch chan int = make(chan int)
        go rcv(ch)   // R1
        go snd(ch)   // S1
        rcv(ch)      // R2

    }

# Data race

    package main

    import "fmt"
    import "time"

    func main() {
        var x int
        y := make(chan int, 1)

        go func() {
            y <- 1
            x++                      // P1
            <-y

        }()

        x++                              // P2
        y <- 1
        <-y

        time.Sleep(1 * 1e9)
        fmt.Printf("%d \n",x)

    }

# Fazit und Ausblick

-   Go hat ausdrucksstarke Konzepte zur nebenläufigen Programmierung

-   Nebenläufige Programmierung ist trickreich.

-   Versteckte Deadlocks und Data Races

-   Modellierung und Programmanalysen zur Verifikation und Validation

-   Statische versus dynamische Methoden
