---
title: Die Programmiersprache Go
description: Martin Sulzmann
---



# Go

Programmiersprache entwickelt von Google: [Go](http://golang.org/)

-   Angelehnt an C
-   Statisches Typsystem
-   Funktionen höherer Ordnung
-   Garbage Collection
-   Objekt-orientierung durch Typschnittstellen (keine Klassen aber
    Methoden können Typen zugewiesen werden)
-   *Unterstützung von Nebenläufigkeit und Kommunikation*
    -   Leichtgewichtige Threads
    -   Kommunikation via Kanälen
        -   Formal fundiert: Communicating Sequential Processes, Sir
            Tony Hoare
    -   Philosophie: “Do not communicate by sharing memory. Instead
        share by communicating.”

# Hello World

    package main

    import "fmt"

    var x int

    func hi(y int) {
            fmt.Printf("hi %d\n",y)
    }

    func main() {
        x= 1
        hi(x)
        fmt.Printf("hello, world\n")
    }

-   Typdeklarationen in 'logischer' Reihenfolge
    -   `var varName varType`
    -   Eine Variable `varName` mit dem Typ `varType`
-   Eine Statement pro Zeile. Semikolon redundant.

# Go Toolchain

-   Ausführung via der "Kommandozeile"
    -   `go run hello.go`

    -   `gofmt hello.go`
        -   Automatischer "pretty printer"
        -   Ausgabe auf Konsole per Default
        -   `gofmt -w hello.go` schreibt ins gleiche File

    -   Den Editor können Sie frei wählen (emacs, ...)

-   Oder via web browser auf [offizieller Go
    Webseite](https://golang.org/)

-   Oder einfach nach Go plugin für IDE suchen.

Zur Info, unsere Programme bestimmen immer aus einer Datei.

# Nebenläufigkeit (goroutine)

Nebenläufige Ausführung: "just say go"

    package main

    import "fmt"
    import "time"

    func thread(s string) {
        for {
            fmt.Print(s)
            time.Sleep(1 * 1e9)
        }
    }

    func main() {

        go thread("A")
        go thread("B")
        thread("C")
    }

-   `go` auch bekannt als "fork" oder "spawn"

-   Nebenläufige Ausführung des Statements, hier der Funktionen
    thread("A") und thread("B").

-   Beachte, thread("C") wird im Haupt-thread ausgeführt. Sprich, es
    werden drei Threads nebenläufig ausgeführt.

-   Scheduling der Threads wird vom Laufzeitsysteme verwaltet.

-   Sobald der Haupt-thread terminiert werden alle innerhalb des
    Haupt-threads gestarteten Threads terminiert (dies ist anders als in
    Java)

## Nebenläufigkeit (concurrency) versus Parallelität (parallelism)

-   Parallelism: Make programs run faster by making use of additional
    CPUs (parallel hardware)

-   Concurrency: Program organized into multiple threads of control.
    Threads may work independently or work on a common task.

-   See also
    [here](https://wiki.haskell.org/Parallelism_vs._Concurrency)

## Multi-threading in Go

### Terminologie

Thread = Sequenz von hintereinander ausgeführten Anweisungen

Threadzustand:

-   Running (wird gerade ausgefuehrt)

-   Waiting (koennte ausgefuehrt werden aber keine CPU verfuegbar)

-   Blocked (kann nicht ausgefuehrt werden)

Multithreading = Abwechselnde Ausführung von mehreren Threads auf einer
CPU

Scheduling = Systematisches Vorgehen zum Multithreading

Preemptiv = Jeder Thread bekommt eine gewisse Zeitscheibe

Kooperativ = Jeder Thread wird solange ausgeführt bis auf eine
blockierende Anweisung gestossen wird

Blockierende Anweisungen:

-   Thread schlafen legen (delay/sleep)

-   Empfang auf Kanal (potentiell blockierend da Kanal 'leer' sein kann)

-   Senden auf Kanal (potentiell blockierend da Kanal 'voll' sein kann)

#### Zustandsbasierte Ausführung

Notation angelehnt an die Ausfuehrung von UPPAAL/kommunizierenden
Automaten.

-   Der Programzustand besteht aus dem Zustand der einzelnen Threads.
    Z.B.

<!-- -->

    (Main.Running, A.Waiting, B.Waiting)

beschreibt den Zustand in dem

1.  der main Thread ausgefuehrt, und

2.  Thread A und B im Wartezustand sind.

-   Erzeugung eines Threads (via dem `go` Schluesselwort) fuegt einen
    neuen Thread hinzu. Initial im Wartezustand.

Betrachte z.B.

    func a() {
      }
    func main() {
     go a()
    }

Initial ist der Programmzustand wie folgt.

    Main.Running

Nach Ausfuehrung von `go a()` befinden wir uns im folgenden
Programmzustand.

    (Main.Running, A.Waiting)

-   Ein Programmpfad wird beschrieben durch die Abfolge der einzelnen
    Programmzustaende. Der Fortschritt vom aktuellen auf den
    Folgezustand wird getrennt durch `-->`.

<!-- -->

          Main.Running

    -->   (Main.Running, A.Waiting)

### Beispiel

Ausfuehrung obigen Programs. Annahme: Eine CPU verfuegbar.

        Main.Running

    --> (Main.Running, A.Waiting)

    --> (Main.Running, A.Waiting, B.Waiting)

    --> (Main.Blocked, A.Waiting, B.Waiting)

-   Main Thread blockiert wegen Sleep Anweisung

-   Einer der wartenden Threads bekommt die Kontrolle

-   Annahme: Der am laengsten wartende Thread bekommt Kontrolle

<!-- -->

    ...

    --> (Main.Blocked, A.Waiting, B.Waiting)

    --> (Main.Blocked, A.Running, B.Waiting)

    --> (Main.Waiting, A.Blocked, B. Waiting)

-   A Thread blockiert wegen Sleep Anweisung

-   In der Zwischenzweit, Blockierung von Main Thread aufgehoben, da
    'Sleep' Zeit um ist

<!-- -->

    ...

    --> (Main.Waiting, A.Blocked, B. Waiting)

    --> (Main.Waiting, A.Blocked, B.Running)

usw

# Lambdas (annonyme Funktionen) in Go.

Unser Beispiel von vorher.

    // Beispiel mit "lambdas" = annonymen Funktionen in Go

    package main

    import "fmt"
    import "time"

    func thread(s string) {
        for {
            fmt.Print(s)
            time.Sleep(1 * 1e9)
        }
    }

    func main() {

        // Direkte Ausfuehrung einer annonymen Funktion
        go func() {
            for {
                fmt.Print("A")
                time.Sleep(1 * 1e9)
            }

        }()

        // bFunc ist eine Funktionsvariable!
        // Typ automatisch inferriert
        bFunc := func() {
            for {
                fmt.Print("A")
                time.Sleep(1 * 1e9)
            }

        }
        go bFunc()
        thread("C")
    }

Und eine weitere Variante.

    // Beispiel mit "lambdas" = annonymen Funktionen in Go

    package main

    import "fmt"
    import "time"

    func thread(s string) {
        for {
            fmt.Print(s)
            time.Sleep(1 * 1e9)
        }
    }

    func main() {

        // Direkte Ausfuehrung einer annonymen Funktion
        go func() {
            for {
                fmt.Print("A")
                time.Sleep(1 * 1e9)
            }

        }()

        // bFunc ist eine Funktionsvariable!
        // Typ explizit deklariert
        var bFunc func()
        bFunc = func() {
            for {
                fmt.Print("A")
                time.Sleep(1 * 1e9)
            }

        }
        go bFunc()
        thread("C")
    }

# Kommunikation ("channels")

Der Nachrichtenaustausch zwischen Threads geschieht mit Hilfe von
Kanälen ("channels"). Folgendes Prinzip gilt:

1.  Jeder Thread kann Nachrichten senden und empfangen.

2.  Eine Nachricht kann von genau einem Thread empfangen werden.

3.  Ein Empfänger muss notwendigerweise auf eine Nachricht warten.

4.  Ein Sender kann fortfahren, solange der Kanal noch einen einen
    Puffer (Zwischenspeicher) zur Verfügung hat.

5.  Der Puffer ist immer endlich. Puffer kann voll sein. Dann kann ein
    Sender nur fortfahren, falls es einen Empfänger gibt.

Im Detail siehe unten.

**Getypte Kanäle**

    var ch chan int

Wir deklarieren eine Variable `ch` als einen Kanal. Die Werte die über
diesen Kanal ausgetauscht werden sollen, müssen vom Typ Integer sein.

**Kanal erzeugen**

    ch = make(chan int)

Ein Kanal muss via `make` erzeugt werden. Eine Deklaration via
`var ch chan int` liefert nur einen *geschlossenen* Kanal auf dem keine
Operationen ausgefuehrt werden koennen.

**Kanal ohne/mit Puffer**

In Go gibt es zwei Arten von Kanälen. Ohne Puffer und mit Puffer. Puffer
= Zwischenspeicher für Nachrichten. Aufgebaut wie eine Schlange (queue).

    ch1 = make(chan int)

    ch2 = make(chan int, 50)

Kanal ch2 hat Platz für maximal 50 (Puffer)Elemente (= Nachrichten).
Kanal ch1 ist ein Kanal ohne Puffer.

Folgende Regeln gelten im Falle von Nachrichtenaustasch.

-   Kanal ohne Puffer (synchrone Kommunikation):

    -   Ein Empfänger blockiert solange bis ein Sender auftaucht.
    -   Gleiches gilt für den Sender (da kein Puffer vorhanden ist)

-   Kanal mit Puffer (asynchrone Kommunikation):

    -   Ein Empfänger blockiert solange bis Nachricht im Puffer
        vorhanden ist.
    -   Ein Sender blockiert nur falls kein Puffer mehr vorhanden ist.
    -   Der Puffer verhält sich wie eine Schlange ("FIFO queue").

Der Unterschied ist also wie folgt.

Im Falle eines Kanals ohne Puffer, muss sich eine Sender immer mit einem
Empfänger *synchronisieren*. Sender und Empfänger blockieren immer. Das
Go Laufzeitsystem prüft, ob es blockierte Sender und Empfänger für den
gleichen Kanal gibt. Falls ja kommunizieren beide miteinander. Die
Blockierung beider wird aufgelöst.

Falls Puffer vorhanden ist, verhält sich der Sender *asynchron*.
Nachricht wird in den Puffer geschrieben. Der Sender blockiert nicht.
Falls der Puffer voll ist, blockiert der Sender bis Puffer wieder
vorhanden ist. Der Empfänger synchronisiert sich immer mit dem Puffer.
Falls Puffer leer blockiert der Empfänger. Sonst wird eine Nachricht aus
dem Puffer geholt.

**Senden**

    ch <- y

Sende Wert `y` an Kanal `ch`

**Empfangen**

    x = <- ch

Empfange von Kanal `ch` und speichere Wert in `x`

## Beispiel

    package main

    import "fmt"
    import "time"

    func snd(s string, ch chan int) {
        var x int = 0
        for {
            x++
            ch <- x
            fmt.Printf("%s sendet %d \n", s, x)
            time.Sleep(1 * 1e9)
        }

    }

    func rcv(ch chan int) {
        var x int
        for {
            x = <-ch
            fmt.Printf("empfangen %d \n", x)

        }

    }

    func main() {
        var ch chan int = make(chan int)
        go snd("A", ch)
        rcv(ch)

    }

## Beispielhafte Ausführung (Zustands-basiert)

        rcv.Running

    --> (rcv.Running, snd.Waiting)

    --> (rcv.Blocked_(<-ch?), snd.Waiting)

         Notation: Im Fall von Blocked beschreibt der 'subscript' den Blockierunsgrund

        <-ch?   Empfaenger ist blockiert
        ch<-1?  Sender ist blockiert


    --> (rcv.Blocked_(<-ch?), snd.Running)

    --> (rcv.Blocked_(<-ch?), snd.Blocked_(ch<-1?))

         Erste Thread wartet auf den Empfang einer Nachricht.
         Zweite Thread versucht eine Nachricht zu versenden.

         Wir sagen beide Threads können sich synchronisieren (es findet eine Art von "hand-shake" statt).
         Der Nachrichtenaustausch findet statt und die Blockierung wird aufgehoben.


    --> (rcv.Waiting, snd.Waiting)

    --> (rcv.Running, snd.Waiting)

    ...

Wir betrachten folgende Variante (1 Empfaenger, 2 Sender).

    func main() {
        var ch chan int = make(chan int)
        go snd("A", ch) // snd1
        go snd("B", ch) // snd2
        rcv(ch)

    }

        rcv.Running

    --> (rcv.Running, snd1.Waiting)

    --> (rcv.Running, snd1.Waiting, snd2.Waiting)

    --> (rcv.Blocked_(<-ch?), snd1.Waiting, snd2.Waiting)

    --> (rcv.Blocked_(<-ch?), snd1.Running, snd2.Waiting)

    --> (rcv.Blocked_(<-ch?), snd1.Blocked_(ch<-1?), snd2.Waiting)

        Mehrere Moeglichkeiten:

        (1) rcv synchronisiert sich mit snd1, oder
        (2) snd2 Thread laeuft weiter.

        Wie waehlen Moeglichkeit (2)

    --> (rcv.Blocked_(<-ch?), snd1.Blocked_(ch<-1?), snd2.Running)

    --> (rcv.Blocked_(<-ch?), snd1.Blocked_(ch<-1?), snd2.Blocked_(ch<-1?))

        Mehrere Moeglichkeiten:

        (1) rcv synchronisiert sich mit snd1, oder
        (2) rcv synchronisiert sich mit snd2.

        Wir waehlen Moeglichkeit (1)

        [Hintergrund:
        Das Go Laufzeitsystem verwaltet blockierende Empfaenger in Sender
        in einer Schlange (queue), deshalb ist es Moeglichkeit (1)
        am wahrscheinlichsten.]

    --> (rcv.Waiting, snd1.Waiting, snd2.Blocked_(ch<-1?))

    ...

Wir betrachten eine weitere Variante (Kanal mit Puffer)

    func main() {
        var ch chan int = make(chan int, 1) // Kanal mit Puffer
        go snd("A", ch)
        rcv(ch)

    }

        rcv.Running

    --> (rcv.Running, snd.Waiting)

    --> (rcv.Blocked_(<-ch?), snd.Waiting)

    --> (rcv.Blocked_(<-ch?), snd.Running)

        // Kanalpuffer mit 1 gefuellt

    --> (rcv.Blocked_(<-ch?), snd.Blocked_(Sleep(1s)?))

    --> (rcv.Waiting, snd.Blocked_(Sleep(1s)?))

        // Kanal wieder leer

    --> (rcv.Running, snd.Blocked_(Sleep(1s)?))

    ...

Als weitere Variante. Kanal mit Puffer 1 und snd ohne Sleep.

    func snd(s string, ch chan int) {
        var x int = 0
        for {
            x++
            ch <- x
            fmt.Printf("%s sendet %d \n", s, x)
        }

    }

        rcv.Running

    --> (rcv.Running, snd.Waiting)

    --> (rcv.Blocked_(<-ch?), snd.Waiting)

    --> (rcv.Blocked_(<-ch?), snd.Running)

        // Kanalpuffer mit 1 gefuellt

    --> (rcv.Blocked_(<-ch?), snd.Blocked_(ch<-2?))

         // Zwei Moeglichkeiten
         // (a) rcv liest aus Kanal, oder
         // (b) direkt von snd
         //
         // Go Semantik/Laufzeitsystem waehlt Variante (a)
         // D.h. im Fall von gepufferten Kanal, synchronisiert sich der Empfaenger immer mit dem Kanal.

    --> (rcv.Running, snd.Blocked_(ch<-2?))

         // Kanal wieder leer

    --> (rcv.Blocked_(<-ch?), snd.Blocked_(ch<-2?))

         // Wiederum zwei Moeglichkeiten
         // (a) snd schreibt in Kanal, oder
         // (b) uebergibt Wert direkt an rcv
         //
         // (a) ist die Go Variante. Siehe oben.

-   Im Falle von 'Sleep' wird die Ausfuehrung oft chaotisch (keine
    Garantie, dass nach exakt einer Sekunde der Thread wieder aufwacht)

-   Im Fall eines Kanals mit Puffer ist das Senden nicht blockierend
    (falls noch genuegend Platz vorhanden).

-   Im Fall von Kanaelen ohne Puffer ist das Vorhalten meistens
    vorhersehbarer, da der Sender sich immer mit einem Empfaenger
    synchronisieren muss.

## Eingeschränkte Kommunikation

Funktionsprototypen können mit Annotationen versehen werden.

Nur Senden

    func snd(ch chan <- int) {
     ...
    }

Nur Empfangen

    func rcv(ch <- chan int) {
     ...
    }

# Beispiele Kanal mit und ohne Puffer

    package main

    // Kanal ohne Puffer.
    // Bleibt immer stecken.
    func test1() {
        ch := make(chan int)

        ch <- 1
        <-ch
    }

    // Kanal ohne Puffer.
    // Sender synchronisiert sich mit Empfaenger.
    func test2() {
        ch := make(chan int)

        go func() {
            ch <- 1
        }()
        <-ch

    }

    // Kanal ohne Puffer.
    // 2 Sender, 1 Empfaenger. Kann stecken bleiben.
    func test3() {
        ch := make(chan int)

        snd := func() { ch <- 1 }
        rcv := func() { <-ch }

        go snd()
        go rcv()
        snd()

    }

    // Kanal ohne Puffer.
    // 2 Sender, 2 Empfaenger.
    func test4() {
        ch := make(chan int)

        snd := func() { ch <- 1 }
        rcv := func() { <-ch }

        go snd() // S1
        go snd() // S2
        rcv()    // R1 empfaengt von S1 oder S2
        rcv()    // R2
        // Falls R1 empfaengt von S1, dann empfaengt R2 von S2
        // Falls R1 empfaengt von S2, dann empfaengt R2 von S1

    }

    // Kanal mit Puffer.
    // Bleibt nie stecken.
    func test5() {
        ch := make(chan int, 1)

        ch <- 1
        <-ch
    }

    // Kanal mit Puffer.
    // Bleibt nie stecken.
    func test6() {
        ch := make(chan int, 2)

        ch <- 1
        ch <- 1
        <-ch
        ch <- 1
    }

    func main() {
        // test1()
        test2()
        test3()
        test4()
        test3()

    }

# Synchrone versus Asynchrone Kommunikation

Zur Wiederholung.

-   Kanal ohne Puffer (synchrone Kommunikation, synchroner Kanal)
    -   Sender blockiert falls kein Empfänger vorhanden
    -   Empfänger blockiert falls kein Sender vorhanden
    -   Direkte (synchrone) Kommunikation zwischen Sender und Empfänger
    -   Sender übergibt Nachricht an Empfänger
-   Kanal mit Puffer (asynchrone Kommunikation, asynchroner Kanal)
    -   Sender blockiert falls Puffer voll
    -   Empfänger blockiert falls Puffer leer
    -   Indirekte (asynchrone) Kommunikation zwischen Sender und
        Empfänger
    -   Sender legt Nachricht in Puffer. Empfänger holt Nachricht aus
        Puffer

Beide Kommunikationsarten sind gleichmächtig. D.h. ein Kanal mit Puffer
kann durch Kanäle ohne Puffer emuliert werden. Eine Reihe bekannter
Synchronisationsprimitive (z.B. Mutex) kann mit Hilfe von Kanälen
emuliert werden.

## Aufgabe: Mutex

Go unterstützt die bekannten Synchronisationsprimitive via Mutex etc.
Siehe [http://golang.org/pkg/sync/](sync). Jedoch können wir uns recht
einfach einen Mutex mit Hilfe von Kanälen selber bauen (Die nativen
Mutexe in Go sind sicherlich effzienter implementiert, aber hier geht es
nur um das Prinzip).

-   Idee: Mutex ist repräsentiert als Kanal mit einem Pufferelement.
-   Der Puffer ist initial leer.
-   `lock` sendet und `unlock` empfängt.

    type Mutex (chan int)

    func newMutex() Mutex {
        var ch = make(chan int, 1)
        return ch
    }

    func lock(m Mutex) {
        m <- 1
    }

    func unlock(m Mutex) {
        <-m
    }

Obige Implementierung basiert auf einen Kanal mit Puffer der Grösse 1.
Es geht auch ohne Puffer. Unten finden sich dazu teilweise Lösungen (die
mit Problemen behaftet sind). Eine komplette Lösungen findet sich am
Schluss in der Aufgaben Sektion.

## Aufgabe: Mutierbare Variable

Implementieren sie eine mutierbare Variable, die durch folgende
Schnittstelle beschrieben ist.

    type MVar (chan int)
    func newMVar(x int) MVar
    func takeMVar(m MVar) int
    func putMVar(m MVar, x int)

-   Eine MVar ist entweder voll oder leer
-   Initial ist eine MVar mit einem Integer Wert gefüllt
-   `takeMVar`
    -   lesen des Wertes falls voll
    -   blockiert ansonsten
-   `putMVar`
    -   schreiben eines Wertes falls leer
    -   blockiert ansonsten
-   Hinweise
    -   `takeMVar` entspricht Empfangen
    -   `putMVar` entspricht Senden
    -   Initial ist eine MVar voll, deshalb sollte `takeMVar` initial
        nicht blockieren
    -   Implementierung trivial falls wir einen Kanal mit einem Puffer
        der Größe 1 verwenden.
    -   Ziel hier, verwenden Sie einen rein synchronen Kanal ohne Puffer

Anmerkung: Mit Hilfe einer MVar können wir ganz einfach einen Mutex
emulieren.

-   newMutx = newMVar mit einem Dummy Element.

-   lock = takeMVar

-   unlock = putMVar eines Dummy Elements.

### MVar Beispiel komplett

    package main

    import "fmt"
    import "time"

    type MVar (chan int)

    func newMVar(x int) MVar {
        var ch = make(chan int)
        go func() { ch <- x }()
        return ch
    }

Der Trick ist:

-   Wir kreieren einen synchronen Kanal `ch`
-   In einem nebenläufigen Hilfsthread füllen wir den Kanal mit dem
    initalen Element. Der Hilfsthread blockiert zwar, dadurch aber
    garantieren wir, das initial die MVar voll ist.
-   Da die Blockierung nur im nebenläufigen Hilfsthread stattfindet,
    kann der Kanal `ch` wird als Wert zurückgegeben

Die weiteren MVar Primitive können direkt auf die Kanal Operationen
Senden/Empfangen abgebildet werden.

    func takeMVar(m MVar) int {
        var x int
        x = <-m
        return x
    }

    func putMVar(m MVar, x int) {
        m <- x
    }

Es folgt noch eine Beispielanwendung einer MVar.

    func producer(m MVar) {
        var x int = 1
        for {
            time.Sleep(1 * 1e9)
            putMVar(m, x)
            x++
        }
    }

    func consumer(m MVar) {
        for {
            var x int = takeMVar(m)
            fmt.Printf("Received %d \n", x)
        }
    }

    func testMVar() {
        var m MVar

        m = newMVar(1)

        go producer(m)

        consumer(m)

    }

### MVar Kodierungs Probleme

#### Problem direkter Kommunikation

Folgt direkt nach `newMVar` ein `putMVar` folgt, ist es möglich, dass
die `newMVar` Sendeoperation im nebenläufigen Thread von der `putMVar`
Sendeoperation überhohlt wird.

Betrachte dazu folgendes Beispiel.

    func testMVar2() {
        m := newMVar(1) // 1
        go putMVar(m, 2) // 2
        x := takeMVar(m)
        fmt.Printf("Received %d \n", x)
    }

MVar wird initial mit `1` gefühlt. Deshalb erwarten wir die Ausgabe `1`.
Aber auch `2` ist möglich.

#### Problem Kommunikation bleibt stecken

Weiteres Problem tritt ein falls es eine Abfolge von hintereinander
ausgeführten `takeMVar` und `putMvar` Befehlen gibt. Betrachte

    func testMVar3() {
        var m MVar
        m = newMVar(1) // Full
        takeMVar(m)    // Empty
        putMVar(m, 2)  // Full
    }

In Klammern sind die Zustände der MVar beschrieben. Laut MVar
Beschreibung sollte obige Programmabfolge durchlaufen, die Ausführung
bleibt aber stecken. Wieso?

-   Das erstmalige Füllen der MVar in `newMVar` geschieht asynchron
-   Alle weiteren `putMvar` Operationen laufen aber synchron ab!
-   Deshalb blockiert \`putMVar(m, 2)' und das liefert einen Deadlock.

Eine Lösung: Nebenläufiger Thread der den Zustand der MVar kontrolliert.

    const (
        Empty = 0
        Full  = 1
    )

    func newMVar2(x int) MVar {
        var ch = make(chan int)
        go func() {
            var state = Full
            var elem int = x
            for {
                switch {
                case state == Full:
                    ch <- elem
                    state = Empty
                case state == Empty:
                    elem = <-ch
                    state = Full
                }
            }
        }()
        return ch
    }

`takeMVar` und `putVar` wie gehabt.

Problem Kommunikation bleibt stecken ist damit behoben.

Beachte:

-   `takeMvar` und `putMVar` können sich auch direkt synchronisieren,
    ohne Synchronisation via dem nebenläufigen Thread in `newMVar`.
-   Im Falle einer direkten Synchronisation bleibt der MVar Zustand
    (korrekterweise) natürlich invariant.
-   Deshalb bleibt immer noch das "Problem direkter Kommunikation".

## Kompletter Sourcecode

    package main

    import "fmt"
    import "time"

    // Mutex implementiert als Kanal mit Puffer der Groesse 1.
    type Mutex (chan int)

    func newMutex() Mutex {
        var ch = make(chan int, 1)
        return ch
    }

    func lock(m Mutex) {
        m <- 1
    }

    func unlock(m Mutex) {
        <-m
    }

    // MVar mit Hilfe
    type MVar (chan int)

    func newMVar(x int) MVar {
        var ch = make(chan int)
        go func() { ch <- x }()
        return ch
    }

    func takeMVar(m MVar) int {
        var x int
        x = <-m
        return x
    }

    func putMVar(m MVar, x int) {
        m <- x
    }

    // MVar Beispiel
    func producer(m MVar) {
        var x int = 1
        for {
            time.Sleep(1 * 1e9)
            putMVar(m, x)
            x++
        }
    }

    func consumer(m MVar) {
        for {
            var x int = takeMVar(m)
            fmt.Printf("Received %d \n", x)
        }
    }

    func testMVar() {
        var m MVar

        m = newMVar(1)

        go producer(m)

        consumer(m)

    }

    // MVar Beispiel 2
    // 2 ueberholt 1
    func testMVar2() {
        m := newMVar(1)  // 1
        go putMVar(m, 2) // 2
        x := takeMVar(m)
        fmt.Printf("Received %d \n", x)
    }

    // Deadlock
    func testMVar3() {
        var m MVar
        m = newMVar(1) // Full
        takeMVar(m)    // Empty
        putMVar(m, 2)  // Full
    }

    // 2te MVar Kodierung
    const (
        Empty = 0
        Full  = 1
    )

    func newMVar2(x int) MVar {
        var ch = make(chan int)
        go func() {
            var state = Full
            var elem int = x
            for {
                switch {
                case state == Full:
                    ch <- elem
                    state = Empty
                case state == Empty:
                    elem = <-ch
                    state = Full
                }
            }
        }()
        return ch
    }

    // Wir verwenden newMVar2 anstatt newMVar
    func testMVar4() {
        m := newMVar2(1) // 1
        go putMVar(m, 2) // 2
        x := takeMVar(m)
        fmt.Printf("Received %d \n", x)
    }

    func testMVar5() {
        var m MVar
        m = newMVar2(1) // Full
        takeMVar(m)     // Empty
        putMVar(m, 2)   // Full
    }

    func main() {

        // testMVar()
        // testMVar2()
        // testMVar3()

        testMVar4()
        testMVar5()

    }

# Kanäle von Kanälen ("channels of channels")

Kanäle sind Werte ("first-class citizens")

    `var ch chan (chan int)`

Kanal der als Werte Kanäle von Integern enthält

Erlaubt komplexe simultane Programmiermuster

## Beispiel

    package main

    import "fmt"
    import "time"

    type Request struct {
        id  int
        ack chan int
    }

Eine Anfrage besteht aus einer Identifikationsnummer und einem Kanal via
dem wir die erfolgreiche Bearbeitung signalisieren.

    func worker(req chan Request) {
        var c Request
        for {
            c = <-req
            fmt.Printf("request received from %d \n", c.id)
            time.Sleep(1 * 1e9)
            fmt.Println("notify")
            c.ack <- 1
        }
    }

Der Arbeiter wartet auf Anfragen. Nach Abarbeitung jeder Anfrage wird
der Kunde via dem `ack` Kanal benachrichtigt.

    func client(id int, req chan Request) {
        var ack = make(chan int)
        for {
            c := Request{id, ack}
            req <- c
            <-ack
        }

    }

Der Kunde schickt Anfrage und wartet via dem `ack` Kanal auf die
erfolgreiche Bearbeitung.

Hier ist eine Beispielhafe Ausführung.

    func main() {
        var req = make(chan Request)
        go worker(req)
        go client(1, req)
        client(2, req)
    }

## Sleeping barber

Beschreibung: Es gibt einen Barbier und mehrere Kunden. Jeder Kunde
möchte sich die Haare schneiden lassen, falls der Barbier verfügbar ist.
Der Kunde muss warten falls ein anderer Kunde gerade einen Haarschnitt
bekommt.

Unten folgt eine mögliche Implementierung in Go.

    package main

    import "fmt"
    import "time"

    const (
        NUMBER_OF_CHAIRS = 8
    )

    type Request struct {
        id  int
        ack chan int
    }

    func barber(waitQ (chan Request)) {

        for {
            req := <-waitQ
            fmt.Printf("BARBER: Serving customer %d \n", req.id)
            time.Sleep(1 * 1e9)
            fmt.Printf("BARBER: Done with customer %d \n", req.id)
            req.ack <- 1

        } // for

    } // barber

    func customer(waitQ (chan Request), id int) {
        var ack = make(chan int)
        for {

            fmt.Printf("CUSTOMER: %d wants hair cut \n", id)
            req := Request{id, ack}
            waitQ <- req
            fmt.Printf("CUSTOMER: %d sits on chair \n", id)
            <-ack
            fmt.Printf("CUSTOMER: %d served by barber \n", id)
            time.Sleep(1 * 1e9)

        } // for

    } // customer

    func main() {

        var (
            waitQ = make(chan Request, NUMBER_OF_CHAIRS)
        )

        go customer(waitQ, 1)
        go customer(waitQ, 2)
        barber(waitQ)

    }

Beachte:

-   Wir verwenden einen Kanal mit Puffer um das Warten auf einem Stuhl
    zu modellieren
-   Falls noch Stühle vorhanden sind (sprich noch Platz im Puffer), dann
    kann der Kunde noch was sinnvolles machen (Zeitung lesen etc) bis er
    an die Reihe kommt
-   Ansonsten, wird der Kunde blockiert beim Absenden des Requests
    (würde bedeuten der Barbierladen ist voll, und er muss draussen
    warten)
-   In obiger Modellierung, ist das Haareschneiden und die Bestätigung
    miteinander vermischt (könnte man noch trennen, wenn man will)

## Aufgabe: Publish/Subscribe

Ihre Aufgabe ist die Implementierung eines Publish/Subscribe Servers und
mehrer Beispiel Clients. Als Vorgabe können Sie das "channels of
channels" Beispiel aus der Vorlesung verwenden. Folgende Veränderungen
sollten Sie vornehmen.

Anstatt eines Request Kanals gibt es je einen Publish und Subscribe
Kanal. Der Server empfängt auf beiden Kanälen und leitet "Publish"
Nachrichten an die entsprechenden registrierten Clients weiter.

Es gibt es zwei Arten von Clients. Publish Clients und Subscribe
Clients.

Beachte: Falls der Server sämtliche Clients in einem Thread abhandelt,
könnte der Server blockieren falls Subscribe Clients aufhören
Nachrichten zu lesen. Wie könnte diese Problem gelöst werden?

### Wir versuchen es mal

Im folgenden entwickeln wir inkrementell eine Lösung (unten nochmal
komplett).

Zuerst mal ein paar notwendige Datenstrukturen

    type Message struct {
        topic string
        body  string
    }

Jede Nachricht (message) besteht aus einem "topic" und "body".

    type Sub struct {
        topic string
        news  chan Message
    }

Jeder Subscriber registriert ein "topic" und einen "news" Kanal via dem
Nachrichten zu dem entsprechenden "topic" erhalten werden können.

    type Server struct {
        csub chan Sub
        cpub chan Message
    }

Der Server verwaltet zwei Kanäle. Ein Kanal (csub) über den sich
Subscriber registrieren können und ein Kanal (cpub) über den ein
Publizierer Nachrichten schickt.

### Subscriber und Publizierer

    func subscriber(server Server, t string) {
        s := Sub{topic: t, news: make(chan Message)}
        server.csub <- s

        for {
            msg := <-s.news
            fmt.Printf("topic %s: \n message %s \n", t, msg.body)

        }

    }

Ein Subscriber registriert sich und wartet auf Nachrichten.

    func slashdot(server Server) {
        for {
            m := Message{topic: "slashdot", body: "some news"}
            server.cpub <- m
            time.Sleep(2 * 1e9)

        }

    }

Ein Publizierer (hier "slashdot") verschickt Nachrichten über den
entsprechenden Kanal.

### Server

    func pubSubServer(server Server) {
        subscribers := list.New()

        for {

            select {
            case s := <-server.csub:
                subscribers.PushBack(s)
            case m := <-server.cpub:
                for e := subscribers.Front(); e != nil; e = e.Next() {
                    s := (e.Value).(Sub) // type assertion
                    if s.topic == m.topic {
                        s.news <- m                          // (B)
                    }
                }

            }

        }

    }

Der Server verwaltet die Liste von Subscribern. Er horcht gleichzeitig
(via `select`) auf den jeweiligen Kanälen für Subscriber und
Publizierer. Ein Subscriber wird einfach zur Liste hinzugefügt. Eine
Nachricht eines Publizierers wird an den dafür sich registrierten
Subscriber geschickt.

### Blockierung des Servers

Nun zur obigen Problemstellung. Falls der Server sämtliche Clients in
einem Thread abhandelt, könnte der Server blockieren falls Subscribe
Clients aufhören Nachrichten zu lesen. Wieso?

Man betrachte die mit (B) markierte Programmstelle. Falls ein Subscriber
die Nachricht nicht abholt, wird der Server an dieser Stelle blockieren.
Was wären aushilfen?

1.  Der "news" Kanals des Subscribers hat einen Puffer. Was ist aber
    falls der Puffer voll läuft?

2.  Wir legen für jeden Subscriber einen eigenen Thread an. Dieser
    Thread verarbeitet alle für den Subscriber bestimmte Nachrichten.
    Sprich, wir schicken die Nachricht nicht direkt an den Subscriber,
    sondern zuerst an diesen Hilfsthread. Dieser Hilfsthread garantiert
    alle Nachrichten zu verarbeiten und darf natürlich nicht blockieren.
    Falls der Puffer voll läuft, könnte man

    1.  Nachrichten verwerfen, oder
    2.  einen dynamisch wachsenden internen Puffer anlegen.

3.  Es gibt noch eine einfachere Möglichkeit. Ersetze die
    Programmstelle (B) durch

                        go func() { s.news <- m }()

Publizieren der Nachricht geschickt asynchron. Dadurch modellieren wir
effektiv einen Kanal mit unendlicher Puffergröße (nur durch den
vorhandenen Speicher begrenzt).

### Komplette Lösung

-   Wir bauen die zusätzliche Variante ein, dass eine Nachricht
    verworfen wird, falls die Nachricht nicht innerhalb einer
    Zeitschranke abgeholt wird
-   Wir verwenden ein paar Go Bibliotheken, z.B. Umwandlung von Integer
    nach String, Listen etc.

    // publish, subscribe example
    // adopted from Russ Cox

    package main

    import "fmt"
    import "time"
    import "strconv"
    import "container/list"

    type Message struct {
        topic string
        body  string
    }

    type Sub struct {
        topic string
        news  chan Message
    }

    type Server struct {
        csub chan Sub
        cpub chan Message
    }

    func subscriber(server Server, t string) {
        s := Sub{topic: t, news: make(chan Message)}
        server.csub <- s

        for {
            msg := <-s.news
            fmt.Printf("topic %s: \n message %s \n", t, msg.body)

        }

    }

    func pubSubServer(server Server) {
        subscribers := list.New()

        for {

            select {
            case s := <-server.csub:
                subscribers.PushBack(s)
            case m := <-server.cpub:
                for e := subscribers.Front(); e != nil; e = e.Next() {
                    s := (e.Value).(Sub) // type assertion
                    if s.topic == m.topic {
                        // s.news <- m

                        // avoid blocking by publishing asynchronously
                        // go func() { s.news <- m }()

                        // avoid blocking, throw away msg if not picked up after 1sec
                        go func() {
                            select {
                            case s.news <- m:
                            case <-time.After(1 * 1e9):
                            }
                        }()

                    }
                }

            }

        }

    }

    func slashdot(server Server) {
        for {
            m := Message{topic: "slashdot", body: "some news"}
            server.cpub <- m
            time.Sleep(2 * 1e9)

        }

    }

    func reuters(server Server) {
        i := 0
        for {
            s := strconv.Itoa(i)
            // string(i) won't give us the desired effect
            m := Message{topic: "reuters", body: "some news " + s}
            server.cpub <- m
            time.Sleep(1 * 1e9)
            i++

        }

    }

    func main() {
        server := Server{csub: make(chan Sub), cpub: make(chan Message)}

        go pubSubServer(server)
        go subscriber(server, "slashdot")
        go subscriber(server, "reuters")

        go slashdot(server)
        reuters(server)
    }

# Nichtdeterministische Auswahl ("select")

-   Oftmals ist es notwendig gleichzeitig auf mehrere Ereignisse zu
    warten.
    -   Z.B. Anfrage an google maps und map quest.
    -   Eine Antwort/Nachricht ist ausreichend.
    -   Warten bis beide Antworten/Nachrichten vorhanden sind ist nicht
        notwendig (und auch unnötig)
-   Beispiel
    -   Warte auf Kanal1 Nachricht
    -   Warte auf Kanal2 Nachricht
    -   Schicke Nachricht an Kanal3
-   Welche Reihenfolge?

Erster Versuch:

    x = <-ch1
    y = <-ch2
    ch3 <- 1

Was ist falls kein Sender auf `ch1` aber Sender auf `ch2`? Obige
Programmsequenz blockiert.

Probieren wir es damit.

    y = <-ch2
    x = <-ch1
    ch3 <- 1

Blockiert wiederum falls falls kein Sender auf `ch2` aber Sender auf
`ch1`?

-   Alle drei der obigen Ereignisse können blockieren
    -   Ereigniss = Senden/Empfangen via einem Kanal
-   Wir wollen aber fortfahren, sobald eines der Ereignisse eintrift!
-   Das `select` Primitv erlaubt das gleichzeitige Warten auf mehrere
    Ereignisse

    select {
      case x = <-ch1: ...
      case y = <-ch2: ...
      case ch3 <- 1:
      // default and timeout possible
    }

`select` funktioniert wie folgt:

1.  `select` blockiert falls alle Ereignisse (cases) blockieren.

2.  Falls ein Ereignis (case) eintrifft, wird dieser Fall ausgewählt.

3.  Falls mehrere Ereignisse (cases) eintreffen, wird ein Fall
    (zufällig) ausgewählt.

4.  Alle nicht ausgewählten Ereignisse sind immer noch verfügbar!

## Beispiel: Zufällige Auswahl

    package main

    import "fmt"
    import "time"

    func sel(ch1, ch2, ch3 chan int) {

        select {
        case x := <-ch1:
            fmt.Printf("\n ?ch1 = %d", x)
        case y := <-ch2:
            fmt.Printf("\n ?ch2 = %d", y)
        case ch3 <- 1:
            fmt.Printf("\n !ch3")
        }

    }

    // Auswahl von case ist zufaellig.
    func test1() {

        // Weitesgehend egal ob wir hier synchrone oder asynchrone Kanaele verwenden.
        ch1 := make(chan int)
        ch2 := make(chan int, 1)
        ch3 := make(chan int)

        go func() {
            ch1 <- 1
        }()

        ch2 <- 2

        go func() {
            <-ch3
        }()

        sel(ch1, ch2, ch3)

    }

    // Nicht ausgewaehltes Ereignis bleibt verfuegbar.
    // In diesem Beispiel kann es sein, dass
    // case ch3 <- 3:
    // nicht ausgewaehlt wird.
    func test2() {

        // Weitesgehend egal ob wir hier synchrone oder asynchrone Kanaele verwenden.
        ch1 := make(chan int)
        ch2 := make(chan int, 1)
        ch3 := make(chan int)

        go func() {
            ch1 <- 1
        }()

        ch2 <- 2

        go func() {
            <-ch3
            fmt.Printf("\n received ch3")
        }()

        sel(ch1, ch2, ch3)

        ch3 <- 3
        time.Sleep(1 * 1e9)
        // sleep so dass wir print received beobachten koennen
    }

    func main() {

        // test1()
        test2()
    }

## Beispiel: Auswahl ist "fair"

Beachte:

1.  Reihenfolge der cases spielt keine Rolle.
2.  Die Auswahl ist zufällig und ungefähr gleichverteilt.

    package main

    import "fmt"
    import "time"

    func sel(a, b chan int) {

        for {
            select {
            case <-a:
                fmt.Printf("A")
            case <-b:
                fmt.Printf("B")
            }

        }

    }

    func snd(x time.Duration, c chan int) {
        for {
            c <- 1
            time.Sleep(x * 1e9)

        }
    }

    func main() {
        a := make(chan int)
        b := make(chan int)

        go snd(1, a)
        go snd(1, b)
        sel(a, b)

    }

## Beispiel: Auswahl mit Priorisierung

Wie kann ein Fall priorisiert werden?

    package main

    import "fmt"
    import "time"

    func sel(x time.Duration, a, b chan int) {

        for {
            select {
            case <-a:
                fmt.Printf("A")
                /*
                    case <-a:
                        fmt.Printf("A")
                    case <-a:
                        fmt.Printf("A")
                    case <-a:
                        fmt.Printf("A")
                    case <-a:
                        fmt.Printf("A")
                    case <-a:
                        fmt.Printf("A") */

            case <-b:
                fmt.Printf("B")
            }
            time.Sleep(x * 1e9)
        }

    }

    func snd(c chan int) {
        for {
            c <- 1

        }
    }

    func main() {
        a := make(chan int)
        b := make(chan int)

        go snd(a)
        go snd(b)
        sel(1, a, b)

    }

Trick: Wir duplizieren den zu priorisierenden Fall.

## Beispiel: Emulationsversuch von `select` am Beispiel Newsreader

    package main

    import "fmt"

    func reuters(ch chan string) {
        ch <- "REUTERS"

    }

    func bloomberg(ch chan string) {
        ch <- "BLOOMBERG"

    }

    func newsReaderWithThreads(reutersCh chan string, bloombergCh chan string) {
        ch := make(chan string)

        go func() {
            ch <- (<-reutersCh)
        }()

        go func() {
            ch <- (<-bloombergCh)
        }()

        x := <-ch
        fmt.Printf("got news from %s \n", x)

    }

    func newsReaderWithSelect(reutersCh chan string, bloombergCh chan string) {
        var x string

        select {
        case x = <-reutersCh:
        case x = <-bloombergCh:
        }

        fmt.Printf("got news from %s \n", x)

    }

    func test1() {
        reutersCh := make(chan string)
        bloombergCh := make(chan string)

        go reuters(reutersCh)
        go bloomberg(bloombergCh)
        newsReaderWithThreads(reutersCh, bloombergCh)
        newsReaderWithThreads(reutersCh, bloombergCh)
    }

    func test2() {
        reutersCh := make(chan string)
        bloombergCh := make(chan string)

        go reuters(reutersCh)
        go bloomberg(bloombergCh)
        newsReaderWithSelect(reutersCh, bloombergCh)
        newsReaderWithSelect(reutersCh, bloombergCh)
    }

    func main() {
            // test1() fuehrt potentiell zum deadlock
        test2()
    }

-   Wir betrachten einen Versuch `select` mittels Hilfsthreads zu
    emulieren.

-   Die Idee ist, dass jeweils zwei Threads auf entweder eine Reuters
    oder Bloomberg Nachricht warten. Diese Nachricht wird dann
    weitergeleitet zu dem Newsreader. Siehe `newsReaderWithThreads`.

-   Es gibt jedoch ein Problem im Falle mehrerer Newsreader.

    -   Der Newsreader erwartet nur eine Nachricht (entweder von Reuters
        oder Bloomberg).

    -   Beide Nachrichten werden aber potentiell aus dem jeweiligen
        Nachrichtenkanal geholt.

    -   Da nur eine Nachricht verwendet wird, bleibt die andere
        Nachricht ungenutzt und wird quasi weggeworfen

    -   Aus diesem Grund fuehrt eine weiterer Aufruf von
        `newsReaderWithThreads` zu einem Deadlock.

-   Anders im Fall von `newsReaderWithSelect`. Dank dem `select` wird
    nur entweder eine Nachricht aus dem Reuters oder eine Nachricht aus
    dem Bloomberg Kanal geholt.

-   Sprich falls der erste `newsReaderWithSelect` Aufruf die Reuters
    Nachricht verwendet, hat der zweite `newsReaderWithSelect` Aufruf
    immer noch die Moeglichkeit die Bloomberg Nachricht zu holen.

## Beispiel: Ausführung mehrer Tasks

-   Mehrere Tasks sollen gleichzeitig ausgeführt werden.
-   Das Programm soll fortfahren sobald alle Tasks abgeschlossen sind.
-   Dieses Nebenläufige Programmiermuster ist als *barrier* bekannt.

    package main

    import "fmt"
    import "time"

    func task1() { time.Sleep(1 * 1e9) }
    func task2() { time.Sleep(2 * 1e9) }
    func task3() { time.Sleep(3 * 1e9) }

    func barrier() {
        var ch = make(chan int)
        // run all three tasks concurrently
        go func() {
            task1()
            ch <- 1 // signal done
        }()
        go func() {
            task2()
            ch <- 1
        }()
        go func() {
            task3()
            ch <- 1
        }()

            // collect results concurrently
        timeout := time.After(4 * 1e9)
        for i := 0; i < 3; i++ {
            select {
            case <-ch:
            case <-timeout:
                fmt.Println("timed out")
                return
            }

        }
        fmt.Println("done")
    }

    func main() {
        barrier()
    }

Beachte

-   Wir modellieren effektiv eine zählende Semaphore
-   Im einfachsten könnten wir einfach dreimal einen Empfang ausführen

    // barrier
    <- ch
    <- ch
    <- ch

-   In obiger Modellierung, wurde noch zusätzlich ein Timeout modelliert
    (mit Hilfe von `select`)

## Select mit timeouts und default

-   `select` wählt einen Fall (case) zufällig aus

-   Falls kein Fall eintritt blockiert `select`

-   Mit Hilfe eines Timeouts kann die Blockierung aufgehoben werden
    (Beispiel siehe oben)

-   Es ist auch möglich eine Blockierung immer zu verhindern mit Hilfe
    von `default`.

-   Betrachte folgendes Beispiel

    select {
      case <-ch1:
      case ch2<-1:
      default:
    }

-   Falls keiner der ersten beiden Fälle eintritt, wird der dritte
    (default) Fall ausgewählt.

-   Mit Hilfe von default können Ereignisse priorisiert werden. Siehe
    Übungsaufgabe sleeping barber.

## Erweiterung "barrier" (Ausführung mehrer Tasks)

Obige Lösung garantiert, dass *alle* Tasks innerhalb einer gewissen
Zeitschranke abgearbeitet werden. Wir betrachten folgende Erweiterung
bei der *ein* Task innerhalb einer Zeitschranke abgearbeitet seind muss.
Z.B. alle Tasks sollen innerhalb von 500ms abgearbeitet sein, wobei
jeder Task maximal 100ms Zeit beanspruchen soll.

### Erster Versuch

Hier ist ein erster Versuch. Wir betrachten nur einen Auszug ("code
snippet").

        var ch = make(chan int)
        // run all three tasks concurrently
        go func() {
            task1()
            ch <- 1 // signal done
        }()
        go func() {
            task2()
            ch <- 1
        }()
        go func() {
            task3()
            ch <- 1
        }()

        timeout := time.After(500 * time.Millisecond)
        for i := 0; i < 3; i++ {
            timeoutEach := time.After(100 * time.Millisecond)
            select {
            case <-ch:
            case <-timeout:
                fmt.Println("timed out (global)")
                return
            case <-timeoutEach:
                fmt.Println("timed out (local)")
                return
            }

        }
        fmt.Println("done")

Wir setzen einen globalen als auch einen lokalen Timeout. Der lokale
Timeout wird in jeder Rund neu gestartet und soll einen einzelnen Task
überwachen.

Funktioniert diese Lösung?

Nein! Der lokale Timeout wird neu gestartet, aber die einzelnen Tasks
werden schon ausgeführt. Deshalb haben wir keine Garantie, dass ein
einzelner Task maximal 100ms Zeit beansprucht.

### Korrektur

Wir benötigen eine Zeitüberwachung für jeden Task. Dazu führen wir
folgende Hilfsfunktion ein.

    func completeWithin(task func(), ms time.Duration) chan bool {
        var ch = make(chan int)
        var res = make(chan bool)
        go func() {
            task()
            ch <- 1
        }()
        t := time.After(ms * time.Millisecond)
        go func() {
            select {
            case <-ch:
                res <- true
            case <-t:
                res <- false
            }
        }()
        return res
    }

Die Funktion `completeWithin` liefert als Rückgabewert einen Kanal mit
dessen Hilfe wir testen können, ob die Zeit eingehalten wurde.

        // 1. run all three tasks concurrently
        // must complete within 500ms
        r1 := completeWithin(task1, 500)
        r2 := completeWithin(task2, 500)
        r3 := completeWithin(task3, 500)

        // 2. query tasks
        b1 := <-r1
        b2 := <-r2
        b3 := <-r3

        // 3. check for any timeout
        if b1 && b2 && b3 {
            fmt.Println("done")
        } else {
            fmt.Println("timed out")
        }

Beachte, Funktion `completeWithin` ist nicht blockierend.

1.  Alle drei Tasks und deren Zeitüberwachung werden gestartet.

2.  Via des Kanals werden der jeweiligen Status abgefragt.

3.  Überprüfung ob Zeitüberschreitung

## Implementierung von \`select'

### Go Laufzeitsystem (grobe Uebersicht)

1.  Alle 'cases' werde in einem Feld (array) verwaltet.

2.  Periodisch schaut das Go Laufzeitsystem nach, ob einer der 'cases'
    verfuegbar ist (sprich synchronisiert werden kann). Im Detail:

-   Zuerst werden die Feldelemente (zufaellig) permutiert.

-   Dann wird ein Element nach dem anderen geprueft (ob Synchronisation
    moeglich). Falls keine Synchronisation moeglich, macht das Go
    Laufzeitsystem mit anderen Threads weiter. Ansonsten wird der erste
    zu synchroniserend 'case' (Feldelement) ausgewaehlt.

### Alternative Implementierung

Das `select` Kommando ist eine maechtige Erweiterung. Eine naive
Kodierung mit Hilfe von Hilfsthreads und Kanaelen liefert ein anderes
Ergebnis (siehe 'newsReader' Beispiel).

Interessanterweise, ist eine vollstaendige Kodierung von `select` nur
mit Threads und Kanaelen moeglich. Bei Interesse kann dieses Thema in
einer Projektarbeit behandelt werden.

# Was alles schief gehen kann

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

-   Beobachtung des Programmverhaltens als Programmspur ("trace").

-   Trace = Sequenz von Ereignissen

## Deadlock (Verklemmung)

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

Wir untersuchen das mögliche Verhalten obiges Programms. Dazu verwenden
wir die Bezeichner R1, S1 und R2, um auf die jeweiligen Threads
verweisen zu können.

Die Programausführung impliziert Ereignisse (events) wie das Senden und
Empfangen via einem Kanal. Für Ereignisse verwenden wir folgende
Notation.

    ch?    empfangen via Kanal ch

    ch!    senden via Kanal ch

Beachte:

Ereignisse sind blockierend. Empfangen ist blockierend im Allgemeinen.
Senden ist blockierend falls der Puffer voll ist oder wir einen nicht
gepufferten Kanal verwenden.

Deshalb die Frage. Was ist die genaue Bedeutung der Ereignisse. Folgende
zwei Optionen.

1.  Ereignis `ch?` bedeutet wir **wollen** empfangen via Kanal `ch`.

2.  Ereignis `ch?` bedeutet wir **haben** empfangen via Kanal `ch`.

Das gleiche gilt für das Ereignis `ch!`.

Wir führen deshalb folgende erweiterte Notation ein.

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
*Programmspur* (trace auf Englisch). Eine Programmspur ist eine Sequenz
von Ereignissen und entspricht der abwechselnden Ausführung
("interleaved execution") der einzelnen Threads.

Ist die Trace-basierte Programmablauf Beschreibung verwandt mit der
zustandsbasierten Ausführung? Ja, beide Notationen/Konzepte haben das
Ziel (nebenläufige) Programmabläufe zu beschreiben. Das Verhältnis
beider ist in etwa wie reguläre Ausdrücke versus endliche Automaten.

Für die Darstellung der Programmspur verwenden wir eine tabellarische
Notation. Wir schreiben `ch?_1` um auf das Event `ch?` an der Position 1
in der Programmspur zu verweisen.

        R1        S1            R2

    1.  pre(ch?)
    2.                          pre(ch?)
    3.            pre(ch!)
    4.            post(ch!)
    5.  post(ch?)

Im obigen Ablauf, kommuniziert S1 mit R1. Dies ist aus dem Trace
ablesbar. Da auf `pre(ch!)` in S1 ein `post(ch!)` folgt. Auf `pre(ch?`)
in R1 folgt ein `post(ch?)`. Im Fall einer Kommunikation
(Sende-Empfange) nehmen wir an, dass das post Eregnis der Sendeoperation
immer vor dem post Ereignis der Empfangsoperation im Trace aufgezeichnet
ist.

Threads S1 und R1 terminieren. Thread R2 blockiert da es keinen
Kommunikationspartner für `ch?_2` gibt. Alle Threads (hier nur R2) sind
blockiert. Deshalb Deadlock!

Betrachte folgenden Alternativen Programmablauf.

        R1         S1            R2

    1.  pre(ch?)
    2.                         pre(ch?)
    3.            pre(ch!)
    4.            post(ch!)
    5.                         post(ch?)

In diesem Ablauf kommuniziert S1 mit R2. R1 ist blockiert. Da aber der
Main Thread R2 terminiert, wird der Thread R1 auch terminiert. Ein
Deadlock ist deshalb nicht beobachtbar.

## Starvation (Verhungerung)

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

# Aufgabe: Quantifizierter Semaphor

Wir betrachten eine Implementierung eines Kanal mit Puffer basierend
rein auf Pufferlosen Kanälen.

Als Vereinfachung betrachten wir einen quantifizierter Semaphor. Sprich
wir ignorieren die eigentlichen Nachrichten. Folgende Schnittstelle ist
vorgegeben.

    type QSem
    func newQSem(q int) QSem
    func wait(QSem)
    func signal(QSem)

Beachte, `QSem` muss geeignet definiert werden. In Ihrer Implementierung
sollten Sie nur \`\`einfache'' nicht gepufferte Kanäle verwenden
(ansonsten ist die Aufgabenstellung trivial).

Initial wird die Quantität durch `newQSem` gesetzt. Funktion `wait`
erniedrigt die Quantität und blockiert falls Quantität gleich Null ist.
Funktion `signal` erhöht die Quantität und blockiert falls Quantität
gleich der initial gesetzten Quantität wird. Ein blockierter `wait`
Aufruf wird durch `signal` wieder freigegeben.

Wir betrachten ein Beispiel mit 4 simultan ausgeführten Threads. Zwei
Threads führen `wait` aus, die anderen zwei `signal`. Wir nehmen an die
Quantiät ist maximal 1, wobei am Anfang die aktuelle Quantität schon auf
1 ist.

### Notation

-   R = Run - Thread läuft
-   D = Done - Thread fertig
-   B = Blocked - Thread blockiert
-   Ui = Unblock Thread i - Thread i wird von blockiert auf wartend
    gestellt.

### Beispielausführung

<table>
<thead>
<tr class="header">
<th style="text-align: left;">Quantität</th>
<th style="text-align: left;">Thread 1</th>
<th style="text-align: left;">Thread 2</th>
<th style="text-align: left;">Thread 3</th>
<th style="text-align: left;">Thread 4</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;">1</td>
<td style="text-align: left;">wait</td>
<td style="text-align: left;">wait</td>
<td style="text-align: left;">signal</td>
<td style="text-align: left;">signal</td>
</tr>
<tr class="even">
<td style="text-align: left;"></td>
<td style="text-align: left;">R</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
</tr>
<tr class="odd">
<td style="text-align: left;">0</td>
<td style="text-align: left;">D</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
</tr>
<tr class="even">
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;">R</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
</tr>
<tr class="odd">
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;">B</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
</tr>
<tr class="even">
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;">R</td>
<td style="text-align: left;"></td>
</tr>
<tr class="odd">
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;">U2</td>
<td style="text-align: left;"></td>
</tr>
<tr class="even">
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;">D</td>
<td style="text-align: left;"></td>
</tr>
<tr class="odd">
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;">D</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
</tr>
<tr class="even">
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;">R</td>
</tr>
<tr class="odd">
<td style="text-align: left;">1</td>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;"></td>
<td style="text-align: left;">D</td>
</tr>
</tbody>
</table>

### Erklärung

-   Thread 1 läuft, `wait` dekrementiert Quantität.
-   Thread 2 läuft und blockiert da Quantität nicht unter 0
    dekrementiert werden kann.
-   Thread 3 läuft.
    -   Da es einen blockierten `wait` Thread gibt wird diesem
        signalisiert er darf fortfahren.
    -   Sprich der Zustand von Thread 2 wechselt von blockiert auf
        wartend.
    -   Thread 3 ist immer noch an der Reihe und terminiert.
-   Thread 2 kommt jetzt wieder an die Reihe.
    -   Beachte, Quantität ist 0, da sich `wait` in Thread 2 und
        `signal` in Thread 3 gegenseitig aufheben.
-   Thread 4 kommt an die Reihe und erhöht die Quantität auf 1.

### Hilfestellung und Kommentare

Der Zugriff auf die in gespeicherte aktuelle Quantität muss geschützt.
Um den gegenseiten Ausschluss bei gleichzeitig ablaufenden und Aufrufen
zu garantieren sollten Sie einen Mutex verwenden (siehe oben).

    type Mutex (chan int)
    type QSem struct {
       q    int     // max quantity
       curr int     // current quantity
       m    Mutex   // guarantee mutually exclusive access
    }

### Eine erster Implementierungsansatz

    func newQSem(q int) QSem {
        var m = newMutex()
        qsem := QSem{q, q, m}

        return qsem
    }

    func wait(qsem *QSem) {
        lock(qsem.m)
            qsem.curr--
            unlock(qsem.m)
    }

    func signal(qsem *QSem) {
        lock(qsem.m)
            qsem.curr++
            unlock(qsem.m)
    }

-   Funktion `wait` dekrementiert und Funktion `signal` inkrementiert
    die aktuelle Quantität. Der Zugriff auf `qsem.curr` ist geschützt
    durch den Mutex.

-   Beachte: `QSem` wird als Zeiger übergeben, da ja die
    Dekrementierung/Inkrementierung auch nach aussen sichtbar sein soll.
    \[In C/C++ müßte man `qsem->curr` schreiben was nicht notwendig ist
    in Go\]

Obiges ist sicherlich nur eine partielle Lösung. Z.B. in `wait` sollte
der Wert `qsem.curr` nur dann dekrementiert werden wenn größer als Null.

Was soll passieren falls `qsem.curr` gleich Null ist? Dann blockiert
`wait` solange bis via einem `signal` Aufruf `qsem.curr` wieder größer
als Null ist.

Was soll passieren falls es mehrere blockierte `wait`s gibt? Dann wähle
den am längsten wartenden (garantiert
\``fairness''). Beachte. Zu jedem Zeitpunkt soll immer nur ein blockierter`wait\`
wieder fortfahren dürfen.

Analoges Vorgehen für `signal`.

### Weitere Verfeinerung

    func wait(qsem *QSem) {
        lock(qsem.m)
            if qsem.curr > 0 {
               qsem.curr--
               // check for any blocked signal call
               // if any, pick the 'first' and unblock
               unlock(qsem.m)
            } else {
              // wait until unblocked by signal call
            }
    }

    func signal(qsem *QSem) {
        lock(qsem.m)
        if qsem.curr < qsem.q {
               qsem.curr++
               // check for any blocked wait call
               // if any, pick the 'first' and unblock
               unlock(qsem.m)
            } else {
              // wait until unblocked by wait call
            }
    }

Wie verwalten wir die blockierten `wait`s/`signal`s? Am besten in einer
dynamisch wachsenden Liste, die wir als Schlange
(`queue'') benutzen (siehe`fairness'').

Wie informieren wir blockierte `wait`s/`signal`s, dass sie fortfahren
dürfen? Wir missbrauchen unseren Mutex. Ein blockierter `wait`/`signal`
führt
`unlock'' aus. Der Thread der den blockierten Thread wieder fortfahren läßt führt`lock''
aus.

### Warteliste für blockierte `wait`s/`signal`s

Hier das endgültige Grundgerüst.

    import "container/list"

    type QSem struct {
        q              int
        curr           int
        m              Mutex
        blockedWaits   *list.List
        blockedSignals *list.List
    }

    func newQSem(q int) QSem {
        var m = newMutex()
        qsem := QSem{q, q, m, list.New(), list.New()}

        return qsem
    }

Informationen zu Listen in Go finden Sie hier:
[list](http://golang.org/pkg/container/list/).

Zu beachten ist, dass Listen in Go heterogen sind. Sprich falls Sie ein
Element aus der Liste holen, müssen Sie das Element explizit auf den
erwarteten Typ casten.

       var s = qsem.blockedSignals.Front()
       qsem.blockedSignals.Remove(s)
       lock(s.Value.(Mutex))

Obiges Codefragment holt sich das erste Element aus der Liste und löscht
dieses auch. Da wir erwarten, dass Listenelemente Mutexe sind führen wir
den cast `s.Value.(Mutex)` durch. Der Aufruf `lock(s.Value.(Mutex))`
erlaubt es einem blockierten `signal` fortzufahren.

### Kompletter Source Code der Lösung

    package main

    import "fmt"
    import "container/list"

    // BEACHTE:
    // Der Einfachheithalber benutzen wir einen Mutex basieren auf Kanal mit Puffer 1.
    // Wie oben beschrieben, kann solch ein Mutex auch mit einem Pufferlosen Kanal implementiert werden.
    type Mutex (chan int)

    func newMutex() Mutex {
        var ch = make(chan int, 1)
        return ch
    }

    func lock(m Mutex) {
        m <- 1
    }

    func unlock(m Mutex) {
        <-m
    }

    type QSem struct {
        q              int
        curr           int
        m              Mutex
        blockedWaits   *list.List
        blockedSignals *list.List
    }

    func newQSem(q int) QSem {
        var m = newMutex()
        qsem := QSem{q, q, m, list.New(), list.New()}

        return qsem
    }

    func wait(qsem *QSem) {
        lock(qsem.m)
        if qsem.curr > 0 {
            if qsem.blockedSignals.Len() > 0 {
                var s = qsem.blockedSignals.Front()
                qsem.blockedSignals.Remove(s)
                unlock(qsem.m)
                lock(s.Value.(Mutex)) // signal blocked signal thread
            } else {
                    qsem.curr--    // we won't decrement if
                                           // wait unblocks a signal
                unlock(qsem.m)
            }
        } else {
            var w = newMutex()
            qsem.blockedWaits.PushBack(w)
            unlock(qsem.m)
            unlock(w) // wait for signal on w
        }
    }

    func signal(qsem QSem) {
        lock(qsem.m)
        if qsem.curr < qsem.q {
            if qsem.blockedWaits.Len() > 0 {
                var w = qsem.blockedWaits.Front()
                qsem.blockedWaits.Remove(w)
                unlock(qsem.m)
                lock(w.Value.(Mutex)) // signal blocked wait thread
            } else {
                    qsem.curr++    // we won't decrement if
                                           // signal unblocks a wait
                unlock(qsem.m)
            }
        } else {
            var s = newMutex()
            qsem.blockedSignals.PushBack(s)
            unlock(qsem.m)
            unlock(s) // wait for signal on s
        }
    }

    func main() {
        var qsem = newQSem(5)
        wait(&qsem)

        wait(&qsem)
        fmt.Printf("done %d \n",qsem.curr)

    }

### Alternative Quantifizierter Semaphor Implementierung

Die Liste der "blocked" `wait`s und `signal`s modelliert eine
Warteschlange. Intern verwendet Go solche Warteschlange im Falle von
blockierten Sendern/Empfängern eines synchronen Kanals. Eine kürzere und
direkte Implementierung der quantifizierten Semaphor ist deshalb wie
folgt.

    type QSem struct {
         q              int
         curr           int
         m              Mutex
         signalWaits    Mutex
         signalSignals  Mutex
         noBlockedWaits int
         noBlockedSignals int
    }

Ein blockierter `signal` Aufruf wartet auf `signalSignals`. Ein `wait`
Aufruf testet, ob es blockierte `signal`s gibt.

Beachte. Da es entweder `wait` und `signal` nie gleichzeitig blockiern,
könnte anstatt `signalWaits` und `signalSignal` ein "signal" ausreichen.

### Kompletter Source Code der Alternative

    package main

    import "fmt"

    type Mutex (chan int)

    func newMutex() Mutex {
        var ch = make(chan int, 1)
        return ch
    }

    func lock(m Mutex) {
        m <- 1
    }

    func unlock(m Mutex) {
        <-m
    }

    type QSem struct {
        q              int
        curr           int
        m              Mutex
            signalWaits    Mutex
            signalSignals  Mutex
            noBlockedWaits int
            noBlockedSignals int
    }

    func newQSem(q int) QSem {
        var m = newMutex()
            qsem := QSem{q, q, m, newMutex(), newMutex(), 0, 0}

        return qsem
    }

    func wait(qsem *QSem) {
        lock(qsem.m)
        if qsem.curr > 0 {
            if qsem.noBlockedSignals > 0 {
                            qsem.noBlockedSignals--
                unlock(qsem.m)
                lock(qsem.signalSignals) // signal blocked signal thread
            } else {
                    qsem.curr--
                unlock(qsem.m)
            }
        } else {
                    qsem.noBlockedWaits++
            unlock(qsem.m)
            unlock(qsem.signalWaits) // wait for signal
        }
    }

    func signal(qsem QSem) {
        lock(qsem.m)
        if qsem.curr < qsem.q {
            if qsem.noBlockedWaits > 0 {
                qsem.noBlockedWaits--
                unlock(qsem.m)
                lock(qsem.signalWaits) // signal blocked wait thread
            } else {
                    qsem.curr++
                unlock(qsem.m)
            }
        } else {
                    qsem.noBlockedSignals++
            unlock(qsem.m)
            unlock(qsem.signalSignals) // wait for signal
        }
    }

    func main() {
        var qsem = newQSem(5)
            wait(&qsem)

            wait(&qsem)
        fmt.Printf("done %d \n",qsem.curr)

    }

### Vergleich der beiden Lösungen

Die erste Lösung mit den expliziten Warteschlangen erscheint unnötig
kompliziert (zumindest aber sehen wir so ein Beispiel von Listen in Go).
Was könnte der Vorteil der ersten über der zweiten Lösung sein?

### Ausnutzung von Nebenläufigkeit

Nebenläufige Konzepte (Threads, Kanäle, ...) dienen zur Strukturierung
komplexer Problemstellungen, wobei Teile von einander unabhängig
(nebenläufig) ablaufen können.

Ein Seiteneffekt der nebenläufigen Programmierung ist, dass falls die
dementsprechende Hardware (z.B. Multicore) zur Verfügung steht,
nebenläufige Programmteile parallel auf verschiedenen Rechnerkernen
ausgeführt werden können.

Bezogen auf die Implementierung des quantifizierten Semaphor, welche
Teile können parallel ausgeführt werden?

Im Falle der ersten Lösung, wartet jeder blockierte Thread auf ein auf
den Thread bezogen eindeutiges Signal. Deshalb ist es möglich, dass
gleichzeitig mehreren Threads ein "darf fortfahren" Signal geschickt
wird. Im Falle der zweiten Lösung werden die "darf fortfahren" Signale
sequentiell (nacheinander) abgearbeitet.

Beachte. Der Flaschenhals ist natürlich der Zugriff auf die
Warteschlange welcher auch in der ersten Lösung strikt nacheinander
geschieht. Das "darf fortfahren" Signal aber kann gleichzeitg
losgeschickt werden.

Als eine weitere Steigerung der Nebenläufigkeit der ersten Lösung,
könnten wir das "darf fortfahren" Signal in einem eigenen Thread
losschicken.

    func wait(qsem *QSem) {
     ...
                unlock(qsem.m)
                go lock(s.Value.(Mutex)) // signal blocked signal thread

     ...
    }

Dadurch kann der "main" Thread schon mit seiner Arbeit fortfahren. Die
Aufgabe des Signals losschicken wird von einem Hilfsthread erledigt.

Beachte. Da Google Go (zum Teil) kooperatives Scheduling benutzt kann es
durchaus sein, dass der theoretisch hohe Grad der Nebenläufigkeit nicht
praktisch (d.h. parallel) ausgenutzt werden kann.

# Aufgabe: Erweiterung Sleeping Barber

Erweitern Sie das Sleeping Barber Beispiel:

1.  Mehrere Barbiere

2.  Kanal pro Barbier

3.  Priorisierung, z.B.

    -   Auswahl eines verfügbaren Barbiers (aus einer Auswahl)

    -   Präferenz

Zur Wiederhohlung, die einfache Version.

    package main

    import "fmt"
    import "time"

    const (
        NUMBER_OF_CHAIRS = 8
    )

    type Request struct {
        id  int
        ack chan int
    }

    func barber(waitQ (chan Request)) {

        for {
            req := <-waitQ
            fmt.Printf("BARBER: Serving customer %d \n", req.id)
            time.Sleep(1 * 1e9)
            fmt.Printf("BARBER: Done with customer %d \n", req.id)
            req.ack <- 1

        } // for

    } // barber

    func customer(waitQ (chan Request), id int) {
        var ack = make(chan int)
        for {

            fmt.Printf("CUSTOMER: %d wants hair cut \n", id)
            req := Request{id, ack}
            waitQ <- req
            fmt.Printf("CUSTOMER: %d sits on chair \n", id)
            <-ack
            fmt.Printf("CUSTOMER: %d served by barber \n", id)
            time.Sleep(1 * 1e9)

        } // for

    } // customer

    func main() {

        var (
            waitQ = make(chan Request, NUMBER_OF_CHAIRS)
        )

        go customer(waitQ, 1)
        go customer(waitQ, 2)
        barber(waitQ)

    }

## Lösungsvorschläge

Zweiter 'barber' Thread.

    func main() {

        var (
            waitQ = make(chan Request, NUMBER_OF_CHAIRS)
        )

        go customer(waitQ, 1)
        go customer(waitQ, 2)
        go barber(waitQ)
        barber(waitQ)

    }

Kanal 'waitQ' ist der Flaschhals.

Idee, designierter Kanal pro 'barber'. Auswahl von 'customer' via
select. Priorisierung möglich.

# Aufgabe: Erweiterung Sleeping Barber II

Eine weitere Variante des Sleeping Barber Problems. Vorgestellt werden
verschiedene Lösungsverschläge. Diskutiert werden trickreiche
Fehlerszenarien wie Deadlocks und Livelocks.

    // Sleeping barber variant with distinction among blond and red haired customers

    package main

    import (
        "fmt"
        "math/rand"
        "time"
    )

    // Barber shall wait for either a group of blonds or reds.
    // The quantities for each group are defined by the following constants.
    const BLONDS = 2
    const REDS = 3

    // Sample solution.
    func barber(blond chan int, red chan int) {
        seenBlonds := 0
        seenReds := 0
        for {

            // Check if group has been formed.
            if seenReds == REDS {
                fmt.Printf("\n Cutting reds!")
                seenReds = 0

            }

            if seenBlonds == BLONDS {
                fmt.Printf("\n Cutting blonds!")
                seenBlonds = 0

            }

            // Check for blonds and reds wanting to join group.
            select {
            case <-blond:
                seenBlonds++
            case <-red:
                seenReds++
            }
        }

    }

    // Customer simulation.
    func customerSimulation(ch chan int) {
        x := 0
        for {
            rand.Seed(time.Now().UnixNano())
            n := rand.Intn(4) // n will be between 0 and 4
            // fmt.Printf("Sleeping %d seconds...\n", n)
            time.Sleep(time.Duration(n) * time.Second)
            x++
            ch <- x
        }
    }

    // Another attempt.
    // Any issues?
    func barber2(b chan int, r chan int) {
        for {
            select {
            case <-b:
                select {
                case <-b:
                    fmt.Println("Working on 2 blond hair customers")
                default:
                    b <- 1
                    fmt.Println("blond released")
                }
            case <-r:
                select {
                case <-r:
                    select {
                    case <-r:
                        time.Sleep(100 * time.Millisecond)
                        fmt.Println("Working on 3 red hair customers")
                    default:
                        r <- 1
                        r <- 1
                        fmt.Println("reds released")
                    }
                default:
                    r <- 1
                    fmt.Println("red released")
                }
            }
        }
    }

    func testBarber() {
        blond := make(chan int)
        red := make(chan int)

        go customerSimulation(blond)
        go customerSimulation(red)

        barber(blond, red)
    }

    // Issue 1:
    // barber2 checks for two blonds,
    // if say there is no second blond available, the first blond is released.
    // See the following code fragment.
    //         select {
    //         case <-b:
    //             select {
    //             case <-b:
    //                 fmt.Println("Working on 2 blond hair customers")
    //             default:
    //                 b <- 1
    //             }
    // What's the issue?
    // Assuming we use unbuffered channels,
    // the barber himself cannot directly release the blond,
    // because we then run into a deadlock.
    // Below is a sample execution run represented as a trace of events.
    // We make use of the following notation.
    //
    //  BLOND    = customerSimulation for blonds thread
    //  RED     = customerSimulation for reds thread
    //  BARBER = barber thread
    //
    //  Events:
    //  b? receive via blond channel
    //      b! send via blond channel
    //
    //      b! is a blocking event in case of unbuffered channels
    //
    //  The trace represents the interleaved execution of the program.
    //  We consider the following specific execution run where
    //  we use a tabular notation to represent the trace.
    //
    //  We write b!_1 to denote the send event at trace position 1 and so on.
    //
    //      BLOND    RED     BARBER
    //
    //  1.    b!
    //  2.                    b?  sync with b!_1
    //  3.           r!
    //  4.                    b!
    //  5.    b!
    //
    //     At trace position 4 we find b! because
    //     the barber has only encountered a single blond,
    //     so attempts to put the first received blond.
    //     BARBER blocks (no matching b?).
    //     RED block (no matching r?).
    //     BLOND continues but also blocks (no matching b?)
    func testBarber2() {
        blond := make(chan int)
        red := make(chan int)

        go customerSimulation(blond)
        go customerSimulation(red)

        barber2(blond, red)

    }

    // Fix for issue 1:
    // Either (a) use helper threads to put back the released blonds and red, or
    // (b) use buffered channels.
    // Any remaining issues?
    // A livelock is possible.
    // Consider the following execution run.
    //
    //   BLOND     RED      BARBER
    //    b!
    //                       b?
    //                       b!  release
    //                       b?
    //                       b!  release
    //                       ...
    //
    //  Assuming there is some progress guarantee where
    //  (a) each thread will not have to wait indefinitely *and*
    //  (b) the default case only applies if no other cases are applicable,
    /// then a livelock can be avoided.
    func testBarber2b() {
        blond := make(chan int, 2)
        red := make(chan int, 3)

        go customerSimulation(blond)
        go customerSimulation(red)

        barber2(blond, red)

    }

    func main() {

        testBarber2b()
    }

# Aufgabe: Speisende Philosophen

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

Ist eine Verklemmung (deadlock) immer noch möglich? Nein, ein 'deadlock'
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

# Aufgabe: The Santa Claus Problem

## Problem statement

Santa repeatedly sleeps until wakened by either all of his nine
reindeer, back from their holidays, or by a group of three of his ten
elves. If awakened by the reindeer, he harnesses each of them to his
sleigh, delivers toys with them and finally unharnesses them (allowing
them to go off on holiday). If awakened by a group of elves, he shows
each of the group into his study, consults with them on toy R&D and
finally shows them each out (allowing them to go back to work).

In general, the following priority rule shall be enforced:

Santa gives priority to the reindeer in the case that there is both a
group of elves and a group of reindeer waiting.

*Plan of attack*

-   Our goal is to encode the santa claus problem in GoLang

-   Next, we will incrementally develop the various solution parts. The
    complete solution can be found at the end.

## Channels to represent elves and deers

Elves and deers are represented as channels with the appropriate buffer
size.

        deers := make(chan int, 9)
        elves := make(chan int, 10)

Initially, all elves and deers are available, i.e. released from any of
their duties.

        release(deers, 9)
        release(elves, 10)

The helper function `release` simply fills the buffer with a dummy
element for each released deer and elf.

    func release(ch chan int, num int) {

        for i := 0; i < num; i++ {
            ch <- 1
        }

    }

## Checking for a waiting group of elves and deers

The task of santa is to check for a waiting group of deers and elves.
That is, to check if there are enough released deers and elves.

    func santa(deers chan int, elves chan int) {
        numOfDeersSeen := 0
        numOfElvesSeen := 0

The idea is to count the number of elves and deers by querying the
respective channel.

        for {

            select {
            case <-deers:
                numOfDeersSeen++
            case <-elves:
                numOfElvesSeen++

            }

The `select` statement allows us to check if there is any deer or elf
available. If there's none, we simply wait.

            if numOfDeersSeen == 9 {
                fmt.Print("Deliver toys \n")
                time.Sleep(1 * 1e9)
                numOfDeersSeen = 0
                release(deers, 9)
            }

            if numOfElvesSeen == 3 {
                fmt.Print("R&D \n")
                time.Sleep(1 * 1e9)
                numOfElvesSeen = 0
                release(elves, 3)
            }

        } // for

    } // santa

Then, we check if we have a large enough group assembled. Either three
elves or nine deers. If yes, we perform the respective task and after
they served their duty, we release them again.

This activity of checking for deers and elves and testing if we have
assembled a group runs in an infinite loop.

## Santa shall give priority to a group of deers

What about the priority rule?

Santa gives priority to the reindeer in the case that there is both a
group of elves and a group of reindeer waiting.

Let's run some tests

    R&D
    R&D
    Deliver toys
    R&D
    R&D
    R&D
    Deliver toys
    R&D
    R&D
    R&D
    R&D
    Deliver toys
    R&D
    R&D
    R&D

It seems that we're more likely to perform R&D than delivering of toys,
even in case there's a group of nine deers waiting.

But don't we favor deers in the `select` statement? Recall

            select {
            case <-deers:
                numOfDeersSeen++
            case <-elves:
                numOfElvesSeen++

            }

It seems that we first check for a waiting deer by performing a receive
over the `deers` channel. If there's a deer available (in the `deers`
channel buffer), then the receive statement will unblock. We say that
the event (here receive) takes place. However, the above textual order
is misleading.

In case several events can take place, here either a waiting deer or
elf, one of the events will be chosen *indeterministically*. The choice
does not depend on the textual order!

Hence, it is entirely possible that there's a waiting deer *and* a
waiting elf but we will favor the elf. So, what can we do to favor
deers?

## Give priority to a group of waiting deers

Thankfully, the `select` statement supports a `default` case which will
be chosen if all other cases are blocked (that is, no event takes place
at the moment). We can make use of `default` as follows.

            select {
            case <-deers:
                numOfDeersSeen++
            case <-elves:
                numOfElvesSeen++

                select {
                case <-deers:
                    numOfDeersSeen++
                default:
                }

            }

If we favor an elf, we immediately check (nested `select`) if there's
also a waiting deer. If there's none, we will choose the `default` case.
Thus, we give priority to the reindeer in the case that there is both a
group of elves and a group of reindeer waiting.

Here's a sample run for the above variant. As we can seen, delivering
toys takes now place more frequently.

    R&D
    Deliver toys
    Deliver toys
    R&D
    R&D
    R&D
    Deliver toys
    R&D
    R&D
    Deliver toys
    R&D
    R&D
    Deliver toys
    R&D
    Deliver toys
    R&D
    R&D
    Deliver toys
    R&D
    Deliver toys

## Alternatives

Consider the following variant

            select {
            case <-deers:
                numOfDeersSeen++
            case <-elves:

                select {
                case <-deers:
                                    numOfDeersSeen++
                                    go func() { elves <- 1 }()
                default:
                                numOfElvesSeen++
                }
            }

-   Release an elf if we find a deer as well.

-   Has the advantage that the order of the `if` statements does not
    matter.

-   On the other hand, the order in which elves are arrive destroyed but
    putting the elf we have seen back into the channel (queue).

Here's yet another alternative.

            select {
            case <-deers:
                numOfDeersSeen++
            default :
                select {
                case <-deers:
                    numOfDeersSeen++
                default:
                }
            }

-   The disadvantage of this version is that we effectively encode a
    busy-waiting loop. For example, consider the case if neither a deer
    nor an elf is available.

## Further challenges and improvements

In our current solution

-   assembling a group,
-   checking for a sufficiently large group, and
-   performing the respective task

is done sequentially.

That is, while santa performs a certain task with a group, the other
group is blocked. It's more realistic that meanwhile the other group
continues.

For example, consider the following scenario:

-   A group of nine deers assembles
-   Santa awakes and delivers toys
-   Meanwhile a group of three elves assembles
-   Santa comes back and immediately picks the group of three waiting
    elves because the deers are still doing something else

Your (challenging) task is to

-   allow that a group can concurrently assemble,
-   while another group is performing a certain task with santa.

## Some runnable code

Santa with and without enforcing the priority rule. None of the
improvements are yet incorporated.

    package main

    import "fmt"
    import "time"

    // Release by sending a (dummy) value.
    func release(ch chan int, num int) {

        for i := 0; i < num; i++ {
            ch <- 1
        }

    }

    // Check for a group of waiting deers or elves.
    // Select the first available group
    // N.B. The priority rule is not enforced here.
    func santa(deers chan int, elves chan int) {
        numOfDeersSeen := 0
        numOfElvesSeen := 0

        for {

            select {
            case <-deers:
                numOfDeersSeen++
            case <-elves:
                numOfElvesSeen++

            }

            if numOfDeersSeen == 9 {
                fmt.Print("Deliver toys \n")
                time.Sleep(1 * 1e9)
                numOfDeersSeen = 0
                release(deers, 9)
            }

            if numOfElvesSeen == 3 {
                fmt.Print("R&D \n")
                time.Sleep(1 * 1e9)
                numOfElvesSeen = 0
                release(elves, 3)
            }

        }

    }

    // Giving priorities to deers
    func santaPrio(deers chan int, elves chan int) {
        numOfDeersSeen := 0
        numOfElvesSeen := 0

        for {

            select {
            case <-deers:
                numOfDeersSeen++
            case <-elves:
                numOfElvesSeen++

                select {
                case <-deers:
                    numOfDeersSeen++
                default:
                }

            }

            if numOfDeersSeen == 9 {
                fmt.Print("Deliver toys \n")
                time.Sleep(1 * 1e9)
                numOfDeersSeen = 0
                release(deers, 9)
            }

            if numOfElvesSeen == 3 {
                fmt.Print("R&D \n")
                time.Sleep(1 * 1e9)
                numOfElvesSeen = 0
                release(elves, 3)
            }

        }

    }

    func main() {
        deers := make(chan int, 9)
        elves := make(chan int, 10)
        release(deers, 9)
        release(elves, 10)
        santaPrio(deers, elves)
        // switch between the prio or non-prio version
        // santa(deers, elves)
        fmt.Print("done \n")

    }

# Zusammenfassung

-   Überblick Go Primitive zur simultanen Programmierung mittels
    Austausch von Nachrichten

    -   Multi-threading

    -   Getypter Kanal

    -   Synchrone (ohne Puffer) und asynchrone Kanaele (mit Puffer)

    -   Nichtdeterministische Auswahl

-   Theoretische Grundlagen: Communicating Sequential Processes von Sir
    Tony Hoare

-   Verwandte Sprachen (die es zum grossen Teil besser können):
    -   Concurrent ML
    -   Haskell
    -   Scala
    -   Erlang

-   Typische Probleme der nebenläufigen Programmierung

    -   Deadlock

    -   Livelock

    -   Starvation

    -   Data race

-   Ausblick

    -   Programmanalyse zum Erkennen von Deadlock, ...
