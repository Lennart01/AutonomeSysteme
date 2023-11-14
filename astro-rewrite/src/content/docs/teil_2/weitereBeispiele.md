---
title: Weitere Beispiele
description: Martin Sulzmann
---



## Go intro + basics

-   Quick intro

-   Go (Concurrency) basics

    -   Multi-threading
    -   Kanal mit Puffer
    -   Deadlocks
    -   Annonyme Funktionen (“lambdas”)

## Quick intro

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
        // Automatische Speicherverwaltung.
        // Dynamisch angelegter Kanal wird automatisch freigegeben.
        fmt.Printf("Ende")
    }

## Go basics

    package main

    import "fmt"
    import "time"

    // Beispiel 1

    // Asynchrones Verhalten.
    // Keine Abhaengigkeiten zwischen den einzelnen Threads.

    func thread(s string) {
        for {
            fmt.Print(s)
            time.Sleep(1 * time.Second)
        }
    }

    func beispiel1() {

        go thread("A")
        go thread("B")
        thread("C")
    }

    /*

    Beispiel 2

    - Kanal mit Puffer.
    - Senden als auch Empfang kann blockieren.
    - Programmablauf kann zu Deadlock fuehren.
    - Solch ein Programmablauf kann sehr selten sein.

    */

    func send(x chan int, i int) {
        x <- i
        fmt.Printf(" send ")
    }

    func beispiel2() {
        var x chan int
        // chan ist ein Datentyp, verwaltet Elemente, diese muessen alle
        // vom gleichen Typ sein.

        x = make(chan int, 1)
        // Legt Kanal der Puffergroesse 1 an.
        // Initial ist der Puffer nicht belegt.

        go send(x, 2)

        // time.Sleep(1 * time.Second)
        /*

           Wir provizieren einen Deadlock durch das "sleep" statement.
           Dieser Ablauf scheint aber sehr, sehr selten vorzukommen!

        */

        x <- 1 // Sende 1 an den Kanal x
        // Senden blockiert falls der Puffer voll ist.

        y := <-x // Empfangsoperation of x
        // An diesem Programmzustand ist der Puffer leer!
        // Falls Empfang auf leerem Puffer dann blockieren wir.

        // durch := kann eine Variable deklariert werden mit einem Init Werten
        // Der Typ von der Variable wird automatisch inferriert.

        fmt.Printf("%d", y)

        fmt.Printf("%d", <-x)
    }

    /*

     (1) Betrachte Ausgabe: "1 send 2"

    Moeglicher Programmablauf:

     Main thread hat Prio.
     Danach wird send(x,2) im Hilfsthread komplett ausgefuehrt.
     Danach, wird das zweite "receive" ausgefuehrt.

     (2) Betrachte Ausgabe: "12 send"

    Moeglicher Programmablauf:

     Main thread hat Prio.
     Falls send(x,2) im Hilfsthread ausgefuehrt wird, dann blockiert die Sendeoperation.
     Das erste "receive" holt sich den Wert 1.
     Falls zweite "receive" ausgefuehrt, blockiert, da Puffer leer.
     Dann wird "x <- 2" als Teil von send(x,2) ausgefuehrt.
     In diesem Fall, hat der Main thread wieder Prio.
     Erst wird "2" geprintet, before "send".


     (3) Ist "send 1 2" moeglich?

       Ja.

       Annahme. Send in main thread hat prio.
       Danach erstes "receive" im main thread.
       Danach zweites send "x <- 2" und
       Ausgabe von "send" auf der Konsole.
       Danach, Ausgabe der empfangenen Werte.

     (4) Ist "send 2 1" moeglich?

       Nein!

      Annahme. Nach "go" wird sofort "send(x,2)" ausgefuehrt.
      Aber dann blockiert "x <- 1"!

      Aber dann kann es auch sein, dass wir in einen Deadlock laufen.

    */

    // beispiel3
    // Wie beispiel2 aber verwendet annonyme Funktionen.

    func beispiel3() {

        var x chan int

        x = make(chan int, 1)

        //  go send(x, 2)

        /*
            Go unterstuetzt annonyme Funktionen ("lambdas").

           Beispiel:
              func() { x <- 2 }

            Funktion ohne Name = annonym.
            Diese Funktionen duerfen auf nicht-lokale
            Variablen verweisen.

             "go" statement erwartet Funktionsaufruf.

           Deshalb

               func() { x <- 2 }()

            Wir rufen an der Stelle an der diese Funktion
            definiert ist, diese Funktion auf.


        */

        /*
            go func() {
                x <- 2
                fmt.Printf(" send ")
            }()
        */

        //  Funktionen koennen wie Werte behandelt werden.
        //  ("first-class functions")
        //
        //      Wir weisen der Variablen f eine Funktion zu.

        /*
           var f func()
           f = func() { x <- 2 }
        */

        // Automatische Typinferenz in Go ist hilfreich.

        f := func() {
            x <- 2
            fmt.Printf(" send ")
        }

        go f()

        x <- 1

        y := <-x

        fmt.Printf("%d", y)

        fmt.Printf("%d", <-x)
    }

    func main() {
        // beispiel1()
        // beispiel2()
        beispiel3()
    }

## Go “channels”

-   Kanal mit und ohne Puffer

