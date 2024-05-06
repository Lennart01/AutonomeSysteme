---
title: Fehlerszenarien und Programmspuren
description: Martin Sulzmann
---



## Was alles schief gehen kann

Wir betrachten Fehlerszenarien im Kontext der nebenläufigen
Programmierung.

Herausforderung:

-   Nicht-deterministische Ausführung

-   Fehler tritt auf, Fehler tritt nicht auf

Wir betrachten:

-   Deadlock

-   Starvation und Livelock

-   Data Race

Methodisches Vorgehen:

-   Beobachtung des Programmverhaltens als Programmspur (“trace”).

-   Trace = Sequenz von Ereignissen

## Motivierendes Beispiel

Eine Deadlock tritt ein falls alle Threads sind blockiert.

Das Go Laufzeitsystem erkennt solch eine Situation und bricht ab.

Betrachte folgendes Beispiel.

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

Was passiert?

-   In der Regel läuft das Programm durch

-   S1 kommuniziert mit R2

In Kurzform schreiben wir oft **S1 &lt;-&gt; R2** für solch eine
Situation.

Muss dies immer der Fall sein?

-   Nein

-   S1 könnte auch mit R1 kommunizieren

-   Dann bleibt R2 stecken und es kommt zu einem Deadlock!

Dieses Verhalten wird von folgender Variante provoziert

    package main

    import (
        "fmt"
        "time"
    )

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
        go rcv(ch) // R1
        go snd(ch) // S1
        time.Sleep(1 * time.Second)
        rcv(ch) // R2

    }

## Programmspuren

Die Programausführung impliziert Ereignisse (events) wie das Senden und
Empfangen via einem Kanal. Für Ereignisse verwenden wir folgende
Notation.

    ch?    empfangen via Kanal ch

    ch!    senden via Kanal ch

Beachte:

Ereignisse sind blockierend. Empfangen ist blockierend im Allgemeinen.
Senden ist blockierend falls der Puffer voll ist oder wir einen nicht
gepufferten Kanal verwenden.

Deshalb verfeinern wir die Aufzeichnung der Ereignisse wie folgt:

1.  Ereignis `ch?` bedeutet wir **wollen** empfangen via Kanal `ch`.

2.  Ereignis `ch?` bedeutet wir **haben** empfangen via Kanal `ch`.

Das gleiche gilt für das Ereignis `ch!`.

Wir führen folgende erweiterte Notation ein.

    pre(ch?)     wollen empfangen via Kanal ch
    post(ch?)    haben empfangen via Kanal ch

    pre(ch!)     wollen senden via Kanal ch
    post(ch!)    haben senden via Kanal ch

Zusammengefasst.

-   `pre` beschreibt das Ereignis bevor die dazu korrespondierende
    Operation stattfindet.

-   `post` beschreibt das Ereignis nachdem die dazu korrespondierende
    Operation stattgefunden hat.

Wir betrachten einen möglichen Programmablauf dargestellt als eine
**Programmspur** (trace auf Englisch). Eine Programmspur ist eine
Sequenz von Ereignissen und entspricht der abwechselnden Ausführung
(“interleaved execution”) der einzelnen Threads.

Ist die Trace-basierte Programmablauf Beschreibung verwandt mit der
zustandsbasierten Ausführung? Ja, beide Notationen/Konzepte haben das
Ziel (nebenläufige) Programmabläufe zu beschreiben. Das Verhältnis
beider ist in etwa wie reguläre Ausdrücke versus endliche Automaten.

## Beispiel

Die Ausführung folgendes Programmes

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

kann folgende Programmspur liefern.

        R1        S1            R2

    1.  pre(ch?)
    2.                          pre(ch?)
    3.            pre(ch!)
    4.            post(ch!)
    5.  post(ch?)

Für die Darstellung der Programmspur verwenden wir eine tabellarische
Notation.

-   Ereignisse finden abwechselnd statt

-   Zu jedem Zeitpunkt immer nur ein Ereignis

-   Für jeden Thread gibt es einen eigenen Eintrag.

Im obigen Ablauf, kommuniziert S1 mit R1. Dies ist aus dem Trace
ablesbar. Da auf `pre(ch!)` in S1 ein `post(ch!)` folgt. Auf `pre(ch?`)
in R1 folgt ein `post(ch?)`.

**Annahme**. Im Fall einer Kommunikation (Sende-Empfange) nehmen wir an,
dass das post Ereignis der Sendeoperation immer vor dem post Ereignis
der Empfangsoperation im Trace aufgezeichnet ist.

