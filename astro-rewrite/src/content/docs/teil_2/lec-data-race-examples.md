---
title: Dynamic data race prediction - TSan and examples
description: Martin Sulzmann
---



## ThreadSanitizer (TSan) “–race”

-   ThreadSanitizer (TSan) “–race”

    -   FastTrack with some Optimizations

    -   [Dynamic Race Detection with LLVM
        Compiler](https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/data-race-test/ThreadSanitizerLLVM.pdf)

    -   [Go race detector](https://go.dev/doc/articles/race_detector) is
        built on top of TSan

## Simple examples

    package main

    import "sync"
    import "fmt"
    import "time"

    func detected() {

        x := 1
        var m sync.RWMutex

        go func() {
            x = 2
            m.Lock()
            m.Unlock()

        }()

        m.Lock()
        x = 3
        m.Unlock()

        fmt.Printf("%d", x)
        time.Sleep(1 * time.Second)
    }

    // false negative
    // because critical sections are not reordered
    func notDetected() {

        x := 1
        var m sync.RWMutex

        go func() {
            x = 2
            m.Lock()
            m.Unlock()

        }()

        time.Sleep(1 * time.Second)

        m.Lock()
        x = 3
        m.Unlock()

        fmt.Printf("%d", x)

    }

    func main() {
        detected()
        notDetected()

    }

## TSan optimizations

-   TSan vector clocks are limited to 256 entries (=threads).

-   TSan only records the four “most recent” reads.

This leads to false negatives.

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

    // Writes don't seem to replace reads.
    // We always run into a write-read race here.
    func manyConcurrentWrites() {
        x := 1
        var m sync.RWMutex

        threadNo := 100 // for 1 we'll encounter the race

        f := func(x int) {}

        protectedWrite := func() {
            m.Lock()
            x = 3
            m.Unlock()

        }

        // unprotected read
        go func() {
            f(x)
        }()

        for i := 0; i < threadNo; i++ {

            go protectedWrite()

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

    /////////////////////////////
    // Playing

    /*

    There are threadNo read-write races.
    TSan only keeps the four most recent reads.
    TSan only reports at most one read-write race.

     From a diagnosis point of view:
       - Would it help to report all read-write races?


    */

    func concReadsRaceWithWrite() {
        x := 1

        threadNo := 100

        f := func(x int) {}

        unprotectedRead := func() {
            f(x)
            time.Sleep(1 * time.Second)
        }

        for i := 0; i < threadNo; i++ {

            go unprotectedRead()

        }

        time.Sleep(1 * time.Second)
        x = 2 // unprotected write
        fmt.Printf("%d", x)

    }

    func main() {

        manyThreads()
        manyConcurrentReads()
        // manyConcurrentWrites()
        // subsequentRW()
        // subsequentRW2()
        // concReadsRaceWithWrite()

    }

## Challenge

The size of vector clocks is limited to 256 entries.

Do we run into false positives?

*I have not managed to come up with such an example yet. Maybe you have
an idea. Below you find some of my (failed) attempts.*

    package main

    import "sync"
    import "fmt"
    import "time"

    // False negatives due to vc limit of 256 threads !?

    type Group chan int

    func newGroup() Group {
        return make(chan int)
    }

    // Wait till notified
    func (g Group) wait() {
        <-g
    }

    func (g Group) notifyAll() {
        b := true
        for b {
            select {
            case g <- 1:
            default:
                b = false
            }
        }
    }

    /*

    Trying to create some false positive.


    1. Protected write access in some thread.
    2. Many threads in between.
    3. Some other thread with a protected write access.
         Under HB, the acquire syncs with the release.
         Is the thread in 1 gone?


    */

    func ex() {
        x := 1

        g := newGroup()

        var m sync.RWMutex

        f := func(c1 chan int, c2 chan int, h func()) {
            <-c1
            h()
            c2 <- 1
            g.wait()
        }

        n := 600
        sigs := make([]chan int, n)
        for i := 0; i < n; i++ {
            sigs[i] = make(chan int)
        }

        // protected write
        go f(sigs[0], sigs[1], func() {
            m.Lock()
            x = 3
            m.Unlock()
            time.Sleep(1 * time.Second)
        })

        for i := 1; i < n-1; i++ {
            go f(sigs[i], sigs[i+1], func() {})

        }

        sigs[0] <- 1
        <-sigs[n-1]

        m.Lock()
        x = 3
        m.Unlock()
        g.notifyAll()
        fmt.Printf("%d", x)

    }

    func ex2() {
        x := 1
        y := 1

        ch := make(chan int, 1)

        //  var m sync.RWMutex

        var m2 sync.RWMutex

        go func() {

            for i := 1; i < 100; i++ {
                go func() {
                    m2.Lock()
                    y++
                    m2.Unlock()
                    time.Sleep(1 * time.Second)

                }()

            }
        }()

        go func() {
            for i := 1; i < 20; i++ {
                m2.Lock()
                y = 4
                m2.Unlock()
            }

            x = 2
            ch <- 1

            time.Sleep(1 * time.Second)
        }()

        go func() {

            for i := 1; i < 1000; i++ {
                go func() {
                    m2.Lock()
                    y++
                    m2.Unlock()
                    time.Sleep(1 * time.Second)

                }()

            }
        }()

        go func() {
            <-ch
            x = 3
        }()

        time.Sleep(3 * time.Second)
        m2.Lock()
        tmp := y + x
        m2.Unlock()
        fmt.Printf("y =%d", tmp)

    }

    func main() {

        ex()
        ex2()
    }