-   Emulation von Mutex, Fork-Join und Barrier

    package main

    import "fmt"
    import "time"

    // In Go gibt es synchrone und asynchrone Kommunikation (Kanal-basiert).
    // Synchron = blockierend
    // Asynchron = nicht-blockierend
    // Im Go Kontext.
    //
    // Empfang ist blockierend, weil ich muss nachschauen, ob ein Wert im Kanal verfuegbar ist.
    // Im Fall kein Wert verfuegbar, dann blockiert die Empfangsoperation.
    //
    // Senden ist blockierend, weil ich muss nachschauen, ob Platz im Kanal vorhanden ist.
    // Aber falls Platz vorhanden, kann der Wert einfach abgelegt werden.

    func beispiel1() {
        x := make(chan int, 2)

        snd := func() {
            x <- 1
        }

        rcv := func() {
            <-x
        }

        snd()
        snd()
        snd() // blockiert da alle Plaetze im Kanal voll
        // deadlock!
        rcv()
        rcv()
        time.Sleep(1 * time.Second)

    }

    func beispiel2() {
        x := make(chan int, 2)

        snd := func() {
            x <- 1
        }

        rcv := func() {
            <-x
        }

        snd()    // A
        snd()    // B
        go snd() // C
        rcv()    // D
        rcv()    // E
        time.Sleep(1 * time.Second)

        /*
           FIFO Kanaele.

            D erhaelt Wert von A.
            E erhalet Wert von B.

           Beachte kein Deadlock.
           C blockiert solange es keinen freien Platz gibt.
           Aber spaetesten nach Ausfuehrung von D, ist Platz verfuegbar.

           Main thread schlaeft fuer 1 Sekunde und terminiert dann.

        */

    }

    func beispiel3() {
        x := make(chan int, 2)

        snd := func() {
            x <- 1
        }

        rcv := func() {
            <-x
        }

        go snd() // A
        go snd() // B
        go snd() // C
        go rcv() // D
        go rcv() // E
        time.Sleep(1 * time.Second)

        /*
           Chaotisches Verhalten.
           Jeder Empfaenger koennte von jedem Sender den Wert erhalten.

           Einfluss der Puffergroesse.
           Je groesser der Puffer, desto wahrscheinlich kann
           der Sender den Wert in den Puffer ablegen.

           Puffergroesse hat keinen Einfluss auf das chaotische Verhalten.

        */

    }

    func beispiel4() {
        /*
           Kanal ohne Puffer.
           Bedeutet fuer den Sender, er muss sich immer mit einem Empfaenger synchronisieren.
           Direkte Synchronisation zwischen Empfaenger und Sender.

        */
        x := make(chan int)

        snd := func() {
            x <- 1
        }

        rcv := func() {
            <-x
        }

        go snd() // A
        go snd() // B
        go snd() // C
        go rcv() // D
        go rcv() // E
        time.Sleep(1 * time.Second)

        /*

           Z.B. A sendet und blockiert, muss sich z.B. mit D synchronisieren.
           Sender verhaelt sich hier nie asynchron.

           Aber, Kommunikation ist immer noch chaotisch = viele Kombinationen sind moeglich.
           Z.B. D <-> A   bedeutet D synchronisiert sich mit A
             usw

           Beachte:
              Kanaele mit Puffer sind gleichmaechtig wie ohne Puffer.
              Koennen gegenseitig emuliert werden. Siehe Unterlagen.

           Aus der Anwendersicht gilt:
             Im Fall von Kanal mit Puffer koennte angenommen,
             senden blockiert nicht (weil Puffer vorhanden),
             aber es koennte zum blockieren (weil der Puffer voll ist).

        */

    }

    // Es gibt Kanaele in Go.
    // Was ist mit weiteren Features wie z.B.
    // Mutex, Semaphoren, ... Aktoren, Barriers, Worker queues,futures, promises, fork (=go), join, ..., Monitore, ...
    // Obige features koennen alle (relativ einfach) durch Kanaele emuliert werden.

    // Kleine Aufgabe.
    // Emuliere Mutex via Kanaelen.

    // Operationen: lock, unlock, new.

    // Idee:

    // Bedeutet der neue Typ "Mutex" ist definiert als "chan int"
    type Mutex chan int

    func newM() Mutex {
        x := make(chan int, 1)
        x <- 1
        return x
        /*
           "Mutex" ist initial mit einem Wert ("Key") gefuellt.
        */
    }

    // Hole den "key"
    func lock(m Mutex) {
        <-m
    }

    // Lege den "key" zurueck
    func unlock(m Mutex) {
        m <- 1
    }

    func beispielMutex() {
        m := newM()
        x := 1

        go func() {
            lock(m)
            x++
            unlock(m)
        }()

        go func() {
            lock(m)
            x++
            unlock(m)
        }()

        time.Sleep(1 * time.Second)
        fmt.Printf("%d", x)
    }

    // fork-join pattern in Go
    // Wir verwenden einen gepufferten Kanal.

    func beispielForkJoin() {
        // Starte Thread T.
        // Main Thread wartet ("join") bis Thread T fertig ist.

        join := make(chan int, 1)

        // Thread T
        go func() {
            fmt.Printf("T does something")
            time.Sleep(1 * time.Second)
            join <- 1
        }()

        // join mit T
        <-join

        fmt.Printf("Main does something")
        time.Sleep(1 * time.Second)

    }

    // Beachte:
    // Puffergroesse ist im Prinzip egal.
    // Wichtig ist:
    //    Main thread "receive" (wartet auf)
    //    T Thread "send"

    // Wir verwenden einen ungepufferten Kanal.

    func beispielForkJoinNoBuffer() {
        // Starte Thread T.
        // Main Thread wartet ("join") bis Thread T fertig ist.

        join := make(chan int)

        // Thread T
        go func() {
            fmt.Printf("T does something")
            time.Sleep(1 * time.Second)
            join <- 1
        }()

        <-join

        fmt.Printf("Main does something")
        time.Sleep(1 * time.Second)

    }

    // Variante mit ungepuffertem Kanal.
    // Da "send" und "receive" sich immer synchronisieren,
    // kann im Main Thread ein "send" und in Thread T ein "receive" verwendet werden.

    func beispielForkJoinNoBufferVariant() {
        // Starte Thread T.
        // Main Thread wartet ("join") bis Thread T fertig ist.

        join := make(chan int)

        // Thread T
        go func() {
            fmt.Printf("T does something")
            time.Sleep(1 * time.Second)
            <-join

        }()

        join <- 1

        fmt.Printf("Main does something")
        time.Sleep(1 * time.Second)

    }

    // Barrier. Warte bis n Tasks (Threads) abgearbeitet wurden.
    // Wir verwenden einen gepufferten Kanal.

    func beispielBarrier() {
        barrier := make(chan int, 2)

        // Thread T1
        go func() {
            fmt.Printf("T1 does something")
            time.Sleep(1 * time.Second)
            barrier <- 1
        }()

        // Thread T2
        go func() {
            fmt.Printf("T2 does something")
            time.Sleep(1 * time.Second)
            barrier <- 2
        }()

        // Barrier, warte auf T1, T2
        <-barrier
        <-barrier

        fmt.Printf("Main does something")
        time.Sleep(1 * time.Second)

    }


    func beispielBarrier2() {
        barrier := make(chan int)

        // Thread T1
        go func() {
            fmt.Printf("T1 does something")
            time.Sleep(1 * time.Second)
            go func() {
                barrier <- 1
            }()
            // do a bit more ...
        }()

        // Thread T2
        go func() {
            fmt.Printf("T2 does something")
            time.Sleep(1 * time.Second)
            barrier <- 2
        }()

        // Barrier, warte auf T1, T2
        <-barrier
        <-barrier

        fmt.Printf("Main does something")
        time.Sleep(1 * time.Second)

    }

    func main() {

        // beispiel1()
        // beispiel2()
        // beispiel3()
        // beispiel4()

        // beispielMutex()

        // beispielForkJoin()

        // beispielForkJoinNoBuffer()

        // beispielForkJoinNoBufferVariant()

        beispielBarrier()

        fmt.Printf("done")

    }

## “Channels are values” + select

-   Kanäle sind Werte (“channel inside channels”)