Threads S1 und R1 terminieren. Thread R2 blockiert da es keinen
Kommunikationspartner gibt. Alle Threads (hier nur R2) sind blockiert.
Deshalb Deadlock!

Betrachte folgenden Alternativen Programmablauf.

        R1         S1            R2

    1.  pre(ch?)
    2.                         pre(ch?)
    3.            pre(ch!)
    4.            post(ch!)
    5.                         post(ch?)

In diesem Ablauf kommuniziert S1 mit R2. R1 ist blockiert. Da aber der
Main Thread R2 terminiert, wird der Thread R1 auch terminiert. Ein
Deadlock ist deshalb nicht beobachtbar!

## Programminstrumentierung

Um die Programmspur zu erhalten muss das Programm instrumentiert.

Betrachte folgenden naiven Ansatz mittels “print”.

    package main

    import (
        "fmt"
    )

    func snd(tid string, ch chan int) {
        fmt.Printf("\nThread %s pre(ch!)", tid)
        ch <- 1
        fmt.Printf("\nThread %s post(ch!)", tid)
    }

    func rcv(tid string, ch chan int) {
        fmt.Printf("\nThread %s pre(ch?)", tid)
        <-ch
        fmt.Printf("\nThread %s post(ch?)", tid)

    }

    func main() {
        var ch chan int = make(chan int)
        go rcv("R1", ch) // R1
        go snd("S1", ch) // S1
        rcv("R2", ch)    // R2

    }

Ausführung kann folgende Ausgabe liefern.

    Thread R2 pre(ch?)
    Thread S1 pre(ch!)
    Thread R1 pre(ch?)
    Thread S1 post(ch!)
    Thread R2 post(ch?)

Die korrespondierende Repräsentation als Tabelle ist wie folgt.

        R1         S1            R2

    1.                         pre(ch?)
    2.            pre(ch!)
    3. pre(ch?)
    4.            post(ch!)
    5.                         post(ch?)

Die exakt gleiche Ausführung kann aber auch folgende Ausgabe liefern.

    Thread R2 pre(ch?)
    Thread S1 pre(ch!)
    Thread R1 pre(ch?)
    Thread R2 post(ch?)

Was ist der Unterschied?

-   `Thread S1 post(ch!)` in der zweitletzten Position fehlt

-   Wie kann dies sein?

Folgendes ist passiert

-   S1 kommuniziert mit R1 (impliziert post(ch!) und post(ch?))

-   Die Ausgabe der Ereignisse (post(ch!) und post(ch?)) erfolgt erst
    danach!

-   Falls R1 terminiert kann es passieren, dass die Ausgabe von
    post(ch!) in thread S1 nicht erfolgt!

Im allgemeinen kann die naive Programminstrumentierung mittels “print”
nicht garantieren, dass die Programmspur der tatsächlichen Ausführung
entspricht.

In der Regeln werden deshalb folgende Ansätze verwendet.

-   Instrumentierung des Laufzeitsystems

-   Instrumentierung des generierten Programmcodes (z.B. auf LLVM Ebene)

Von hier an nehmen wir an, dass die Programmspur immer der tatsächlichen
Ausführung entspricht.

## Beispiele und Zwischenfazit

## Beispiele

Betrachte folgende Programmspur.

Trace A.

        R1        S1            R2            S2

    1.  pre(ch?)
    2.                          pre(ch?)
    3.            pre(ch!)
    4.                                      pre(ch!)
    5.            post(ch!)
    6.                                      post(ch!)
    7.  post(ch?)
    8.                         post(ch?)

Welches Verhalten können wir ablesen?

Folgende Alternativen sind möglich:

1.  R1 &lt;-&gt; S1 und R2 &lt;-&gt; S2

2.  R1 &lt;-&gt; S2 und R2 &lt;-&gt; S1

Annahme. Der tatsächliche Programmablauf ist (1).

Aus Trace A können wir ableiten, dass aber auch der Programmablauf (2)
möglich wäre.

Weiteres Beispiel.

Trace B. Unterschied zu Trace A. Erst “post” von S1, dann R1 und dann
erst S2 und dann R2.

        R1        S1            R2            S2

    1.  pre(ch?)
    2.                          pre(ch?)
    3.            pre(ch!)
    4.                                      pre(ch!)
    5.            post(ch!)
    6.  post(ch?)
    7.                                      post(ch!)
    8.                         post(ch?)

Unsere Annahme war: “post(ch!)” vor dem korresponierenden “post(ch?)”.
Deshalb ist folgendes Verhalten ablesbar.

