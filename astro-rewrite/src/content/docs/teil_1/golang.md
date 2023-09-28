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

Falls Puffer vorhanden ist, verhält sich der Sender asynchron. Nachricht wird in den Puffer geschrieben. Der Sender blockiert nicht. Falls der Puffer voll ist, blockiert der Sender bis Puffer wieder vorhanden ist. Der Empfänger synchronisiert sich immer mit dem Puffer. Falls Puffer leer blockiert der Empfänger. Sonst wird eine Nachricht aus dem Puffer geholt.
