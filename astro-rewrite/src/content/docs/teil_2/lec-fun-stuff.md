---
title: Fun stuff - On-going research topics
description: Martin Sulzmann
---



## Overview

Things that interest me.

## Programming languages + abstractions

-   [Go](https://go.dev/), [Rust](https://www.rust-lang.org/), …

Many “new” languages copy features from “old” languages such as
[Haskell](https://www.haskell.org/)

## Trace-based dynamic verification

Observe the program behavior based on a specific program run.

Try to predict “faulty” behavior (such as data races and deadlocks).

## “Retriable” futures

Consider some booking scenario using our “future” API.

    func bookHotel_A() (int, bool) { return 1, true }
    func bookHotel_B() (int, bool) { return 2, true }
    func bookTrain() (int, bool)   { return 3, true }
    func bookBus() (int, bool)     { return 4, true }

    func booking() {
        hotel_A := future[int](bookHotel_A)
        hotel_B := future[int](bookHotel_B)
        train := future[int](bookTrain)
        bus := future[int](bookBus)

        accommodation := hotel_A.firstSucc(hotel_B)

        transportation := train.firstSucc(bus)

        trip := transportation.then(func(x int) (int, bool) {
            // x ignored
            // in a real world setting, some booking code which might be passed to the Hotel
            return accommodation.get()
        })

        trip.onSuccess(func(x int) {
            fmt.Printf("We got Hotel and transportation!")
        })

        time.Sleep(1 * time.Second)
    }

-   First check for transportation

-   Then check for a Hotel

What if we fail!?

    func bookingRetry() {
        hotel_A := future[int](bookHotel_A)
        hotel_B := future[int](bookHotel_B)
        train := future[int](bookTrain)
        bus := future[int](bookBus)

        accommodation := hotel_A.firstSucc(hotel_B)

        transportation := train.firstSucc(bus)

        trip := transportation.then(func(x int) (int, bool) {
            // x ignored
            // in a real world setting, some booking code which might be passed to the Hotel
            return accommodation.get()
        })

        trip.onSuccess(func(x int) {
            fmt.Printf("We got Hotel and transportation!")
        })

        trip.onFailure(func() {
            fmt.Printf("Failure, let's retry!")
            bookingRetry()
        })

        time.Sleep(1 * time.Second)
    }

-   We start from scratch!

-   But what if booking of Hotel succedded.

-   Only booking of transportation failed (maybe some booking server is
    done, …)

-   Hence, it seems wasteful to start from scratch

Let’s try to be more “clever”.

    func checkTransport(accommodation Future[int]) {
        accommodation.onSuccess(func(x int) {

            train := future[int](bookTrain)
            bus := future[int](bookBus)

            transportation := train.firstSucc(bus)

            transportation.onFailure(func() {
                checkTransport(accommodation)
            })

            transportation.onSuccess(func(x int) {
                fmt.Printf("Finally, We got Hotel and transportation!")

            })

        })
    }

    func bookingRetryTryingToBeMoreClever() {
        hotel_A := future[int](bookHotel_A)
        hotel_B := future[int](bookHotel_B)

        accommodation := hotel_A.firstSucc(hotel_B)

        accommodation.onFailure(func() {
            bookingRetryTryingToBeMoreClever()
        })

        checkTransport(accommodation)

        time.Sleep(1 * time.Second)
    }

-   Manually check if subcomputations (Hotel/Transport bookings) have
    failed

-   Manually restart these bookings (while maintaining earlier
    subcomputations)

-   Complex control flow (prone to errors)

## Retriable futures

    trip := transportation.then(func(x int) (int, bool) {
            return accommodation.get()
        })

    tripSucc = trip.retry()

Some magic `retry` method.

-   Retry automatically restarts (sub)computations if the future has
    failed (we could possibly set a limit on the number of retries).

-   Retry only restarts failed subcomputations

-   User code remains the same

-   Obviously, the magic lies in the implementation (of retriable
    futures)

*Some prototype exists*

*Further examples are “first-class events for Go”,…*

## Go and its design space

## Go without Generics

    type Stringer interface{ Show() string }

    type OnOff struct{ Value bool }

    type Pair struct {
        First  OnOff
        Second OnOff
    }

    func (this OnOff) Show() string {
        if this.Value {
            return "on"
        } else {
            return "off"
        }
    }

    func (this Pair) Show() string {
        return "(" + this.First.Show() + ", " + this.Second.Show() + ")"
    }

    func showTwice(x Stringer, y Stringer) string {
        return x.Show() + y.Show()
    }

    func testShow() {
        showTwice(OnOff{true}, Pair{OnOff{true}, OnOff{false}})
    }

-   Method overloading based on the receiver type

    func (this OnOff) Show() string { ... }
    func (this Pair) Show() string { ... }

-   Interfaces to declare methods that share the same receiver

    type Stringer interface{ Show() string }

-   Structural subtyping

    -   `OnOff` implements the `Stringer` interface

    -   Any value of type `OnOff` is also a value of type `Stringer`

## Go with Generics

    type PairG[A Stringer, B Stringer] struct {
        First  A
        Second B
    }

    func (this PairG[A, B]) Show() string {
        return "(" + this.First.Show() + ", " + this.Second.Show() + ")"
    }

    func testShowG() {
        fmt.Printf("\n %s", showTwice(OnOff{true}, PairG[OnOff, OnOff]{OnOff{true}, OnOff{false}}))

    }

-   Every generic type parameter comes with a type bound

-   Type bound `any` is satisfied by all types

## Open Issues

-   No generic methods, no additional type constraints

    // More flexible variant not accepted by Go 1.21
    func (ft Future[T]) then[S any](f func(T) (S, bool)) Future[S]


    // More flexible variant not accepted by Go 1.21
    type Pair[A any, B any] struct {
      First A
      Second B
    }
    func (this Pair[A Stringer, B Stringer]) Show() string {
      return "(" + this.First.Show() + ", " + this.Second.Show() + ")"
    }

-   Lack of type inference, see
    `PairG[OnOff, OnOff]{OnOff{true}, OnOff{false}}`.

and further issues.

### State of the art

[Featherweight Generic Go](https://arxiv.org/pdf/2005.11710.pdf)

[Generic Go to Go](https://arxiv.org/pdf/2208.06810.pdf)

Own works:

[A Dictionary-Passing Translation of Featherweight
Go](https://arxiv.org/pdf/2106.14586.pdf)

[A Type-Directed, Dictionary-Passing Translation of Featherweight
Generic Go](https://arxiv.org/pdf/2209.08511.pdf)

## Complete source code

    package main

    import "fmt"

    // Go without generics

    type Stringer interface{ Show() string }

    type OnOff struct{ Value bool }

    type Pair struct {
        First  OnOff
        Second OnOff
    }

    func (this OnOff) Show() string {
        if this.Value {
            return "on"
        } else {
            return "off"
        }
    }

    func (this Pair) Show() string {
        return "(" + this.First.Show() + ", " + this.Second.Show() + ")"
    }

    func showTwice(x Stringer, y Stringer) string {
        return x.Show() + y.Show()
    }

    func testShow() {
        fmt.Printf("\n %s", showTwice(OnOff{true}, Pair{OnOff{true}, OnOff{false}}))

    }

    // Go with generics

    type PairG[A Stringer, B Stringer] struct {
        First  A
        Second B
    }

    func (this PairG[A, B]) Show() string {
        return "(" + this.First.Show() + ", " + this.Second.Show() + ")"
    }

    func testShowG() {
        fmt.Printf("\n %s", showTwice(OnOff{true}, PairG[OnOff, OnOff]{OnOff{true}, OnOff{false}}))

    }

    /*
    // More flexible variant not accepted by Go 1.19
    type Pair[A any, B any] struct {
      First A
      Second B
    }
    func (this Pair[A Stringer, B Stringer]) Show() string {
      return "(" + this.First.Show() + ", " + this.Second.Show() + ")"
    }
    */

    func main() {
        testShow()
        testShowG()

    }

## Dynamic data race prediction

## Vector clocks

Clock = Time stamp (per thread)

Vector clock = list of time stamps

Operations are as follows.

-   Happens-before via vector clocks

    \[*k*<sub>1</sub>, ..., *k*<sub>*n*</sub>\] &lt; \[*i*<sub>1</sub>, ..., *i*<sub>*n*</sub>\]
    if all *k*<sub>*j*</sub> &lt;  = *i*<sub>*j*</sub> for
    *j* = 1, ..., *n* and there exists *j* such that
    *k*<sub>*j*</sub> &lt; *i*<sub>*j*</sub>

-   Advance time stamp

*i**n**c*(\[*k*<sub>1</sub>, ..., *k*<sub>*i* − 1</sub>, *k*<sub>*i*</sub>, *k*<sub>*i* + 1</sub>, ..., *k*<sub>*n*</sub>\], *i*) = \[*k*<sub>1</sub>, ..., *k*<sub>*i* − 1</sub>, *k*<sub>*i*</sub> + 1, *k*<sub>*i* + 1</sub>, ..., *k*<sub>*n*</sub>\]

-   Synchronize vector clocks

*s**y**n**c*(\[*i*<sub>1</sub>, ..., *i*<sub>*n*</sub>\], \[*j*<sub>1</sub>, ..., *j*<sub>*n*</sub>\]) = \[*m**a**x*(*i*<sub>1</sub>, *j*<sub>1</sub>), ..., *m**a**x*(*i*<sub>*n*</sub>, *j*<sub>*n*</sub>)\]

## Example

         T1          T2            Vector clocks

    1.   acq(y)                   [1,0]
    2.   rel(y)                   [2,0]
    3.   w(x)                     [3,0]
    4.               acq(y)       [2,1]
    5.               w(x)         [2,2]
    6.               rel(y)       [2,3]

We find \[3, 0\] and \[2, 2\] are incomparable.

We conclude that the two writes are in a data race.

## Open issues

Vector clocks grow with the number of threads.

TSan limits the size of its vector clock to 256!

## Research direction

Find more compact representations of vector clocks/happens-before.

Idea: Use set of events (but not the “full” set!)

Instead of each thread

-   a vector clock

we assume that each thread maintains

-   reads on x that “immediately” happen before and

-   most recent write (if any) that immediately happens before.

Example with happens-before data race:

         T1          T2           ES-T1       ES-T2        Current writes

    1.   acq(y)                   {}                           {}
    3.   rel(y)                   {}                           {}
    3.   w(x)                     {w(x)_1}                     {w(x)_1}
    4.               acq(y)                   {}               {w(x)_1}
    5.               w(x)                     {w(x)_5}                   Data race cause current write not in ES-T2
    6.               rel(y)

Example with no happens-before data race:

         T1          T2           ES-T1       ES-T2        Current writes

    1.   w(x)                     {w(x)_1}                 {w(x)_1}
    2.   acq(y)                   {w(x)_1}                 {w(x)_1}
    3.   rel(y)                   {w(x)_1}                 {w(x)_1}
    4.               acq(y)                  {w(x)_1}   sync with previous rel by merging ES-T1 and ES-T2
    5.               w(x)                    {w(x)_5}   replace w(x)_1 by w(x)_5, no data race cause current write in ES-T2
    6.               rel(y)

## Dynamic deadlock prediction

## Lock dependencies instead of lock graphs

Lock dependencies `D = (id, l, ls)` are constructed if thread id
acquires lock l while holding locks ls. Effectively that corresponds to
a lock tree and the lock dependency construction can be done on a per
thread basis.

A deadlock (warning) is issued if there is a cyclic lock dependency
chain D\_1, …, D\_n:

    (LD-1) ls_i cap ls_j = emptyset for i != j and

    (LD-2) l_i in ls_i+1 for i=1,...,n-1 and

    (LD-3) l_n in ls_1

## Example

        T1         T2

    1.  acq(y)
    2.  acq(x)
    3.  rel(x)
    4.  rel(y)
    5.             acq(x)
    6.             acq(y)
    7.             rel(y)
    8.             rel(x)

    D1 = (T1, {x}, {y})

    D2 = (T2, {y}, {x})

## Open issues

Lockset construction on a per thread basis.

Cross-thread dependencies are not taken into account.

This may yield to false positives as well as false negatives.

### False positive example

        T0            T1            T2

    1.  fork(T2)
    2.                              acq(z)
    3.                              acq(y)
    4.                              acq(x)
    5.                              rel(x)
    6.                              rel(y)
    7.                              rel(z)
    8.  acq(z)
    9.  fork(T1)
    10.               acq(x)
    11.               acq(y)
    12.               rel(y)
    13.               rel(x)
    14. join(T1)
    15. rel(z)

Based on the standard lockset construction, we find

    D1 = (T1,{y},{x})

    D2 = (T2,{x},{y,z})

The above dependencies are in a cyclic lock dependency chain.

This is false positive because the events in thread T1 are guarded by
lock z.

Issue here: D1 is missing the guard lock z.

### False negative example

        T0            T1            T2

    1.  fork(T2)
    2.  acq(x)
    3.  fork(T1)
    4.                acq(y)
    5.                rel(y)
    6.  join(T1)
    7.  rel(x)
    8.                              acq(y)
    9.                              acq(x)
    10.                             rel(x)
    11.                             rel(y)

Based on the standard lockset construction, we find

    D2 = (T2,{x},{y})

This is false negative because the events in thread T1 are guarded by
lock x.

This implies

    D1 = (T1,{y},{x})

which then leads to a cyclic lock dependency chain.

## Research direction

Cross-thread lock set construction!

How?

### The PWR relation

Make use of the PWR relation found in our prior work [Efficient, Near
Complete and Often Sound Hybrid Dynamic Data Race Prediction (extended
version)](https://arxiv.org/abs/2004.06969).

We write &lt;PWR to denote the PWR relation.

Result:

Let e and f be two events such that e &lt;PWR f. Then, event e *must*
happen before event f.

### Cross-thread lock set construction via PWR

Let acq(x)-rel(x) be some critical section.

Let e be some event not necesarily in the same thread as the critical
section acq(x)-rel(x).

Event e is guarded by acq(x)-rel(x) if

-   acq(x) &lt;PWR e and

-   e &lt;PWR rel(x)

Take note.

-   The PWR relation overapproximates.

-   We can compute some but not necessarily all cross-thread guard
    locks.

## Go style mutexes

In Go, ownership of a mutex is not tied to a specific thread.

        var m sync.Mutex

        acq := func() { m.Lock() }
        rel := func() { m.Unlock() }

        go func() {

            go func() {
                rel()
                fmt.Printf("B")
            }()
            acq()
            fmt.Printf("A")

            time.Sleep(1 * time.Second)
        }()
        time.Sleep(2 * time.Second)
        acq()
        rel()

        fmt.Printf("%d", x) // use x

The resulting trace is as follows (enforced via some sleep statements).

           T1         T2          T3

    1.   acq
    2.               rel
    3.                           acq
    4.                           rel

Things to consider:

-   Impact on happens-before race detectors?

-   Impact on computation of lock dependencies?

Another Go feature.

-   Go supports reader-writer locks

-   This also affects the construction of lock dependencies

## If you got interested

## Model-based SW (elective course)

-   Covers Go and programming langauge semantics issues

## Seminar and project

Check out list of topics