-   Nicht-deterministische Auswahl via “select”

    package main

    import "fmt"
    import "time"

    func channelInsideChannelExample() {

        // Channel of channels.
        var ch chan (chan string)

        ch = make(chan chan string) // 'chan' ist rechts-assoziativ

        client := func(id string) {
            clientCh := make(chan string)

            // Client sends request.
            ch <- clientCh

            // Waits for acknowledgment.
            s := <-clientCh
            fmt.Printf("\n Client %s receives %s", id, s)

        }

        go client("A")
        go client("B")

        time.Sleep(1 * time.Second)

        cl := <-ch
        cl <- "Hello"
        time.Sleep(1 * time.Second)
    }

    func selectExample() {
        apples := make(chan int)
        oranges := make(chan int)

        go func() {
            apples <- 1
        }()

        go func() {
            oranges <- 1
        }()

        f := func() {
            // Nur ein "case" wird getriggert.
            select {
            case <-apples:
                fmt.Printf("\n apples")
            case <-oranges:
                fmt.Printf("\n oranges")
            }
        }

        f()
        f()
    }
    // Versuch einer Emulation von "select" via Hilfthreads.
    func selectExampleEmulate() {
        apples := make(chan int)
        oranges := make(chan int)

        go func() {
            apples <- 1
        }()

        go func() {
            oranges <- 1
        }()

        f := func() {
            ch := make(chan int)
            // Wait for apples
            go func() {
                <-apples
                fmt.Printf("\n apples")
                ch <- 1
            }()

            // Wait for oranges
            go func() {
                <-oranges
                fmt.Printf("\n oranges")
                ch <- 1
            }()

            <-ch // wait for either apples or oranges or we block
        }

        f()
        fmt.Printf("\n f once")
        f()
        fmt.Printf("\n f twice")

    /*
     Beobachtung:

    In der Regel erhalten wir folgende Ausgabe

    oranges
     f once
     applesfatal error: all goroutines are asleep - deadlock!


    Was passiert?

    1. Beim ersten Aufruf von f werden zwei Hilfsthreads
       gestartet welche auf "apples" und "oranges" empfangen.

       Auf Grund der Aussage scheint es so zu sein,
       dass wir "oranges" empfangen.

    2. Beim zweiten Aufruf von f werden wieder
       zwei Hilfsthreads gestartet.

       Der eine Hilfsthreads vom ersten Aufruf von f ist
       aber immer noch aktiv und kann "apples" empfangen.

       Deshalb blockieren dann beide Hilfsthreads des
       zweiten Aufrufs von F.
       Wir geraten in einen Deadlock!


    */


    }

    /*

    Weiteres Beispiel mit "Challenge".

    select {
      case x = <-ch1: ...
      case y = <-ch2: ...
      case ch3 <- 1:
      // default and timeout possible
    }

     Koennen wir nicht select emulieren ("nachbauen")?

     Idee.
     Fuer jeden "case" einen "Hilfsthread".
     Falls Ereignis eintrifft, Hilfsthread sendet "notify".

     Skizze in Go.

     notify := make(chan int)

     // T1
     go func() {
          <-ch1       // Teste Ereignis
          notify <- 1  // Sende notify
     }()

     // T2
     go func() {
          <-ch2       // Teste Ereignis
          notify <- 1  // Sende notify
     }()

     // T3
     go func() {
          ch3 <- 1    // Teste Ereignis
          notify <- 1  // Sende notify
     }()

     <-notify     // Warte bis eins der Ereignisse eintrifft.

     select fuehrt immer nur ein Ereignis aus,
     auch wenn alle 3 Ereignisse verfuegbar sind.
     Z.B. Werte sind vorhanden auf ch1 und ch2.
     Deshalb wird entweder <-ch1 oder <-ch2 ausgefuehrt.
     Z.B. wir fuehren <-ch1 aus, d.h. erhalten Wert von
     ch1, aber Wert in ch2 bleibt erhalten.

     Problem der Emulation.

     Betrachte, Werte sind vorhanden auf ch1 und ch2.
     T1 und T2 senden notify.
     D.h. Wert aus ch1 und Wert aus ch2 wird empfangen!
     D.h. zwei "cases" werden ausgefuehrt.
     Dies entspricht nicht der Semantik von select.

    */

    func main() {

        // channelInsideChannelExample()
        // selectExample()
        // selectExampleEmulate()
        fmt.Printf("done")
    }

## Fehlerszenarien und Programmspuren

-   Fehlerszenarien

-   Darstellung von Programmabläufen via Programmspuren (“traces”)

    package main

    import "fmt"
    import "time"


    // Erstes Beispiel

    func philo1(id int, forks chan int) {

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

    func main1() {
        var forks = make(chan int, 3)
        forks <- 1
        forks <- 1
        forks <- 1
        go philo1(1, forks)     // P1
        go philo1(2, forks)     // P2
        philo1(3, forks)        // P3
    }


    /*

     Ausgabe (Ausschnitt).

    1 eats
    2 eats
    3 eats
    1 eats
    2 eats
    3 eats
    1 eats
    2 eats
    3 eats


     Auf Basis dieser Ausgabe, auf welches Programmverhalten (=ablauf) laesst sich schliessen?


    Jeder Philo kann immer 2-mal auf forks empfangen.
    Dies passiert der Reihe nach.


    Ist dies immer so?
    D.h. ist das Programmverhalten deterministisch?

    Was kann alles sonst passieren?

    "Wenn jeder Philosoph eine Gabel aus dem Kanal nimmt ist dieser leer. Beim Versuch eine zweite Gabel zu bekommen wird der Thread blockieren. Dadurch entsteht ein Deadlock."

    Folgender Ablauf ist moeglich.
    Der Kuerze lassen wir die event aus welche den Kanal forks mit 3 Gabeln fuellen!


     Wir schreiben f? also Kurzform fuer Empfang auf dem forks Kanal.
     Wir schreiben f! also Kurzform fuer Senden auf dem forks Kanal.
     Weitere Details zu Programmspuren siehe Vorlesungsunterhalgen.

    Am findet folgende Initialisierung statt.

            P1          P2          P3

    1.                            pre(f!)
    2.                            post(f!)
    3.                            pre(f!)
    4.                            post(f!)
    5.                            pre(f!)
    6.                            post(f!)

    D.h. wir senden dreimal hintereinander in P3 (= main thread).
    Dies entspricht dem bereitlegen von "drei Gabeln".

    In den folgenden Programmspuren, lassen wir diese Initialisierung der Kuerze halber weg.


         P1        P2      P3

     1.  pre(f?)
     2.           pre(f?)
     3.  post(f?)
     4.                    pre(f?)
     5.                    post(f?)
     6.  pre(f?)
     7.           post(f?)
     8.           pre(f?)
     9.                    pre(f?)

    Was koennen wir aus dieser Situation ablesen?

     Deadlock!

     Der Puffer des Kanals forks ist leer.
     P1 und P2 und P3 sind blockiert!
     Ablesbar durch die "pre" Events.


    Weiterer moeglicher Ablauf.
    Wir schreiben f! fuer die Sendeoperation.

         P1        P2      P3          Anzahl Gabel
                                         3
     1.                    pre(f?)
     2.                    post(f?)      2
     3.                    pre(f?)
     4.                    post(f?)      1
     5.  pre(f?)
     6.  post(f?)                        0
     7.           pre(f?)
     8.  pre(f?)
     9.                    pre(f!)
     10.                   post(f!)      1
     11. post(f?)                        0
     12.                   pre(f!)
     13.                   post(f!)      1
     14. pre(f!)
     15. post(f!)                        2
     16. pre(f!)
     17. post(f!)                        3
     18.          post(f?)               2
     19.          pre(f?)
     20.          post(f?)               1
     21.          pre(f!)
     22.          post(f!)               2
     23.          pre(f!)
     24.          post(f!)               3

     Beobachtung:

    B1:  Schritte 1-24 koennen sich beliebig oft wiederholen!
         Dadurch fuer immer und ewig die Ausgabe

    3 eats
    1 eats
    2 eats
    3 eats
    1 eats
    2 eats
    ...

             erzielen.

     B2:  Schritte 1-6 + 8-17 koennen sich beliebig oft wiederholen!
          Dies beschreibt die Starvation von P2.


    Weitere Beobachtung.

     Es gibt verschiedene Ablaeufe welche in einem Deadlock enden.

         P1        P2      P3

     1.                    pre(f?)
     2.  pre(f?)
     3.           pre(f?)
     4.           post(f?)
     5.  post(f?)
     6.                    post(f?)
     8.  pre(f?)
     8.           pre(f?)
     9.                    pre(f?)


     Beachte:
        Die beiden Programmspuren sind verschieden!
        Beiden gemeinsam ist aber, fuer jeden Thread (Philo)
        findet sich ein "pre" event. Deshalb in beiden Faellen kommt es zum Deadlock.


     */


    // Zweites Beispiel

    func philo2(id int, forks chan int) {
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

    func main2() {
        var forks = make(chan int, 3)
        forks <- 1
        forks <- 1
        forks <- 1
        go philo2(1, forks)
        go philo2(2, forks)
        philo2(3, forks)
    }


    /*

    Wir beobachten folgende Ausgabe.

    1 eats
    3 eats
    2 eats
    3 eats
    2 eats
    1 eats
    3 eats
    2 eats
    3 eats
    1 eats
    2 eats
    3 eats
    2 eats
    3 eats
    2 eats
    1 eats
    2 eats
    3 eats
    1 eats
    3 eats
    1 eats

     Beobachtung: Die Reihenfolge ist nicht mehr immer die gleiche
     (weniger "deterministisches" Verhalten erkennbar)

      Einer der Gruende.

      Wir verwenden ein "select" statement.
      Die "select" Operation ist viel aufwaendiger wie ein einfaches "<-forks".
      Hat groesseren Einfluss auf das scheduling Threads.


     Welche Fehlerszenarien sind moeglich?


     Deadlock?
        Nein, der Deadlock wird durch das Select gelöst.
        Im Detail.
         1. Falls "case <-forks:" blockiert wird "default" ausgewaehlt.
         2. Im "default" Fall wird die Gabel zurueckgegeben.
            Dies ist wichtig.
         3. Dadurch wird der "Gabel Zustand" des Philo auf "Null" gesetzt.
         4. D.h entweder erreicht der Philo den "Gabel Zustand = Zwei" oder
            den "Gabel Zustand = Null".
         5. Sprich, der fuer einen Deadlock kritische Zustand
            "Gabel Zustand = Eins" wird nie erreicht.

     Anmerkung: "Gabel Zustand = Eins" kommt als "fluechtiger" Zwischenzustand vor.
                Es ist garantiert, dass wir immer entweder
                "Gabel Zustand = Zwei" oder "Gabel Zustand = Null" erreichen.

     */

    /*

    Livelock in unserem Fall. Die Ausgabe "eats" tritt nie ein!


           P1          P2       P3       Anzahl Gabeln
                                           3

     1.    pre(f?)
     2.    post(f?)                        2
     3.              pre(f?)
     4.              post(f?)              1
     5.                        pre(f?)
     6.                        post(f?)    0
     7.    pre(f?)
     8.    pre(f!)
     9.    post(f!)                        1

     Beachte: 1-9 kann sich beliebig oft wiederholen.
              Ist dies ein Livelock?

              Jein. Keiner der Threads ist blockiert und P1 schreitet immer voran.
              Threads P2 und P3 sind wartend.

      Hier ist eine weitere Variante.

           P1          P2       P3       Anzahl Gabeln
                                           3

     1.    pre(f?)
     2.    post(f?)                        2
     3.              pre(f?)
     4.              post(f?)              1
     5.                        pre(f?)
     6.                        post(f?)    0
     7.    pre(f?)
     8.              pref(?)
     9.                        pref(?)
     10.   pre(f!)
     11.   post(f!)                        1
     12.             pre(f!)
     13.             post(f!)              2
     14.                       pre(f!)
     15.                       post(f!)    3

     All drei Threads holen eine Gabel und geben diese zurueck,
     ohne das Ziel (zwei Gabeln) zu erreichen.

     Schritte 1-15 koennen sich beliebig oft wiederholen => Livelock.

     Hausaufgabe: Welche verschiedenen Ablaeufe
                  gibt es welche zu einem Livelock fuehren.

    */




    // Drittes Beispiel
    // Variante von zweitem Beispiel, siehe (LOC)

    func philo3(id int, forks chan int) {
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
                // forks <- 1  // (LOC)
            }
        }

    }

    func main3() {
        var forks = make(chan int, 3)
        forks <- 1
        forks <- 1
        forks <- 1
        go philo3(1, forks)   // P1
        go philo3(2, forks)   // P2
        philo3(3, forks)      // P3
    }

    /*

    Wir beobachten folgende Ausgabe.
     (Wie immer lassen wir die Initialisierung mit "drei Gabeln" der Kuerze halber weg).


       DEADLOCK !!!

          P1        P2       P3

     1.                    pre(f?)
     2.                    post(f?)
     3.                    pre(f?)
     4.                    post(f?)
     5.  pre(f?)
     6.  post(f?)
     7.  pre(f?)                            -- blockiert, wir sind im Select und gehen in den "default" Fall
     8.
     9.  pre(f?)
     10.           pre(f?)
     11.                   pre(f!)
     12.                   post(f!)
     13.                   pre(f!)
     14.                   post(f!)         -- zu beachten, es gibt nur noch 2 Gabeln!
     15. post(f?)
     16.           post(f?)                 -- P1 und P2 holen die erste Gabel
     17. pre(f?)
     18.           pre(f?)                  -- P1 und P2 fuehren "select" aus
                                            -- blockiert => default
     19. pre(f?)
     20.           pre(f?)
     21.                   pre(f?)

            An diesem Punkt sind P1, P2 und P3 blockiert.
            P1 hat zwar 2 Gabeln geholt, diese aber einfach "liegen gelassen".
            P2 hat auch 1 Gabeln geholt, deise auch einfach "liegen gelassen".



     Laufen wir immer in einen Deadlock?


    Es muss nicht immer ein Deadlock sein. Das passiert in diesem Fall wahrscheinlich nur, weil der Main-Thread schneller ist als die anderen beiden.

     In der Tat, betrachte folgende Variante obigen Ablaufs.


          P1        P2       P3

     1.                    pre(f?)
     2.                    post(f?)
     3.                    pre(f?)
     4.                    post(f?)
     5.  pre(f?)
     6.  post(f?)
     7.  pre(f?)                            -- blockiert, wir sind im Select und gehen in den "default" Fall
     8.
     9.  pre(f?)
     10.           pre(f?)
     11.                   pre(f!)
     12.                   post(f!)
     13.                   pre(f!)
     14.                   post(f!)         -- zu beachten, es gibt nur noch 2 Gabeln!

         Zu diesem gibt es noch 2 Gabeln.
         Es ist moeglich, dass immer einer der Philos sich beide Gabeln holt und
         diese auch wieder zurueckgibt.



     */


    func main() {
    //  main1()
    //  main2()
        main3()
    }

