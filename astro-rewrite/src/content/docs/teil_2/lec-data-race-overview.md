---
title: Dynamic data race prediction (Overview)
description: Martin Sulzmann
---



## Dynamic versus static analysis methods

Dynamic analysis:

-   Execute the program

-   Observe if there is any potential bad behavior based on this
    specific program run

Static analysis:

-   Predict all possible program runs without actually executing the
    program

Here we consider *dynamic* data race prediction:

-   Exectue the program

-   Record the events that took place in a trace

-   Analyze the trace to check if there is any potential bad behavior
    (in our case if there is a potential data race)

We restrict our attention to programs that make use of *acquire/release*
operations (aka lock/unlock).

## Motivating example

Consider the following Go program where we emulate acquire/release via a
buffered channel.

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
        x = 4 // P2
        acquire()
        release()

        time.Sleep(1 * 1e9)
        fmt.Printf("%d \n", x)

    }

We find a variable `x` that is *shared* by threads T1 and T2. Access to
variable `x` at location P2 is not protected by a lock. Hence, there is
a potential data race that involves the conflicting operations labeled
as P1 and P2.

## Program trace

Events are collected in a program **trace** where the trace is a linear
sequence of events and represents an interleaved execution of the
program.

By event we refer to program behavior/locations we are interested. For
the above example, we assume write events `w(x)` and acquire/release
events `acq(y)` and `rel(y)`. Each event is connected to one of the
operations we are interested in.

For each event we also record the thread from where the event results
from. As events are stored in a trace, each event can be identified by
its trace position. For better readability, we often use a tabular
notation for traces where we introduce for each thread a separate column
and the trace position can be identified via the row number.

Here is some trace that results from some program run.

    Trace A:

         T1          T2

    e1.   w(x)
    e2.   acq(y)
    e3.   rel(y)
    e4.               acq(y)
    e5.               w(x)
    e6.               rel(y)

The above trace tells us something about the specific program run we
consider. We find that first the operations in thread T1 are executed,
see trace positions 1-3, followed by execution of the operations in
thread T2, see trace positions 4-6.

What about the data race? Recall that by “looking” at the program text
we “guess” that there is a potential data race. However, based on the
observed program behavior represented by the above trace, there is no
data race as we explain in the following.

## Conflicting events and data race

A **data race** arises if two conflicting events appear right next to
each other in the trace. That means that both events can happen at the
same time. By **conflicting events** we refer to two read/write events
that result from different threads where at least one of the events is a
write event.

For the above trace, we find two conflicting events at trace positions 1
and 5. At position 1 we find `w(x)` from thread T1 and at position 5 we
find `w(x)` from thread T2. Both events *do not* appear right next to
each other in the trace. Hence, based on the above trace we cannot
conclude that there is a data race.

## Rerun of program versus reordering of trace

We could simply try and rerun our program. Suppose, for some program run
thread T2 executes before T1. The resulting trace is given below.

    Trace B:

         T1          T2
    e4.               acq(y)
    e5.               w(x)
    e6.               rel(y)
    e1.   w(x)
    e2.   acq(y)
    e3.   rel(y)

The same operations are executed. Hence, we encounter the same events
but in a different order due to a different schedule. To highlight this
point, we maintain the trace positions of the original trace (trace A).

What about the data race? There is still *no* data race present in the
above trace (B). Conflicting events, the writes in T1 and T2, do not
appear right next to each other in the trace.

Let’s try again and again, … Suppose, we encounter the following trace.

    Trace C:

         T1          T2
    e4.               acq(y)
    e5.               w(x)
    e1.   w(x)
    e6.               rel(y)
    e2.   acq(y)
    e3.   rel(y)

Like in case of trace B, thread T2 executes first. Unlike trace B, we
assume a program run where the write in thread T1 takes place a bit
earlier. The two writes appear right next to each other. This represents
a data race!

Instead of rerunning the program to obtain traces A, B and C, another
method is to consider valid trace reorderings that result from trace A.
Reordering of a trace means that we mix up the order among events such
that the resulting sequence of events still represents a sensible
execution sequence. Indeed, traces B and C are valid trace reorderings
of trace A.

## Valid trace reorderings

### Program order must be maintained

