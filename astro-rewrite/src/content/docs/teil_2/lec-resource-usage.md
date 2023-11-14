---
title: Resource usage (dynamic and static) verification
description: Martin Sulzmann
---



# Motivation and overview: Static versus dynamic verification

## Verification by example

Consider the program.

    int f(int n) {
      if(n == 0)
         return 1;

      if(n > 0)
         return f(n-1);

      if(n < -2)
        return f(n+1);

      return f(n-1);
    }

We observe.

    f(5) => f(4) => f(3) => f(2) => f(1) => f(0) => terminates

    f(10) => ... => f(0) => terminates

    f(-4) => f(-3) => f(-2) => f(-3) => f(-2) => ....

    does not seem to terminate (maybe we need to wait a bit longer?)

We verify. For all positive inputs, the function terminates. For
example, via an inductive proof.

Formal verification: Prove (or disprove) that a system satisfies some
property.

By "system" we refer here to software systems (functions, algorithms,
...).

Properties are often described in terms of specification (languages).
For example, first-order logic, regular expressions etc.

## Verification versus Validation

Verification:

-   "The product we have built is right"

-   No bugs, ...

-   Implementation meets the specification ("programmer needs")

Validation:

-   "We have built the right product"

-   Specification meets the problem description ("customer needs")

## Dynamic verification

Dynamic = run-time

-   At run-time, execute the program.

-   Observe its (actual) behavior.

-   Also commonly referred to as run-time verification and testing.

## Static verification

Static = compile-time

-   Build approximation of the program's behavior

-   Verify that the approximation satisfies some properties.

-   To remain decidable, we generally need to over-approximate.

## Selection of verification methods

### Static program analysis

1.  Data-flow analysis

2.  Control-flow analysis

3.  Type and effect systems

4.  Modelchecking

### Dynamic program analysis

1.  Testing:

    -   Unit-Tests

    -   Invariants/Assertions

    -   Oracle-based testing

2.  Run-time verification:

    -   Monitor run-time behavior

    -   Check for invalid patterns of behavior

This is just a selection

# Resource usage verification (overview)

Resource = File

Usage = File access (open, close, write, read).

## Simple "while" language for resource usages

     b ::=   Boolean expressions

     p ::= p ; p                   -- Sequence
        |  if b { p } else {p }    -- Conditional statements
        |  for b { p }             -- Iteration
        |  open
        |  close
        |  read
        |  write
        | ...                      -- Further stuff, assignment etc

Some simplified language in style of Go. We assume some file primitives
(open, close, write, read).

Single-threaded.

## (Formal) Specification

We wish to ensure that file primitives are used according to certain
rules (policy).

File usage policy (preventing bad behavior/safety):

1.  After opening a file there can be reads, writes and closing the
    file.

2.  After a write there shall be no reads.

How can such rules be specified? Regular expressions, finite state
machines, ...