## Dynamische Data Race Erkennung

-   Dynamische Data Race Erkennung (Motivation)

-   Dynamic data race prediction: Happens-before.

-   Beobachtung zu Korrektheit und Vollständigkeit von Programmspuren
    (Traces)

## Dynamische Data Race Erkennung (Motivation)

    package main

    import "fmt"
    import "time"

    func example1() {
        var x int
        y := make(chan int, 1)

        acquire := func() {
            y <- 1
        }
        release := func() {
            <-y
        }

        // Thread T2
        go func() {
            acquire()
            x = 3 // P1
            release()

        }()

        // Thread T1 = Main Thread

        time.Sleep(1 * 1e9)
        acquire()
        release()
        x = 4 // P2



        fmt.Printf("%d \n", x)

    }

    /*

    Definition Data Race.

    Betrachte einen Programablauf in welchem alle Ereignisse in einer
    Programmspur aufgezeichnet werden.
    Eine Data Race liegt vor falls zwei sich im Konflikt befindliche
    Lese-/Schreiboperationen auf die gleiche Variable nebeneinander
    in der Programmspur vorkommen.

    Zwei Lese-/Schreiboperationen sind im Konflikt falls mindestens
    eine Operation eine Schreiboperation ist.


    Beobachtung.

     Data race zwischen P1 und P2 (moeglich).

     Durch testen erreichen wir es nie,
     dass P1 und P2 nebeneinander (gleichzeitig) stattfinden.

     Betrachte den Ablauf als Programmspur (Trace).


    Trace A.

          T1               T2

    1.  acquire
    2.  release
    3.  write(x)
    4.                      acquire
    5.                      write(x)
    6.                      release

     Kein Data Race in obigem Trace,
     da die beiden writes getrennt sind durch
     weitere Events.


     Betrachte folgende Variante.

    Trace B.

          T1               T2

    1.  acquire
    2.  release
    3.                      acquire
    4.  write(x)
    5.                      write(x)
    6.                      release


      Jetzt haben wir einen Data Race!

     Problem.

    Durch Testen ("Programm ausfuehren"), koennen
    wir diese Situation nie herstellen.


    Idee.

    Trace B kann aus Trace A abgeleitet werden
    durch Umordnung der Events!

    Was bedeutet Umordnung?
    Wir betrachtet ein alternatives Scheduling der Events.

    In unserem Fall, durch Umordungen erkennen wir den Data Race! Siehe Trace B.


    Umordnungen sind nicht praktikabel ("exhaustive methods").
    Deshalb betrachten wir approximative Methoden
    wie "lockset" und "happens-before".

    Was meinen wir mit "approximativ"?

    Im Fall von happens-before kann es false negatives geben.

    Im Fall von lockset kann es false positives geben.

    */

    func main() {
        example1()
    }

