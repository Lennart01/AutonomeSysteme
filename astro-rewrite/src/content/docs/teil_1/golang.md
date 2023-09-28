---
title: Die Programmiersprache Go
description: Martin Sulzmann
---

## Go

Programmiersprache entwickelt von Google: [Go](https://go.dev/)

- Angelehnt an C
- Statisches Typsystem
- Funktionen höherer Ordnung
- Garbage Collection
- Objekt-orientierung durch Typschnittstellen (keine Klassen aber Methoden können Typen zugewiesen werden)
- Unterstützung von Nebenläufigkeit und Kommunikation
    - Leichtgewichtige Threads
    - Kommunikation via Kanälen
      - Formal fundiert: Communicating Sequential Processes, Sir Tony Hoare
    - Philosophie: “Do not communicate by sharing memory. Instead share by communicating.”

## Hello World

```go
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
```


- Typdeklarationen in 'logischer' Reihenfolge
    - var varName varType
    - Eine Variable varName mit dem Typ varType
- Eine Statement pro Zeile. Semikolon redundant.

## Go Toolchain

Ausführung via der "Kommandozeile"
- `go run hello.go`
- `gofmt hello.go``
    - Automatischer "pretty printer"
    - Ausgabe auf Konsole per Default
    - `gofmt -w hello.go` schreibt ins gleiche File

- Den Editor können Sie frei wählen (emacs, ...)
- Oder via web browser auf offizieller [Go Webseite](https://go.dev/)
- Oder einfach nach Go plugin für IDE suchen.

Zur Info, unsere Programme bestimmen immer aus einer Datei.

## Nebenläufigkeit (goroutine)

Nebenläufige Ausführung: "just say go"

```go
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
```

- go auch bekannt als "fork" oder "spawn"
- Nebenläufige Ausführung des Statements, hier der Funktionen thread("A") und thread("B").
- Beachte, thread("C") wird im Haupt-thread ausgeführt. Sprich, es werden drei Threads nebenläufig ausgeführt.
- Scheduling der Threads wird vom Laufzeitsysteme verwaltet.
- Sobald der Haupt-thread terminiert werden alle innerhalb des Haupt-threads gestarteten Threads terminiert (dies ist anders als in Java)

## Nebenläufigkeit (concurrency) versus Parallelität (parallelism)

- Parallelism: Make programs run faster by making use of additional CPUs (parallel hardware)
- Concurrency: Program organized into multiple threads of control. Threads may work independently or work on a common task.
- See also [here](https://wiki.haskell.org/Parallelism_vs._Concurrency)

## Multi-threading in Go

### Terminologie

Thread = Sequenz von hintereinander ausgeführten Anweisungen
Threadzustand:
- Running (wird gerade ausgefuehrt)
- Waiting (koennte ausgefuehrt werden aber keine CPU verfuegbar)
- Blocked (kann nicht ausgefuehrt werden)

Multithreading = Abwechselnde Ausführung von mehreren Threads auf einer CPU
Scheduling = Systematisches Vorgehen zum Multithreading
Preemptiv = Jeder Thread bekommt eine gewisse Zeitscheibe
Kooperativ = Jeder Thread wird solange ausgeführt bis auf eine blockierende Anweisung gestossen wird
Blockierende Anweisungen:
- Thread schlafen legen (delay/sleep)
- Empfang auf Kanal (potentiell blockierend da Kanal 'leer' sein kann)
- Senden auf Kanal (potentiell blockierend da Kanal 'voll' sein kann)
  
### Zustandsbasierte Ausführung

Notation angelehnt an die Ausfuehrung von UPPAAL/kommunizierenden Automaten.

- Der Programzustand besteht aus dem Zustand der einzelnen Threads. Z.B.

    ```(Main.Running, A.Waiting, B.Waiting)```

    beschreibt den Zustand in dem
    1. der main Thread ausgefuehrt, und
    2. Thread A und B im Wartezustand sind.
- Erzeugung eines Threads (via dem go Schluesselwort) fuegt einen neuen Thread hinzu. Initial im Wartezustand.
    Betrachte z.B.
    ```go
    func a() {
    }
    func main() {
    go a()
    }
    ```
    Initial ist der Programmzustand wie folgt.
    ```
    Main.Running
    ```
    Nach Ausfuehrung von go a() befinden wir uns im folgenden Programmzustand.

    ```(Main.Running, A.Waiting)```

    Ein Programmpfad wird beschrieben durch die Abfolge der einzelnen Programmzustaende. Der Fortschritt vom aktuellen auf den Folgezustand wird getrennt durch -->.
    ```
    Main.Running

    -->   (Main.Running, A.Waiting)
    ```

#### Beispiel

Ausfuehrung obigen Programs. Annahme: Eine CPU verfuegbar.
```
Main.Running

--> (Main.Running, A.Waiting)

--> (Main.Running, A.Waiting, B.Waiting)

--> (Main.Blocked, A.Waiting, B.Waiting)
```
- Main Thread blockiert wegen Sleep Anweisung
- Einer der wartenden Threads bekommt die Kontrolle
- Annahme: Der am laengsten wartende Thread bekommt Kontrolle
  
```
...

--> (Main.Blocked, A.Waiting, B.Waiting)

--> (Main.Blocked, A.Running, B.Waiting)

--> (Main.Waiting, A.Blocked, B. Waiting)
```
- A Thread blockiert wegen Sleep Anweisung
- In der Zwischenzweit, Blockierung von Main Thread aufgehoben, da 'Sleep' Zeit um ist

usw

## Lambdas (annonyme Funktionen) in Go.

Unser Beispiel von vorher.

```go
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
```
Und eine weitere Variante.
```go
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
```

## Kommunikation ("channels")

Der Nachrichtenaustausch zwischen Threads geschieht mit Hilfe von Kanälen ("channels"). Folgendes Prinzip gilt:

1. Jeder Thread kann Nachrichten senden und empfangen.
2.  Eine Nachricht kann von genau einem Thread empfangen werden.
3. Ein Empfänger muss notwendigerweise auf eine Nachricht warten.
4. Ein Sender kann fortfahren, solange der Kanal noch einen einen Puffer (Zwischenspeicher) zur Verfügung hat.
5. Der Puffer ist immer endlich. Puffer kann voll sein. Dann kann ein Sender nur fortfahren, falls es einen Empfänger gibt.

Im Detail siehe unten.

### Getypte Kanäle

```go
var ch chan int
```
Wir deklarieren eine Variable ch als einen Kanal. Die Werte die über diesen Kanal ausgetauscht werden sollen, müssen vom Typ Integer sein.

### Kanal erzeugen

```go
ch = make(chan int)
```
Ein Kanal muss via make erzeugt werden. Eine Deklaration via var ch chan int liefert nur einen geschlossenen Kanal auf dem keine Operationen ausgefuehrt werden koennen.

### Kanal ohne/mit Puffer

In Go gibt es zwei Arten von Kanälen. Ohne Puffer und mit Puffer. Puffer = Zwischenspeicher für Nachrichten. Aufgebaut wie eine Schlange (queue).
```go
ch1 = make(chan int)

ch2 = make(chan int, 50)
```
Kanal ch2 hat Platz für maximal 50 (Puffer)Elemente (= Nachrichten). Kanal ch1 ist ein Kanal ohne Puffer.
Folgende Regeln gelten im Falle von Nachrichtenaustasch.
- Kanal ohne Puffer (synchrone Kommunikation):
  - Ein Empfänger blockiert solange bis ein Sender auftaucht.
  - Gleiches gilt für den Sender (da kein Puffer vorhanden ist)

- Kanal mit Puffer (asynchrone Kommunikation):
  - Ein Empfänger blockiert solange bis Nachricht im Puffer vorhanden ist.
  - Ein Sender blockiert nur falls kein Puffer mehr vorhanden ist.
  - Der Puffer verhält sich wie eine Schlange ("FIFO queue").

Der Unterschied ist also wie folgt.  
Im Falle eines Kanals ohne Puffer, muss sich eine Sender immer mit einem Empfänger *synchronisieren*. Sender und Empfänger blockieren immer. Das Go Laufzeitsystem prüft, ob es blockierte Sender und Empfänger für den gleichen Kanal gibt. Falls ja kommunizieren beide miteinander. Die Blockierung beider wird aufgelöst.

Falls Puffer vorhanden ist, verhält sich der Sender *asynchron*. Nachricht wird in den Puffer geschrieben. Der Sender blockiert nicht. Falls der Puffer voll ist, blockiert der Sender bis Puffer wieder vorhanden ist. Der Empfänger synchronisiert sich immer mit dem Puffer. Falls Puffer leer blockiert der Empfänger. Sonst wird eine Nachricht aus dem Puffer geholt.

### Senden

```go
ch <- y
```
Sende Wert y an Kanal ch

### Empfangen

```go
x = <- ch
```
Empfange von Kanal ch und speichere Wert in x

### Beispiel

```go
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
```

### Beispielhafte Ausführung (Zustands-basiert)

```
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
```

Wir betrachten folgende Variante (1 Empfaenger, 2 Sender).

```go
func main() {
    var ch chan int = make(chan int)
    go snd("A", ch) // snd1
    go snd("B", ch) // snd2
    rcv(ch)

} 
```
```
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
```

Wir betrachten eine weitere Variante (Kanal mit Puffer)

```go
func main() {
    var ch chan int = make(chan int, 1) // Kanal mit Puffer
    go snd("A", ch)
    rcv(ch)

}
```

```
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
```

Als weitere Variante. Kanal mit Puffer 1 und snd ohne Sleep.

```go
func snd(s string, ch chan int) {
    var x int = 0
    for {
        x++
        ch <- x
        fmt.Printf("%s sendet %d \n", s, x)
    }

}
```

```
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
```

- Im Falle von 'Sleep' wird die Ausfuehrung oft chaotisch (keine Garantie, dass nach exakt einer Sekunde der Thread wieder aufwacht)
- Im Fall eines Kanals mit Puffer ist das Senden nicht blockierend (falls noch genuegend Platz vorhanden).
- Im Fall von Kanaelen ohne Puffer ist das Vorhalten meistens vorhersehbarer, da der Sender sich immer mit einem Empfaenger synchronisieren muss.
  
### Eingeschränkte Kommunikation

Funktionsprototypen können mit Annotationen versehen werden.  
Nur Senden

```go
func snd(ch chan <- int) {
 ...
} 
```
Nur Empfangen

```go
func rcv(ch <- chan int) {
 ...
}
```

## Beispiele Kanal mit und ohne Puffer

```go
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
```


## Synchrone versus Asynchrone Kommunikation

Zur Wiederholung.

- Kanal ohne Puffer (synchrone Kommunikation, synchroner Kanal)
    - Sender blockiert falls kein Empfänger vorhanden
    - Empfänger blockiert falls kein Sender vorhanden
    - Direkte (synchrone) Kommunikation zwischen Sender und Empfänger
    - Sender übergibt Nachricht an Empfänger
- Kanal mit Puffer (asynchrone Kommunikation, asynchroner Kanal)
    - Sender blockiert falls Puffer voll
    - Empfänger blockiert falls Puffer leer
    - Indirekte (asynchrone) Kommunikation zwischen Sender und Empfänger
    - Sender legt Nachricht in Puffer. Empfänger holt Nachricht aus Puffer

Beide Kommunikationsarten sind gleichmächtig. D.h. ein Kanal mit Puffer kann durch Kanäle ohne Puffer emuliert werden. Eine Reihe bekannter Synchronisationsprimitive (z.B. Mutex) kann mit Hilfe von Kanälen emuliert werden.

### Aufgabe: Mutex

Go unterstützt die bekannten Synchronisationsprimitive via Mutex etc. Siehe http://golang.org/pkg/sync/. Jedoch können wir uns recht einfach einen Mutex mit Hilfe von Kanälen selber bauen (Die nativen Mutexe in Go sind sicherlich effzienter implementiert, aber hier geht es nur um das Prinzip).

- Idee: Mutex ist repräsentiert als Kanal mit einem Pufferelement.
- Der Puffer ist initial leer.
- lock sendet und unlock empfängt.

```go
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
```

Obige Implementierung basiert auf einen Kanal mit Puffer der Grösse 1. Es geht auch ohne Puffer. Unten finden sich dazu teilweise Lösungen (die mit Problemen behaftet sind). Eine komplette Lösungen findet sich am Schluss in der Aufgaben Sektion.

### Aufgabe: Mutierbare Variable

Implementieren sie eine mutierbare Variable, die durch folgende Schnittstelle beschrieben ist.

```go
type MVar (chan int)
func newMVar(x int) MVar
func takeMVar(m MVar) int
func putMVar(m MVar, x int)
```

- Eine MVar ist entweder voll oder leer
- Initial ist eine MVar mit einem Integer Wert gefüllt
- takeMVar
    - lesen des Wertes falls voll
    - blockiert ansonsten
- putMVar
    - schreiben eines Wertes falls leer
    - blockiert ansonsten
- Hinweise
    - takeMVar entspricht Empfangen
    - putMVar entspricht Senden
    - Initial ist eine MVar voll, deshalb sollte takeMVar initial nicht blockieren
    - Implementierung trivial falls wir einen Kanal mit einem Puffer der Größe 1 verwenden.
    - Ziel hier, verwenden Sie einen rein synchronen Kanal ohne Puffer

Anmerkung: Mit Hilfe einer MVar können wir ganz einfach einen Mutex emulieren.
- newMutx = newMVar mit einem Dummy Element.
- lock = takeMVar
- unlock = putMVar eines Dummy Elements.

#### MVar Beispiel komplett

```go
package main

import "fmt"
import "time"

type MVar (chan int)

func newMVar(x int) MVar {
    var ch = make(chan int)
    go func() { ch <- x }()
    return ch
}
```

Der Trick ist:

- Wir kreieren einen synchronen Kanal ch
- In einem nebenläufigen Hilfsthread füllen wir den Kanal mit dem initalen Element. Der Hilfsthread blockiert zwar, dadurch aber garantieren wir, das initial die MVar voll ist.
- Da die Blockierung nur im nebenläufigen Hilfsthread stattfindet, kann der Kanal ch wird als Wert zurückgegeben

Die weiteren MVar Primitive können direkt auf die Kanal Operationen Senden/Empfangen abgebildet werden.

```go
func takeMVar(m MVar) int {
    var x int
    x = <-m
    return x
}

func putMVar(m MVar, x int) {
    m <- x
}
```

Es folgt noch eine Beispielanwendung einer MVar.

```go
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
```

#### MVar Kodierungs Probleme
##### Problem direkter Kommunikation

Folgt direkt nach newMVar ein putMVar folgt, ist es möglich, dass die newMVar Sendeoperation im nebenläufigen Thread von der putMVar Sendeoperation überhohlt wird.

Betrachte dazu folgendes Beispiel.

```go
func testMVar2() {
    m := newMVar(1) // 1
    go putMVar(m, 2) // 2
    x := takeMVar(m)
    fmt.Printf("Received %d \n", x)
}
```

MVar wird initial mit 1 gefühlt. Deshalb erwarten wir die Ausgabe 1. Aber auch 2 ist möglich.

##### Problem Kommunikation bleibt stecken

Weiteres Problem tritt ein falls es eine Abfolge von hintereinander ausgeführten takeMVar und putMvar Befehlen gibt. Betrachte

```go
func testMVar3() {
    var m MVar
    m = newMVar(1) // Full
    takeMVar(m)    // Empty
    putMVar(m, 2)  // Full
}
```

In Klammern sind die Zustände der MVar beschrieben. Laut MVar Beschreibung sollte obige Programmabfolge durchlaufen, die Ausführung bleibt aber stecken. Wieso?

- Das erstmalige Füllen der MVar in newMVar geschieht asynchron
- Alle weiteren putMvar Operationen laufen aber synchron ab!
- Deshalb blockiert `putMVar(m, 2)' und das liefert einen Deadlock.

Eine Lösung: Nebenläufiger Thread der den Zustand der MVar kontrolliert.

```go
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
```

takeMVar und putVar wie gehabt.

Problem Kommunikation bleibt stecken ist damit behoben.

Beachte:
- takeMvar und putMVar können sich auch direkt synchronisieren, ohne Synchronisation via dem nebenläufigen Thread in newMVar.
- Im Falle einer direkten Synchronisation bleibt der MVar Zustand (korrekterweise) natürlich invariant.
- Deshalb bleibt immer noch das "Problem direkter Kommunikation".

### Kompletter Sourcecode

```go
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
```

## Kanäle von Kanälen ("channels of channels")

Kanäle sind Werte ("first-class citizens")

```go
var ch chan (chan int)
```

Kanal der als Werte Kanäle von Integern enthält

Erlaubt komplexe simultane Programmiermuster

### Beispiel

```go
package main

import "fmt"
import "time"

type Request struct {
    id  int
    ack chan int
}
```

Eine Anfrage besteht aus einer Identifikationsnummer und einem Kanal via dem wir die erfolgreiche Bearbeitung signalisieren.

```go
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
```


Der Arbeiter wartet auf Anfragen. Nach Abarbeitung jeder Anfrage wird der Kunde via dem ack Kanal benachrichtigt.

func client(id int, req chan Request) {
    var ack = make(chan int)
    for {
        c := Request{id, ack}
        req <- c
        <-ack
    }

}

Der Kunde schickt Anfrage und wartet via dem ack Kanal auf die erfolgreiche Bearbeitung.

Hier ist eine Beispielhafe Ausführung.

func main() {
    var req = make(chan Request)
    go worker(req)
    go client(1, req)
    client(2, req)
}

Sleeping barber

Beschreibung: Es gibt einen Barbier und mehrere Kunden. Jeder Kunde möchte sich die Haare schneiden lassen, falls der Barbier verfügbar ist. Der Kunde muss warten falls ein anderer Kunde gerade einen Haarschnitt bekommt.

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

    Wir verwenden einen Kanal mit Puffer um das Warten auf einem Stuhl zu modellieren
    Falls noch Stühle vorhanden sind (sprich noch Platz im Puffer), dann kann der Kunde noch was sinnvolles machen (Zeitung lesen etc) bis er an die Reihe kommt
    Ansonsten, wird der Kunde blockiert beim Absenden des Requests (würde bedeuten der Barbierladen ist voll, und er muss draussen warten)
    In obiger Modellierung, ist das Haareschneiden und die Bestätigung miteinander vermischt (könnte man noch trennen, wenn man will)

Aufgabe: Publish/Subscribe

Ihre Aufgabe ist die Implementierung eines Publish/Subscribe Servers und mehrer Beispiel Clients. Als Vorgabe können Sie das "channels of channels" Beispiel aus der Vorlesung verwenden. Folgende Veränderungen sollten Sie vornehmen.

Anstatt eines Request Kanals gibt es je einen Publish und Subscribe Kanal. Der Server empfängt auf beiden Kanälen und leitet "Publish" Nachrichten an die entsprechenden registrierten Clients weiter.

Es gibt es zwei Arten von Clients. Publish Clients und Subscribe Clients.

Beachte: Falls der Server sämtliche Clients in einem Thread abhandelt, könnte der Server blockieren falls Subscribe Clients aufhören Nachrichten zu lesen. Wie könnte diese Problem gelöst werden?
Wir versuchen es mal

Im folgenden entwickeln wir inkrementell eine Lösung (unten nochmal komplett).

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

Jeder Subscriber registriert ein "topic" und einen "news" Kanal via dem Nachrichten zu dem entsprechenden "topic" erhalten werden können.

type Server struct {
    csub chan Sub
    cpub chan Message
}

Der Server verwaltet zwei Kanäle. Ein Kanal (csub) über den sich Subscriber registrieren können und ein Kanal (cpub) über den ein Publizierer Nachrichten schickt.
Subscriber und Publizierer

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

Ein Publizierer (hier "slashdot") verschickt Nachrichten über den entsprechenden Kanal.
Server

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

Der Server verwaltet die Liste von Subscribern. Er horcht gleichzeitig (via select) auf den jeweiligen Kanälen für Subscriber und Publizierer. Ein Subscriber wird einfach zur Liste hinzugefügt. Eine Nachricht eines Publizierers wird an den dafür sich registrierten Subscriber geschickt.
Blockierung des Servers

Nun zur obigen Problemstellung. Falls der Server sämtliche Clients in einem Thread abhandelt, könnte der Server blockieren falls Subscribe Clients aufhören Nachrichten zu lesen. Wieso?

Man betrachte die mit (B) markierte Programmstelle. Falls ein Subscriber die Nachricht nicht abholt, wird der Server an dieser Stelle blockieren. Was wären aushilfen?

    Der "news" Kanals des Subscribers hat einen Puffer. Was ist aber falls der Puffer voll läuft?

    Wir legen für jeden Subscriber einen eigenen Thread an. Dieser Thread verarbeitet alle für den Subscriber bestimmte Nachrichten. Sprich, wir schicken die Nachricht nicht direkt an den Subscriber, sondern zuerst an diesen Hilfsthread. Dieser Hilfsthread garantiert alle Nachrichten zu verarbeiten und darf natürlich nicht blockieren. Falls der Puffer voll läuft, könnte man
        Nachrichten verwerfen, oder
        einen dynamisch wachsenden internen Puffer anlegen.

    Es gibt noch eine einfachere Möglichkeit. Ersetze die Programmstelle (B) durch

                    go func() { s.news <- m }()

Publizieren der Nachricht geschickt asynchron. Dadurch modellieren wir effektiv einen Kanal mit unendlicher Puffergröße (nur durch den vorhandenen Speicher begrenzt).
Komplette Lösung

    Wir bauen die zusätzliche Variante ein, dass eine Nachricht verworfen wird, falls die Nachricht nicht innerhalb einer Zeitschranke abgeholt wird
    Wir verwenden ein paar Go Bibliotheken, z.B. Umwandlung von Integer nach String, Listen etc.

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



slide 10/18
* help? contents? 