---
title: Concurrency models
description: Martin Sulzmann
---



## Programming language *models*

-   Hide implementation details

-   Capture recurring **programming patterns**

-   Close(r) to the problem domain

-   Examples:

    -   System-level programming in C
    -   Business applications in Java

-   Not every model fits every purpose

-   Need a rich tool box of models

-   Models are either built into the language (e.g. OO in Java) or can
    be provided as libraries/design patterns

**Here, we consider programming language models to solve concurrent
programming tasks.**

Go comes with built-in channel-based communication primitives. Highly
useful and expressive as we have seen.

For some (concurrent) programming tasks, directly using channels may not
be the best fit. We need something else.

Examples are:

-   mutex

-   fork/join

-   barrier

-   wait, notify

-   actors, and

-   futures.

We show how each of the above can be expressed in terms of Go.

## Mutex

Channels to implement a mutex.

Exercise: Consider various channel-based implemenatations.

    package main

    import "fmt"
    import "time"

    /////////////////////////////////////
    // Mutex = Buffered channel
    //

    // "Mutex" is a new type, isomorphic to "chan int"
    type Mutex chan int

    func newM() Mutex {
        x := make(chan int, 1)
        x <- 1
        return x

    }

    // Take key
    func lock(m Mutex) {
        <-m
    }

    // Put pack key
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

    func main() {
        beispielMutex()
        testLock()
    }

    // JUST PLAYING
    // 1. Lock Interface
    // 2. Implemented as a buffered channel
    // 3. Generic code
    // 4. Used for a concrete type (via structural subtyping)

    type Lock interface {
        init()
        lock()
        unlock()
    }

    type M struct {
        ch chan int
    }

    func (m *M) init() {
        m.ch = make(chan int, 1)
    }

    func (m *M) lock() {
        m.ch <- 1
    }

    func (m *M) unlock() {
        <-m.ch
    }

    func beispielLock(l Lock) {

        l.init()
        x := 1

        go func() {
            l.lock()
            x++
            l.unlock()
        }()

        go func() {
            l.lock()
            x++
            l.unlock()
        }()

        time.Sleep(1 * time.Second)
        fmt.Printf("%d", x)
    }

    func testLock() {
        var m M

        beispielLock(&m) // *M <= Lock

    }

## Fork/join

Many concurrency patterns (“models”) can be emulated via channels. If
possible, we would like to hide the (channel) implementation. As an
example, we consider “fork/join”.