## Dynamic data race prediction: Happens-before

    // Dynamic data race prediction: Happens-before.


    ////////////////////////
    // HAPPENS-BEFORE

    /*

    Grundlagen.

    Ordung. Wir schreiben e < f falls e "kleiner" ist wie f.
     Wir bezeichen < als eine (binaere) Ordnungsrelation.

    Totale Ordnung:
        Gegeben Menge von Events.
        Fuer je zwei Events e und f gilt
         entweder e < f oder f < e.
        Die Ordnung ist auch transitiv.
        D.h. falls e < f und f < g dann gilt auch e < g.

     Partielle Ordung:
        Gegeben Menge von Events.
        Fuer je zwei Events e und f gilt
     entweder (1) e und f sind nicht geordnet, oder
     (2)  es gilt entweder (2a) e < f oder (2b) f < e.
        Die Ordnung ist auch transitiv.
        D.h. falls e < f und f < g dann gilt auch e < g.

    */


    /*

    Beispiel

    Trace A2.

          T1               T2

    1.                    acquire
    2.                    write(x)
    3.                    release
    4.  write(x)
    5.  acquire
    6.  release


    Happens-before relation wird aus dem Trace abgeleitet.

    Beachte. Reihenfolge im Trace ist eine totale Ordnung.

     Idee:
        - e < f bedeutet e "happens-before" f
        - Happens-before ist eine partielle Ordnung zwischen Events.
         - Falls (e,f) sich im Konflikt befindene Events sind,
           und es gilt e < f, dann sind befinden sich (e,f)
           nicht in einem Data Race.

        - Falls e und f nicht geordnet unter der
          Happens-before Relation, dann duerfen wir
          e und f umordnen (im Trace).
          D.h. ein umgeordneter Trace is ableitbar in
          welchem e und f sich nebeneinander befinden.

     Happens-before (HB) data race check.

     Betrachte zwei sich im Konflikt befindene Events (e,f).
     Falls e und f nicht geordnet sind bzgl. der HB Relation,
     dann signalisiere es gibt einen Data Race.


     Motivation:
        Welche Happens-before Regeln muessen gelten?

     1. Events betrachtet fuer einen bestimmenten Trace sind
        geordnet in der Reihenfolge wie geschrieben im Trace.

        Betrachte Trace A2.
        Also

         T2##acquire_1 < T2##write(x)_2 < T2##release_3

         T1##write(x)_4 < T1##acquire_5 < T1##release_6

     2. Was ist mit der Ordnung zwischen Events in Thread T1 und T2?

        Annahme: Keine Ordnung.

        Die Konsequenz waere

         T2##release_3   und T1##acquire_5  sind nicht geordnet !!!

         D.h. auch

         T2##release_3   und T1##write_4 sind nicht geordnet.

         D.h Events in T2 sind nicht geordnet relativ zu Events in T1.

       D.h. wir koennten folgende Umordnung ableiten.

     Trace A2'    ("Warning, this trace is not valid").

          T1               T2

    4.  write(x)
    1.                    acquire
    2.                    write(x)
    5.  acquire
    3.                    release
    6.  release

        Beachte Trace A2' abgeleitet aus Trace A2, wir nehmen Umordungen vor.
        Diese Umordungen muessen obige Happens-before Relation erfuellen.

     Beobachtung:

        Trace A2' ist kein gueltiger Trace weil die Lock Semantik verletzt wird,
        weil nach acquire in T2 findet sich acquire in T1 und das release in T2
        kommt erst danach.

     Beobachtung:

        Unsere Happen-before Relation welche nur Events innerhalb eines Threads ordnet
        ist zu "schwach".
            - Notwendig aber nicht hinreichend, weil wir nicht gueltige Umordnungen
              ableiten koennen.

     Beobachtung:

        Wir brauchen weitere Happens-before Relationen um zu garantieren,
        dass die Lock Semantik erfuellt ist.

     Stichwort: Lock Semantik.

        Informell, zwischen einem acquire-release Paar darf kein weiteres acquire oder
        release vorkommen (im Trace, bezogen auf eine bestimmte Lock Variable).

      Idee von Lamport.

     Die Happens-before Ordnung zwischen kritischen Sektionen (d.h. acquire-release Paare),
     ist genau wie die Ordnung im Trace.


     Bezogen auf Beispiel Trace A2, d.h.

          T2##release_3 < T1##acquire_5

      Konsquenz, basierend auf der "Lamport" Happens-before Relation kann Trace A2' nicht aus
      Trace A2 abgeleitet werden!

    Zusammengefasst. Aus Trace A2 werden folgende "Lamport" Happens-before Relationen abgeleitet.

     1. Happens-before Relationen basierend auf "program order" (bezogen auf jeden Thread).

         T2##acquire_1 < T2##write(x)_2 < T2##release_3

         T1##write(x)_4 < T1##acquire_5 < T1##release_6

     2. Kritische Sektionen geordnet wie im Trace notiert.

                T2##release_3 < T1##acquire_5

     Beachte:

        Es gilt auch

         T2##release_3 < T1##release_6

       wegen   T2##release_3 < T1##acquire_5
               T1##acquire_5 < T1##release_6

    Trace A2'' abgeleitet durch Umordung aus Trace A2
    wobei "Lamport" Happens-before Relationen gelten
    muessen.

          T1               T2

    1.                    acquire
    2.                    write(x)
    4.  write(x)
    3.                    release
    5.  acquire
    6.  release


      Beachte.  Die zwei writes sind nicht geordnet!
      Deshalb ist eine Umordnung moeglich, in welcher
      die zwei writes direkt hintereinander stehen
     => DATA RACE !!!


    Formale Definition:
    Lamport's happens-before Relation besteht aus
    zwei Bedingungen. Gegeben trace T.

     (1)    j##e_i und j##f_i+n wobei n > 0

            dann gilt

             j##e_i < j##f_i+n

     (2)  j##acq(x)_k+n   i##rel(x)_k wobei i != j und n > 0

            dann gilt

           i##rel(x)_k < j##acq(x)_k+n


     (Siehe auch Beispiele oben).
    Angewandt auf Beispiel Trace A2.

     Aus (1) folgt.

     acquire_1 < write(x)_2 < release_3

     write(x)_4 < acquire_5 < release_6

     Aus (2) folgt.

        release_3 < acquire_5

     z.B. wegen Transitivitaet folgt auch

         release_3 < release_6


     Frage:  Sind write(x)_2 und write(x)_4 geordnet?

     Nein. Sind nicht geordnet.
     Beweis: Betrachte alle erlaubten Ordnungsrelationen
             die ableitbar sind.


    HB Eigenschaften.

     "incomplete" (d.h. es gibt false negatives), siehe Unterlagen, oder folgendes Beispiel.

    Trace B2.

          T1               T2

    1.                    acquire
    2.                    write(x)
    3.                    release
    4.  acquire
    5.  release
    6.  write(x)

    Folgende HB Relation gelten.

     T2##acquire_1 < T2##write(x)_2 < T2##release_3

     T1##acquire_4 < T1##release_5 < T1##write(x)_6

     T2##release_3 < T1##acquire_4

    Daraus folgt

     T2##write(x)_2 < T1##write(x)_6

    weil   T2##write(x)_2 < T2##release_3
           T2##release_3 < T1##acquire_4
           T1##acquire_4 < T1##write(x)_6

    D.h. die zwei writes sind geordnet.
    Die HB Methode sagt deshalb "NO DATA RACE".

    Aber folgendes ist eine gueltige Umordnung.

    Trace B2'.

          T1               T2

    4.  acquire
    5.  release
    1.                    acquire
    2.                    write(x)
    6.  write(x)
    3.                    release


    Aha!. DATA RACE!

    D.h. die "Lamport" Happens-before Methode ist nicht vollstaendig (incomplete).
    D.h. es sind "false negatives" moeglich.


    Die "Lamport" Happens-before Methode is "unsound" (inkorrekt => es gibt "false positives"),
    falls wir "sequential consistency" annehmen.

    Betrachte

    Trace I:

         T1            T2

    1.   w(x)
    2.   w(y)
    3.                 r(y)
    4.                 w(x)


    Nicht geordnet und im Konflikt sind

     (w(x)_1, w(x)_4)   und (w(y)_2, r(y)_3)

    D.h. es muss eine Umordnung geben,
    bei der die zwei writes nebeneinander stehen.


    Umordnung von Trace I. Urspruengliche Trace Positionen
    bleiben erhalten.

         T1            T2

    3.                 r(y)
    4.                 w(x)
    1.   w(x)
    2.   w(y)

    Beachte.   "read" vor "write", d.h. wir
                lesen womoeglich einen anderen Wert aus der
                Variablen y.

                Dies hat womoeglich Einfluss auf das
                Programmverhalten.

    In unserem Beispiel, siehe Unterlagen, wird deshalb das w(x)_4 gar nicht exisitieren!


    Was ist im Fall von "weak memory models"?
    Dann sind Umordnungen innerhalb eines Traces moeglich
    und im Fall von Trace I kann es zu einem Data Race zwischen den zwei writes auf x kommen.

     */