1.  R1 &lt;-&gt; S1 und R2 &lt;-&gt; S2

Alternative (2) hat nicht stattgefunden.

Jedoch können wir argumentieren, dass auch (2) möglich ist.

Dazu betrachten wir folgenden Umordnung von Trace B.

Trace C.

        R1        S1            R2            S2

    1.  pre(ch?)
    2.                          pre(ch?)
    3.            pre(ch!)
    4.                                      pre(ch!)
    5.            post(ch!
    8.                         post(ch?)
    7.                                      post(ch!)
    6. post(ch?)

Wir erhalten Trace C aus Trace B wie folgt:

-   Vertausche Eintrag an Stelle 8 mit Eintrag an der Stelle 6

-   In Trace C verwenden wir die Tracepositionen von Trace B

Aus Trace C folgt:

1.  R1 &lt;-&gt; S2 und R2 &lt;-&gt; S1

## Zwischenfazit

-   Wir lassen das Program *einmal* laufen und erhalten einen Trace.

-   Wir analysieren das Programmverhalten auf Basis dieses Traces.

-   Durch Umordnung des Traces können wir weitere mögliche
    Programmabläufe herleiten (ohne das Programm erneut auszuführen).

## Fehlerszenarien

## Deadlock

Unser laufendes Beispiel.

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

Ein möglicher Programmablauf dargestellt als Trace.

        R1         S1            R2

    1.                         pre(ch?)
    2.            pre(ch!)
    3. pre(ch?)
    4.            post(ch!)
    5.                         post(ch?)

Der Main Thread terminiert, deshalb ist nicht direkt erkennbar das
Thread R1 stecken bleibt.

Im “go slang” bezeichnet man das als “goroutine leak”.

## Starvation (“verhungert”)

Betrachte folgende Variante des obigen Beispiels. Alle Kanaloperationen
(Senden/Empfangen) befinden sich in einer Endlosschleife (deshalb
terminiert das Programm nie).

    package main

    import "fmt"
    import "time"

    func snd(ch chan int) {
        var x int = 0
        for {
            x++
            ch <- x
            time.Sleep(1 * 1e9)
        }

    }

    func rcv(ch chan int) {
        var x int
        for {
            x = <-ch
            fmt.Printf("received %d \n", x)

        }

    }

    func main() {
        var ch chan int = make(chan int)
        go rcv(ch)   // R1
        go snd(ch)   // S1
        rcv(ch)      // R2

    }

Ein Deadlock tritt nicht ein. Es ist aber möglich, dass z.B. R2
verhungert (nie einen Fortschritt macht), weil immer S1 und R1
miteinander kommunizieren. Solch eine Situation wird als Starvation
(Verhungerung) bezeichnet.

Konkreter Ausführungspfad.

        R1          S1             R2

    1.  pre(ch?)
    2.                             pre(ch?)
    3.             pre(ch!)
    4.             post(ch!)
    5.  post(ch?)
    6.  pre(ch?)
    7.             pre(ch!)
    8.             post(ch!)
    9.  post(ch?)
    ....

Wir gehen davon aus, dass S1 immer mit R1 kommuniziert (aber nie mit
R2). D.h. die Schritte 6-9 wiederholen sich immer. Extrem
unwahrscheinlich in der Praxis aber theoretisch möglich.

## Livelock

Ein Livelock beschreibt einen Situation in welcher immer mindestes ein
Thread nicht blockiert ist, aber kein Thread einen Forschritt erzielt.

Ein Livelock tritt in obigem Beispiel nicht auf. Als anschauliches
Beispiel für einen Livelock betrachten wir im Kapitel Aufgaben das
Problem der Speisenden Philosophen.

## Data race

Ein data race beschreibt eine Situation in der zwei nicht geschützte, im
Konflikt stehende Speicheroperationen (wobei mindestens eine
Schreiboperation involviert ist) gleichzeitig stattfinden.

Betrachte folgendes Beispiel.

    package main

    import "fmt"
    import "time"

    func main() {
        var x int
        y := make(chan int, 1)

        // T2
        go func() {
            y <- 1
            x++
            <-y

        }()

        x++
        y <- 1
        <-y

        time.Sleep(1 * 1e9)
        fmt.Printf("done \n")

    }

Mit T1 bezeichnen wir den Main Thread und mit T2 den weiteren Thread.
Zusätzlich zu Senden/Empfangs Ereignissen betrachten wir auch
Schreib/Lese Ereignisse.

Wir schreiben `w(x)` um das Schreibeereignisse der Variable x zu
bezeichnen. Für das Leseereignis schreiben wir `r(x)`.

Wir betrachten einen möglichen Programmablauf dargestellt als eine
Programmspur (trace). Für die Operation `x++` zeichnen wir der
Einfachheithalber nur das Ereignis `w(x)` auf.

Wir unterscheiden hier nicht zwischen pre und post Ereignissen. Alle
Eregnisse sind post Ereignisse. Deshalb lassen wir pre und post
Annotationen einfach weg.

         T1          T2

    1.               y!
    2.               w(x)
    3.   w(x)

In dem Programmablauf dargestellt als Programmspur tritt ein Data Race
ein falls zwei im Konflikt stehende Schreib/Lese-Ereignisse direkt
hintereinander auftraten. Siehe oben.

Betrachte folgenden alternativen Programmablauf.

         T1          T2

    1.               y!
    2.               w(x)
    3.               y?
    4.   w(x)

Anhand der Programmspur ist der Data Race nicht mehr ersichtlich, da
zwischen `w(x)_2` und `w(x)_4` sich `y?_3` befindet.

Die Programmspur kann aber umgeordnet werden, so dass der Data Race
eintritt. Folgende Umordnung ist erlaubt.

         T1          T2

    1.               y!
    2.               w(x)
    3.   w(x)
    4.               y?

Wir betrachten einen weiteren Programmablauf.

         T1          T2

    1.   w(x)
    2.   y!
    3.   y?
    4.               y!
    5.               w(x)
    6.               y?

Für diesen Programmablauf tritt der Data Race nicht ein.

*Beachte*. Um den Data Race (zwischen den zwei writes auf `y`)
aufzudecken, Bedarf es einer Umordnung der kritischen Sektionen. Eine
dynamische Data Race Analyse basiered auf der Lamport happens-before
Relation ist nicht in der Lage die kritischen Sektion an Tracepositionen
2-3 und an Tracepositionen 4-6 umzuordnen. Es gibt aber Verfahren die
eine solche Umordnung erlauben. Mehr Details zu dynamischer Data Race
Analyse gibt es in einem eigenen Abschnitt.

## Fazit

Ein Deadlock (falls er Eintritt) ist beobachtbar, da das Gesamtsystem
zum Stillstand kommt. Starvation und Livelock zu beobachten ist
trickreicher. Für alle Fehlerszenarien gilt. Sie können, müssen aber
nicht eintreten. Z.B. ein Deadlock manifestiert sich nur für einen
bestimmten Programmablauf (unter einer ganz bestimmten Konfiguration
etc). Im Fall von einem Data Race ist der Data Race nicht direkt aus der
Programmspur ablesbar und Bedarf einer Umordnung der Programmspur.
Nebenläufige Programmierfehler aufzudecken ist deshalb trickreich.

## Aufgabe: Speisende Philosophen

Wir betrachten das Problem der speisenden Philosophen. Die Anordnung der
Gabeln soll dabei keine Rolle spielen. Sprich wir gehen von N
Philosophen aus die an einem Tisch sitzen an welchen sich N Gabeln
befinden. Zum Essen sind pro Philosoph 2 Gabeln notwendig.

## Versuch 1

Hier ist eine mögliche Umsetzung.

    package main

    import "fmt"
    import "time"

    func philo(id int, forks chan int) {

        for {
            <-forks
            <-forks
            fmt.Printf("%d eats \n", id)
            time.Sleep(1 * 1e9)
            forks <- 1
            forks <- 1

            time.Sleep(1 * 1e9) // think

        }

    }

    func main() {
        var forks = make(chan int, 3)
        forks <- 1
        forks <- 1
        forks <- 1
        go philo(1, forks)
        go philo(2, forks)
        philo(3, forks)
    }

Wir modellieren die Gabeln als gepufferten Kanal. Jeder Philosoph
benötigt zwei Gabeln. Ergo, zweifaches Lesen auf dem `fork` Kanal.

Welche Probleme können auftreten?

### Diskussion

Verhungerung (starvation) ist möglich.

Verklemmung (deadlock) ist möglich.

Aufgabe: Liefern sie konkrete Beispiele (als Programmspur).

Musterlösung siehe unten.

Anstatt `forks?` schreiben wir `f?` usw. P1 bezeichnet Philosphenthread
1 usw. P3 ist der Main Thread.

Beispiel 1:

            P1          P2          P3

    1.                            pre(f!)
    2.                            post(f!)
    3.                            pre(f!)
    4.                            post(f!)
    5.                            pre(f!)
    6.                            post(f!)
    7.    pre(f?)
    8.                 pre(f?)
    9.                 post(f?)
    10.                pre(f?)
    11.                           pre(f?)
    12.                           post(f?)
    11.                           pre(f?)
    12.                           post(f?)
                                  // EAT
    13.                           pre(f!)
    14.                           post(f!)
    15.                           pre(f!)
    16.                           post(f!)
    ...

Die Schritte 11-16 wiederholen sich immer. Wozu ist dieses Beispiel gut?
Antwort siehe unten.

Beispiel 2:

            P1          P2          P3

    1.                            pre(f!)
    2.                            post(f!)
    3.                            pre(f!)
    4.                            post(f!)
    5.                            pre(f!)
    6.                            post(f!)
    7.    pre(f?)
    8.    post(f?)
    9.                 pre(f?)
    10.                post(f?)
    11.                           pre(f?)
    12.                           post(f?)
    13.   pre(f?)
    14.                pre(f?)
    15.                           pre(f?)

Wozu ist dieses Beispiel gut?

Beispiel 2 beschreibt einen Deadlock. Anhand Beispiel 1 sehen wir dass
Starvation möglich ist.

## Version 2

Hier ist ein weiterer Versuch.

    package main

    import "fmt"
    import "time"

    func philo(id int, forks chan int) {
        for {
            <-forks
            select {
            case <-forks:
                fmt.Printf("%d eats \n", id)
                time.Sleep(1 * 1e9)
                forks <- 1
                forks <- 1

                time.Sleep(1 * 1e9) // think
            default:
                forks <- 1
            }
        }

    }

    func main() {
        var forks = make(chan int, 3)
        forks <- 1
        forks <- 1
        forks <- 1
        go philo(1, forks)
        go philo(2, forks)
        philo(3, forks)
    }

### Diskussion

Verhungerung (starvation) ist weiterhin möglich. Beispiel 1 ist auch
anwendbar auf Version 2.

Ist eine Verklemmung (deadlock) immer noch möglich? Nein, ein ‘deadlock’
wird vermieden. Falls eine zweite Gabel nicht verfügbar, wird die erste
Gabel zurückgelegt.

Durch diesen Trick bekommen wir ein neues Problem. Ein Livelock ist
möglich. Anders als im Falle eines Deadlocks, kommt das System nie zum
Stillstand. Das Ziel (Philosoph isst) wird aber nie erreicht. Dazu
folgendes Beispiel.

Beispiel 3:

            P1          P2          P3

    1.                            pre(f!)
    2.                            post(f!)
    3.                            pre(f!)
    4.                            post(f!)
    5.                            pre(f!)
    6.                            post(f!)
    7.    pre(f?)
    8.    post(f?)
    9.                 pre(f?)
    10.                post(f?)
    11.                           pre(f?)
    12.                           post(f?)
    13.   pre(f?)
    14.                pre(f?)
    15.                           pre(f?)
    16.   pre(f!)
    17.   post(f!)
    18.                pre(f!)
    19.                post(f!)
    20.                           pre(f!)
    21.                           post(f!)
    ...

Die Schritte 7-21 wiederholen sich immer. In Schritt 7-8 Philo P1 holt
Philo P1 eine Gabel (erste Anweisung `<-forks`). In Schritt 16-17 gibt
Philo P1 die Gabel wieder zurück (`default` Fall). Analges Verhalten im
Fall von Philo P2 und P2.

Wir fassen zusammen. Das System kommt nie zum Stillstand. aber keiner
der Philosophen kann essen (= kein Fortschritt). Diese Situation wird
als Livelock bezeichnet.

### Version 3

Betrachte folgende weitere Variante.

    package main

    import "fmt"
    import "time"

    func philo(id int, forks chan int) {

        for {
            <-forks
            <-forks
            fmt.Printf("%d eats \n", id)
            time.Sleep(1 * 1e9)
            forks <- 1
            forks <- 1

            time.Sleep(1 * 1e9) // think

        }

    }

    func main() {
        var forks = make(chan int)
        go func() { forks <- 1 }()
        go func() { forks <- 1 }()
        go func() { forks <- 1 }()
        go philo(1, forks)
        go philo(2, forks)
        philo(3, forks)
    }

Welche der oben beschriebenen Probleme können noch auftreten?

## Zusammenfassung

-   Typische Probleme der nebenläufigen Programmierung

    -   Deadlock

    -   Livelock

    -   Starvation

    -   Data race

-   Aufzeichnung des Programmverhaltens (in einer Programmspur)

-   Analyse der Programmspur

-   Ausblick

    -   Programmanalyse zum Erkennen von Deadlock, …