Exercise: Consider various channel-based implemenatations.

    package main

    import "fmt"
    import "time"

    // Fork-join pattern in Go.

    // 1. Start a new Thread T
    // 2. Wait till T is done ("join")
    func exampleForkJoin() {

        join := make(chan int, 1)

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

    // Hide the implementation details via some "clever" API.

    type J chan int

    func fork(f func()) J {
        j := make(chan int)

        go func() {
            f()
            // There may several threads that want to "join".
            for {
                j <- 1
            }
        }()

        return j

    }

    func join(j J) {
        <-j
    }

    func exampleForkJoin2() {

        // Thread S
        thread_T := func() {
            fmt.Printf("S does something")
            time.Sleep(1 * time.Second)
        }

        j := fork(thread_T)

        join(j)

        fmt.Printf("Other main does something")
        time.Sleep(1 * time.Second)

    }

    func main() {

        exampleForkJoin()
        exampleForkJoin2()
    }

## Barrier

Wait for n tasks to finish.

    package main

    import "fmt"
    import "time"

    // 1. We use a buffered channel.
    // 2. Once done, transmit a message to the channel.
    // 3. Barrier waits till all tasks have transmitted their message.
    func exampleBarrier() {
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

        // Barrier, wait for T1, T2 to finish
        <-barrier
        <-barrier

        fmt.Printf("Main does something")
        time.Sleep(1 * time.Second)

    }

    // Include some timeout.
    // "channels" are "everywhere", we might want to hide some of the implementation details.
    func exampleBarrierWithTimeout() {
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

        // Barrier, wait for T1, T2 to finish with some timeout
        signal := make(chan int)
        go func() {
            <-barrier
            <-barrier
            signal <- 1
        }()

        select {
        case <-signal:
            fmt.Printf("OK")
        case <-time.After(1 * time.Second):
            fmt.Printf("Timeout")

        }

        fmt.Printf("Main does something")
        time.Sleep(1 * time.Second)

    }

    func main() {

        exampleBarrier()
        exampleBarrierWithTimeout()

    }

## Wait and notify

Java concurrency supports `wait` and `notify` methods to put a thread to
sleep (via `wait`), and to wake up a thread (via `notify`).

Requirements for wait and notify are as follows.

-   We shall wait until notified.

-   If there are several waiting threads, notify will wake up only one
    of these threads. Which one will be woken up is largely random.

-   If there are no waiting threads, the notify signal will get lost.

We show how to model such functionality in Go via channels.

We define a data type `Group` on which methods `wait` and `notify`
operate. Each group is represented via an unbuffered channel. Values
transmitted via the channel do not matter. We simply use a channel of
Integers.

    type Group chan int

    func newGroup() Group {
        return make(chan int)
    }

    func (g Group) wait() {
        <-g
    }

    func (g Group) notify() {
        select {
        case g <- 1:
        default:
        }
    }

The wait method performs a blocking receive and notify performs a send
on the group’s channel. Notify shall not block, in case there is no
waiting thread. We model this behavior by using select with a default
case.

Here are two additional methods.

    func (g Group) waitSomeTime(s time.Duration) {
        select {
        case <-g:
        case <-time.After(s):
        }

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

Method `waitSomeTime` takes an additional argument and only waits a
certain duration. Method `notifyAll` notifies all waiting threads.

## Example

We consider a variant of the sleeping barber example where waiting
customers will be notified by the barber to get a hair cut.

    func sleepingBarber() {
        g := newGroup()

        customer := func(s string) {
            for {
                g.wait()
                fmt.Printf("%s got haircut! \n", s)
                time.Sleep(1 * time.Second)

            }
        }

        barber := func() {
            for {
                g.notify() // single barber checks for waiting customer
                // g.notifyAll()  // as many barbers as there are waiting customers
                fmt.Printf("cut hair! \n")
                time.Sleep(3 * time.Second)
            }

        }

        go customer("A")
        go customer("B")
        go customer("C")

        barber()

    }

## Complete source code

    package main

    import "fmt"
    import "time"

    // Modeling wait/notify in Go with channels

    type Group chan int

    func newGroup() Group {
        return make(chan int)
    }

    // Wait till notified
    func (g Group) wait() {
        <-g
    }

    func (g Group) waitSomeTime(s time.Duration) {
        select {
        case <-g:
        case <-time.After(s):
        }

    }

    // Notify one of the waiting threads.
    // If nobody is waiting, the signal gets lost.
    func (g Group) notify() {
        select {
        case g <- 1:
        default:
        }
    }

    // notifyAll
    // Loop till all waiting threads are notified.
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

    // Sleeping barber example making use of wait/notify
    func sleepingBarber() {
        g := newGroup()

        customer := func(s string) {
            for {
                g.wait()
                fmt.Printf("%s got haircut! \n", s)
                time.Sleep(1 * time.Second)

            }
        }

        barber := func() {
            for {
                g.notify() // single barber checks for waiting customer
                // g.notifyAll()  // as many barbers as there are waiting customers
                fmt.Printf("cut hair! \n")
                time.Sleep(3 * time.Second)
            }

        }

        go customer("A")
        go customer("B")
        go customer("C")

        barber()

    }

    func main() {

        sleepingBarber()

    }

## Actors

An *actor* represents a computational unit which responds to messages
which can be sent from multiple sources. Sending a message to an actor
is a non-blocking operation by placing the message into the actor’s
mailbox. Processing of messages in the mailbox is done by testing for
different types of message patterns.

For a general overview of the actor model see
[here](https://en.wikipedia.org/wiki/Actor_model). There exists several
programming languages that support the actor model. The most popular and
well-known languages with support for actors are Erlang and Java.

We wish to get to know the actor model from Go’s point of view where we
use Go’s concurrency features to emulate actors. An actor can be viewed
as a thread and the actor’s mailbox can be represented via channels. The
difference compared to channel-based communication as found in Go is
that there can be multiple senders but there is only a receiver. We
consider various encoding schemes of actors in Go and discuss the
semantic subtleties to faithfully emulate actors in Go.

## Summary of main features

       Each actor can act independently.
       Each actor has a mailbox.

    actor <- msg

       We can send a message to the actor's mailbox


    actor = receive {
               case msg1 => ...
               ...
               case msgN => ...
           }

       Processing of messages via some receive statement.
       We pattern match over the actor's mailbox and
       check for the first message that matches any of the cases.

## Actors - Ping Pong Example

There are two actors:

-   ping

-   pong

They ping/pong each other.

    func pingPong() {

        pingMailBox := make(chan int)

        pongMailBox := make(chan int)

        ping := func() {
            for {
                <-pingMailBox
                fmt.Printf("ping received \n")
                time.Sleep(1 * time.Second)
                go func() {
                    pongMailBox <- 1
                }()

            }
        }

        pong := func() {
            for {
                go func() {
                    pingMailBox <- 1
                }()
                <-pongMailBox
                fmt.Printf("pong received \n")
                time.Sleep(1 * time.Second)

            }
        }

        go ping()

        pong()

    }

Points to note:

-   Mailbox = channel

-   Sending a mailbox message = asynchronously sending a message

-   There’s only a single type of message. Hence, there is no need to
    pattern match and we can immediately retrieve the message from the
    mailbox (channel).

We use unbuffered channels and carry out the transmission of messages
via a helper thread. We could use buffered channels but still would need
a helper thread as the buffer may be full and the send operation
therefore potentially may block.

## Actors - Santa Example

We consider a variant of the “Santa Claus Problem”. We assume that there
are three actors:

-   santa

-   deer

-   elf

Their purpose is as follows. The deer actor deliver toys. The elf actor
pursues toy R&D (research and development). Santa coordinates the deer
and elf actor. If the deer is ready, the deer will be sent to deliver
toys. If the elf is ready, the elf will be asked to pursue toy R&D. Once
elf and deer are done, they report back to santa that they are ready for
their next task.

Here is a possible implementation.

    type Message int

    const (
        Stop        Message = 1
        DeerReady   Message = 2
        ElfReady    Message = 3
        DeliverToys Message = 4
        PursueRandD Message = 5
    )

    func send(mailbox chan Message, m Message) {
        go func() {
            mailbox <- m
        }()
    }

    func santa() {
        mailboxSanta := make(chan Message)
        mailboxDeer := make(chan Message)
        mailboxElf := make(chan Message)

        santa := func() {
            b := true
            for b {
                m := <-mailboxSanta
                switch {
                case m == DeerReady:
                    send(mailboxDeer, DeliverToys)
                case m == ElfReady:
                    send(mailboxElf, PursueRandD)
                case m == Stop:
                    fmt.Printf("Santa: good-bye \n")
                    b = false

                }

            }

        }

        deer := func() {
            b := true
            for b {

                m := <-mailboxDeer
                switch {
                case m == DeliverToys:
                    fmt.Printf("Deer: Deliver toys \n")
                    time.Sleep(1 * time.Second) // deliver toys
                    send(mailboxSanta, DeerReady)
                case m == Stop:
                    fmt.Printf("Deer: good-bye \n")
                    b = false

                }

            }

        }

        elf := func() {
            b := true
            for b {

                m := <-mailboxElf
                switch {
                case m == PursueRandD:
                    fmt.Printf("Elf: R&D \n")
                    time.Sleep(1 * time.Second) // do some R&D
                    send(mailboxSanta, ElfReady)
                case m == Stop:
                    fmt.Printf("Elf: good-bye \n")
                    b = false

                }

            }

        }

        send(mailboxSanta, DeerReady)
        send(mailboxSanta, ElfReady)
        go func() {
            time.Sleep(10 * time.Second)
            send(mailboxSanta, Stop)
            send(mailboxDeer, Stop)
            send(mailboxElf, Stop)

        }()
        go santa()
        go deer()
        elf()

    }

Points to note:

-   Mailbox = channel

-   Sending a mailbox message = asynchronous channel send

-   Processing (receiving) of messages = switch-case statement

## Actors - Santa Example II

We extend the example as follows. We assume there is another actor:

-   rudolph

The rudolph actor is another deer. Once rudolph arrives, santa waits for
the second deer and only then santa gives the command to deliver toys.

## First (buggy) attempt

We adjust our implementation as follows.

        santa := func() {
            b := true
            for b {
                m := <-mailboxSanta
                switch {
                case m == RudolphReady:
                    m := <-mailboxSanta
                    switch {
                    case m == DeerReady:
                        send(mailboxRudolph, DeliverToys)
                        send(mailboxDeer, DeliverToys)
                    }
                case m == ElfReady:
                    send(mailboxElf, PursueRandD)
                case m == Stop:
                    fmt.Printf("Santa: good-bye \n")
                    b = false

                }

            }

        }

There are some issues! Consider the following order of messages sent to
santa’s mailbox.

1.  DeerReady

2.  RudolphReady

3.  ElfReady

We expect that santa

-   tells the deer and rudolph to deliver toys, and

-   tells the elf to pursue R&D.

The above implementation does not reflect this behavior.

-   The outer switch-case skips DeerReady (message received but no case
    to process this message).

-   We process RudolphReady and proceed to the inner switch-case.

-   The inner switch-case checks for DeerReady but only finds ElfReady.
    ElfReady is again skipped.

What to do?

-   The outer switch-case needs to process all possible patterns of
    messages.

-   We need to maintain some internal state that tells us if DeerReady
    has already arrived or not.

Here are the necessary changes.

        santa := func() {
            seenDeer := false
            seenRudolph := false
            b := true
            for b {
                m := <-mailboxSanta
                switch {
                case m == DeerReady && !seenRudolph:
                    seenDeer = true
                case m == RudolphReady && !seenDeer:
                    seenRudolph = true
                case (m == DeerReady && seenRudolph) || (m == RudolphReady && seenDeer):
                    send(mailboxRudolph, DeliverToys)
                    send(mailboxDeer, DeliverToys)
                    seenDeer = false
                    seenRudolph = false
                case m == ElfReady:
                    send(mailboxElf, PursueRandD)
                case m == Stop:
                    fmt.Printf("Santa: good-bye \n")
                    b = false
                }

            }

        }

The above works but is not a *nice* solution. Checking for patterns of
mailbox messages is mixed up with checking the internal state of the
actor.

## Another (nicer) attempt (mapping messages to specific channels)

There is no need to maintain internal state (deer seen, rudolph seen).

-   For each message type we introduce a channel.

-   Checking for message patterns is done by receiving a value via a
    specific channel.

-   Instead of a switch-case statement we use select.

    type MailboxSanta struct {
        DeerReady    chan int
        RudolphReady chan int
        ElfReady     chan int
        Stop         chan int
    }

    // Elf, deer and rudolph share the same mailbox type.
    type MailboxThing struct {
        Proceed chan int
        Stop    chan int
    }



        mailboxSanta := MailboxSanta{make(chan int), make(chan int), make(chan int), make(chan int)}
        mailboxDeer := MailboxThing{make(chan int), make(chan int)}
        mailboxRudolph := MailboxThing{make(chan int), make(chan int)}
        mailboxElf := MailboxThing{make(chan int), make(chan int)}

        send := func(ch chan int) {
            go func() {
                ch <- 1
            }()
        }

        santa := func() {
            b := true
            for b {
                select {
                case <-mailboxSanta.RudolphReady:
                    select {
                    case <-mailboxSanta.DeerReady:
                        send(mailboxDeer.Proceed)
                        send(mailboxRudolph.Proceed)
                    case <-mailboxSanta.Stop:
                        fmt.Printf("Santa: good-bye \n")
                        b = false
                    }

                case <-mailboxSanta.ElfReady:
                    send(mailboxElf.Proceed)
                case <-mailboxSanta.Stop:
                    fmt.Printf("Santa: good-bye \n")
                    b = false

                }

            }

        }

Let’s reconsider the tricky situation we discussed earlier. Messages
arrive in the following order.

1.  DeerReady

2.  RudolphReady

3.  ElfReady

Santa behaves as expected and tells the deer and rudolph to deliver toys
and tells the elf to pursue R&D.

-   The outer select statement blocks until
    `case <-mailboxSanta.RudolphReady` applies.

-   We proceed to the inner select statement where
    `case <-mailboxSanta.DeerReady` is chosen.

-   We tell deer and rudolph to deliver toys.

-   Finally, we come back to the outer select statement where
    `case <-mailboxSanta.ElfReady` applies and we tell the elf to pursue
    R&D.

Point to note.

In our *nice* solution (mapping messages to specific channels), after
rudolph has arrived, we either wait for the deer or the stop message.
What if the elf arrives? We (santa) do not tell the elf to proceed!

In our *not so nice* solution (mixing mailbox messages and some internal
actor state), santa would tell the elf to proceed!

Which solution is correct? Above it says: “Once rudolph arrives, santa
waits for the second deer …”. The *nice* solution appears closer to the
specification.

Exercise.

-   Extend the *nice* solution to allow that the elf proceeds while we
    (santa) still wait for the deer.

-   Restrict the *not so nice* solution to forbid the elf to proceed
    while we wait for the deer (after having already seen rudolph).

To summarize.

-   We introduce message specific channels.

-   We check for message patterns by performing a receive operation on
    the corresponding channel.

-   We use select to test if one of the message patterns applies.

## Actors - complete source code

    package main

    import "fmt"
    import "time"

    func pingPong() {

        pingMailBox := make(chan int)

        pongMailBox := make(chan int)

        ping := func() {
            for {
                <-pingMailBox
                fmt.Printf("ping received \n")
                time.Sleep(1 * time.Second)
                go func() {
                    pongMailBox <- 1
                }()

            }
        }

        pong := func() {
            for {
                go func() {
                    pingMailBox <- 1
                }()
                <-pongMailBox
                fmt.Printf("pong received \n")
                time.Sleep(1 * time.Second)

            }
        }

        go ping()

        pong()

    }

    // Santa example

    type Message int

    const (
        Stop        Message = 1
        DeerReady   Message = 2
        ElfReady    Message = 3
        DeliverToys Message = 4
        PursueRandD Message = 5
    )

    func send(mailbox chan Message, m Message) {
        go func() {
            mailbox <- m
        }()
    }

    func santa() {
        mailboxSanta := make(chan Message)
        mailboxDeer := make(chan Message)
        mailboxElf := make(chan Message)

        santa := func() {
            b := true
            for b {
                m := <-mailboxSanta
                switch {
                case m == DeerReady:
                    send(mailboxDeer, DeliverToys)
                case m == ElfReady:
                    send(mailboxElf, PursueRandD)
                case m == Stop:
                    fmt.Printf("Santa: good-bye \n")
                    b = false

                }

            }

        }

        deer := func() {
            b := true
            for b {

                m := <-mailboxDeer
                switch {
                case m == DeliverToys:
                    fmt.Printf("Deer: Deliver toys \n")
                    time.Sleep(1 * time.Second) // deliver toys
                    send(mailboxSanta, DeerReady)
                case m == Stop:
                    fmt.Printf("Deer: good-bye \n")
                    b = false

                }

            }

        }

        elf := func() {
            b := true
            for b {

                m := <-mailboxElf
                switch {
                case m == PursueRandD:
                    fmt.Printf("Elf: R&D \n")
                    time.Sleep(1 * time.Second) // do some R&D
                    send(mailboxSanta, ElfReady)
                case m == Stop:
                    fmt.Printf("Elf: good-bye \n")
                    b = false

                }

            }

        }

        send(mailboxSanta, DeerReady)
        send(mailboxSanta, ElfReady)
        go func() {
            time.Sleep(10 * time.Second)
            send(mailboxSanta, Stop)
            send(mailboxDeer, Stop)
            send(mailboxElf, Stop)

        }()
        go santa()
        go deer()
        elf()

    }

    // Santa example II

    const (
        RudolphReady Message = 6
    )

    func santa2Buggy() {
        mailboxSanta := make(chan Message)
        mailboxDeer := make(chan Message)
        mailboxRudolph := make(chan Message)
        mailboxElf := make(chan Message)

        santa := func() {
            b := true
            for b {
                m := <-mailboxSanta
                switch {
                case m == RudolphReady:
                    m := <-mailboxSanta
                    switch {
                    case m == DeerReady:
                        send(mailboxRudolph, DeliverToys)
                        send(mailboxDeer, DeliverToys)
                    }
                case m == ElfReady:
                    send(mailboxElf, PursueRandD)
                case m == Stop:
                    fmt.Printf("Santa: good-bye \n")
                    b = false
                }

            }

        }

        rudolph := func() {
            b := true
            for b {

                m := <-mailboxRudolph
                switch {
                case m == DeliverToys:
                    fmt.Printf("Rudolph: Deliver toys \n")
                    time.Sleep(1 * time.Second) // deliver toys
                    send(mailboxSanta, RudolphReady)
                case m == Stop:
                    fmt.Printf("Rudolph: good-bye \n")
                    b = false

                }

            }

        }

        deer := func() {
            b := true
            for b {

                m := <-mailboxDeer
                switch {
                case m == DeliverToys:
                    fmt.Printf("Deer: Deliver toys \n")
                    time.Sleep(1 * time.Second) // deliver toys
                    send(mailboxSanta, DeerReady)
                case m == Stop:
                    fmt.Printf("Deer: good-bye \n")
                    b = false

                }

            }

        }

        elf := func() {
            b := true
            for b {

                m := <-mailboxElf
                switch {
                case m == PursueRandD:
                    fmt.Printf("Elf: R&D \n")
                    time.Sleep(1 * time.Second) // do some R&D
                    send(mailboxSanta, ElfReady)
                case m == Stop:
                    fmt.Printf("Elf: good-bye \n")
                    b = false

                }

            }

        }

        send(mailboxSanta, DeerReady)
        send(mailboxSanta, ElfReady)
        send(mailboxSanta, RudolphReady)
        go func() {
            time.Sleep(10 * time.Second)
            send(mailboxSanta, Stop)
            send(mailboxDeer, Stop)
            send(mailboxRudolph, Stop)
            send(mailboxElf, Stop)

        }()
        go santa()
        go rudolph()
        go deer()
        elf()

    }

    func santa2Fixed() {
        mailboxSanta := make(chan Message)
        mailboxDeer := make(chan Message)
        mailboxRudolph := make(chan Message)
        mailboxElf := make(chan Message)

        santa := func() {
            seenDeer := false
            seenRudolph := false
            b := true
            for b {
                m := <-mailboxSanta
                switch {
                case m == DeerReady && !seenRudolph:
                    seenDeer = true
                case m == RudolphReady && !seenDeer:
                    seenRudolph = true
                case (m == DeerReady && seenRudolph) || (m == RudolphReady && seenDeer):
                    send(mailboxRudolph, DeliverToys)
                    send(mailboxDeer, DeliverToys)
                    seenDeer = false
                    seenRudolph = false
                case m == ElfReady:
                    send(mailboxElf, PursueRandD)
                case m == Stop:
                    fmt.Printf("Santa: good-bye \n")
                    b = false
                }

            }

        }

        rudolph := func() {
            b := true
            for b {

                m := <-mailboxRudolph
                switch {
                case m == DeliverToys:
                    fmt.Printf("Rudolph: Deliver toys \n")
                    time.Sleep(1 * time.Second) // deliver toys
                    send(mailboxSanta, RudolphReady)
                case m == Stop:
                    fmt.Printf("Rudolph: good-bye \n")
                    b = false

                }

            }

        }

        deer := func() {
            b := true
            for b {

                m := <-mailboxDeer
                switch {
                case m == DeliverToys:
                    fmt.Printf("Deer: Deliver toys \n")
                    time.Sleep(1 * time.Second) // deliver toys
                    send(mailboxSanta, DeerReady)
                case m == Stop:
                    fmt.Printf("Deer: good-bye \n")
                    b = false

                }

            }

        }

        elf := func() {
            b := true
            for b {

                m := <-mailboxElf
                switch {
                case m == PursueRandD:
                    fmt.Printf("Elf: R&D \n")
                    time.Sleep(1 * time.Second) // do some R&D
                    send(mailboxSanta, ElfReady)
                case m == Stop:
                    fmt.Printf("Elf: good-bye \n")
                    b = false

                }

            }

        }

        send(mailboxSanta, DeerReady)
        send(mailboxSanta, ElfReady)
        send(mailboxSanta, RudolphReady)
        go func() {
            time.Sleep(10 * time.Second)
            send(mailboxSanta, Stop)
            send(mailboxDeer, Stop)
            send(mailboxRudolph, Stop)
            send(mailboxElf, Stop)

        }()
        go santa()
        go rudolph()
        go deer()
        elf()

    }

    type MailboxSanta struct {
        DeerReady    chan int
        RudolphReady chan int
        ElfReady     chan int
        Stop         chan int
    }

    // Elf, deer and rudolph share the same mailbox type.
    type MailboxThing struct {
        Proceed chan int
        Stop    chan int
    }

    func santa2() {
        mailboxSanta := MailboxSanta{make(chan int), make(chan int), make(chan int), make(chan int)}
        mailboxDeer := MailboxThing{make(chan int), make(chan int)}
        mailboxRudolph := MailboxThing{make(chan int), make(chan int)}
        mailboxElf := MailboxThing{make(chan int), make(chan int)}

        send := func(ch chan int) {
            go func() {
                ch <- 1
            }()
        }

        santa := func() {
            b := true
            for b {
                select {
                case <-mailboxSanta.RudolphReady:
                    select {
                    case <-mailboxSanta.DeerReady:
                        send(mailboxDeer.Proceed)
                        send(mailboxRudolph.Proceed)
                    case <-mailboxSanta.Stop:
                        fmt.Printf("Santa: good-bye \n")
                        b = false
                    }

                case <-mailboxSanta.ElfReady:
                    send(mailboxElf.Proceed)
                case <-mailboxSanta.Stop:
                    fmt.Printf("Santa: good-bye \n")
                    b = false

                }

            }

        }

        rudolph := func() {
            b := true
            for b {
                select {
                case <-mailboxRudolph.Proceed:
                    fmt.Printf("Rudolph: Deliver toys \n")
                    time.Sleep(1 * time.Second) // deliver toys
                    send(mailboxSanta.RudolphReady)
                case <-mailboxRudolph.Stop:
                    fmt.Printf("Rudolph: good-bye \n")
                    b = false
                }

            }

        }

        deer := func() {
            b := true
            for b {
                select {
                case <-mailboxDeer.Proceed:
                    fmt.Printf("Deer: Deliver toys \n")
                    time.Sleep(1 * time.Second) // deliver toys
                    send(mailboxSanta.DeerReady)
                case <-mailboxDeer.Stop:
                    fmt.Printf("Deer: good-bye \n")
                    b = false
                }

            }

        }

        elf := func() {
            b := true
            for b {
                select {
                case <-mailboxElf.Proceed:
                    fmt.Printf("Elf: R&D \n")
                    time.Sleep(1 * time.Second) // do some R&D
                    send(mailboxSanta.ElfReady)
                case <-mailboxElf.Stop:
                    fmt.Printf("Elf: good-bye \n")
                    b = false
                }

            }

        }

        send(mailboxSanta.DeerReady)
        send(mailboxSanta.RudolphReady)
        send(mailboxSanta.ElfReady)

        go func() {
            time.Sleep(10 * time.Second)
            send(mailboxSanta.Stop)
            send(mailboxDeer.Stop)
            send(mailboxRudolph.Stop)
            send(mailboxElf.Stop)

        }()
        go santa()
        go rudolph()
        go deer()
        elf()

    }

    func main() {

        // pingPong()
        // santa()
        // santa2Buggy()
        // santa2Fixed()
        santa2()
    }

## Futures

Futures and promises are a high-level concurrency construct to support
asynchronous programming. A future can be viewed as a placeholder for a
computation that will eventually become available. The term promise is
often referred to a form of future where the result can be explicitly
provided by the programmer. For a high-level overview, see
[here](https://en.wikipedia.org/wiki/Futures_and_promises).

It is folklore knowledge to represent futures in terms of channels. For
example, in Go a future of type `T` is represented as `chan T`. We can
satisfy a future by writing a value into the channel. Obtaining the
result from a future corresponds to reading from the channel. This is
the general idea and we will work out the details next.

## Summary of main features

    type Future

    future(func() (T,bool)) Future

    (Future) get() (T,bool)

    (Future) onSuccess(func(T))

    (Future) onFail(func())

-   `Future` holds a value of some type `T` that becomes available
    eventually.

-   Function `future`:

    -   Executes a computation (asynchronously) to produce a value of
        type `T`.

    -   Once the computation is completed, this value will be bound to
        the future.

    -   We assume an extra Boolean return parameter to indicate if the
        computation was successful (true) or has failed (false).

    -   Failure arises for example in case an http required has timed
        out etc.

-   Method `get`:

    -   Queries the value bound to the future.

    -   Blocks if the value is not available yet.

-   Method `onSuccess`:

    -   The call to `onSuccess` is non-blocking.

    -   Takes a callback function to process the value bound to the
        future (once the value is available).

    -   Only applies if the computation to produce the future result was
        successful.

-   Method `onFailure`:

    -   The call to `onFailure` is non-blocking.

    -   Takes a callback function (with no arguments).

    -   Only applies if the computation to produce the future result has
        failed.

## Channel-based futures in Go

    type Comp struct {
        val    interface{}
        status bool
    }

    type Future chan Comp

    func future(f func() (interface{}, bool)) Future {
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

    func (f Future) get() (interface{}, bool) {
        v := <-f
        return v.val, v.status
    }

    func (ft Future) onSuccess(cb func(interface{})) {
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

-   We represent the type `T` via `interface{}` (Go does not support
    generics).

-   We use a Boolean value to indicate success or failure of a
    computation. Hence, the type `Comp` to represent the result of a
    (future) computation.

-   A value of type `Future` is an initially empty program variable. We
    represent this via an unbuffered channel of type `Comp`.

-   Function `future` carries out the computation asynchronously (in its
    own thread).

-   The result of the computation will be transmitted via the channel.

-   We repeatedly transmit the value (in an infinite loop) to retrieve
    the value of a `Future`an arbitrary number of times (multiple `get`,
    `onSuccess`, `onFail` calls).

-   We can access the value via `get` by performing a receive operation
    on the channel. This operation blocks if no value is available yet.

-   We can asynchronously access the value via methods `onSuccess` and
    `onFailure`.

-   Both methods take as arguments a callback functions. Callbacks will
    be applied once the computation has finished.

## Example

Here is an example application where we asynchronously execute some http
request. While waiting for the request, we can “do something else”.

    func getSite(url string) Future {
        return future(func() (interface{}, bool) {
            resp, err := http.Get(url)
            if err == nil {
                return resp, true
            }
            return err, false
        })
    }

    func printResponse(response *http.Response) {
        fmt.Println(response.Request.URL)
        header := response.Header
        // fmt.Println(header)
        date := header.Get("Date")
        fmt.Println(date)

    }

    func example1() {

        stern := getSite("http://www.stern.de")

        stern.onSuccess(func(result interface{}) {
            response := result.(*http.Response)
            printResponse(response)

        })

        stern.onFailure(func() {
            fmt.Printf("failure \n")
        })

        fmt.Printf("do something else \n")

        time.Sleep(2 * time.Second)

    }

## More expressive functionality for futures

Suppose we fire up several http requests (say stern and spiegel) and
would like to retrieve the first available request. How can this be
implemented?

A naive (inefficient) solution would check for each result one after the
other (via `get`). Can we be more efficient? Yes, we can make use of
`select` to check for the first available future result.

## `first` and `firstSucc`

    // Pick first available future
    func (ft Future) first(ft2 Future) Future {

        return future(func() (interface{}, bool) {

            var v interface{}
            var o bool

            // check for any result to become available
            select {
            case x := <-ft:
                v = x.val
                o = x.status

            case x2 := <-ft2:
                v = x2.val
                o = x2.status

            }

            return v, o
        })
    }

    // Pick first successful future
    func (ft Future) firstSucc(ft2 Future) Future {

        return future(func() (interface{}, bool) {

            var v interface{}
            var o bool

            select {
            case x := <-ft:
                if x.status {
                    v = x.val
                    o = x.status
                } else {
                    v, o = ft2.get()
                }

            case x2 := <-ft2:
                if x2.status {
                    v = x2.val
                    o = x2.status
                } else {
                    v, o = ft.get()
                }

            }

            return v, o
        })
    }

## Example

Our example with three http requests where we are only interested in the
first available request.

        spiegel := getSite("http://www.spiegel.de")
        stern := getSite("http://www.stern.de")
        welt := getSite("http://www.welt.com")

        req := spiegel.first(stern.first(welt))

        req.onSuccess(func(result interface{}) {
            response := result.(*http.Response)
            printResponse(response)

        })

        req.onFailure(func() {
            fmt.Printf("failure \n")
        })

        fmt.Printf("do something else \n")

        time.Sleep(2 * time.Second)

## Futures - complete source code

    package main

    import "fmt"
    import "time"
    import "net/http"

    ////////////////////
    // Simple futures

    // A future, once available, will be transmitted via a channel.
    // The Boolean parameter indicates if the (future) computation succeeded or failed.

    type Comp struct {
        val    interface{}
        status bool
    }

    type Future chan Comp

    func future(f func() (interface{}, bool)) Future {
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

    func (f Future) get() (interface{}, bool) {
        v := <-f
        return v.val, v.status
    }

    func (ft Future) onSuccess(cb func(interface{})) {
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

    ///////////////////////////////
    // Adding more functionality

    // Pick first available future
    func (ft Future) first(ft2 Future) Future {

        return future(func() (interface{}, bool) {

            var v interface{}
            var o bool

            // check for any result to become available
            select {
            case x := <-ft:
                v = x.val
                o = x.status

            case x2 := <-ft2:
                v = x2.val
                o = x2.status

            }

            return v, o
        })
    }

    // Pick first successful future
    func (ft Future) firstSucc(ft2 Future) Future {

        return future(func() (interface{}, bool) {

            var v interface{}
            var o bool

            select {
            case x := <-ft:
                if x.status {
                    v = x.val
                    o = x.status
                } else {
                    v, o = ft2.get()
                }

            case x2 := <-ft2:
                if x2.status {
                    v = x2.val
                    o = x2.status
                } else {
                    v, o = ft.get()
                }

            }

            return v, o
        })
    }

    ///////////////////////
    // Examples

    func getSite(url string) Future {
        return future(func() (interface{}, bool) {
            resp, err := http.Get(url)
            if err == nil {
                return resp, true
            }
            return err, false
        })
    }

    func printResponse(response *http.Response) {
        fmt.Println(response.Request.URL)
        header := response.Header
        // fmt.Println(header)
        date := header.Get("Date")
        fmt.Println(date)

    }

    func example1() {

        stern := getSite("http://www.stern.de")

        stern.onSuccess(func(result interface{}) {
            response := result.(*http.Response)
            printResponse(response)

        })

        stern.onFailure(func() {
            fmt.Printf("failure \n")
        })

        fmt.Printf("do something else \n")

        time.Sleep(2 * time.Second)

    }

    func example2() {

        spiegel := getSite("http://www.spiegel.de")
        stern := getSite("http://www.stern.de")
        welt := getSite("http://www.welt.com")

        req := spiegel.first(stern.first(welt))

        req.onSuccess(func(result interface{}) {
            response := result.(*http.Response)
            printResponse(response)

        })

        req.onFailure(func() {
            fmt.Printf("failure \n")
        })

        fmt.Printf("do something else \n")

        time.Sleep(2 * time.Second)

    }

    func main() {

        // example1()

        example2()
    }

## Summary

In Go, we can support the following three concurrency models by
emulating them via channels. Such emulations are useful to (a)
understand the inner-workings of these concurrency models, and (b) to
make them available in Go.

-   wait/notify

-   Actors

-   Futures

Further reading:

-   [Mixing Metaphors: Actors as Channels and Channels as
    Actors](https://arxiv.org/abs/1611.06276)

-   [Actors with Multi-Headed Message Receive
    Patterns](https://www.researchgate.net/publication/220993985_Actors_with_Multi-Headed_Message_Receive_Patterns)

-   [Futures and promises in Haskell and
    Scala](https://www.researchgate.net/publication/330066278_Futures_and_promises_in_Haskell_and_Scala)

-   [Why Do Scala Developers Mix the Actor Model with Other Concurrency
    Models?](https://core.ac.uk/download/pdf/10201439.pdf)