## Beobachtung zu Korrektheit und Vollständigkeit von Programmspuren (Traces)

    package main

    import "fmt"
    import "time"

    /*

     Gegeben Programmspur (trace) erhalten aus einem konkreten Programmablauf.

     Annahme: Programmspur entpricht tatsaechlichem Programmablauf.

     Wie erhalten wir Programmspur?
     Durch Instrumentierung des Programmcodes
     (oder auch Instrumentierung des Laufzeitsystems).

    */

    // Betrachte Data Race Beispiel.
    // Naive Instrumentierung via "print".

    func example1() {
        var x int
        y := make(chan int, 1)

        acquire := func(tid int) {
            fmt.Printf("\nacquire(%d)", tid)
            y <- 1

        }
        release := func(tid int) {
            <-y
            fmt.Printf("\nrelease(%d)", tid)

        }

        // Thread T2
        go func() {
            t2 := 2
            acquire(t2)
            fmt.Printf("\nwrite(%d)", t2)
            x = 3 // P1

            release(t2)

        }()

        // Thread T1 = Main Thread
        t1 := 1
        fmt.Printf("\nwrite(%d)", t1)
        x = 4 // P2
        acquire(t1)
        release(t1)

        time.Sleep(1 * time.Second)

    }

    func main() {
        example1()
    }

    /*

    Ausgabe z.B.

    write(1)
    acquire(1)
    release(1)
    acquire(2)
    write(2)
    release(2)

    In tabellarischer Darstellung

          T1               T2

    1.  write
    2.  acquire
    3.  release
    4.                    acquire
    5.                    write
    6.                    release


    Ist folgende Ausgabe moeglich?

    acquire(2)
    write(2)
    write(1)
    acquire(1)
    release(2)
    release(1)


    In tabellarischer Darstellung

          T1               T2

    1.                    acquire
    2.                    write
    3.  write
    4.  acquire
    5.                    release
    6.  release

    Der Trace erscheint "komisch".
    Zwei acquire in verschiedenen Threads die
    hintereinander erfolgen!?

     Beachte:
     - print(acquire) VOR dem tatsaechlichen acquire.
     - print(release) NACH dem tatsaechlichen release.

    Obiger Trace koennt vorkommen
    ABER entspricht keinem gueltigen Programmablauf!

    Zusammenfassung.

     Beobachtung 1:
       Falls der Trace fehlerhaft ist,
       dann sind womoeglicherweise auch Aussagen ueber
       das Programm basierend auf diesem Trace fehlerhaft!

     In dieser Vorlesung gehen wir in der Regel davon
     aus, dass der Trace ein korrektes Programmverhalten
     darstellt.

     Beobachtung 2:
       Was ist falls wir hier einen read-write Mutex
       betrachten?
       read-write Mutex hat read_lock und read_unlock
       Operationen wie auch write_lock und write_unlock.
       "write" schliesst sich immer gegenseitig aus.
       Es darf aber mehrere "reader" geben.

      In unserem obigen Trace, koennten die
      Events acquire und release von read_lock und
      read_unlock Operationen herkommen!

       Der Trace enthaelt nicht alle Informationen.
     D.h. gewissen Operationen (read_lock und write_lock) werden nicht genau dargestellt.

     In dieser Vorlesung gehen wir in der Regel davon
     aus, dass der Trace das komplette Programmverhalten
     darstellt (d.h. alle fuer die Analyse notwendigen
     Informationen sind dargellt).


    */

## Lockset Methode

-   Lockset Methode

    -   Alternative zur Happens-before Method

    -   Sehr effzient

    -   Nachteil sind false positives

## Lockset Methode

    // Dynamic data race prediction: Lockset.

    ////////////////////////
    // LOCK SET

    /*

    Betrachte.

    Trace A:

         T1          T2          Lockset

    1.   w(x)                       {}
    2.   acq(y)                     {y}
    3.   rel(y)                     {}
    4.               acq(y)         {y}
    5.               w(x)           {y}
    6.               rel(y)         {}

    Wir schreiben Lockset_i um den "lockset" an der
    Trace Position i zu bezeichnen.

     lockset = Menge der Locks die zu diesem Zeitpunkt von einem
               Thread "acquired" wurden.

     Lockset data race check.
     Betrachte zwei sich im Konflikt befindende Events (e,f)
     wobei e an der Trace Position i und f an der
     Trace Position f.
     Falls Lockset_i und Lockset_j disjunkt sind,
     dann signalisiere einen Data Race.

     Betrachte  (w(x)_1, w(x)_5)
     wobei Lockset_1 = {} und Lockset_5 = {y}.
     Lockset_1 = {} und Lockset_5 sind disjunkt!
     Deshalb signalisiere einen Data Race.

     Bemerkung:
        Falls in den Locksets sich eine gemeinsame Lockvariable
     befindet (d.h. nicht disjunkt), sind die im Konflikt
     befindlichen Events geschuetzt durch eine gemeinsame
     Lockvariable.

     Aus obiger Bemerkung folgt, Lockset ist vollstaendig.

     Aber die Lockset Method ist "unsound" (d.h. es gibt einen "false positive"). Betrachte.


         T1          T2              Lockset

     1.   acq(y1)                     {y1}
     2.   acq(y2)                     {y1, y2}
     3.   rel(y2)                     {y1}
     4.   w(x)                        {y1}             <===
     5.   rel(y1)                     {}
     6.               acq(y2)         {y2}
     7.               acq(y1)         {y2, y1}
     8.               rel(y1)         {y2}
     9                w(x)            {y2}             <===
     10.              rel(y2)         {}


     {y1} und {y2} sind disjunkt,
     deshalb signalisiere Data Race zwischen w(x)_4 und w(x)_9.

     Aber es kommt zu keinem Data Race weil es keine Umordnung des obigen Traces gibt
     in welchem w(x)_4 und w(x)_9 direkt hintereinander vorkommen.

     Versuchen Sie solche eine Umordnung zu bauen. Sie werden feststellen dies ist nicht moeglich
     (weil wir immer in einen Deadlock laufen).


    Weiteres "false positive" Beispiel.


     Bisher gehen wir immer davon aus, dass alle Threads gleich am Anfang gestartet ("forked") werden.
     Wir betrachten eine Erweiterung mit expliziten "fork" events.

        T1             T2            Lockset

     1. w(x)                         {}
     2. fork(T2)
     3.               w(x)           {}


     Die Locksets von w(x)_1 und w(x)_3 sind disjunkt.
     Die Lockset Methode wuerde hier also einen Data Race melden.
     Jedoch wird Thread T2 erst nach w(x)_1 gestartet.
     D.h. es kann nie zu einem Data Race kommen,
     da w(x)_1 immer vor w(x)_3 ausgefuehrt wird.


    */