Regular property, can be specified via a [regular
expression](https://en.wikipedia.org/wiki/Regular_expression):

    open . (read* . (write . write* + epsilon)) . close

We use the following notation:

    . denotes concatenation

    * denotes the Kleene star

    + denotes alternatives where we assume that * binds tighter than . and +,
    and . binds tighter than +

    epsilon denotes the empty word

The above property can also be specified via the following finite state
machine (FSA).

    Initial state: 1
    Final state: 3

    1 --open--> 2
    2 --read--> 2
    2 --close--> 3
    2 --write--> 4
    4 --write--> 4
    4 --close--> 3

Error state and transitions are left implicit.

## Verification

How to ensure that the rules (policy) are satisfied?

Need to decide if we wish to enforce the rules *dynamically* or
*statically*.

## Dynamic Verification

Dynamic = run-time

### Online

While executing the program, for each file access, check if resource
usage policy still holds.

1.  Need to monitor run-time behavior, keep track of each file access.

2.  Turn resource usage policy into a finite state machine (FSA).

3.  While executing the program, check if FSA may be in a bad state
    (after processing of a file primitive).

### Offline

1.  Execute the program and log (record) each file access (yields a
    trace).

2.  Run the program a finite number of steps (to obtain the trace).

3.  Run the FSA on the trace.

### Instrumentation and Tracing

Both methods (online and offline) assume that the running program is
instrumented such that we can keep track of the events we are interested
in. In our case, events are open, close, read and write.

### Observations: Membership test versus prefix test

The offline method yields a *finite* trace (sequence of events) as we
execute the program a finite number of steps.

For the online method, the resulting trace from executing the program is
implicit (because we immediately process events). The trace is possibly
infinite (as the program may not terminate).

**Dynamic verification boils down to a prefix text (which is variant of
the membership test for regular expressions)** (in both cases, offline
or online).

#### Membership

Recall the membership problem for regular expressions.

Notation we use: `L(r)` refers to the language denoted by `r`. We write
`w in L(r)` if `w` is a member (element) in `L(r)`.

The membership problem is the problem of deciding if `w` is a member
(element) in the language described by the regular expression `r`.

##### Prefix test

The resource usage policy is specified in terms of a regular expression
`r`.

The trace is a word `w` in the formal language of resource usage events.

BUT, in our (dynamic verification) case, we do not test or membership.
Instead, we check if the trace is a prefix of a word in `L(r)`. Prefix
means that by adding some parts to the trace we obtain an actual word in
the language `L(r)`. The **prefix test** is similar to the membership
test but slightly different.

Why do we only test for prefixes? Consider a simplified policy where for
each `open` event we require a `close` event. In terms of a regular
expression, we find `(open . close)*`.

The word `open . close` is a member of (the language denoted by) the
regular expression.

Suppose we run a program (a finite number of steps) and obtain the trace
(word) `open . close . open`. The trace `open. close . open` is a prefix
of the language denoted by regular expression `(open . close)*` (but not
a member).

Is this an error, shall dynamic analysis report that the policy is
violated? Well, if we simply would execute the program a little longer,
then possibly we would encounter the "missing" `close`.

Suppose another program run that yields the trace
`open . close . close`. This trace cannot be a prefix and we must report
that the policy is violated.

To summarize, dynamic verification makes sure nothing bad will ever
happen (referred to as a safety property). We do not test if something
good will eventually happen (referred to as a liveness property). Hence,
we use the prefix test (details to be explained later).

## Static Verification

Static = compile-time

Check that for all possible program runs, the resource usage policy
holds.

Approximate program in terms of regular expressions.

Apply language containment for static verification.

# Dynamic resource usage verification in Go (via an EDSL)

Step 1. Formalize a simple resource usage language (in Go).

Step 2. Define the set of events we are interested in.

Step 3. Specify resource usage policies in terms of regular expressions.

Step 4. Enforce that any program run satisfies a resource usage policy
specified in terms of a regular expression (online or offline).

**DSL versus GPL**

We will embed our (domain-specific) resource usage language in the
(general-purpose) Go language.

GPL = general-purpose language (C, Java, Kotlin, Haskell, Go, Python,
...)

DSL = domain-specific language (SQL, Latex, bash, perl, ...)

DSLs are usually *external* languages. Come with their own syntax,
interpreter, compiler, ... ("eco-system").

Internal DSLs (a.k.a. embedded DSLs aka APIs aka Frameworks. The short
form of embedded DSL is EDSL.), make use of the host language (GPL) to
provide similar functionality like a external DSL. Often easier to
evolve and adapt. Can reuse existing eco-system. Might to be not as
optimized as external DSL. Other issues, domain-specific error handling
etc.

# Step 1: Simple resource usage language (RUL) as an EDSL in GO

We embed our resource usage language (RUL) in Go. We make use of Go
interfaces to describe the (type) behavior of resource usage primitives.

    type RU interface {
        open()
        close()
        write(int)
        read() int
    }

We only embed the main primitive functions of a resource usage EDSL.
Further language constructs such as if-then-else etc are 'borrowed' from
Go.

Here are some resource usage examples.

    func example1(x RU) {

        x.open()
        x.write(2)
        for i := 0; i < 10; i++ {
            x.read()
        }
        x.close()

    }

    func example2(x RU) {

        x.open()
        for i := 0; i < 3; i++ {
            y := x.read()
            x.write(y + 1)
        }
        x.close()

    }

Points to note:

`RU` is the type of the interface. A value of type `RU` represents an
object on which the resource usage primitives can operate. Like in
Java/C++, Go uses the method calling convention, e.g. `x.open()` to call
method `open` on `x`.

In Go speak, the object on which the method operates is called
*receiver*. Methods can be defined for various types of receivers. We
consider such definitions shortly.

As already mentioned, conditional statements and control structures
(loops, functions), variables etc are represented in terms of native Go.

## RUL instances

### Standard I/O

We consider a concrete instance of RUL where resource usage primitives
are mapped to standard I/O functions.

    type IO struct{}

    func (x IO) open()  {} // nothing to be done in case of standard I/O
    func (x IO) close() {} // nothing to be done in case of standard I/O
    func (x IO) write(y int) {
        fmt.Printf("%d", y)
    }
    func (x IO) read() int {
        var y int
        fmt.Scanf("%d", &y)
        return y
    }

`IO` represents a dummy type where values of that type are 'empty'. We
then provide overloaded method definitions for `IO`.

In Go overloaded method definitions can be defined separately (unlike
Java/C++ where method definitions are always part of the class/interface
declaration). Each of the methods in the `RU` interface is defined for
`IO`. Hence, `IO` satisfies the `RU` interface.

    func testIO() {
        var io IO

        example1(io)

        example2(io)

    }

### O without user input

We consider another instance where the user input will be simulated.
This is useful for running automated tests.

    type O struct{ i int }

    func mkO() O {
        return O{1}
    }

    // Pointer receiver as we increment the 'read' values.
    func (x *O) open()  {}
    func (x *O) close() {}
    func (x *O) write(y int) {
        fmt.Printf("%d", y)
    }
    func (x *O) read() int {
        (*x).i++
        return (*x).i
    }

Points to note:

The receiver on which the above methods operate is a pointer. This is
referred to as a *pointer receiver* in Go.

The reason for using a pointer (receiver) is that we wish to increment
the counter variable without having to return the updated counter (so we
effectively employ call-by-reference).

    func testO() {

        o := mkO()
        p := &o

        example1(p)

        example2(p)

    }

# Step 2: Events

During program execution, an *event* represents a particular
point/behavior we are interested.

In our case, we are interested in resource usage primitives such as
close etc. For each of these primitives we introduce a corresponding
event.

    // Events:
    // Open | Close | Write | Read
    // Special event DONE to indicate we're done with tracing.

    type Kind int

    const (
        DONE  Kind = 0
        Open  Kind = 1
        Close Kind = 2
        Write Kind = 3
        Read  Kind = 4
    )

    type Event struct {
        kind Kind
    }

    func mkEvt(k Kind) Event {
        return Event{kind: k}
    }

    func showEvt(e Event) string {
        var s string
        switch {
        case e.kind == DONE:
            s = "DONE"
        case e.kind == Open:
            s = "O"
        case e.kind == Close:
            s = "C"
        case e.kind == Write:
            s = "W"
        case e.kind == Read:
            s = "R"
        }
        return s
    }

    func printEvt(e Event) {
        fmt.Printf("\n %s", showEvt(e))
    }

# Step 3: Policy as regular expressions

Below we define regular expressions in Go where the alphabet equals the
set of events `{Open, Close, Write, Read}`.

    // Resource usage policy.
    // We assume that the proper usage of resource usages are specified
    // in terms of regular expressions.

    // Regular expressions in Go:

    // Behavior described in terms of an interface.

    type RE interface {
        deriv(Event) RE
        nullable() bool
        empty() bool
    }

    // The structure (syntax) of regular expression structure is as follows.

    type Eps int
    type Phi int
    type Kleene [1]RE
    type Alt [2]RE
    type Seq [2]RE

    // Sample policy.
    func policy1() RE {
        o := mkEvt(Open)
        c := mkEvt(Close)
        w := mkEvt(Write)
        r := mkEvt(Read)
        // (o w (w+r)* c)*

        return star(seq(o, seq(w, seq(star(alt(w, r)), c))))

    }

Some (regular expression) functionality we need later. No need to
understand all the technical details. If you are interested, check out
[derivatives](https://en.wikipedia.org/wiki/Brzozowski_derivative) and
[left
quotient](https://en.wikipedia.org/wiki/Quotient_of_a_formal_language).

    // Defining the behavior.

    func eps() RE {
        return Eps(1)
    }

    func phi() RE {
        return Phi(1)
    }

    func evt(k Kind) RE {
        return mkEvt(k)
    }

    func alt(l RE, r RE) RE {
        return (Alt)([2]RE{l, r})
    }

    func seq(l RE, r RE) RE {
        return (Seq)([2]RE{l, r})
    }

    func star(x RE) RE {
        return (Kleene)([1]RE{x})
    }

    // Instances.

    // test if regex is nullable (contains the empty word)
    func (r Eps) nullable() bool {
        return true
    }
    func (r Phi) nullable() bool {
        return false
    }
    func (r Event) nullable() bool {
        return false
    }

    func (r Kleene) nullable() bool {
        return true
    }
    func (r Alt) nullable() bool {
        return r[0].nullable() || r[1].nullable()
    }
    func (r Seq) nullable() bool {
        return r[0].nullable() && r[1].nullable()
    }

    // test if regex is empty (denotes the empty language)
    func (r Eps) empty() bool {
        return false
    }
    func (r Phi) empty() bool {
        return true
    }
    func (r Event) empty() bool {
        return false
    }

    func (r Kleene) empty() bool {
        return false
    }
    func (r Alt) empty() bool {
        return r[0].empty() && r[1].empty()
    }
    func (r Seq) empty() bool {
        return r[0].empty() || r[1].empty()
    }

    // Build the derivative wrt x
    func (r Eps) deriv(x Event) RE {
        return Phi(1)
    }
    func (r Phi) deriv(x Event) RE {
        return Phi(1)
    }

    func (r Event) deriv(x Event) RE {
        if r.kind == x.kind {
            return Eps(1)
        } else {
            return Phi(1)
        }
    }

    func (r Kleene) deriv(x Event) RE {
        return (Seq)([2]RE{r[0].deriv(x), r})
    }

    func (r Alt) deriv(x Event) RE {
        return (Alt)([2]RE{r[0].deriv(x), r[1].deriv(x)})
    }

    func (r Seq) deriv(x Event) RE {
        if r[0].nullable() {
            return (Alt)([2]RE{(Seq)([2]RE{r[0].deriv(x), r[1]}), r[1].deriv(x)})
        } else {
            return (Seq)([2]RE{r[0].deriv(x), r[1]})
        }
    }

# Step 4a: Online dynamic resource usage verification via regular expressions

Approach:

-   Instrument the program to obtain the events we are interested in.

-   As we consider an *online* analysis, we immediately process each
    event.

## Processing of an event and prefix test

-   We make use of regular expressions to represent the states of a FSA.

-   Via the `deriv` method we compute the successor state after
    consuming an event.

-   An empty regular expression denotes the empty language. The empty
    language represents the failure state.

Thus, processing (prefix test) is implemented as follows:

    func prefixTest(r *RE, x Event) bool {
        *r = (*r).deriv(x)
        b := (*r).empty()
        if b {
            fmt.Printf("\n resource usage policy violation")
        }
        return !b
    }

We use call-by-reference (pointer argument) so the updates are visible
outside the function. The `deriv` method builds the successor state and
`empty` checks if we have reached a failure state.

## Online instrumentation

Instrumentation has the following effect: Along the program we run
another program that derives the stream of events to be processed.

In our case, we simply need to define an appropriate instance of the
`RU` interface.

    type Online struct {
        rul   RU
        regex *RE
    }

    // We trace events *after* the actual operation has been executed.

    func (x Online) open() {
        x.rul.open()
        prefixTest(x.regex, mkEvt(Open))
    }

    func (x Online) close() {
        x.rul.close()
        prefixTest(x.regex, mkEvt(Close))
    }

    func (x Online) write(i int) {
        x.rul.write(i)
        prefixTest(x.regex, mkEvt(Write))
    }

    func (x Online) read() int {
        i := x.rul.read()
        prefixTest(x.regex, mkEvt(Read))
        return i
    }

Some helper function to initialize our online dynamic analysis.

    func initOnlineTracer(rul RU, r RE) Online {
        return Online{rul, &r}
    }

`rul` represents the actual semantics of the program and
`Online{rul, &r}` is a wrapper to carry out the online analysis.

Our two running examples.

    func testOnlineTracer() {
        fmt.Printf("\n")

        regex := policy1()
        o := mkO()
        p := &o
        {

            fmt.Printf("\n Online Example 1 \n")
            online := initOnlineTracer(p, regex)
            example1(online)
        }

        {
            o := mkO()
            p := &o
            fmt.Printf("\n Online Example 2 \n")
            online := initOnlineTracer(p, regex)
            example2(online)
        }

    }

# Step 4b: Offline dynamic resource usage verification via regular expressions

Approach:

-   Instrument the program to obtain the events we are interested in.

-   As we consider an *offline* analysis, we store all events for
    processing later.

## Offline trace processing

We assume the complete trace is available in terms of [Go's
list](https://golang.org/pkg/container/list/) data type. We iterate over
all events in the trace and apply function `prefixTest` to check if
after consuming the current event the policy is violated or not.

    func prefixTestTrace(r RE, trace *list.List) bool {
        b := true
        for e := trace.Front(); e != nil; e = e.Next() {
            b = b && prefixTest(&r, e.Value.(Event))
        }
        return b
    }

## Offline instrumentation and tracing

In the offline setting, we collect all events (while executing the
program) and store them in a trace for later processing.

After each primitive, we could add each corresponding event to a trace
(list of events). Here is a sketch.

    rul.open()
    addToTrace(mkEvt(Open))

That means, before we can continue executing the program we first need
to add the event to the trace. We might want to carry out this task
*asynchronously* (as much as possible) because we anyway process the
trace only after the program has been executed (offline).

Hence, we make use of a log channel to which we sent all events that
arise during program execution. Some additional *tracer* thread picks up
these events and builds the trace of all events that arise while running
the program.

    type Offline struct {
        rul     RU
        logChan chan Event
    }

    func (x Offline) open() {
        x.rul.open()
        x.logChan <- mkEvt(Open)
    }

    func (x Offline) close() {
        x.rul.close()
        x.logChan <- mkEvt(Close)
    }

    func (x Offline) write(i int) {
        x.rul.write(i)
        x.logChan <- mkEvt(Write)
    }

    func (x Offline) read() int {
        i := x.rul.read()
        x.logChan <- mkEvt(Read)
        return i
    }

### Tracer thread: Collection of events (potentially buggy)

We use [Go's list](https://golang.org/pkg/container/list/) data type to
collect events. Below, we make use of an asynchronous channel and some
helper (tracer) thread to collect all events that are issued while
running the program.

    func initOfflineTracerBuggy(rul RU, kill chan int) (Offline, *list.List) {
        o := Offline{rul, make(chan Event, 10)}
        trace := list.New()

        // Tracer thread to collect all issued events and store them in the trace.
        go func() {
            b := true
            for b {
                select {
                case x := <-o.logChan:
                    trace.PushBack(x)
                case <-kill:
                    b = false
                }
            }

        }()

        return o, trace
    }

Via the `kill` channel we terminate the collection of events. The kill
message will be sent once the program is fully executed.

Here is an example.

        o := mkO()                                           // L1
        p := &o                                              // L2
        kill := make(chan int)                               // L3
        offline, trace := initOfflineTracerBuggy(p, kill)    // L4
        example1(offline)                                    // L5
        kill <- 1                                            // L6
        prefixTestTrace(policy1(), trace)                    // L7

L1-L3: Setup of the RUL instance and auxiliary kill channel.

L4: Setup of the tracer thread.

L5: Run the instrumented program.

L6: Tell tracer thread, we are done.

L7: Processing of trace (offline).

There is an issue that will be discussed in more detail in some upcoming
exercises.

### Tracer thread: Collection of events via `DONE`

Here is another solution where we make use of the `DONE` event to
indicate that we are done with tracing.

    func initOfflineTracer(rul RU, doneConfirm chan int) (Offline, *list.List) {
        o := Offline{rul, make(chan Event, 5)}
        trace := list.New()

        // Tracer thread to collect all issued events and store them in the trace.
        // Check for done evt and then confirm we're done.
        go func() {
            b := true
            for b {
                x := <-o.logChan
                trace.PushBack(x)
                if x.kind == DONE {
                    b = false
                }

            }
            doneConfirm <- 1
        }()

        return o, trace
    }

There is no kill message. Instead, we assume that after program
execution we sent the `DONE` message and the tracer thread replies via
the `doneConfirm` channel that tracing is completed.

Here is a method that sends out the `DONE` message.

    func (x Offline) done() {
        x.logChan <- mkEvt(DONE)
    }

Below you can find a complete example.

        o := mkO()
        p := &o
        doneConfirm := make(chan int)
        offline, trace := initOfflineTracer(p, doneConfirm)
        example1(offline)
        offline.done()
        <-doneConfirm
        // Get rid of DONE.
        el := trace.Back()
        trace.Remove(el)
        prefixTestTrace(policy1(), trace)   

Compared to the "kill" version, this version is more robust (to be
discussed in some upcoming exercises)

# Complete source for online/offline run-time verification

    package main

    import "fmt"
    import "container/list"

    /*

    Dynamic resource usage verification.

     1. Embedding of simple resource usage language in Go. We call this language RUL (resource usage language).
    2. Embedding of regular expressions in Go.
    3. Instrumentation, tracing and (dynamic) verification of resource usage events.


    */

    // Abstract description of resource usage primitives in terms of Go interfaces.
    // Represents an embedding of RUL in Go.
    // As we only embed primitives we call the interface RU.

    type RU interface {
        open()
        close()
        write(int)
        read() int
    }

    // Terminology:
    // DSL = Domain-specific language
    // Internal DSL = DSL that is embedded in some other language
    //            (e.g. our example here, DB interface/framework in Java, ...)
    // External DSL = DSL that comes with is own compiler, ... (e.g. latex, SQL, ...)
    //
    // Internal DSL sometimes also called embedded DSLs (EDSLs)

    // Examples
    // NOTE:
    // We only embed the main primitive functions of a resource usage DSL.
    // Further language constructs such as if-then-else etc are 'borrowed' from Go.

    func example1(x RU) {

        x.open()
        x.write(2)
        for i := 0; i < 3; i++ {
            x.read()
        }
        x.close()

    }

    func example2(x RU) {

        x.open()
        for i := 0; i < 3; i++ {
            y := x.read()
            x.write(y + 1)
        }
        x.close()

    }

    // We consider some possible instances of RUL.
    // In Go, the methods part of an interface operate on a receiver.
    // In Java/C++ you would call the receiver the object on which the method is called.
    // Like in Java/C++, Go methods can be overloaded (operated on distinct receivers)
    // but in Go the definition of methods can be defined separately
    // (unlike Java/C++ where method definitions are always part of the class/interface declaration).

    // (Standard) IO instance

    type IO struct{}

    func (x IO) open()  {} // nothing to be done in case of standard I/O
    func (x IO) close() {} // nothing to be done in case of standard I/O
    func (x IO) write(y int) {
        fmt.Printf("%d", y)
    }
    func (x IO) read() int {
        var y int
        fmt.Scanf("%d", &y)
        return y
    }

    // Variant without any user input (useful for running automated tests).

    type O struct{ i int }

    func mkO() O {
        return O{1}
    }

    // Pointer receiver as we increment the 'read' values.
    func (x *O) open()  {}
    func (x *O) close() {}
    func (x *O) write(y int) {
        fmt.Printf("%d", y)
    }
    func (x *O) read() int {
        (*x).i++
        return (*x).i
    }

    func testIO() {
        var io IO

        example1(io)

        example2(io)

    }

    func testO() {

        o := mkO()
        p := &o

        example1(p)

        example2(p)

    }

    // Events:
    // Open | Close | Write | Read
    // Special event DONE to indicate we're done with tracing.

    type Kind int

    const (
        DONE  Kind = 0
        Open  Kind = 1
        Close Kind = 2
        Write Kind = 3
        Read  Kind = 4
    )

    type Event struct {
        kind Kind
    }

    func mkEvt(k Kind) Event {
        return Event{kind: k}
    }

    func showEvt(e Event) string {
        var s string
        switch {
        case e.kind == DONE:
            s = "DONE"
        case e.kind == Open:
            s = "O"
        case e.kind == Close:
            s = "C"
        case e.kind == Write:
            s = "W"
        case e.kind == Read:
            s = "R"
        }
        return s
    }

    func printEvt(e Event) {
        fmt.Printf("\n %s", showEvt(e))
    }

    // Resource usage policy.
    // We assume that the proper usage of resource usages are specified
    // in terms of regular expressions.

    // Regular expressions in Go:

    // Behavior described in terms of an interface.

    type RE interface {
        deriv(Event) RE
        nullable() bool
        empty() bool
    }

    // The structure (syntax) of regular expression structure is as follows.

    type Eps int
    type Phi int
    type Kleene [1]RE
    type Alt [2]RE
    type Seq [2]RE

    // Sample policy.
    func policy1() RE {
        o := mkEvt(Open)
        c := mkEvt(Close)
        w := mkEvt(Write)
        r := mkEvt(Read)
        // (o w (w+r)* c)*

        return star(seq(o, seq(w, seq(star(alt(w, r)), c))))

    }

    // Defining the behavior.

    func eps() RE {
        return Eps(1)
    }

    func phi() RE {
        return Phi(1)
    }

    func evt(k Kind) RE {
        return mkEvt(k)
    }

    func alt(l RE, r RE) RE {
        return (Alt)([2]RE{l, r})
    }

    func seq(l RE, r RE) RE {
        return (Seq)([2]RE{l, r})
    }

    func star(x RE) RE {
        return (Kleene)([1]RE{x})
    }

    // Instances.

    // test if regex is nullable (contains the empty word)
    func (r Eps) nullable() bool {
        return true
    }
    func (r Phi) nullable() bool {
        return false
    }
    func (r Event) nullable() bool {
        return false
    }

    func (r Kleene) nullable() bool {
        return true
    }
    func (r Alt) nullable() bool {
        return r[0].nullable() || r[1].nullable()
    }
    func (r Seq) nullable() bool {
        return r[0].nullable() && r[1].nullable()
    }

    // test if regex is empty (denotes the empty language)
    func (r Eps) empty() bool {
        return false
    }
    func (r Phi) empty() bool {
        return true
    }
    func (r Event) empty() bool {
        return false
    }

    func (r Kleene) empty() bool {
        return false
    }
    func (r Alt) empty() bool {
        return r[0].empty() && r[1].empty()
    }
    func (r Seq) empty() bool {
        return r[0].empty() || r[1].empty()
    }

    // Build the derivative wrt x
    func (r Eps) deriv(x Event) RE {
        return Phi(1)
    }
    func (r Phi) deriv(x Event) RE {
        return Phi(1)
    }

    func (r Event) deriv(x Event) RE {
        if r.kind == x.kind {
            return Eps(1)
        } else {
            return Phi(1)
        }
    }

    func (r Kleene) deriv(x Event) RE {
        return (Seq)([2]RE{r[0].deriv(x), r})
    }

    func (r Alt) deriv(x Event) RE {
        return (Alt)([2]RE{r[0].deriv(x), r[1].deriv(x)})
    }

    func (r Seq) deriv(x Event) RE {
        if r[0].nullable() {
            return (Alt)([2]RE{(Seq)([2]RE{r[0].deriv(x), r[1]}), r[1].deriv(x)})
        } else {
            return (Seq)([2]RE{r[0].deriv(x), r[1]})
        }
    }

    // Process an event and check if the resource usage policy
    // specified as a regular expression is violated.
    // Yields true if policy is not violated.
    // 1. The regular expressions represents the current state of the policy.
    // 2. We process the advance by building the derivative.
    // 3. We use call-by-reference (pointer argument) so the updates are visible outside the function.
    // 4. We check if the policy is violated by testing if the regular expression denotes the empty language.
    func prefixTest(r *RE, x Event) bool {
        *r = (*r).deriv(x)
        b := (*r).empty()
        if b {
            fmt.Printf("\n resource usage policy violation")
        }
        return !b
    }

    // Offline analysis:
    // Run the program and generate a trace.
    // This is called 'offline' because
    // (a) the trace could be stored for some later analysis, or
    // (b) we could immediately process the events in the trace.

    // Instrument RUL as follows to generate a trace.

    type Offline struct {
        rul     RU
        logChan chan Event
    }

    // We trace events *after* the actual operation has been executed.

    func (x Offline) open() {
        x.rul.open()
        x.logChan <- mkEvt(Open)
    }

    func (x Offline) close() {
        x.rul.close()
        x.logChan <- mkEvt(Close)
    }

    func (x Offline) write(i int) {
        x.rul.write(i)
        x.logChan <- mkEvt(Write)
    }

    func (x Offline) read() int {
        i := x.rul.read()
        x.logChan <- mkEvt(Read)
        return i
    }

    func (x Offline) done() {
        x.logChan <- mkEvt(DONE)
    }

    func initOfflineTracer(rul RU, doneConfirm chan int) (Offline, *list.List) {
        o := Offline{rul, make(chan Event, 5)}
        trace := list.New()

        // Tracer thread to collect all issued events and store them in the trace.
        // Check for done evt and then confirm we're done.
        go func() {
            b := true
            for b {
                x := <-o.logChan
                trace.PushBack(x)
                if x.kind == DONE {
                    b = false
                }

            }
            doneConfirm <- 1
        }()

        return o, trace
    }

    // Buggy.
    // Events are sent (possibly asynchronously) and therefore
    // the kill msg will be sent and received while there are still
    // events to be processed.
    //
    // Assuming that we use a synchronous log channel
    //          o := Offline{rul, make(chan Event)}
    // the kill msg won't be able to 'overtake' any of the be stored events.
    func initOfflineTracerBuggy(rul RU, kill chan int) (Offline, *list.List) {
        o := Offline{rul, make(chan Event, 10)}
        trace := list.New()

        // Tracer thread to collect all issued events and store them in the trace.
        go func() {
            b := true
            for b {
                select {
                case x := <-o.logChan:
                    trace.PushBack(x)
                case <-kill:
                    b = false
                }
            }

        }()

        return o, trace
    }

    func printTrace(trace *list.List) {
        for e := trace.Front(); e != nil; e = e.Next() {
            printEvt(e.Value.(Event))
        }
    }

    // We stop (by using short-circuit evaluation) once we encounter policy violation.
    func prefixTestTrace(r RE, trace *list.List) bool {
        b := true
        for e := trace.Front(); e != nil; e = e.Next() {
            b = b && prefixTest(&r, e.Value.(Event))
        }
        return b
    }

    func testOffline() {
        o := mkO()
        p := &o

        {
            fmt.Printf("\n Offline Example 1 \n")
            doneConfirm := make(chan int)
            offline, trace := initOfflineTracer(p, doneConfirm)
            example1(offline)
            offline.done()
            <-doneConfirm
            // Get rid of DONE.
            el := trace.Back()
            trace.Remove(el)

            // Print entire trace and check.
            printTrace(trace)
            prefixTestTrace(policy1(), trace)
        }

        {
            fmt.Printf("\n Offline Example 2 \n")
            doneConfirm := make(chan int)
            offline, trace := initOfflineTracer(p, doneConfirm)
            example2(offline)
            offline.done()
            <-doneConfirm
            // Get rid of DONE.
            el := trace.Back()
            trace.Remove(el)

            // Print entire trace and check.
            printTrace(trace)
            prefixTestTrace(policy1(), trace)
        }
    }

    func testOfflineBuggy() {
        o := mkO()
        p := &o

        {
            fmt.Printf("\n Offline Example 1 \n")
            kill := make(chan int)
            offline, trace := initOfflineTracerBuggy(p, kill)
            example1(offline)
            kill <- 1
            printTrace(trace)
            prefixTestTrace(policy1(), trace)
        }

        {
            fmt.Printf("\n Offline Example 2 \n")
            kill := make(chan int)
            offline, trace := initOfflineTracerBuggy(p, kill)
            example2(offline)
            kill <- 1
            printTrace(trace)
            prefixTestTrace(policy1(), trace)
        }
    }

    // Online analysis.
    // Immediate processing of events where
    // we make use of regular expressions to validate the trace.
    // We refer to this logger as the regular expression logger.

    // Instrument RUL to issue for each primitive operation an event and
    // process this event immediately.

    type Online struct {
        rul   RU
        regex *RE
    }

    // We trace events *after* the actual operation has been executed.

    func (x Online) open() {
        x.rul.open()
        prefixTest(x.regex, mkEvt(Open))
    }

    func (x Online) close() {
        x.rul.close()
        prefixTest(x.regex, mkEvt(Close))
    }

    func (x Online) write(i int) {
        x.rul.write(i)
        prefixTest(x.regex, mkEvt(Write))
    }

    func (x Online) read() int {
        i := x.rul.read()
        prefixTest(x.regex, mkEvt(Read))
        return i
    }

    func initOnlineTracer(rul RU, r RE) Online {
        return Online{rul, &r}
    }

    func testOnlineTracer() {
        fmt.Printf("\n")

        regex := policy1()
        o := mkO()
        p := &o
        {

            fmt.Printf("\n Online Example 1 \n")
            online := initOnlineTracer(p, regex)
            example1(online)
        }

        {
            o := mkO()
            p := &o
            fmt.Printf("\n Online Example 2 \n")
            online := initOnlineTracer(p, regex)
            example2(online)
        }

    }

    // Main functions with some tests. Add your own!
    func main() {
        // testIO()
        // testO()

        testOffline()

        // testOfflineBuggy()

        // testOnlineTracer()
    }

# Exercises (Online/Offline run-time verification)

## Online resource usage verification

### Exercise: Play around

Try out the online method for `example2` and `policy1`.

Simply execute the `testOnlineTracer` that comes with the source code
provided for you.

*What do you notice?*

For `example2` we encounter the event sequence `O R W ...` but `policy1`
demands that there must be a `W` after `O`.

Hence, the policy is violated.

### Exercise: Catch policy violations by stopping the program

*Could we catch such violations?*

The issue is the following. We wish to stop the program *before* the
policy will be violated. How can this be achieved?

Currently, events are issued *after* the corresponding operation has
been executed. Then, each event is checked against the current state the
policy is in.

To catch violations before they actually takes place, the following
changes are required.

1.  Issue events *before* the corresponding operation.

2.  Check if the event would violated the policy.

3.  Only if there will be no violation, execute the corresponding
    operation.

4.  Otherwise, stop the program.

### Exercise: Catch policy violations by skipping "faulty" operations

Instead of abruptly stopping the program, an alternative "catch policy
violation" method is to simply skip "faulty" operations.

Recall `example2` where we encounter the event sequence `O R W ...` but
`policy1` does not accept `R` after `O`.

The alternative method would be to simply skip the read operation.

How can this alternative method implemented?

The read operation yields a value and this value will be used in the
running program. If we skip the read, what value shall we provide?

## Offline resource usage verification

### Exercise: Collection of events (potentially buggy)

We consider the variant `initOfflineTracerBuggy`.

This variant has a serious issue. Try out `testOfflineBuggy`. What do
you observe?

### Exercise: Collection of events via `DONE`

The above mentioned issue goes away. Why?

Consider (parts of) the definition of `initOfflineTracer`.

    initOfflineTracer(rul RU, doneConfirm chan int) (Offline, *list.List) {
         o := Offline{rul, make(chan Event, 5)}
         ...
    }    

What changes if we adapt the buffer size? Say, we use 2 instead of 5, 20
instead of 5?

Depending on the number of events issue and how quick the tracer thread
fetches events, the buffer might become full.

What if we use synchronous channel.

         o := Offline{rul, make(chan Event)}

In the instrumentation, we then execute all sends to the log channel in
their own thread.

    // Another variant (we only consider open)
    func (x Offline) open() {
        x.rul.open()
        go func() {
          x.logChan <- mkEvt(Open)
        }()
    }

Will this work?

## Sample solutions

### Exercise: Collection of events (potentially buggy)

The issue is as follows:

1.  The program has been executed.

2.  We sent the kill message.

3.  But the tracer thread is still collecting events (because events are
    sent asynchronously to the tracer thread).

4.  Hence, the tracer thread stops prematurely!

We could fix the problem by using a synchronous log channel instead
(this enforces obviously a tighter synchronization between the running
program and the tracer thread).

### Exercise: Collection of events via `DONE`

Consider the suggested alternative.

    // Another variant (we only consider open)
    func (x Offline) open() {
        x.rul.open()
        go func() {
          x.logChan <- mkEvt(Open)
        }()
    }

There is a serious issue.

I1: There is no guarantee that the order among events received by the
tracer thread corresponds to the actual program order!

I2: Furthermore, the `DONE` event might overtake some of the other
events. Hence, the tracer thread might stop prematurely.

Aside: For sent operations performed on an asynchronous channel we have
the following guarantee. Suppose we have two sent operations (say s1 and
s2) that happen in sequence. Say, s1 happens before s2. Suppose r1 is
the corresponding receive for s1 and r2 is the corresponding receive for
s2. Then, we have the guarantee that r1 happens before r2.

Hence, I1 and I2 are not an issue for our current method.

How to fix the alternative method (and issues I1 and I2)?

We could attach a program counter to each event. This will fix I1. We
might have to (re)shuffle the trace to ensure that all program counter
of events are in increasing order.

The tracer thread needs to keep track of the number of events received.
Once the tracer thread receives the `DONE` event (plus the program
counter), based on the `DONE` counter and the number of events received
so far, the tracer thread can decide if it needs to continue or can
stop.

# Static resource usage verification

## Motivation - Static type checking

Consider conditional expressions in the C programming language.

    int x;
    float f;

    f = x > 1? 1.0 : 3.0;

C applies static type checking.

1.  The first operand of a conditional expression must yield a Boolean
    value.
2.  The second and third operand must be of matching type.

This type checking rule is enforced by the compiler to guarantee that
*nothing goes wrong* at run-time.

Consider the following example.

    struct {
      float x;
    } position;

    f() {
     position p;
     int y = 1;
     float f;

     f = y >= 1 ? 1.0 : p;
    }

The compiler rejects the above program because `1.0` and `p` are not of
matching type.

Note: Nothing goes wrong at run-time!

### Short summary

If type checking succeeds we can rule out certain run-time errors.

If type checking fails there might not be necessarily a problem at
run-time.

Static type checking performs an overapproximation of the program's
run-time behavior. For example, the type `bool` represents the set of
values `true` and `false`. This overapproximation allows type checking
to be carried statically and efficiently. On the other hand, due to the
overapproximation, type checking fails where there is actually no
problem. This is referred to as a *false positive*.

## Resource usage example

How to approximate the resource usage behavior?

    for b {

       if x > y {
          read;
       } else {
          write;
       }
    }

The above program may produce the following traces:

    1. read
    2. write
    3. read write     (write follows read)
    4. write read
    5. read read
    6. write write
    ...

Above represents a set of traces.

We make use of regular expressions to describe the set of traces that
result from executing resource usage programs.

The regular expression representing the resource usage behavior of a
program is derived from the program text at compile-time.

As we will see shortly, regular expressions represent an
(over)approximation of the program's resource usage behavior.

We write `p ==> r` to denote the approximation of program `p` via
regular expression `r`. Approximation is performed by observing the
structure of programs.

## Regular expressions

We assume the following set of regular expressions.

    Alphabet Sigma = { open, close, write, read }


    r, s denote regular expressions

    r . s denotes concatenation

    r + s denotes alternatives

    r* denotes Kleene star

    epsilon denotes the empty word

## Approximation

We write `p ==> r` to denote the approximation of program `p` via
regular expression `r`. Approximation is performed by observing the
structure of programs.

    open     ==>     open

    close    ==>     close

    write    ==>     write

    read     ==>     read

    Point to note:
    "open" on the left-hand side of "==>" refers to the operation.
    "open" on the right-hand side of "==>" refers to the event that is issued when executing this operation.


    p ; q    ==>     r . s
    where
    p  ==>  r
    q  ==>  s


    if b { p } else { q }  ==> r + s
    where
    p  ==>  r
    q  ==>  s

    for b { p }   ==>  r*
    where
    p  ==>  r

Examples using pseudo Go code.

Example 1.

    open;
    if (...) { read } else { write }

Its approximation is as follows.

    open . (read + write)

Example 2.

    open;
    for (...) {
    x = 1
    if (x >= 1) { read } else { write }
    };
    close

Its approximation is as follows.

    open . (read + write)* . close

## Static verification via a form of language containment

1.  Suppose `p ==> s` and `r` describes the resource usage policy.

2.  Check that `s` is prefix-closed with respect to `r`: For any word
    `w in L(s)` there exists some word `v` such that `w . v in L(r)`.

Why prefix-closed? Because programs may not terminate and we only
consider safety properties (and not liveness properties here). For such
technical details, check the mentioned APLAS'03 paper below.

The above check is decidable. Standard language containment is too
strong as we only want to check if some error state is reachable.

For property

    open . (read* . (write . write* + epsilon)) . close

we find that the approximation of Example 1 satisfies this property (is
prefix-closed) whereas the approximation of Example 2 violates this
property.

Recall the approximation of Example 2.

    open . (read + write)* . close

The above implies the word `open . read . write . read . close` which
clearly violates the property.

A closer inspection of Example 2 shows that the behavior
`open . read . write . read . close` is not reproducible in the actual
program. Hence, this is an example for a false positive.

For further details, see [Resource Usage Verification,
APLAS'03](https://www.researchgate.net/publication/221323167_Resource_Usage_Verification)

# Summary

Things we have seen.

-   Verification versus Validation

-   Static versus dynamic verification

-   Dynamic verification

    -   Does not guarantee correctness in general

    -   Main purpose is to find bugs

    -   Does not suffer from false positives

    -   But only applies to safety properties

    -   Safety properties guarantee that something bad will not happen
        (e.g. no read after write)

-   Static verification

    -   Guarantees correctness (if successful)

-   But suffers from false positives

-   Applies to safety and liveness properties

-   Liveness properties guarantee that something good will eventually
    happen (e.g. there will be some close operation following an open
    operation)