Consider the following reordering of the events in trace A.

    Trace D:

         T1          T2

    e2.   acq(y)
    e3.   rel(y)
    e4.               acq(y)
    e1.   w(x)
    e5.               w(x)
    e6.               rel(y)

It looks like as if we detected a data race. However, the above trace D
is not a *valid* reordering of trace A.

The **Program order Condition** is violated.

The **Program order Condition** states:

-   Let P be some trace and P’ be some reordering of P.

-   The releative order of events for specific thread in P and P’ must
    remain the same.

In the above, we take P=A and P’=D. However, the releative order of
events for thread T1 differs in A and D! In trace A, we find

    [e1, e2, e3]

and in trace D we find

    [e2, e3, e1]

where we use list notation to represent a sequence of events.

### Lock semantics must be maintained

Consider the following reordering of the events in trace A.

    Trace E:

         T1          T2

    e1.   w(x)
    e2.   acq(y)
    e4.               acq(y)
    e5.               w(x)
    e6.               rel(y)
    e3.   rel(y)

The above is not a valid reordering of trace A.

The **Lock Semantics Condition** is violated.

The **Lock Semantics Condition** states:

-   Let P be some trace and P’ be some reordering of P.

-   Between any two acquire events acq(y)\_i and acq(y)\_j where i&lt;j
    and i and j refer to the trace position, we must find some rel(y)\_k
    where i&lt;k&lt;j

In the above trace D, the Lock Semantics Condition is violated. We find
two acquire events acq(y) without any rel(y) event in between.

### Last writer must be maintained

To explain the **Last Writer Condition** we consider another example.

Consider the program

    func example3() {
        x := 1
        y := 1

        // Thread T1
        go func() {
            x = 2
            y = 2
        }()

        // Thread T2 = Main Thread
        if y == 2 {
            x = 3
        }

    }

We consider a specific execution run that yields the following trace.

    Trace F:

         T1            T2

    e1.   w(x)
    e2.   w(y)
    e3.                 r(y)
    e4.                 w(x)

Consider the following reordering of the events in trace F.

    Trace G:

          T1            T2

    e3.                 r(y)
    e4.                 w(x)
    e1.   w(x)
    e2.   w(y)

The two writes on x appear now right next to each other. It seems that
we encounter a data race. However, the reordering G is not valid because
the **Last Writer Condition** is violated.

The **Last Writer Condition** states:

-   Let P be some trace and P’ be some reordering of P.

-   Let r(x) be a read event in P’. Then, r(x) must have the same *last
    writer* in P’ as in P.

We define the *last writer* of read event r(x) as the write event w(x)
that appears before r(x) in the trace where there is no other write on x
in between w(x) and r(x).

In trace F, we find that e2 is the last writer of e3. In the reordering
G, e3 has no last writer. Hence, the Last Writer Condition is violated.

## Summary and outlook

The above example shows us that detection of a data race can be
challenging. We need to find the *right* trace and program run. We can
hope to rerun the program over and over again to encounter such a trace
but this is clearly very time consuming and likely we often encounter
the same (similar) traces again. Finding a devious schedule under which
the data race manifest itself can be tough to find.

What to do? We consider a specific program run and the trace that
results from this run. Two conflicting events may not appear in the
trace right next to each other. However, we may be able to predict that
there is some trace reordering under which the two conflicting events
appear right next to each other (in the reordered trace). This approach
is commonly referred to as **dynamic data race prediction**.

**Exhaustive** predictive methods attempt to identify as many as
possible (all!) reorderings. Exhaustive methods often do not scale to
real-world settings because program runs and the resulting traces may be
large and considering all possible reorderings generally leads to an
exponential blow up.

Here, we consider **efficient** predictive methods. By efficient we mean
a run-time that is linear in terms of the size of the trace. Because we
favor efficiency over being exhaustive, we may compromise completeness
and soundness.

**Complete** means that all valid reorderings that exhibit some race can
be predicted. If incomplete, we refer to any not reported race as a
**false negative**.

**Sound** means that races reported can be observed via some appropriate
reordering of the trace. If unsound, we refer to wrongly a classified
race as a **false positive**.

Specifically, we consider two popular, efficient dynamic data race
prediction methods:

-   Happens-before

-   Lockset

As we will see later, the Lockset method is unsound whereas the
Happens-before method is incomplete.