## ThreadSanitizer (TSan) “–race”

-   ThreadSanitizer (TSan) “–race”

    -   Umsetzung von FastTrack auf der LLVM Platform

    -   [Dynamic Race Detection with LLVM
        Compiler](https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/data-race-test/ThreadSanitizerLLVM.pdf)

    -   Pragmatische Optimierungen welche zu false negatives führen

## ThreadSanitizer (TSan)

    package main

    import "sync"
    import "fmt"
    import "time"

    // TSan vector clock size is limited to 256
    // If there are more active threads,
    // we might not be able to detect the race.
    func manyThreads() {
        x := 1
        var m sync.RWMutex

        threadNo := 500 // for 200 we'll encounter the race

        protectedWrite := func() {

            time.Sleep(1 * time.Second)
            m.Lock()
            x = 3
            m.Unlock()
            time.Sleep(4 * time.Second)
        }

        for i := 0; i < threadNo; i++ {

            go protectedWrite()

        }
        time.Sleep(3 * time.Second)
        fmt.Printf("%d", x) // unprotected read

        time.Sleep(5 * time.Second)

    }

    // TSan only records four "most recent" reads.
    // If there's an unprotected read followed by many protected reads,
    // we might not be able to detect the race.
    func manyConcurrentReads() {
        x := 1
        var m sync.RWMutex

        threadNo := 100 // for 1 we'll encounter the race

        f := func(x int) {}

        protectedRead := func() {
            m.Lock()
            f(x)
            m.Unlock()

        }

        // unprotected read
        go func() {
            f(x)
        }()

        for i := 0; i < threadNo; i++ {

            go protectedRead()

        }

        time.Sleep(1 * time.Second)
        m.Lock()
        x = 1 // protected write
        m.Unlock()

    }

    // TSan reports two data race (pairs).
    func subsequentRW() {
        x := 1
        y := 2

        go func() {
            fmt.Printf("%d", x)
            fmt.Printf("%d", y)

        }()

        x = 3
        y = 3
        time.Sleep(1 * time.Second)

    }

    // There are two data races: (R1,W) and (R2,W).
    // TSan reports (R2,W).
    // The later R2 "overwrites" the earlier R1.
    func subsequentRW2() {
        x := 1

        go func() {
            fmt.Printf("%d", x)   // R1
            fmt.Printf("%d", x+1) // R2

        }()

        x = 3 // W

        time.Sleep(1 * time.Second)

    }

    func main() {

        // manyThreads()
        // manyConcurrentReads()
        // subsequentRW()
        // subsequentRW2()
    }

## Deadlock Analyse

    /*
    Betrachte folgenden Ablauf

       T1         T2

    1.  acq(y)                   -- acq(y), bedeutet, hole lock y
    2.  acq(x)
    3.  rel(x)                   -- rel(x), bedeutet gebe lock x zurueck
    4.  rel(y)
    5.             acq(x)
    6.             acq(y)
    7.             rel(y)
    8.             rel(x)

    Reales Beispiel.
    Atomare Ueberweisung (Bank Transfer von x nach y).
    Viele weitere Beispiele.

    Uns interessieren nur acquire und release events (Kontext ist Deadlock Analyse).

    Aus dem Trace laesst sich kein "bug" ableiten.
    Z.B. kein Deadlock ist aufgetreten.

    Was koennte passieren?
    Wir betrachten alternative Programmablaeufe.

       T1         T2

    1.  acq(y)
    5.             acq(x)
        -- BLOCKED
    2.  acq(x)
                -- BLOCKED
    6.             acq(y)

    Aus dem Trace ist ein Deadlock ablesbar.
    Durch geeignete Umordnung der events.

    Problem, Deadlock Situationen sind oft sehr schwer
    waehrend der Ausfuehrung feststellbar.

    D.h.
     - das mehrfaches ausfuehren des Programms fuehrt oft nicht zu der Deadlock Situation.
     - stattdessen wollen wir den bestehenden Trace umordnen.
     - diese Umordnung soll eine moegliche Programmausfuehrung darstellen

    Beachte.
       Umordnungen muessen gewissen Spielregeln einhalten.
         - Ordnung innerhalb eines Threads muss erhalten bleiben.
         - lock Semantik muss erhalten bleiben,
           ein acquire(y) ist nur moeglich falls y im "released" Zustand.

    Fuer unser Beispiel ist folgende weitere Umordnung moeglich.


       T1         T2

    5.             acq(x)
    6.             acq(y)
    7.             rel(y)
    8.             rel(x)
    1.  acq(y)
    2.  acq(x)
    3.  rel(x)
    4.  rel(y)

    Jetzt zuerst Thread T2 und dann der Thread T1.
    Ablauf ist immer noch gutartig!
    Kein Deadlock ist aufgetreten!

    Weitere Umordnungen sind z.B.

       T1         T2

    1.  acq(y)
    5.             acq(x)

    2.  acq(x) -- BLOCKIERT !!! weil T2 die lock x hat.

    6.             acq(y)  -- BLOCKIERT !!! weil T1 die lock y hat.


     ==> Deadlock!

    Wir haben eine Umordung welche zu einem Deadlock fuehrt!

    Weitere Umordung welche zu einem Deadlock fuehrt.

       T1         T2

    5.             acq(x)
    1.  acq(y)

    6.             acq(y)  -- BLOCKIERT !!! weil T1 die lock y hat.

    2.  acq(x) -- BLOCKIERT !!! weil T2 die lock x hat.


     Kurze Zusammenfassung:


      - Generierung aller moeglichen Umordung skaliert nicht fuer grosse Traces.
        => exponentielle Laufzeit (der Programmanalyse).

      - Wir suchen nach einer "effizienten" Deadlock Analyse Methode.

     => lineare Laufzeit als Wunsch.


     Idee:

      Waehrend der Programmausfuehrung, bauen wir einen "Lock Graphen".

        - Knoten sind locks x, y, z, ...

        - Kanten von x -> y falls ein Thread die lock x besitzt und
        "acquired" danach die lock y.

      Wir verwenden wir locksets (bekannt aus "data race prediction").


    Beispiel.

       T1         T2           Lockset

    1.  acq(y)                 T1 hat die lock y
    2.  acq(x)                 T1 hat die lock x

                               An dieser Stelle gilt:
                                 - T1 besitzt die lock y
                                 - T1 acquired die lock x

                               Daraus folgt eine Kante der Form

                                    y -> x

                               Bedeutet, ausgehend vom dem Besitz der Lock y wird die Lock x geholt.



    3.  rel(x)
    4.  rel(y)
    5.             acq(x)
    6.             acq(y)

                                x -> y

                                weil Thread T2 besitzt lock x und holt sich die lock y.


    7.             rel(y)
    8.             rel(x)


    Lockgraph fuer obigen Trace.

     (1) Knoten sind hier x und y.

     (2) Kanten sind

          y -> x

          x -> y


    Was koennen wir aus dem Lock Graphen ablesen.

          ein Thread besitzt y und acquired x.

          ein Thread besitzt x und acquired y.


    Deadlock Situation!

    Aus Sicht des Lock Graphen ist dies ein Zyklus.

     Zyklus = Ein Pfad x1 -> x2 -> x3 -> ... -> x1


     Idee:

        Jeder Zyklus impliziert eine potentielle Umordnung welche
        zu einem Deadlock fuehrt?


    Deadlock Kriterium.

         Falls Zyklus im Lock Graphen dann melde "Deadlock".

     Beobachtung:

         Zyklus im Lock Graphen ist eine notwendige aber nicht hinreichende
         Bedingung.

     Konsequenz:

        Deadlock Analyse mit Lock Graphen liefert "false positives".

     Beispiele zu "false positives" siehe Unterlagen.

     Beispiele zu "false negatives" siehe Unterlagen.
        */

    /*

    False positive Beispiel.

        T1         T2     LS_T1     LS_T2

     1.  acq(y)            {y}
     2.  acq(x)            {y,x}                 impliziert die Kante y -> x
     3.  rel(x)            {y}
     4.  rel(y)            {}
     5.  acq(x)            {x}
     6.  acq(y)            {x,y}                 impliziert die Kante x -> y
     7.  rel(y)            {x}
     8.  rel(x)            {}

    Lockgraph besteht aus

     y -> x

     x -> y

    Zyklus!

    Wir melden einen Deadlock!

    Dies ist ein false positive!
    Alle Events finden im gleichen Thread statt.

    Verbesserungsvorschlaege?

    Annotiere Kanten mit Thread IDs!

    Adaptieres Deadlock Kriterium.
     Im Fall von Zyklus muessen Kanten von unterschiedlichen Threads herstammen.
     Kann anhand der Kantenannotation festgestellt werden.

        T1            T2           T1_LS          T2_LS

     1.  acq(z)                      z
     2.  acq(y)                      z,y                        z -T1-> y
     3.  acq(x)                      z,y,x                      y -T1-> x  z -T1-> x
     4.  rel(x)                      z,y
     5.  rel(y)                      z
     6.  rel(z)
     7.             acq(z)                        z
     8.             acq(x)                        z,x           z -T2-> x
     9.             acq(y)                        z,x,y         x -T2-> y  z -T2-> y
     10.            rel(y)                        z,x
     11.            rel(x)                        z
     12.            rel(z)

    Zusammengefasst, erhalten wir folgenden Lockgraphen.

    z -T1-> y
    y -T1-> x
    z -T1-> x
    z -T2-> x
    x -T2-> y
    z -T2-> y

    Zyklus, betrachte

    y -T1-> x
    x -T2-> y

    Beachte Kanten sind mit verschiedenen Thread IDs annotiert!

    Deshalben melden wir einen Deadlock!

    Dies ist in false positive, wegen der "guard lock" z.

    Weitere Verfeinerung.
    Annotiere Lockgraphen mit "guards locks".


    Beachte: Auch mit guard locks sind noch false positives moeglich.
    Grund, gewisse Synchronizationsbedingungen sind aus dem Trace nicht ersichtlich.

    Beispiel.

       T1         T2

    1.  acq(y)
    2.  acq(x)
    3.  rel(x)
    4.  rel(y)
        snd(z)
                   rcv(z)
    5.             acq(x)
    6.             acq(y)
    7.             rel(y)
    8.             rel(x)


    Im obigen Trace befinden sich nur acquire und release events.
    Im Programm wird aber ein ungepufferter Kanal z verwendent,
    mit Hilfe dessen sich Thread T1 mit Thread T2 synchronisiert.


    False positives sind verwirrend!
    Aber in praktischen Analyse Tools muessen wir damit leben.
    Ziel der Forschung. False positives soweit wie moeglich eliminieren
    und die Effizienz der Analyse erhalten.


    */

## Futures und Promises

## Motivation

    package main

    import "time"
    import "fmt"

    // Running example.
    //
    // Inform friends about some booking request.
    // 1. Request a quote from some Hotel (via booking).
    // 2. Tell your friends.

    // Book some Hotel. Report price (int) and some poential failure (bool).
    func booking() (int, bool) {

        time.Sleep(1 * time.Second)

        return 30, true
    }

    /*

    Idea:

    - Channel to communicate result.

    - Asynchronous (non-blocking) computation of booking by using a separate thread.

    Issue?

        Only one of the friends obtains the result.


    */

    type Comp struct {
        val    int
        status bool
    }

    func buggy_attempt() {

        ch := make(chan Comp)
        go func() {
            r, s := booking()
            ch <- Comp{r, s}
        }()

        // friend 1
        go func() {
            v := <-ch
            fmt.Printf("\n %d %t", v.val, v.status)
        }()

        // friend 2
        go func() {
            v := <-ch
            fmt.Printf("\n %d %t", v.val, v.status)
        }()

        // We assume some other stuff is happening.
        time.Sleep(2 * time.Second)

    }

    /*

    How to fix the issue?

    Either one of the following must hold.

     ServerSolution: Server guarantees that result can be obtained multiple times.

     ClientSolution: Client guarantees that other clients can obtain the (same) result.


    */

    func server_solution() {

        ch := make(chan Comp)
        go func() {
            r, s := booking()
            for {
                ch <- Comp{r, s} // Supply result many times.
            }
        }()

        // friend 1
        go func() {
            v := <-ch
            fmt.Printf("\n %d %t", v.val, v.status)
        }()

        // friend 2
        go func() {
            v := <-ch
            fmt.Printf("\n %d %t", v.val, v.status)
        }()

        time.Sleep(2 * time.Second)

    }

    func client_solution() {

        ch := make(chan Comp)
        go func() {
            r, s := booking()
            ch <- Comp{r, s}
        }()

        // friend 1
        go func() {
            v := <-ch
            go func() {
                ch <- v // Make sure other friends obtain the result as well.
            }()
            fmt.Printf("\n %d %t", v.val, v.status)
        }()

        // friend 2
        go func() {
            v := <-ch
            go func() {
                ch <- v // Make sure other friends obtain the result as well.
            }()
            fmt.Printf("\n %d %t", v.val, v.status)
        }()

        time.Sleep(2 * time.Second)

    }

    /*

    Summary

        Something "simple" gets complicated.

        Design choice hard coded.

        User code hard to read and to maintain (manage threads, channels, ...).

     ==>

        Need proper (programming language) abstraction to hide implementation details.


    */

    // Channel-based futures.

    type Future chan Comp

    func future(f func() (int, bool)) Future {
        ch := make(chan Comp)
        go func() {
            r, s := f()
            v := Comp{r, s}
            for {
                ch <- v
            }
        }()
        return ch

    }

    func (f Future) get() (int, bool) {
        v := <-f
        return v.val, v.status
    }

    func (ft Future) onSuccess(cb func(int)) {
        go func() {
            v, o := ft.get()
            if o {
                cb(v)
            }
        }()

    }

    func (ft Future) onFailure(cb func()) {
        go func() {
            _, o := ft.get()
            if !o {
                cb()
            }
        }()

    }

    // Example using futures.

    func future_example() {
        f := future(booking)

        // friend 1
        f.onSuccess(func(x int) {
            fmt.Printf("\n friend 1: our quote is %d", x)
        })

        // friend 2
        f.onSuccess(func(x int) {
            fmt.Printf("\n friend 2: our quote is %d", x)
        })

        // friend 3, also considers the possibility of failure
        f.onFailure(func() {
            fmt.Printf("\n Folks, our booking failed, need another try")
        })

        time.Sleep(2 * time.Second)
    }

    func main() {

        //  buggy_attempt()
        //  server_solution()
        //  client_solution()
            future_example()

    }

## Mehr zu Futures versus Promises

Futures versus promises.

    A future can be viewed as a placeholder for a computation
    that will eventually become available.

    The term promise is often referred to a form of future
    where the result can be explicitly
    provided by the programmer.

Check out [Futures and
promises](https://sulzmann.github.io/ModelBasedSW/futures-promises.html)
