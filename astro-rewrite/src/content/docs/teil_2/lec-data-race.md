---
title: Dynamic data race prediction
description: Martin Sulzmann
---



## Overview

We consider verification methods in the context of concurrently
executing programs that make use of multiple threads, shared reads and
writes, and acquire/release (lock/unlock) operations to protect critical
sections. Specifically, we are interested in data races. A *data race*
arises if two unprotected, conflicting read/write operations from
different threads happen at the same time.

We give an introduction to dynamic data race prediction by reviewing two
popular methods:

-   Establishing a
    [Lamport](https://en.wikipedia.org/wiki/Leslie_Lamport) style
    [happens-before](https://en.wikipedia.org/wiki/Happened-before)
    relation.

-   Computing the lockset.

Much of the material below is based on [Efficient, Near Complete and
Often Sound Hybrid Dynamic Data Race Prediction (extended
version)](https://arxiv.org/abs/2004.06969).

## Motivating examples

Detection of data races via traditional run-time testing methods where
we simply run the program and observe its behavior can be tricky. Due to
the highly non-deterministic behavior of concurrent programs, a data
race may only arise under a specific schedule. Even if we are able to
force the program to follow a specific schedule, the two conflicting
events many not not happen at the same time.

Consider the following Go program. The pair of functions acquire/release
corresponds to lock/unlock. We simply prefer the names acquire/release.
We encode acquire/release in terms of a buffered channel (Go supports
locks natively).

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

How could a dynamic analysis detect that there is a data race? We just
let the program run and during program execution we record the
**events** that took place. Events are collected in a program **trace**
where the trace is a linear sequence of events and represents an
interleaved execution of the program.

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

    1.   w(x)
    2.   acq(y)
    3.   rel(y)
    4.               acq(y)
    5.               w(x)
    6.               rel(y)

The above trace tells us something about the specific program run we
consider. We find that first the operations in thread T1 are executed,
see trace positions 1-3, followed by execution of the operations in
thread T2, see trace positions 4-6.

What about the data race? Recall that by "looking" at the program text
we "guess" that there is a potential data race. However, based on the
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
    4.               acq(y)
    5.               w(x)
    6.               rel(y)
    1.   w(x)
    2.   acq(y)
    3.   rel(y)

The same operations are executed. Hence, we encounter the same events
but in a different order due to a different schedule. To highlight this
point, we maintain the trace positions of the original trace (trace A).

What about the data race? There is still *no* data race present in the
above trace (B). Conflicting events, the writes in T1 and T2, do not
appear right next to each other in the trace.

Let's try again and again, ... Suppose, we encounter the following
trace.

    Trace C:

         T1          T2
    4.               acq(y)
    5.               w(x)
    1.   w(x)
    6.               rel(y)
    2.   acq(y)
    3.   rel(y)

Like in case of trace B, thread T2 executes first. Unlike trace B, we
assume a program run where the write in thread T1 takes place a bit
earlier. The two writes appear right next to each other. This represents
a data race!

Instead of rerunning the program to obtain traces A, B and C, another
method is to consider valid trace reorderings. Reordering of a trace
means that we mix up the order among events such that the resulting
sequence of events still represents a sensible execution sequence.
Indeed, traces B and C are valid trace reorderings of trace A.

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

As we will see, the Lockset method is unsound whereas the Happens-before
method is incomplete.

## Run-time events, instrumentation and tracing

We use the Go programming language here. For the purpose of data race
prediction, we consider a simplified language that only supports
multi-threading, shared variables and locks.

## Events and traces

We write `w(x)` to denote a write event on variable `x`.

We write `r(x)` to denote a read event on variable `x`.

We write `acq(y)` to denote an acquire event on lock `y`.

We write `rel(y)` to denote a release event on lock `y`.

We sometimes use math mode and write *w*(*x*), *a**c**q*(*y*) and so on.

A trace is a sequence of events and represents the interleaved execution
of the program. We often write *T* to refer to a trace.

To uniquely identify events, we add the trace position as a subscript to
the event. For example, *w*(*x*)<sub>1</sub> refers to the event at
trace position 1. We write *e*, *f*, *g* to arbitrary events. We write
*e*<sub>*i*</sub> to refer to event *e* at trace position *i*.

Each event is connected to a thread where each thread is identified via
a distinct thread id.

We write *j*\##*e*<sub>*i*</sub> to denote event *e* at trace position
*i* in thread *j*.

We often use a tabular notation for traces where we introduce for each
thread a separate column and the trace position can be identified via
the row number.

Consider the trace

\[1\##*w*(*x*)<sub>1</sub>, 1\##*a**c**q*(*y*)<sub>2</sub>, 1\##*r**e**l*(*y*)<sub>3</sub>, 2\##*a**c**q*(*y*)<sub>4</sub>, 2\##*w*(*x*)<sub>5</sub>, 2\##*r**e**l*(*y*)<sub>6</sub>\]

and its tabular representation

         T1          T2

    1.   w(x)
    2.   acq(y)
    3.   rel(y)
    4.               acq(y)
    5.               w(x)
    6.               rel(y)

## Instrumentation and tracing

We ignore the details of how to instrument programs to carry out tracing
of events. For our examples, we generally choose the tabular notation
for traces. In practice, the entire trace does not need to be present as
events can be processed *online* in a stream-based fashion. A more
detailed *offline* analysis, may get better results if the trace in its
entire form is present.

## Happens-before method

1.  Given a trace resulting from a specific program run.

2.  Derive a happens-before ordering relation from this trace.

3.  If two conflicting events are unordered, we have found a data race.

We write *e* &lt; *f* to denote that event *e* is ordered before *f*.
The idea is that if *e* &lt; *f* then the operation connected to event
*e* must be executed before the operation connected to event *f*. If
*e* &lt; *f* then we say that *e* *happens-before* *f*.

The least requirement we impose on the (happens-before) ordering
relation is that it is a [strict partial
order](https://en.wikipedia.org/wiki/Partially_ordered_set##Strict_and_non-strict_partial_orders).
*Partial* means that not all events need be ordered. This is a sensible
requirement. For example, consider events resulting from two distinct
threads where there is no interaction among the threads. Then, we don't
expect any ordering constraints among two events *e* and *f* where *e*
is from one thread and *f* is from the order thread. *Strict* partial
order means that the ordering relation is (a) transitive but (b) not
reflexive. Case (a) means that if *e* &lt; *f* and *f* &lt; *g* then
also *e* &lt; *g*. Case (b) means that an event cannot happen itself.

## Happens-before data race check

If for two conflicting events *e* and *f* we have that neither
*e* &lt; *f* nor *f* &lt; *e*, then we say that (*e*,*f*) is a *HB data
race pair*.

The argument is that if *e* &lt; *f* nor *f* &lt; *e* we are free to
reorder the trace such that *e* and *f* appear right next to each other
(in some reordered trace).

Note. If (*e*,*f*) is a *HB data race pair* then so is (*f*,*e*). In
such a situation, we consider (*e*,*f*) and (*f*,*e*) as two distinct
representative for the same data race. When reporting (and counting) HB
data races we only consider a specific representative.

## Lamport's happens-before (HB) relation

We consider a specific happens-before relation due to Leslie Lamport. We
refer to this relation as the *HB* relation. The HB relation imposes an
order am events within each thread and orders critical sections based on
the order as they appear in the trace.

**Program order condition**. Let *e*, *f* be two events belonging to the
same thread where *e* appears before *f* in the trace. Then, we have
that *e* &lt; *f*.

**Critical section order condition**. Let *a**c**q*(*y*) and
*r**e**l*(*y*) be two acquire and release events on the same lock *y*
where both events result from different threads and *r**e**l*(*y*)
appears before *a**c**q*(*y*) in the trace. Then, we have that
*r**e**l*(*y*) &lt; *a**c**q*(*y*).

Let's consider some examples. Recall the earlier trace.

    Trace A:

         T1          T2

    1.   w(x)
    2.   acq(y)
    3.   rel(y)
    4.               acq(y)
    5.               w(x)
    6.               rel(y)

The program order condition implies the following ordering relations:

*w*(*x*)<sub>1</sub> &lt; *a**c**q*(*y*)<sub>2</sub> &lt; *r**e**l*(*y*)<sub>3</sub>

and

*a**c**q*(*y*)<sub>4</sub> &lt; *w*(*x*)<sub>5</sub> &lt; *r**e**l*(*y*)<sub>6</sub>.

The critical section order condition implies

*r**e**l*(*y*)<sub>3</sub> &lt; *a**c**q*(*y*)<sub>4</sub>.

Based on the above we can conclude that

*w*(*x*)<sub>1</sub> &lt; *w*(*x*)<sub>5</sub>.

How? From above we find that

*w*(*x*)<sub>1</sub> &lt; *a**c**q*(*y*)<sub>2</sub> &lt; *r**e**l*(*y*)<sub>3</sub>
and *r**e**l*(*y*)<sub>3</sub> &lt; *a**c**q*(*y*)<sub>4</sub>.

By transitivity we find that

*w*(*x*)<sub>1</sub> &lt; *a**c**q*(*y*)<sub>4</sub>.

In combination with
*a**c**q*(*y*)<sub>4</sub> &lt; *w*(*x*)<sub>5</sub> &lt; *r**e**l*(*y*)<sub>6</sub>
and transitivity we find that
*w*(*x*)<sub>1</sub> &lt; *w*(*x*)<sub>5</sub>.

Because of *w*(*x*)<sub>1</sub> &lt; *w*(*x*)<sub>5</sub>, the HB method
concludes that there is no data race because the conflicting events
*w*(*x*)<sub>1</sub> and *w*(*x*)<sub>5</sub> are ordered. Hence, there
is no data race.

## HB summary and limitations

The HB relation is incomplete and unsound as the following examples
demonstrate.

### HB incomplete (due to fixed critical section order)

Consider the above example `example1`. Suppose we run the program and
obtain trace A.

    Trace A:

         T1          T2

    1.   w(x)
    2.   acq(y)
    3.   rel(y)
    4.               acq(y)
    5.               w(x)
    6.               rel(y)

The above calculations show that
*w*(*x*)<sub>1</sub> &lt; *w*(*x*)<sub>5</sub>. Hence, there is no data
race.

Suppose we run the program and obtain trace B.

    Trace B:

         T1          T2
    4.               acq(y)
    5.               w(x)
    6.               rel(y)
    1.   w(x)
    2.   acq(y)
    3.   rel(y)

Let's derive the HB relations for trace B. The program order relations
remain the same. We find

*w*(*x*)<sub>1</sub> &lt; *a**c**q*(*y*)<sub>2</sub> &lt; *r**e**l*(*y*)<sub>3</sub>

and

*a**c**q*(*y*)<sub>4</sub> &lt; *w*(*x*)<sub>5</sub> &lt; *r**e**l*(*y*)<sub>6</sub>.

The critical section order relation is different because of the slightly
different schedule. In trace B, T2's critical section comes before T1's
critical section. Hence, we find

*r**e**l*(*y*)<sub>6</sub> &lt; *a**c**q*(*y*)<sub>2</sub>.

However, this means that under the HB relations derived from trace B
*w*(*x*)<sub>1</sub> and *w*(*x*)<sub>5</sub> are unordered. That is, we
have neither *w*(*x*)<sub>1</sub> &lt; *w*(*x*)<sub>5</sub> nor
*w*(*x*)<sub>5</sub> &lt; *w*(*x*)<sub>1</sub>. Hence, we can argue that
*w*(*x*)<sub>1</sub> and *w*(*x*)<sub>5</sub> are in race (although
there is no data race in trace B). The point is that we can reorder
trace B and obtain trace C. The data race is now present in trace C.

    Trace C:

         T1          T2
    4.               acq(y)
    5.               w(x)
    1.   w(x)
    6.               rel(y)
    2.   acq(y)
    3.   rel(y)

The HB relations derived from trace B and trace are the same!

We summarize.

For trace A, based on the HB relation we could not detect that there is
a data race. For the HB relation resulting from trace B, the data race
could be detected. Hence, the HB relation is sensitive to the schedule
of critical sections and therefore the HB relation is incomplete.

The above shows that the HB relation is incomplete and the pair
*w*(*x*)<sub>1</sub> and *w*(*x*)<sub>5</sub> is a false negative. If we
use trace A as our starting point, the HB method does not detect that
there is a data race. If we assume a slightly different schedule where
critical sections are reordered (trace B), the HB method is able to
detect the data race.

### HB unsound (due to write-read dependencies)

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

    Trace I:

         T1            T2

    1.   w(x)
    2.   w(y)
    3.                 r(y)
    4.                 w(x)

We encounter a write-read race because *w*(*y*)<sub>2</sub> and
*r*(*y*)<sub>3</sub> appear right next to each other in the trace.

It seems that there is also a HB write-write data race. The HB relations
derived from the above trace are as follows:

*w*(*x*)<sub>1</sub> &lt; *w*(*y*)<sub>2</sub> and
*r*(*y*)<sub>3</sub> &lt; *w*(*x*)<sub>4</sub>.

Hence, *w*(*x*)<sub>1</sub> and *w*(*x*)<sub>4</sub> are unordered.
Hence, we find the write-write data race
(*w*(*x*)<sub>4</sub>,*w*(*x*)<sub>1</sub>).

We reorder the above trace (while maintaining the program order HB
relations). For the reordered trace we keep the original trace
positions.

    Trace II:

         T1            T2

    3.                 r(y)
    4.                 w(x)
    1.   w(x)
    2.   w(y)

In the reordered trace II, the two writes on x appear right next to each
other. Is there a program run and that yields the above reordered trace?
No!

In the reordered trace II, we violate the write-read dependency between
*w*(*y*)<sub>2</sub> and *r*(*y*)<sub>3</sub>. *w*(*y*)<sub>2</sub> is
the last write that takes place before *r*(*y*)<sub>3</sub>. The read
value *y* influences the control flow. See the above program where we
only enter the if-statement if *w*(*y*)<sub>2</sub> takes place (and
sets *y* to 2).

We conclude that the HB relation does not take into account write-read
dependencies and therefore HB data races may not correspond to *actual*
data traces.

We say *may not* because based on the trace alone we cannot decide if
the write-read dependency actually affects the control flow.

For example, trace I could be the result of a program run where we
assume the following program.

    func example4() {
        var tmp int
        x := 1
        y := 1

        // Thread T1
        go func() {
            x = 2
            y = 2 // WRITE
        }()

        // Thread T2 = Main Thread
        tmp = y // READ
        x = 3

    }

There is also a write-read dependency, see locations marked WRITE and
READ. However, the read value does not influence the control flow.
Hence, for the above program trace II would be a valid reordering of
trace I.

### Further reading

### [What Happens-After the First Race?](https://arxiv.org/pdf/1808.00185.pdf)

Shows that the "first" race reported by Lamport's happens-before
relation is sound.

### [ThreadSanitizer](https://github.com/google/sanitizers/wiki/ThreadSanitizerCppManual)

C/C++ implementation of Lamport's happens-before relation (to analyze
C/C++).

### [Go's data race detector](https://golang.org/doc/articles/race_detector)

Based on ThreadSanitizer.

## Lockset

A different method is based on the idea to compute the set of locks that
are held when processing a read/write event. We refer to this set as the
*lockset*.

## Lockset data race check

If two conflicting events share the same lock *y* then both events must
belong to two distinct critical sections involving lock *y*. As critical
sections are mutually exclusive, two conflicting events that share the
same lock cannot be in a data race.

Hence, if the lockset of two conflicting events *e* and *f* is disjoint
then we say that (*e*,*f*) is a *Lockset data race pair*.

## Lockset computation

We assume that critical sections are always identified by pairs of
*a**c**q*(*y*) and *r**e**l*(*y*) events where events *a**c**q*(*y*) and
*r**e**l*(*y*) belong to the same thread. That means the (matching)
release for an acquire event cannot be issued by another thread.

We say an event *e* appears within a critical section belonging to lock
*y* if we find events *a**c**q*(*y*) and *r**e**l*(*y*) such that (1)
*e*, *a**c**q*(*y*) and *r**e**l*(*y*) all belong to the same thread,
(2) *e* appears after *a**c**q*(*y*) and in between *a**c**q*(*y*) and
*e* there is no other *r**e**l*(*y*) event, and (3) *e* appears before
*r**e**l*(*y*) and in between *e* and *r**e**l*(*y*) there is no other
*a**c**q*(*y*) event.

**Lockset**. Let *e* be a read or write event. Then, the locket of *e*,
written *L**S*(*e*), consists of all *y*s where *e* appears within a
critical section belonging to lock *y*.

Recall the earlier trace.

    Trace A:

         T1          T2

    1.   w(x)
    2.   acq(y)
    3.   rel(y)
    4.               acq(y)
    5.               w(x)
    6.               rel(y)

We find two critical sections for lock variable *y*. In thread T1, we
have the critical section identified by *a**c**q*(*y*)<sub>2</sub> and
*r**e**l*(*y*)<sub>3</sub> In thread T2, we have the critical section
identified by *a**c**q*(*y*)<sub>4</sub> and *r**e**l*(*y*)<sub>6</sub>.

We consider the locksets of events *w*(*x*)<sub>1</sub> and
*w*(*x*)<sub>5</sub>.

*L**S*(*w*(*x*)<sub>1</sub>) = {}.

*L**S*(*w*(*x*)<sub>5</sub>) = {*y*}.

We find that the two locksets are disjoint. That is,
*L**S*(*w*(*x*)<sub>1</sub>) ∩ *L**S*(*w*(*x*)<sub>5</sub>) = {}. Hence,
we argue that conflicting events *w*(*x*)<sub>1</sub> and
*w*(*x*)<sub>5</sub> represent a data race.

## Lockset summary and limitations

The lockset method is complete. Any conflicting pair of events that
represent a data race can be shown to be a lockset data race pair.
However, the lockset method is unsound.

Like in case of HB, the lockset method ignores write-read dependency
(and therefore the earlier HB unsoundness example also applies to
lockset). There is a further reason for unsoundness because lockset
allows to reorder critical sections. By reordering critical sections (to
exhibit the data race) we may run into a deadlock.

Consider the following trace.

         T1          T2

    1.   acq(y1)
    2.   acq(y2)
    3.   rel(y2)
    4.   w(x)
    5.   rel(y1)
    6.               acq(y2)
    7.               acq(y1)
    8.               rel(y1)
    9                w(x)
    10.              rel(y2)

There are two lock variables *y*<sub>1</sub> and *y*<sub>2</sub>. We
find the two conflicting events *w*(*x*)<sub>4</sub> and
*w*(*x*)<sub>9</sub>. Their lockset is as follows.

*L**S*(*w*(*x*)<sub>4</sub>) = {*y*<sub>1</sub>}.

*L**S*(*w*(*x*)<sub>9</sub>) = {*y*<sub>2</sub>}.

Based on the lockset data race check, we argue that *w*(*x*)<sub>4</sub>
and *w*(*x*)<sub>9</sub> represents a data race. But is this an actual
data race? No!

The reason is that there is no valid trace reordering (of the above
trace) under which the two writes on *x* appear right next to each
other. We proof this statement by contradiction.

Suppose, there exists a valid trace reordering. For example,
…, *w*(*x*)<sub>4</sub>, *w*(*x*)<sub>5</sub>. As the program order must
remain intact, the events in thread T1 must appear before
*w*(*x*)<sub>4</sub> and the events in thread T2 must appear before
*w*(*x*)<sub>5</sub>. But that means, thread T1 acquired locks
*y*<sub>1</sub> and *y*<sub>2</sub> and the same applies to thread T2!
This is impossible (and if we would try we would run into a deadlock).

Hence, the lockset method is unsound and the above is an example of a
false positive.

## Comparing HB and Lockset

The lockset method is complete but unsound. The HB method is incomplete
and unsound. In practice, it appears that the lockset method gives rise
to too many false positives. This is of course also an issue for the HB
method but the HB method appears report fewer false positives.

In our own recent work, we combine the HB and lockset method to achieve
[Efficient, Near Complete and Often Sound Hybrid Dynamic Data Race
Prediction (extended version)](https://arxiv.org/abs/2004.06969).

## Data race predictor algorithms

Next, we discuss how to implement the lockset and the HB method
efficiently.

## Lockset based data race predictor algorithm

We annotate the trace with lockset information.

## Example 1

          T0      T1        Lockset
    1.   acq(y)
    2.   w(x)              {y}
    3.   rel(y)
    4.   r(x)              {}
    5.           w(x)      {}
    6.           acq(y)
    7.           rel(y)

Lockset of the two writes on `x` in thread T0 and T1 are disjont. Hence,
the lockset method reports that there's a data race.

## Example 2

          T0      T1        Lockset
    1.   w(x)              {}
    2.   acq(y)
    3.   w(x)              {y}
    4.   rel(y)
    5.           acq(y)
    6.           w(x)      {y}
    7.           rel(y)

The lockset of the write at trace position 1 and the write at trace
position 6 are disjoint. Hence, we expect that the lockset method
signals that there is a data race.

To be efficient, implemementation based on the lockset method only keep
track of the most recent locksets. That is, each thread maintains a list
of the most recent reads/writes plus their locksets.

Applied to the above example, we encounter the following behavior.

-   Thread T0 processes *w*(*x*)<sub>1</sub> and records that
    *L**S*(*w*(*x*)) = {}.

-   Once thread T0 processes *w*(*x*)<sub>3</sub> and records that
    *L**S*(*w*(*x*)) = {*y*}.

-   This means that the history of earlier locksets for writes on *x* is
    lost.

-   This means that algorithms that only record locksets for most recent
    writes/reads will not signal a data race here.

## Example 3

          T0      T1        Lockset
    1.   w(x)              {}
    2.   acq(y)
    3.   rel(y)
    4.           acq(y)
    5.           w(x)      {y}
    6.           rel(y)

Locksets are disjoint. Hence, the algorithm signals that there is a data
race.

However, in the actual program, thread T0 forks thread T1. We assume
that after the release at trace position 3 there is a go statement to
create thread T1. For example, the above trace could result from the
following program.

        x = 3
        acq(y)
        rel(y)

        go func() {
            acq(y)
            x = 4
            rel(y)
        }()

This "fork" information is not recorded in the trace. As we only compare
locksets, we encounter here another case of a false positive.

## Example 4

          T0      T1      T2        Lockset
    1.   acq(y)
    2.           w(x)              {}
    3.   rel(y)
    4.                   acq(y)
    5.                   w(x)      {y}
    6.                   rel(y)

Shouldn't the lockset at trace position 2 include lock variable y!?

No!

-   The write at trace position 2 seems to be protected by lock variable
    y.

-   However, thread T1 does not "own" this lock variable!

## Implementation in Go

Lockset-based data race predictor where the trace is annotated with
lockset information.

    package main

    import "fmt"
    import "time"
    import "strconv"
    import "strings"

    ///////////////////////////////////////////
    // Lockset-based data race predictor
    // where we provide a lockset annotated trace.

    // Auxiliary functions

    func max(x, y int) int {
        if x < y {
            return y
        }
        return x
    }

    // Set of strings.
    // We use map[string]bool to emulate sets of strings.
    // The default value for bool is true.
    // Hence, if the (string) key doesn't exist, we obtain false = element not part of the set.
    // In case of add and remove, we use pointers to emulate call-by-reference.

    type Set map[string]bool

    func mkSet() Set {
        return make(map[string]bool)
    }

    func (set Set) copy() Set {
        c := make(map[string]bool)
        for k, v := range set {
            c[k] = v
        }
        return c
    }

    func (set Set) show(vars []string) string {
        var s string
        i := 1
        for k, v := range set {
            if v {
                s = s + k
                i++
                if i < len(set) {
                    s = s + ","
                }
            }

        }
        return ("{" + s + "}")
    }

    func (set Set) empty() bool {
        return len(set) == 0
    }

    func (set Set) elem(n string) bool {
        return set[n]
    }

    func (set Set) add(n string) Set {
        s := set
        s[n] = true
        return s
    }

    //  union(a,b) ==> c,true
    //    if there's some element in b that is not an element in a
    //  union(a,b) ==> c,false
    //    if all elements in b are elements in a
    func (a Set) union(b Set) (Set, bool) {
        r := true
        for x, _ := range b {
            if !a.elem(x) {
                r = false
                a = a.add(x)
            }
        }
        return a, r

    }

    func (a Set) intersection(b Set) Set {
        c := mkSet()

        for x, _ := range a {
            if b.elem(x) {
                c = c.add(x)
            }

        }
        return c

    }

    func (a Set) disjoint(b Set) bool {
        return a.intersection(b).empty()
    }

    func (set Set) remove(n string) Set {
        s := set
        s[n] = false
        return s
    }

    func debug(s string) {
        fmt.Printf(s)
    }

    ///////////////////////////////////////////
    // Basic user interface for a simple language that supports
    //     acquire + release
    //     reads + writes
    // y string refers to a lock variable.
    // x string refers to a global integer variable.
    //
    // init(locks, readwrites) must be called to declare
    //  the set of used lock and readwrites variables.
    //
    type SimpLang interface {
        init([]string, []string)
        acq(tid int, y string)
        rel(tid int, y string)
        w(tid int, x string, n int)
        r(tid int, x string) int
        done()
    }

    // There is no "go" operation.
    // We assume that this is supported by the host language.
    // This also means that we do not trace "go" statements.

    ///////////////////////////////////////////
    // Examples

    func example1(simp SimpLang) {
        // y lock variable
        // x shared variable
        simp.init([]string{"y"}, []string{"x"})

        // T1
        go func() {
            t := 1
            simp.w(t, "x", 3)
            simp.acq(t, "y")
            simp.rel(t, "y")
        }()

        // T0
        t := 0
        simp.acq(t, "y")
        simp.w(t, "x", 4)
        simp.rel(t, "y")
        tmp := simp.r(t, "x")
        fmt.Printf("x=%d", tmp)

        simp.done()
    }

    // An earlier unprotected write might be overshadowed by a protected write.
    // If each thread only keeps track of the most recent lockset, we might miss a race.
    func example2(simp SimpLang) {
        simp.init([]string{"y"}, []string{"x"})

        // T1
        go func() {
            t := 1
            simp.acq(t, "y")
            simp.w(t, "x", 4)
            simp.rel(t, "y")
        }()

        // T0
        t := 0
        simp.w(t, "x", 3)
        simp.acq(t, "y")
        simp.w(t, "x", 4)
        simp.rel(t, "y")

        simp.done()
    }

    // Lockset on its own potentially yields many false positives.
    // In our example, T0 happens before T1, hence there's no race,
    // despite the fact that the locksets of the two writes are disjoint.
    func example3(simp SimpLang) {
        simp.init([]string{"y"}, []string{"x"})

        // T0
        t := 0
        simp.w(t, "x", 3)
        simp.acq(t, "y")
        simp.rel(t, "y")

        // T1
        go func() {
            t := 1
            simp.acq(t, "y")
            simp.w(t, "x", 4)
            simp.rel(t, "y")
        }()

        simp.done()
    }

    func example4(simp SimpLang) {
        simp.init([]string{"y1", "y2"}, []string{"x"})

        // T1
        go func() {
            t := 1
            simp.acq(t, "y1")
            simp.acq(t, "y2")
            simp.rel(t, "y2")
            simp.w(t, "x", 4)
            simp.rel(t, "y1")
        }()

        // T0
        t := 0

        simp.acq(t, "y2")
        simp.acq(t, "y1")
        simp.rel(t, "y1")

        simp.w(t, "x", 3)
        simp.rel(t, "y2")
        simp.done()
    }

    // "sync" threads to enforce a certain program run.
    // Example makes the following point:
    // write in T1 seems protected by acq(y)-rel(y) in T2.
    // But y not part of the T1:write's lockset.
    // Rightly so, cause thread T1 does not own lock y.
    func example4b(simp SimpLang) {
        simp.init([]string{"y"}, []string{"x"})
        sync := make(chan int)
        sync2 := make(chan int)

        // T1
        go func() {
            t := 1
            <-sync
            simp.w(t, "x", 4)
            sync <- 1
        }()

        // T2
        go func() {
            t := 2
            <-sync2
            simp.acq(t, "y")
            simp.w(t, "x", 5)
            simp.rel(t, "y")
            sync2 <- 1
        }()

        // T0
        t := 0
        simp.acq(t, "y")
        sync <- 1
        <-sync
        simp.rel(t, "y")
        sync2 <- 1
        <-sync2
        simp.done()
    }

    ///////////////////////////////////////////
    // Default implementation

    // Mutex
    type Mutex chan int

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

    type State struct {
        mutex    map[string]Mutex
        variable map[string]int
    }

    // *State implements the SimpLang interface

    // maintain also the number of threads, starting with id 0.
    // makes things easier,
    // can later build an abstraction that manages threads dynamically

    func (s *State) init(locks []string, vars []string) {
        s.mutex = make(map[string]Mutex)
        s.variable = make(map[string]int)

        for _, e := range locks {
            s.mutex[e] = newMutex()
        }

        for _, e := range vars {
            s.variable[e] = 0
        }

    }

    // What for all threads to finish
    func (s *State) done() {
        time.Sleep(1 * time.Second)
    }

    func (s *State) acq(tid int, y string) {
        lock(s.mutex[y])
    }

    func (s *State) rel(tid int, y string) {
        unlock(s.mutex[y])
    }

    func (s *State) w(tid int, x string, n int) {
        s.variable[x] = n
    }

    func (s *State) r(tid int, x string) int {
        return s.variable[x]
    }

    ///////////////////////////////////////////
    // Trace + Events

    type EvtKind int

    const (
        AcquireEvt EvtKind = 0
        ReleaseEvt EvtKind = 1
        WriteEvt   EvtKind = 2
        ReadEvt    EvtKind = 3
    )

    type Event interface {
        thread() int
        loc() int
        kind() EvtKind
        name() string
    }

    type EVENT struct {
        k_   EvtKind
        id_  int
        loc_ int
        n_   string
    }

    func (e EVENT) thread() int   { return e.id_ }
    func (e EVENT) loc() int      { return e.loc_ }
    func (e EVENT) kind() EvtKind { return e.k_ }
    func (e EVENT) name() string  { return e.n_ }

    // Some convenience functions.
    func mkRead(i int, l int, n string) Event {
        return EVENT{ReadEvt, i, l, n}
    }

    func mkWrite(i int, l int, n string) Event {
        return EVENT{WriteEvt, i, l, n}
    }

    func mkAcq(i int, l int, n string) Event {
        return EVENT{AcquireEvt, i, l, n}
    }

    func mkRel(i int, l int, n string) Event {
        return EVENT{ReleaseEvt, i, l, n}
    }

    // Tabular display of trace.

    const (
        ROW_OFFSET = 8
    )

    // Omit thread + loc info.
    func displayEvtSimple(e Event) string {
        var s string
        switch {
        case e.kind() == AcquireEvt:
            s = "acq(" + e.name() + ")"
        case e.kind() == ReleaseEvt:
            s = "rel(" + e.name() + ")"
        case e.kind() == WriteEvt:
            s = "w(" + e.name() + ")"
        case e.kind() == ReadEvt:
            s = "r(" + e.name() + ")"
        }
        return s
    }

    func displayEvt(e Event) string {
        s := displayEvtSimple(e)
        s = strconv.Itoa((int)(e.thread())) + "##" + s + "_" + strconv.Itoa(e.loc())
        return s
    }

    func blanks(i int) string {
        return strings.Repeat(" ", i)
    }

    func colOffset(i int) string {
        n := (int)(i)
        return blanks(n * ROW_OFFSET)
    }

    func showThread(i int) string {
        //  return (strconv.Itoa(i) + "##")
        return ("T" + strconv.Itoa(i))
    }

    // Thread ids fully cover [0..n]
    func displayTrace(t []Event) string {
        s := ""
        m := 0
        for _, e := range t {
            row_start := "\n" + strconv.Itoa(e.loc()) + "."
            row := row_start + blanks(6-len(row_start)) + colOffset(e.thread()) + displayEvtSimple(e)
            s = s + row
            m = max(m, (int)(e.thread()))
        }
        // Add column headings.
        heading := "      "
        for i := 0; i <= m; i++ {
            heading += showThread(i) + strings.Repeat(" ", ROW_OFFSET-2)
        }
        s = heading + s

        return s
    }

    ///////////////////////////////////////////
    // Tracing
    //
    // We trace events while executing the corresponding operations.

    type Tracer struct {
        t   []Event  // trace
        s   State    // program state
        loc chan int // current location
    }

    /*

    TRACING.

     The current (trace) location is stored in a mutable variable represented by a buffered channel of size 1.
    Thus, the location can be accessed and updated concurrently in a consistent manner.

    When executing an operation we issue an event.
    Events are recorded in a trace in linear sequence identified via their location numbers.
    The event order shall correspond to the actual sequence of operations executed.
    This is challenging because we need to

     (1) execute the operation, and
     (2) store the corresponding event

    atomically. Otherwise, there might be inconsistencies.
    Consider the following examples.

    Suppose, thread 1 executes w(x) and only later thread 2 executes r(x).
    If we store r(x) before w(x), based on the trace it seems
    that the read is independent from the write.

    Suppose, thread 1 executes rel(y) and then thread 2 executes acq(y).
    If we store acq(y) before rel(y), based on the trace it looks like a lock
    has been acquired while being held by another thread.

    ATOMIC execution and tracing.

    What about using a global mutex to atomically execute and trace?
    Tricky in case of blocking operations such as acquire.

    Our solution.

    Reads and writes are atomic.
    We use the buffered channel that holds the current location as a mutex.

    We first execute the acquire operation and then store the event.
    In case of release we first store the event and then execute release.

    The above provides the following guarantees.

     (a) Sequence of reads/writes is consistent
     (b) acq-rel on the same lock are consistent

    But

     (c) acq-rel on distinct locks may appear in a slightly different order  in the trace
    compared to the actual execution sequence.
     (d) acq/rel and r/w in different threads may appear in a slightly different in the trace
    compared to the actual execution sequence.

    For the lockset construction, (c) and (d) should not have any impact.



    */

    func (tracer *Tracer) init(locks []string, vars []string) {
        tracer.t = make([]Event, 0)
        tracer.loc = make(chan int, 1)
        tracer.loc <- 1
        (&tracer.s).init(locks, vars)

    }

    func (tracer *Tracer) done() {
        tracer.s.done()
        output := displayTrace(tracer.t)
        fmt.Print("\n")
        fmt.Print(output)
    }

    func (tracer *Tracer) acq(tid int, y string) {
        tracer.s.acq(tid, y)
        l := <-tracer.loc
        tracer.t = append(tracer.t, mkAcq(tid, l, y))
        tracer.loc <- l + 1

    }

    func (tracer *Tracer) rel(tid int, y string) {
        tracer.s.rel(tid, y)
        l := <-tracer.loc
        tracer.t = append(tracer.t, mkRel(tid, l, y))
        tracer.loc <- l + 1

    }

    func (tracer *Tracer) w(tid int, x string, n int) {
        l := <-tracer.loc
        tracer.s.w(tid, x, n)
        tracer.t = append(tracer.t, mkWrite(tid, l, x))
        tracer.loc <- l + 1
    }

    func (tracer *Tracer) r(tid int, x string) int {
        l := <-tracer.loc
        n := tracer.s.r(tid, x)
        tracer.t = append(tracer.t, mkRead(tid, l, x))
        tracer.loc <- l + 1
        return n
    }

    /////////////////////////////////////////////////////////////
    // Lockset

    // Compute locksets and add this info to the trace.

    type Thread struct {
        lockset Set
        reads   map[string]Set
        writes  map[string]Set
    }

    type LS struct {
        t      Tracer
        vars   []string
        thread map[int]Thread
    }

    type EventLS interface {
        Event
        lockset() Set
    }

    type EVENT_LS struct {
        evt EVENT
        ls  Set
    }

    func displayLS(vars []string, e_ Event) string {
        var s string

        switch e := e_.(type) {
        case EVENT_LS:
            s = e.lockset().show(vars)
        default:
            s = ""

        }
        return s

    }

    // Thread ids fully cover [0..n]
    func displayTraceLS(vars []string, t []Event) string {
        s := ""
        m := 0
        for _, e := range t {
            m = max(m, (int)(e.thread()))
        }

        for _, e := range t {
            row_start := "\n" + strconv.Itoa(e.loc()) + "."
            row := row_start + blanks(6-len(row_start)) + colOffset(e.thread()) + displayEvtSimple(e)
            row2 := strings.Repeat(" ", (m+2)*ROW_OFFSET-len(row)) + displayLS(vars, e)
            // locksets appear to the very right
            s = s + row + row2
        }
        // Add column headings.
        heading := "      "
        for i := 0; i <= m; i++ {
            heading += showThread(i) + strings.Repeat(" ", ROW_OFFSET-2)
        }
        s = heading + "  Lockset" + strings.Repeat(" ", ROW_OFFSET-2) + s

        return s
    }

    func (e EVENT_LS) thread() int   { return e.evt.thread() }
    func (e EVENT_LS) loc() int      { return e.evt.loc() }
    func (e EVENT_LS) kind() EvtKind { return e.evt.kind() }
    func (e EVENT_LS) name() string  { return e.evt.name() }
    func (e EVENT_LS) lockset() Set  { return e.ls }

    // Need to copy maps!
    func mkReadLS(i int, l int, n string, ls Set) EventLS {
        return EVENT_LS{EVENT{ReadEvt, i, l, n}, ls.copy()}
    }

    func mkWriteLS(i int, l int, n string, ls Set) EventLS {
        return EVENT_LS{EVENT{WriteEvt, i, l, n}, ls.copy()}
    }

    const MAX_TID = 10

    func (ls *LS) init(locks []string, vars []string) {
        (&ls.t).init(locks, vars)

        ls.vars = vars
        ls.thread = make(map[int]Thread)
        for i := 0; i < MAX_TID; i++ {
            ls.thread[i] = Thread{mkSet(), make(map[string]Set), make(map[string]Set)}
        }

    }

    func (ls *LS) done() {
        ls.t.s.done()
        output := displayTraceLS(ls.vars, ls.t.t)
        fmt.Print("\n")
        fmt.Print(output)
    }

    func (ls *LS) acq(tid int, y string) {
        ls.t.acq(tid, y)
        t := ls.thread[tid]
        t.lockset = t.lockset.add(y)
    }

    func (ls *LS) rel(tid int, y string) {
        t := ls.thread[tid]
        t.lockset = t.lockset.remove(y)
        ls.t.rel(tid, y)
    }

    func (ls *LS) w(tid int, x string, n int) {
        thread := ls.thread[tid]
        thread.writes[x] = thread.lockset
        l := <-ls.t.loc
        ls.t.s.w(tid, x, n)

        ls.t.t = append(ls.t.t, mkWriteLS(tid, l, x, thread.writes[x]))
        ls.t.loc <- l + 1
    }

    func (ls *LS) r(tid int, x string) int {

        thread := ls.thread[tid]
        thread.reads[x] = thread.lockset

        l := <-ls.t.loc
        n := ls.t.s.r(tid, x)
        ls.t.t = append(ls.t.t, mkReadLS(tid, l, x, thread.reads[x]))
        ls.t.loc <- l + 1

        return n
    }

    func testBasic() {

        var s State
        example1(&s)

        var t Tracer
        example1(&t)
    }

    func testLockset() {

        var ls LS
        example1(&ls)
        example2(&ls)
        example3(&ls)
        // example4(&ls)
        example4b(&ls)
    }

    func main() {

        // testBasic()

        testLockset()

        fmt.Printf("\ndone")
    }

## Vector clock based data race predictor algorithms - Highlights

The HB and the lockset method can be implemented efficiently. The
computation of locksets is rather straightforward. The HB method
requires to derive a happens-before order from the trace. In practice,
the happens-before order is checked via [vector
clocks](https://en.wikipedia.org/wiki/Vector_clock).

## Vector clocks

A vector clock is a data structure that manages a time stamp for each
thread. Each thread maintains its own vector clock. When processing
events we advance the time stamp of the thread we are in.

Consider our running example.

    Trace A:

         T1              T2

    1.   w(x)
    2.   acq(y)
    3.   rel(y)
    4.                   acq(y)
    5.                   w(x)
    6.                   rel(y)

We will annotate events with vector clocks.

Thread T1 starts with vector clock `[1,0]`. We can interpret `[1,0]` as
an array where the first array position represents the time stamp of T1
and the second array position the time stamp of T2.

Initially, all entries (time stamps) are zeroed but the time stamp of
the thread which is set to 1. Hence, T1 starts with `[1,0]` and T2
starts with `[0,1]`.

We consider processing of the first event.

    Trace A:

         T1                  T2

    1. [1,0]_w(x)_[2,0]
    2.       acq(y)
    3.       rel(y)
    4.                           acq(y)
    5.                           w(x)
    6.                           rel(y)

T1's time stamp is incremented by 1. Hence, we find `[2,0]`. We continue
till we reach thread T2.

We write `[1,0]_w(x)_[2,0]` to indicate that `[1,0]` is the vector clock
at the time we reach `w(x)` and `[2,0]` is the vector clock after
processing `w(x)`. We refer to `[1,0]` as `w(x)`'s **pre** vector clock
and to `[2,0]` as `w(x)`'s **post** vector clock.

    Trace A:

          T1                    T2

    1. [1,0]_w(x)_[2,0]
    2. [2,0]_acq(y)_[3,0]
    3. [3,0]_rel(y)_[4,0]
    4.                     [0,1]_acq(y)
    5.                           w(x)
    6.                           rel(y)

We are about to process *a**c**q*(*y*)<sub>4</sub>. So far, we enforced
the program order condition by incrementing the thread's time stamp. We
also need to enforce the critical section order condition. In terms of
the HB relation, this means that
*r**e**l*(*y*)<sub>3</sub> &lt; *a**c**q*(*y*)<sub>4</sub>.

Via vector clocks we enforce this condition by synchronizing
*r**e**l*(*y*)<sub>3</sub>'s pre vector clock `[3,0]` with
*a**c**q*(*y*)<sub>4</sub>'s pre vector clock `[0,1]` (before
incrementing T2's time stamp). Note that `[4,0]` is the vector clock
*after* processing *r**e**l*(*y*)<sub>3</sub> whereas `[3,0]` is the
vector clock at the time we reach *r**e**l*(*y*)<sub>3</sub>.

Synchronizing means we take the maximum of the time stamps at each array
position.

    synchronize([3,0], [0,1]) = [max(3,0), max(0,1)] = [3,1]

After synchronization, we increment T2's time stamp and obtain `[3,2]`.
This yields the following annotated trace.

    Trace A:

          T1                    T2

    1. [1,0]_w(x)_[2,0]
    2. [2,0]_acq(y)_[3,0]
    3. [3,0]_rel(y)_[4,0]
    4.                     [0,1]_acq(y)_[3,2]
    5.                           w(x)
    6.                           rel(y)

From here on we only need increment T2's time stamp. This yields the
following annotated trace.

    Trace A:

          T1                    T2

    1. [1,0]_w(x)_[2,0]
    2. [2,0]_acq(y)_[3,0]
    3. [3,0]_rel(y)_[4,0]
    4.                     [0,1]_acq(y)_[3,2]
    5.                     [3,2]_w(x)_[3,3]
    6.                     [3,3]_rel(y)_[3,4]

## HB data races by comparing vector clocks

We can test if two events are in HB relation by comparing their vector
clocks.

Vector clock *V*<sub>1</sub> is smaller than vector clock
*V*<sub>2</sub>, written *V*<sub>1</sub> &lt; *V*<sub>2</sub>, if (1)
for all array positions *i*,
*V*<sub>1</sub>\[*i*\] ≤ *V*<sub>2</sub>\[*i*\], and (2) there exists an
array position *j*, *V*<sub>1</sub>\[*j*\] &lt; *V*<sub>2</sub>\[*j*\].
If neither *V*<sub>1</sub> &lt; *V*<sub>2</sub> nor
*V*<sub>2</sub> &lt; *V*<sub>1</sub> then we say that
*V*<sub>1</sub>, *V*<sub>2</sub> are *incomparable*.

We are only interested in writes/reads that are possibly involved in a
HB data race. For writes/reads we use their pre vector clock for
comparison.

    Write/reads and their pre vector clock.

    1. w(x)   [1,0]
    5. w(x)   [3,2]

Two events *e*, *f* are in HB relation *e* &lt; *f* if *e*'s vector
clock is smaller compared to *f*'s vector clock.

For example, we find *w*(*x*)<sub>1</sub> &lt; *w*(*x*)<sub>5</sub>
because \[1, 0\] &lt; \[3, 2\]. For the first position we find 1 &lt; 3,
for the second position we find 0 &lt; 2. Hence, there is no HB data
race for this example.

## Pre vector clocks for synchronization

We synchronize the pre vector clock of the release with the pre vector
clock of the acquire. The reason is that we use pre vector clocks when
checking for data races. Using the post vector clock of the release
instead would lead to wrong results (unless we use post vector clocks
when checking for data races).

Here is an example to explain this point in more detail. Consider

         T1              T2

    1.   acq(y)
    2.   rel(y)
    3.   w(x)
    4.                   acq(y)
    5.                   w(x)
    6.                   rel(y)

We annotate the trace with pre/post vector clocks.

         T1                   T2

    1.   [1,0]_acq(y)_[2,0]
    2.   [2,0]_rel(y)_[3,0]
    3.   [3,0]_w(x)_[4,0]
    4.                        [0,1]_acq(y)_[2,2]

              synchronize([2,0],[0,1]) = [2,1]

    5.                        [2,2]_w(x)_[2,3]
    6.                        [2,3]_rel(y)_[2,4]

The post vector clock of `acq(y)` in thread T2 is `[2,2]`. We first
synchronize pre vector clocks which yields `[2,1]`. Incrementing T2's
time stamp finally yields `[2,2]`.

We conclude that the two writes on x are in a race because their pre
vector clocks are incomparable. Neither \[3, 0\] &lt; \[2, 2\] nor
\[2, 2\] &lt; \[3, 0\] holds.

Let's use the post vector clock of the release for synchronization.
Then, we obtain the following annotated trace.

         T1                   T2

    1.   [1,0]_acq(y)_[2,0]
    2.   [2,0]_rel(y)_[3,0]
    3.   [3,0]_w(x)_[4,0]
    4.                        [0,1]_acq(y)_[3,2]

              synchronize([3,0],[0,1]) = [3,1]

    5.                        [3,2]_w(x)_[3,3]
    6.                        [3,3]_rel(y)_[3,4]

We find that \[3, 0\] &lt; \[3, 2\]. This (wrongly) implies that the
write at position 3 happens before the write at position 5. This is
wrong because under Lamport's happens-before relation, the two writes
are not ordered.

We conclude that using the post vector clock of the release for
synchronization leads to wrong results. We must use the pre vector clock
instead.

Please note. It is possible to use the post vector clock of the release
for synchronization. But then we can no longer use the pre vector clocks
when checking for data races. Instead we must use post vector clocks.

## HB relations versus vector clocks

If we wish to compare vector clocks of release and acquire events we use
the acquire's post and the release's pre vector clock. This is because
we record the release's pre vector clock for synchronization with a
subsequent acquire. The effect of synchronization is only observable in
terms of the acquire's post vector clock.

Consider *r**e**l*(*y*)<sub>3</sub>'s pre vector clock \[3, 0\] and
*a**c**q*(*y*)<sub>4</sub>'s post vector clock \[3, 2\].
\[3, 0\] &lt; \[3, 2\] and therefore we conclude that
*r**e**l*(*y*)<sub>3</sub> &lt; *a**c**q*(*y*)<sub>4</sub>.

There is an odd case. Consider *a**c**q*(*y*)<sub>2</sub>'s post vector
clock \[3, 0\] and *r**e**l*(*y*)<sub>3</sub>'s pre vector clock
\[3, 0\] for comparison, it turns out that \[3, 0\] =  = \[3, 0\]. So,
both events appear to happen at the same time. This is a special case
because the critical section marked by *a**c**q*(*y*)<sub>2</sub> and
*r**e**l*(*y*)<sub>3</sub> is empty.

## Vector clock based data race predictor algorithm - Offline Approach

We present the details of the vector clock data race predictor algorithm
outlined earlier. For each event we compute its pre and post vector
clock. We compare the pre vector clock of conflicting events to detect
HB data races.

We refer to this approach as an *offline* approach because the whole
trace needs to be available. We first compute pre/post vector clocks and
annotate each event with this information. Then, we consider consider
all combinations of conflicting events to detect HB races by comparing
pre vector clocks.

## Vector clocks

We write \[*k*<sub>1</sub>, ..., *k*<sub>*n*</sub>\] to denote a vector
clock where the time stamp of thread *i* is *k*<sub>*i*</sub>.

Vector clocks are of a constant size as we assume that the number of
threads is fixed to *n*.

We introduce auxiliary functions to (1) increment the time stamp of
thread *i* and (2) to synchronize two vector clocks.

*i**n**c*(\[*k*<sub>1</sub>,...,*k*<sub>*i* − 1</sub>,*k*<sub>*i*</sub>,*k*<sub>*i* + 1</sub>,...,*k*<sub>*n*</sub>\],*i*) = \[*k*<sub>1</sub>, ..., *k*<sub>*i* − 1</sub>, *k*<sub>*i*</sub> + 1, *k*<sub>*i* + 1</sub>, ..., *k*<sub>*n*</sub>\]

*s**y**n**c*(\[*i*<sub>1</sub>,...,*i*<sub>*n*</sub>\],\[*j*<sub>1</sub>,...,*j*<sub>*n*</sub>\]) = \[*m**a**x*(*i*<sub>1</sub>,*j*<sub>1</sub>), ..., *m**a**x*(*i*<sub>*n*</sub>,*j*<sub>*n*</sub>)\]

where *m**a**x* computes the maximum of two natural numbers.

## Thread vector clocks and event processing

Each thread *i* maintains its own vector clock written *T**h*(*i*). We
can think of *T**h* as an array where for each thread id *i* there is an
entry *T**h*(*i*) that corresponds to the thread's vector clock.
(Notation *T**h*(*i*) effectively equals the the common array notation
*T**h*\[*i*\] but we simply prefer to write *T**h*(*i*).)

Initially, all time stamps in *T**h*(*i*) are zero but the time stamp of
entry *i* that is set to one.

For each lock variable *y*, we record the vector clock of the last
release event in *R**e**l*(*y*). Initially, all time stamps in
*R**e**l*(*y*) are zero.

For each kind of event in in the trace we introduce an event processing
procedure.

    Algorithm VC for computing vector clocks:

    acq(i,y) {
      Th(i) = sync(Rel(y), Th(i))
      Th(i) = inc(Th(i), i)
    }

    rel(i,y) {
      Rel(y) = Th(i)
      Th(i) = inc(Th(i), i)
    }

    read(i,x) {
      Th(i) = inc(Th(i), i)
    }

    write(i,x) {
      Th(i) = inc(Th(i), i)
    }

where *i* refers to the thread id.

Recall

    Trace A:

         T1              T2

    1.   w(x)
    2.   acq(y)
    3.   rel(y)
    4.                   acq(y)
    5.                   w(x)
    6.                   rel(y)

Initially,

*T**h*(1) = \[1, 0\]

*T**h*(2) = \[0, 1\]

*R**e**l*(*y*) = \[0, 0\].

We process the above trace by calling the respective event processing
procedure.

    Call write(1,x) yields Th(1) = [2,0].

    Call acq(1,y) yields Th(1) = [3,0].

    Call rel(1,y) yields Rel(y) = [3,0] and Th(1) = [4,0].

    Call acq(2,y) yields first Th(2) = sync(Rel(y), Th(2)) = [3,1] and
                         then Th(2) = [3,2]

    Call write(2,x) yields Th(2) = [3,3]

    Call rel(2,y) yields Rel(y) = [3,3] and Th(2) = [3,4]

We consider a slight extension of algorithm `VC` where we record for
each event its pre and post vector clock. For this purpose, each event
processing procedure takes an additional parameter *k* that represents
the trace position of the event. We store pre vector clocks in the array
`Pre` and post vector clocks in the array `Post`.

    Algorithm VC_pre_post for annoting events with their pre and post vector clock:

    acq(i,y,k) {
      Pre(k) = Th(i)
      Th(i) = sync(Rel(y), Th(i))
      Th(i) = inc(Th(i), i)
      Post(k) = Th(i)
    }

    rel(i,y,k) {
      Pre(k) = Th(i)
      Rel(y) = Th(i)
      Th(i) = inc(Th(i), i)
      Post(k) = Th(i)
    }

    read(i,x,k) {
      Pre(k) = Th(i)
      Th(i) = inc(Th(i), i)
      Post(k) = Th(i)
    }

    write(i,x,k) {
      Pre(k) = Th(i)
      Th(i) = inc(Th(i), i)
      Post(k) = Th(i)
    }

## Happens before via vector clocks

By comparing vector clocks associated to each event we can check if one
event happens before the other event.

We only consider read/write events for which we always use their pre
vector clocks.

If the pre vector clocks of two conflicting events are incomparable we
have detected a HB data race.

We introduce the following auxiliary function.

*h**a**p**p**e**n**s**B**e**f**o**r**e*(\[*i*<sub>1</sub>,...,*i*<sub>*n*</sub>\],\[*j*<sub>1</sub>,...,*j*<sub>*n*</sub>\]) = *t**r**u**e*
if *i*<sub>*k*</sub> &lt;  = *j*<sub>*k*</sub> for all *k* = 1...*n* and
there exists *k* such that *i*<sub>*k*</sub> &lt; *j*<sub>*k*</sub>.

*h**a**p**p**e**n**s**B**e**f**o**r**e*(\[*i*<sub>1</sub>,...,*i*<sub>*n*</sub>\],\[*j*<sub>1</sub>,...,*j*<sub>*n*</sub>\]) = *f**a**l**s**e*
otherwise.

Examples:

*h**a**p**p**e**n**s**B**e**f**o**r**e*(\[2,1\],\[2,3\]) = *t**r**u**e*

*h**a**p**p**e**n**s**B**e**f**o**r**e*(\[2,1\],\[1,3\]) = *f**a**l**s**e*

Instead of
*h**a**p**p**e**n**s**B**e**f**o**r**e*(*V*<sub>1</sub>,*V*<sub>2</sub>)
we often write *V*<sub>1</sub> &lt; *V*<sub>2</sub> for short.

## Examples

Applying algorithm `VC_pre_post` on our running example yields the
following annotated trace where thread ids are enumerated starting with
0. We write 0## to denote the first thread and so on.

    Trace A:

          0##                    1##

    1. [1,0]_w(x)_[2,0]
    2. [2,0]_acq(y)_[3,0]
    3. [3,0]_rel(y)_[4,0]
    4.                     [0,1]_acq(y)_[3,2]
    5.                     [3,2]_w(x)_[3,3]
    6.                     [3,3]_rel(y)_[3,4]

Consider the two writes *w*(*x*)<sub>1</sub> and *w*(*x*)<sub>5</sub>
and their pre vector clocks \[1, 0\] and \[3, 2\]. We find
\[1, 0\] &lt; \[3, 2\]. Hence, there is no HB data race.

Consider another trace on which we run algorithm `VC_pre_post`.

       0##                  1##
    1. [1,0]_acq(y)_[2,0]
    2. [2,0]_rel(y)_[3,0]
    3. [3,0]_w(x)_[4,0]
    4.                     [0,1]_acq(y)_[2,2]
    5.                     [2,2]_w(x)_[2,3]
    6.                     [2,3]_rel(y)_[2,4]

We encounter the following write-write HB data race pair
(0\##*w*(*x*)<sub>3</sub>,1\##*w*(*x*)<sub>5</sub>) because neither
\[3, 0\] &lt; \[2, 2\] nor \[2, 2\] &lt; \[3, 0\] holds. That is, we
find that !*h**a**p**p**e**n**s**B**e**f**o**r**e*(\[3,0\],\[2,2\]) and
!*h**a**p**p**e**n**s**B**e**f**o**r**e*(\[2,2\],\[3,0\]).

## Offline approach summary

Based on algorithm VC we can store the pre vector clock for each
read/write event.

We can then consider all pairs of conflicting events and compare their
(pre) vector clocks to check if they represent a HB data race pair.

The advantage of this approach is that all HB races can be identified.

There are also several disadvantages.

Two passes are necessary. The first pass computes all pre vector clocks.
The second pass considers all combinations of conflicting events and
carries out the happens before check.

This means we need extra space to store all pre vector clocks and extra
time due to the second pass.

This approach can also be only run offline as the whole trace needs to
be available (because we record for each event its vector clock).

## Vector clock based data race predictor algorithms - Online Approach

We consider an *online* approach. While processing events we immediately
report races. There is no longer the need to store pre vector clocks for
all events in the trace. This saves space and time but has the
disadvantage that not necessarily all HB races can be detected.

The online approach works as follows. Instead of storing the (pre)
vector clock for each write/read event, we maintain two sets *W*(*x*)
and *R*(*x*). *W*(*x*) represents the set of writes we have processed so
far where the (pre) vector clocks of each write are pairwise
incomparable. *R*(*x*) represents the set of reads we have processed so
far where the (pre) vector clocks of each read are pairwise
incomparable.

Recall. Incomparable vector clocks means that the corresponding events
are not in happens before relation.

Initially, *W*(*x*) and *R*(*x*) are empty.

    Algorithm VC_W_R for computing W(x) and R(x)

    acq(i,y) {
      Th(i) = sync(Rel(y), Th(i))
      Th(i) = inc(Th(i), i)
    }

    rel(i,y) {
      Rel(y) = Th(i)
      Th(i) = inc(Th(i), i)
    }

    read(i,x) {
      R(x) = { Th(i) } cup { V | V in R(x) /\ !happensBefore(V,Th(i)) }
      W(x) = { V | V in W(x) /\ !happensBefore(V,Th(i)) }
      Th(i) = inc(Th(i), i)
    }

    write(i,x) {
      R(x) = { V | V in R(x) /\ !happensBefore(V,Th(i)) }
      W(x) = { Th(i) } cup { V | V in W(x) /\ !happensBefore(V,Th(i)) }
      Th(i) = inc(Th(i), i)
    }

Note. The test `!happensBefore(V,Th(i))` is sufficient to check that
vector clocks *V* and *T**h*(*i*) are incomparable. The test
`!happensBefore(Th(i),V)` always holds because the vector clock of an
event that appears later can never be smaller than the vector clock of
an event that appears earlier.

We maintain the following invariant.

For *V*<sub>1</sub>, *V*<sub>2</sub> ∈ *W*(*x*) ∪ *R*(*x*) we have that
!*h**a**p**p**e**n**s**B**e**f**o**r**e*(*V*<sub>1</sub>,*V*<sub>2</sub>)
and
!*h**a**p**p**e**n**s**B**e**f**o**r**e*(*V*<sub>2</sub>,*V*<sub>1</sub>).

Thus, each pair (*V*<sub>1</sub>,*V*<sub>2</sub>) where
*V*<sub>1</sub>, *V*<sub>2</sub> ∈ *W*(*x*) represents a write-write HB
data race (where we identify events via vector clocks).

Each pair (*V*<sub>1</sub>,*V*<sub>2</sub>) where
*V*<sub>1</sub> ∈ *W*(*x*) and *V*<sub>2</sub> ∈ *R*(*x*) represents a
write-read HB data race.

The following variant of algorithm `VC_W_R` reports data race pairs
immediately while processing events.

    Algorithm VC_W_R_Races, variant of algorithm VC_W_R for reporting data races:

    acq(i,y) {
      Th(i) = sync(Rel(y), Th(i))
      Th(i) = inc(Th(i), i)
    }

    rel(i,y) {
      Rel(y) = Th(i)
      Th(i) = inc(Th(i), i)
    }

    read(i,x) {
      R(x) = { Th(i) } cup { V | V in R(x) /\ !happensBefore(V,Th(i)) }
      W(x) = { V | V in W(x) /\ !happensBefore(V,Th(i)) }
      For each V in W(x), V != Th(i), report (V, Th(i)) as a write-read data race
      Th(i) = inc(Th(i), i)
    }

    write(i,x) {
      R(x) = { V | V in R(x) /\ !happensBefore(V,Th(i)) }
      W(x) = { Th(i) } cup { V | V in W(x) /\ !happensBefore(V,Th(i)) }
      For each V in R(x), V != Th(i), report (Th(i), V) as a write-read data race
      For each V in W(x), V != Th(i), report (V, Th(i)) as a write-write data race
      Th(i) = inc(Th(i), i)
    }

Race pairs are reported in terms of vector clocks. Each vector clocked
is linked to a specific event which in turn results from In an actual
implementation, we would therefore report the events, respectively, the
code locations that were executed and resulted in the event.

## Examples

We consider a run of algorithm `VC_W_R` (and its extension
`VC_W_R_Races`) on the above trace where for clarity we keep pre and
post vector clock annotations. There are no reads, so we only consider
*W*(*x*).

       0##                  1##                        W(x)                    Race pairs
    1. [1,0]_acq(y)_[2,0]                            {}
    2. [2,0]_rel(y)_[3,0]                            {}
    3. [3,0]_w(x)_[4,0]                              { [3,0] }
    4.                     [0,1]_acq(y)_[2,2]        { [3,0] }
    5.                     [2,2]_w(x)_[2,3]          { [3,0], [2,2] }       ([3,0], [2,2])
    6.                     [2,3]_rel(y)_[2,4]        { [3,0], [2,2] }

The difference (compared to `VC_pre_post`) is that with algorithm
`VC_W_R` (and its extension `VC_W_R_Races`) we can immediately report
data race pairs while processing events.

Consider another trace. As before we annotate the trace with the
information collected by `VC_pre_post` and `VC_W_R_Races`.

       0##                  1##                   W(x)                   Race pairs
    1. [1,0]_w(x)_[2,0]                        { [1,0] }
    2. [2,0]_w(x)_[3,0]                        { [2,0] }
    3.                     [0,1]_w(x)_[0,2]    { [2,0], [0,1] }       ([2,0], [0,1])

We find the race pair (\[2,0\],\[0,1\]) which corresponds to the pair of
events (*w*(*x*)<sub>2</sub>,*w*(*x*)<sub>3</sub>). Based on the pre
vector clocks provided as annotations in the trace, we find another race
pair (\[1,0\],\[0,1\]) corresponding to
(*w*(*x*)<sub>1</sub>,*w*(*x*)<sub>3</sub>). This pair is *not* reported
by `VC_W_R_Races`.

The issue is that *W*(*x*) only maintains the most recent writes that
are not in happens before relation. By adding *w*(*x*)<sub>2</sub> (we
actually add the corresponding vector clock \[2, 0\]), we remove
*w*(*x*)<sub>1</sub> because \[1, 0\] &lt; \[2, 0\]. By the time we
process *w*(*x*)<sub>3</sub> we therefore only report the race pair
(*w*(*x*)<sub>2</sub>,*w*(*x*)<sub>3</sub>).

The offline approach based on algorithm `VC_pre_post` is able to detect
the write-write data race (*w*(*x*)<sub>1</sub>,*w*(*x*)<sub>3</sub>).

## Race pairs versus race locations

To be more efficient, we use a more more space efficient representation
for sets *W*(*x*) and *R*(*x*). Instead of the set *W*(*x*) of vector
clocks we only maintain a single vector clock *W**v*(*x*) that
represents the supremum of *W*(*x*). The same applies to *R*(*x*) where
we use vector clock *R**v*(*x*). This obviously saves space and time but
has the consequence that we can only report race locations (and not
pairs of events that are in a data race).

    Algorithm VC_RaceLoc for reporting data race locations:

    acq(i,y) {
      Th(i) = sync(Rel(y), Th(i))
      Th(i) = inc(Th(i), i)
    }

    rel(i,y) {
      Rel(y) = Th(i)
      Th(i) = inc(Th(i), i)
    }

    read(i,x) {
      Rv(x) = sync(Rv(x), Th(i))
      If !happensBefore(Wv(x), Th(i)) then the read Th(i) is part of a write-read data race
      Th(i) = inc(Th(i), i)
    }

    write(i,x) {
      If !happensBefore(Rv(x), Th(i)) then the write Th(i) is part of a write-read data race
      If !happensBefore(Wv(x), Th(i)) then the write Th(i) is part of a write-write data race
      Wv(x) = sync(Wv(x), Th(i))
      Th(i) = inc(Th(i), i)
    }

Let's compare algorithms `VC_W_R_Races` and `VC_RaceLoc`.

We make the following observations.

*V* ≤ *R**v*(*x*) for *V* ∈ *R*(*x*). *R**v*(*x*) is the supremum of
*R*(*x*).

*V* ≤ *W**v*(*x*) for *V* ∈ *W*(*x*). *W**v*(*x*) is the supremum of
*W*(*x*).

**Lemma:** If not *W**v*(*x*) &lt; *T**h*(*i*) then there exists
*V* ∈ *W*(*x*) such that not *V* &lt; *T**h*(*i*).

**Proof:** Suppose for all *V* ∈ *W*(*x*) we have *V* &lt; *T**h*(*i*).
In combination with *W**v*(*x*) &lt; *T**h*(*i*) contradiction to the
fact that *W**v*(*x*) is the supremum of *W*(*x*). QED.

**Lemma:** If not *R**v*(*x*) &lt; *T**h*(*i*) then there exists
*V* ∈ *R*(*x*) such that not *V* &lt; *T**h*(*i*).

**Proof:** Adaption of the proof of Lemma 1. QED.

Based on the above Lemmas we can argue that the read Th(i) and write
Th(i) reported by algorithm `VC_RaceLoc` are part of a HB data race
pair. We refer to Th(i) (respectively the corresponding event) as a
*race location*.

It also immediately follows that race locations cover all race pairs.
For each race pair (*V*<sub>1</sub>,*V*<sub>2</sub>) reported by
`VC_W_R_Races` we have that `VC_RaceLoc` reports the race location
*V*<sub>2</sub>.

## Optimization - Update time stamp instead of full synchronization

Algorithm `VC_RaceLoc` maintains vector clocks `Wv(x)` and `Rv(x)`. Both
represent the supremum of the most recent concurrent writes and reads
that we have seen so far. The supremum is built by applying `sync`.

    Rv(x) = sync(Rv(x), Th(i))     // R1

and

    Wv(x) = sync(Wv(x), Th(i))     // W1

Function `sync` requires time *O*(*k*) where *k* is the number of
threads (and size of vector clocks). In this specific context, `sync` is
actually not required. It suffices to adjust the time stamp of
*R**v*(*x*) and *W**v*(*x*) for thread i. The above statements R1 and W2
can be replaced as follows

    Rv(x)(i) = Th(i)(i)             // R2

and

    Wv(x)(i) = Th(i)(i)             // W2

where we write *V*(*i*) to access the time stamp of thread *i* for
vector clock *V*. For example, via *T**h*(*i*)(*i*) we access the time
stamp of thread *i*. Recall that *T**h*(*i*) refers to thread *i*'s
vector clock.

Statements W1 and W2 as well as R1 and R2 are equivalent. This is
guaranteed by the following property.

**Lemma:**

Let *W*(*x*) = {*V*<sub>1</sub>, ..., *V*<sub>*n*</sub>} be the set of
concurrent writes as found in algorithm `VC_W_R_Races`. Consider
*V*<sub>*p*</sub>, *V*<sub>*q*</sub> ∈ *W*(*x*) where *V*<sub>*p*</sub>
results from thread *i* and *V*<sub>*q*</sub> results from thread *j*.
Then, we find that *V*<sub>*p*</sub>(*i*) ≥ *V*<sub>*q*</sub>(*i*) and
*V*<sub>*q*</sub>(*j*) ≥ *V*<sub>*p*</sub>(*j*).

**Proof:**

We prove the above statements by contradiction.

Suppose *V*<sub>*p*</sub>(*i*) &lt; *V*<sub>*q*</sub>(*i*). This means
that thread *i* must have been synchronized with thread *j* where
synchronization involves some critical sections. But this then implies
that *V*<sub>*p*</sub> and *V*<sub>*q*</sub> are not concurrent (i.e.
incomparable) which is a contradiction. Hence, we find that
*V*<sub>*p*</sub>(*i*) ≤ *V*<sub>*q*</sub>(*i*).

Similarily, we can establish that
*V*<sub>*q*</sub>(*j*) ≥ *V*<sub>*p*</sub>(*j*). QED.

A similar property applies to *R*(*x*).

Based on the earlier lemma that shows that *W**v*(*x*) is the supremum
of *W*(*x*) and the above lemma, the statement

    Wv(x) = sync(Wv(x), Th(i))     // W1

can be replaced by

    Wv(x)(i) = Th(i)(i)             // W2

with no change in result.

The same applies to *R**v*(*x*).

Here's the optimized variant of algorithm `VC_RaceLoc`.

    Algorithm VC_RaceLoc_Optimized:

    acq(i,y) {
      Th(i) = sync(Rel(y), Th(i))
      Th(i) = inc(Th(i), i)
    }

    rel(i,y) {
      Rel(y) = Th(i)
      Th(i) = inc(Th(i), i)
    }

    read(i,x) {
      Rv(x)(i) = Th(i)(i)
      If !happensBefore(Wv(x), Th(i)) then the read Th(i) is part of a write-read data race
      Th(i) = inc(Th(i), i)
    }

    write(i,x) {
      If !happensBefore(Rv(x), Th(i)) then the write Th(i) is part of a write-read data race
      If !happensBefore(Wv(x), Th(i)) then the write Th(i) is part of a write-write data race
      Wv(x)(i) = Th(i)(i)
      Th(i) = inc(Th(i), i)
    }

## Optimization - Epochs (thread id + time stamp) instead of vector clocks

So far, we compare vector clocks to decide if events involved are
(un)ordered with respect to the HB relation, Consider read/write events
*e*, *f* where *V*<sub>*e*</sub> is *e*'s pre vector clock
*V*<sub>*f*</sub> is *f*'s pre vector clock. Events *e*, *f* are
unordered with respect to the HB relation iff vector clocks
*V*<sub>*e*</sub>, *V*<sub>*f*</sub> are incomparable.

It turns out that we do not need to consider the entire vector clock
when deciding if events are unordered with respect to the HB relation.
It suffices to compare time stamps of the later event in the trace.

Let *V* be a vector cock and *i* be a thread id. We write *V*\[*i*\] to
denote the time stamp of thread *i* for vector clock *V*.

**Lemma:**

Let *e*, *f* be two read/write events where *V*<sub>*e*</sub> is *e*'s
pre vector clock and *V*<sub>*f*</sub> is *f*'s pre vector clock. Event
*e* appears before *f* in the trace and *e*, *f* result from different
threads. Event *e* is in thread *j* and event *f* is in thread *i*.

Then, we have that
*V*<sub>*f*</sub>\[*j*\] &lt; *V*<sub>*e*</sub>\[*j*\] iff *e*, *f* are
unordered with respect to the HB relation.

**Proof:**

Consider the direction from left to right. If
*V*<sub>*f*</sub>\[*j*\] &lt; *V*<sub>*e*</sub>\[*j*\] then immediately
*V*<sub>*e*</sub> &lt; *V*<sub>*f*</sub> does not hold. Because *e*
appears before *f* in the trace, we also find that
*V*<sub>*f*</sub> &lt; *V*<sub>*e*</sub> does not hold. Hence, vector
clocks *V*<sub>*e*</sub>, *V*<sub>*f*</sub> are incomparable and this
means that events *e*, *f* are unordered with respect to the HB
relation.

Consider the direction from right to left. Events *e*, *f* are unordered
with respect to the HB relation. Hence, their vector clocks
*V*<sub>*e*</sub>, *V*<sub>*f*</sub> are incomparable.

Suppose *V*<sub>*e*</sub>\[*j*\] ≤ *V*<sub>*f*</sub>\[*j*\]. This means
that there must have been some synchronization between thread *j* and
*i* when processing *e* or some later event in thread *j*. But this then
impliesthat *V*<sub>*e*</sub> ≤ *V*<sub>*f*</sub> which is a
contradiction to the assumption that vector clocks
*V*<sub>*e*</sub>, *V*<sub>*f*</sub> are incomparable. Hence,
*V*<sub>*f*</sub>\[*j*\] &lt; *V*<sub>*e*</sub>\[*j*\]. QED.

Based on the above lemma, instead of vector clocks we use sets of
epochs.

An **epoch** is a pair of a thread id *j* and time stamp *k*, written
*j*\##*k*.

Each write/read event can be uniquely identified by an epoch. Suppose
*V* is the pre vector clock of read/write in thread *i*. Then, the
read/write's epoch is *i*\##*V*(*i*).

We adapt algorithm `VC_RaceLoc` as follows. Instead of *W**v*(*x*) and
*R**v*(*x*), we use set *W**e*(*x*) where *W**e*(*x*) maintains a set of
(write) epochs and set *R**e*(*x*) where *R**e*(*x*) maintains a set of
(read) epochs. We no longer compare entire vector clocks to decide if
two events are in happens-before relation. We only compare their epochs.

    Algorithm VC_RaceLoc_epochs for reporting data race locations using epochs:

    acq(i,y) {
      Th(i) = sync(Rel(y), Th(i))
      Th(i) = inc(Th(i), i)
    }

    rel(i,y) {
      Rel(y) = Th(i)
      Th(i) = inc(Th(i), i)
    }

    read(i,x) {
      Re(x) = { i ## Th(i)(i) } cup { j ## k | j ## k in Re(x) /\ k > Th(i)(j) }
      If exists j ## k in We(x) such that k > Th(i)(j) then Th(i) is part of a write-read data race
      Th(i) = inc(Th(i), i)
    }

    write(i,x) {
      If exists j ## k in Re(x) such that k > Th(i)(j) then Th(i) is part of a write-read data race
      If exists j ## k in We(x) such that k > Th(i)(j) then Th(i) is part of a write-write data race
      We(x) = { i ## Th(i)(i) } cup { j ## k | j ## k in We(x) /\ k > Th(i)(j) }
      Wv(x) = sync(Wv(x), Th(i))
      Th(i) = inc(Th(i), i)
    }

Based on the above lemma, we can argue that `VC_RaceLoc` and
`VC_RaceLoc_epochs` report the same set of race locations.

Observations.

### Epochs to identify race pairs

Based on the epoch representation of concurrent reads/writes and the
fact that epochs uniquely identify events, it would be straightforward
to report race pairs instead of just race locations.

### Set of epochs as vector clock

Maintaining a growing and shrinking set of epochs can be costly. This
applies for cases where many elements are added but also removed.

A 'simple' representation of *W**e*(*x*) and *R**e*(*x*) is to use
vector clocks where the time stamps of not present entries are set to
zero. Then, there are no longer any significant performance gains as
instead of epochs/time stamps we manage and compare vector clocks. The
actual benefit is that based on epochs represented as part of vector
clocks, we can identify race pairs instead of just reporting race
locations.

### Adaptive approach

To enjoy the performance benefits of epoch when checking for
happens-before we consider an adaptive approach where we switch between
an epoch and a vector clock (representing a set of epochs).

We write \[0, ..., 0\] to denote an initially zeroed vector clock. We
write \[*j*\##*k*, *i*\##*l*\] to denote a vector clock where entry *j*
has time stamp *k*, entry *i* has time stamp *l* and all other time
stamps are zeroed.

Components *R**h*(*x*) and *W**h*() may either refer to an epoch or a
vector clock (h stands for hybrid) We use switch-case pattern-matching
notation to distinguish between the two cases.

    Algorithm Adaptive_Epoch:
    Initially,
      Rh(x) = [0,...,0]
      Wh(x) = [0,...,0]

    acq(i,y) {
      Th(i) = sync(Rel(y), Th(i))
      Th(i) = inc(Th(i), i)
    }

    rel(i,y) {
      Rel(y) = Th(i)
      Th(i) = inc(Th(i), i)
    }

    read(i,x) {
      // check for write-read races
      switch Wh(x) {
        case j ## k:
           if k < Th(i)(j)
           then write-read race pair (j ## k, i ## Th(i)(i))

        case V:
           if !(V < Th(i))
           then read i ## Th(i)(i) is part of a write-read race
      }

      // adaptive update Rh(x)
      switch Rh(x) {
        case j ## k:
           if k < Th(i)(j)
           then Rh(x) = [ j ## k, i ## Th(i)(i) ]
           else Rh(x) = i ## Th(i)(i)

        case V:
           if V < Th(i)
           then Rh(x) = i ## Th(i)(i)
           else V(i) = Th(i)(i)
                Rh(x) = V

      }
      Th(i) = inc(Th(i), i)
    }

    write(i,x) {
      // check for write-write races
      switch Wh(x) {
        case j ## k:
           if k < Th(i)(j)
           then write-write race pair (j ## k, i ## Th(i)(i))
        case V:
           if !(V < Th(i))
           then write i ## Th(i)(i) is part of a write-write race
      }

      // check for read-write races
      switch Rh(x) {
        case j ## k:
           if k < Th(i)(j)
           then read-write race pair (j ## k, i ## Th(i)(i))

        case V:
           if !(V < Th(i))
           then write i ## Th(i)(i) is part of a read-write race
      }

      // adaptive update Wh(x)
      switch Wh(x) {
        case j ## k:
           if k < Th(i)(j)
           then Rh(x) = [ j ## k, i ## Th(i)(i) ]
           else Rh(x) = i ## Th(i)(i)

        case V:
           if V < Th(i)
           then Wh(x) = i ## Th(i)(i)
           else V(i) = Th(i)(i)
                Wh(x) = V
      }

      Th(i) = inc(Th(i), i)
    }

We first check for races and then update *R**e**h*(*x*) and
*W**e**h*(*x*). Some of the checks (e.g. `V < Th(i)`) are carried out
twice. In an efficient implementation, we could carry out updating of
*R**e**h*(*x*) and *W**e**h*(*x*) as part of the race check. For ease of
presentation, we prefer to keep the race check part and the update part
separate.

In case *R**h*(*x*) and *W**h*(*x*) refer to an epoch, we only need to
compare time stamps instead of entire vector clocks. In this case it is
also straightforward to identify race pairs instead of just race
locations.

*R**h*(*x*) and *W**h*(*x*) may become vector clocks in case of multiple
concurent reads/writes. A vector clock may be turned back into an epoch
if the current read/write subsumes the reads/writes we have seen so far.
We say that *R**h*(*x*) and *W**h*(*x*) are fully adaptive. Being fully
adaptive requires some vector clock comparison.

### FastTrack - Semi adaptive

The [FastTrack](https://dl.acm.org/doi/10.1145/1543135.1542490)
algorithm implements a semi-adaptive approach.

    Algorithm FastTrack style:
    Initially,
      Rh(x) = 0 ## 0
      Ws(x) = 0 ## 0

    acq(i,y) {
      Th(i) = sync(Rel(y), Th(i))
      Th(i) = inc(Th(i), i)
    }

    rel(i,y) {
      Rel(y) = Th(i)
      Th(i) = inc(Th(i), i)
    }

    read(i,x) {
      // check for write-read races
      switch Ws(x) {
        case j ## k:
           if k < Th(i)(j)
           then write-read race pair (j ## k, i ## Th(i)(i))
      }

      // semi-adaptive update Rh(x)
      switch Rh(x) {
        case j ## k:
           if k < Th(i)(j)
           then Rh(x) = [ j ## k, i ## Th(i)(i) ]
           else Rh(x) = i ## Th(i)(i)

        case V:
           V(i) = Th(i)(i)
           Rh(x) = V

      }
      Th(i) = inc(Th(i), i)
    }

    write(i,x) {
      // check for write-write races
      switch Ws(x) {
        case j ## k:
           if k < Th(i)(j)
           then write-write race pair (j ## k, i ## Th(i)(i))
      }

      // check for read-write races
      switch Rh(x) {
        case j ## k:
           if k < Th(i)(j)
           then read-write race pair (j ## k, i ## Th(i)(i))

        case V:
           if !(V < Th(i))
           then write i ## Th(i)(i) is part of a read-write race
      }

      // update Ws(x)
      Ws(x) = i ## Th(i)(i)

      Th(i) = inc(Th(i), i)
    }

Once we switch to a vector clock for reads, we maintain this vector
clock. The assumption is that concurrent reads are very frequent. In
case of writes, we always maintain an epoch represented by *W**s*(*x*)
(single epoch). This assumes that writes are totally ordered (not the
case in general).

Algorithm `Adaptive_Epoch` reports the same race locations as all othe
other (online) algorithms. Algorithm `FastTrack` may miss out on some
locations.

Consider the following example.

       T1        T2

    1. w(x)
    2.          w(x)
    3.          w(x)

`FastTrack` does not report that *w*(*x*)<sub>3</sub> is part of a data
race.

### Further variants

The [go data race
detector](https://golang.org/doc/articles/race_detector.html) does not
seem to use vector clocks to represent concurrent reads/writes and only
keeps track of the last four accesses.

## Summary

For an efficient offline approach to compute all HB data race pairs see
[Efficient, Near Complete and Often Sound Hybrid Dynamic Data Race
Prediction (extended version)](https://arxiv.org/abs/2004.06969).

## Open questions

Algorithm `VC_RaceLoc` versus the DJIT+ algorithm presented in
[MultiRace: Efficient on-the-fly datarace detection in multithreaded C++
programs](https://dl.acm.org/doi/10.1145/781498.781529)

Both are the same, any differences?

## Implementation in Go

    package main

    // Dynamic data race predictors based on HB and lockset.
    //
    // We only consider the trace and ignore the issue of instrumentation and tracing.

    // Fairly generic framework
    // where we consider HB and lockset as instances.
    // We include fork/join events.
    // Lockset race predictor ignores cases that are
    // happens-before ordered based on fork/join events.

    import "fmt"
    import "strconv"
    import "strings"

    ///////////////////////////////////////////////////////////////
    // Helpers

    func max(x, y int) int {
        if x < y {
            return y
        }
        return x
    }

    func debug(s string) {

        fmt.Printf("%s", s)
    }

    // Set of strings.
    // We use map[string]bool to emulate sets of strings.
    // The default value for bool is true.
    // Hence, if the (string) key doesn't exist, we obtain false = element not part of the set.
    // In case of add and remove, we use pointers to emulate call-by-reference.

    // We won't define an interface as we only use a specific instance of Set.

    type Set map[string]bool

    func mkSet() Set {
        return make(map[string]bool)
    }

    func (set Set) copy() Set {
        c := make(map[string]bool)
        for k, v := range set {
            c[k] = v
        }
        return c
    }

    func (set Set) show(vars []string) string {
        var s string
        i := 1
        for k, v := range set {
            if v {
                s = s + k
                i++
                if i < len(set) {
                    s = s + ","
                }
            }

        }
        return ("{" + s + "}")
    }

    func (set Set) empty() bool {
        return len(set) == 0
    }

    func (set Set) elem(n string) bool {
        return set[n]
    }

    func (set Set) add(n string) Set {
        s := set
        s[n] = true
        return s
    }

    //  union(a,b) ==> c,true
    //    if there's some element in b that is not an element in a
    //  union(a,b) ==> c,false
    //    if all elements in b are elements in a
    func (a Set) union(b Set) (Set, bool) {
        r := true
        for x, _ := range b {
            if !a.elem(x) {
                r = false
                a = a.add(x)
            }
        }
        return a, r

    }

    func (a Set) intersection(b Set) Set {
        c := mkSet()

        for x, _ := range a {
            if b.elem(x) {
                c = c.add(x)
            }

        }
        return c

    }

    func (a Set) disjoint(b Set) bool {
        return a.intersection(b).empty()
    }

    func (set Set) remove(n string) Set {
        s := set
        s[n] = false
        return s
    }

    ///////////////////////////////////////////////////////////////
    // Events

    type EvtKind int

    const (
        AcquireEvt EvtKind = 0
        ReleaseEvt EvtKind = 1
        WriteEvt   EvtKind = 2
        ReadEvt    EvtKind = 3
        ForkEvt    EvtKind = 4
        JoinEvt    EvtKind = 5
    )

    type THREAD_ID int

    // Acquire - Read make use of arg1
    // Fork and Join make use of arg2
    type ARGUMENTS struct {
        arg1_ string
        arg2_ THREAD_ID
    }

    type EVENT struct {
        k_   EvtKind
        id_  THREAD_ID
        loc_ int
        arg_ ARGUMENTS
    }

    type Event interface {
        thread() THREAD_ID
        loc() int
        kind() EvtKind
        args() ARGUMENTS
        name() string
        forkedJoined() THREAD_ID
    }

    func (e EVENT) thread() THREAD_ID { return e.id_ }
    func (e EVENT) loc() int          { return e.loc_ }
    func (e EVENT) kind() EvtKind     { return e.k_ }
    func (e EVENT) args() ARGUMENTS   { return e.arg_ }

    // Only applies to read/write and acquire/release.
    func (e EVENT) name() string { return e.arg_.arg1_ }

    // Only applies to fork/join.
    func (e EVENT) forkedJoined() THREAD_ID { return e.arg_.arg2_ }

    // "make" functions.
    func mkRead(i THREAD_ID, l int, n string) Event {
        return EVENT{ReadEvt, i, l, ARGUMENTS{arg1_: n}}
    }

    func mkWrite(i THREAD_ID, l int, n string) Event {
        return EVENT{WriteEvt, i, l, ARGUMENTS{arg1_: n}}
    }

    func mkAcq(i THREAD_ID, l int, n string) Event {
        return EVENT{AcquireEvt, i, l, ARGUMENTS{arg1_: n}}
    }

    func mkRel(i THREAD_ID, l int, n string) Event {
        return EVENT{ReleaseEvt, i, l, ARGUMENTS{arg1_: n}}
    }

    func mkFork(i THREAD_ID, l int, n THREAD_ID) Event {
        return EVENT{ForkEvt, i, l, ARGUMENTS{arg2_: n}}
    }

    func mkJoin(i THREAD_ID, l int, n THREAD_ID) Event {
        return EVENT{JoinEvt, i, l, ARGUMENTS{arg2_: n}}
    }

    ///////////////////////////////////////////////////////////////
    // Trace + Display

    // Assumptions:
    // Threads have ids in ascending order starting with 0.
    // Names of read/writes and acquire/release are disjoint.
    type TRACE []Event

    // Pre-process trace and compute a triple consisting of
    // (names of reads+writes, names of locks, hightest thread id)
    func preprocess(t TRACE) (Set, Set, THREAD_ID) {
        rw_names := mkSet()
        lock_names := mkSet()
        n := 0

        for _, e := range t {
            if (int)(e.thread()) > n {
                n = (int)(e.thread())
            }
            switch {
            case e.kind() == ReadEvt || e.kind() == WriteEvt:
                rw_names = rw_names.add(e.name())
            case e.kind() == AcquireEvt || e.kind() == ReleaseEvt:
                lock_names = lock_names.add(e.name())

            }

        }

        return rw_names, lock_names, (THREAD_ID)(n)

    }

    // Tabular display of trace.

    const (
        ROW_OFFSET = 8
    )

    // Omit thread + loc info.
    func displayEvtSimple(e Event) string {
        var s string
        switch {
        case e.kind() == AcquireEvt:
            s = "acq(" + e.name() + ")"
        case e.kind() == ReleaseEvt:
            s = "rel(" + e.name() + ")"
        case e.kind() == WriteEvt:
            s = "w(" + e.name() + ")"
        case e.kind() == ReadEvt:
            s = "r(" + e.name() + ")"
        case e.kind() == ForkEvt:
            s = "fork(" + strconv.Itoa((int)(e.forkedJoined())) + ")"
        case e.kind() == JoinEvt:
            s = "join(" + strconv.Itoa((int)(e.forkedJoined())) + ")"
        }
        return s
    }

    func displayEvt(e Event) string {
        s := displayEvtSimple(e)
        s = strconv.Itoa((int)(e.thread())) + "##" + s + "_" + strconv.Itoa(e.loc())
        return s
    }

    func colOffset(i THREAD_ID) string {
        n := (int)(i)
        return strings.Repeat(" ", n*ROW_OFFSET)
    }

    // Thread ids fully cover [0..n]
    func displayTrace(t TRACE) string {
        s := ""
        m := 0
        for _, e := range t {
            row := "\n" + strconv.Itoa(e.loc()) + ". " + colOffset(e.thread()) + displayEvtSimple(e)
            s = s + row
            m = max(m, (int)(e.thread()))
        }
        // Add column headings.
        heading := "   "
        for i := 0; i <= m; i++ {
            heading += strconv.Itoa(i) + "##" + strings.Repeat(" ", ROW_OFFSET-2)
        }
        s = heading + s

        return s
    }

    // Vector clocks

    type Vectorclock interface {
        print()
        copy() Vectorclock
        length() int
        inc(THREAD_ID) Vectorclock
        get(THREAD_ID) int
        sync(Vectorclock) Vectorclock
        happensBefore(Vectorclock) bool
    }

    type VCasSLICE []int

    // Init vector clock of thread i
    func initVC(t int, i int) Vectorclock {
        // make zeroed slice of len t
        v := make([]int, t)
        // then set thread i's timestamp to 1
        v[i] = 1
        return (VCasSLICE)(v)

    }

    // Init vector clock where all entries set to zero.
    func zeroVC(t int) Vectorclock {
        // make zeroed slice of len t
        v := make([]int, t)
        return (VCasSLICE)(v)

    }

    func resizeSlice(v VCasSLICE, t int) VCasSLICE {
        current := len(v)

        for len(v) <= t {

            current = len(v) * 2
        }

        newV := make([]int, current)
        copy(newV, v)

        return newV
    }

    func (v VCasSLICE) print() {
        fmt.Printf("[")
        for index, elem := range v {
            fmt.Printf("%d:%d ", index, elem)

        }
        fmt.Printf("]")

    }

    func (v VCasSLICE) copy() Vectorclock {
        new := make(VCasSLICE, len(v))
        copy(new, v)
        return new
    }

    func (v VCasSLICE) length() int {
        return len(v)
    }

    func (v VCasSLICE) inc(t THREAD_ID) Vectorclock {
        v[t] = v[t] + 1
        return v
    }

    func (v VCasSLICE) get(t THREAD_ID) int {
        n := (int)(t)
        if len(v) < n {
            return 0
        }
        return v[n]
    }

    func (v VCasSLICE) sync(v2 Vectorclock) Vectorclock {
        l := max(v.length(), v2.length())

        v3 := make([]int, l)

        for index, _ := range v3 {

            tid := (THREAD_ID)(index)
            v3[index] = max(v.get(tid), v2.get(tid))
        }

        return (VCasSLICE)(v3)
    }

    func (v VCasSLICE) happensBefore(v2 Vectorclock) bool {
        b := false
        for i := 0; i < max(v.length(), v2.length()); i++ {
            tid := (THREAD_ID)(i)
            if v.get(tid) > v2.get(tid) {
                return false
            } else if v.get(tid) < v2.get(tid) {
                b = true
            }

        }
        return b

    }

    ///////////////////////////////////////////////////////////////
    // Generic data race predictor

    // Each event comes with a vector clock.
    // The lockset entry will be used by only only some data race predictor instances.
    // The generic data race predictor part does not refer to the lockset entry.
    type EvtInfo struct {
        evt Event
        vc  Vectorclock
        ls  Set
    }

    // Given some event e and its vector clock vc,
    // select from cs all events that are concurrent wrt (e,vc).
    // If vector clock of vc `happens before` vc, then not concurent.
    // Otherwise, concurrent.
    func selConc(e Event, vc Vectorclock, cs []EvtInfo) []EvtInfo {

        new := make([]EvtInfo, 0, len(cs))
        for _, elem := range cs {
            b := elem.vc.happensBefore(vc)
            if !b {
                new = append(new, elem)
            }

        }
        return new
    }

    func printEvtInfo(es []EvtInfo) {
        fmt.Printf("\n")
        for _, e := range es {
            fmt.Printf("%s ", displayEvt(e.evt))
            e.vc.print()
            fmt.Printf(" ")
        }

    }

    type RacePair struct {
        left  EvtInfo
        right EvtInfo
    }

    func addRacePairs(ps []RacePair, new []RacePair) []RacePair {
        if cap(ps) < len(ps)+len(new) {
            new := make([]RacePair, len(ps), 2*len(ps)+len(new)+1)
            copy(new, ps)
            ps = new

        }
        ps = append(ps, new...)
        return ps
    }

    func printRaces(r []RacePair) {
        for _, p := range r {
            fmt.Printf("\n%s -- %s", displayEvt(p.left.evt), displayEvt(p.right.evt))
        }

    }

    type RacePredictor interface {
        init(TRACE)
        acquire(Event)
        release(Event)
        fork(Event)
        join(Event)
        write(Event) []RacePair
        read(Event) []RacePair
    }

    func run(r RacePredictor, t TRACE) []RacePair {
        races := make([]RacePair, 0, 10)
        r.init(t)

        for _, e := range t {
            switch {
            case e.kind() == AcquireEvt:
                r.acquire(e)
            case e.kind() == ReleaseEvt:
                r.release(e)
            case e.kind() == ForkEvt:
                r.fork(e)
            case e.kind() == JoinEvt:
                r.join(e)
            case e.kind() == WriteEvt:
                newRaces := r.write(e)
                races = addRacePairs(races, newRaces)
            case e.kind() == ReadEvt:
                newRaces := r.read(e)
                races = addRacePairs(races, newRaces)

            }

        }
        return races

    }

    ///////////////////////////////////////////////////////////////
    // Lockset style data race predictor (similar to TSan V1)
    //
    // We consider fork-join happens-before relations.

    // Clone lockset and vectorclock.
    func mkEvtInfoLS(e Event, v Vectorclock, l Set) EvtInfo {
        l_ := l.copy()
        v_ := v.copy()
        return EvtInfo{evt: e, vc: v_, ls: l_}
    }

    type LS struct {
        namesRW   Set                    // names of shared variables
        namesLock Set                    // names of lock variables
        ls        []Set                  // each thread has its lockset
        thread    []Vectorclock          // each thread has its vector clock
        writes    map[string]([]EvtInfo) // current set of concurrent writes for each variable
        reads     map[string]([]EvtInfo) // current set of concurent reads for each variable
    }

    func (tsan *LS) init(t TRACE) {
        var max_tid THREAD_ID

        tsan.namesRW, tsan.namesLock, max_tid = preprocess(t)
        n := (int)(max_tid)

        // Make + init locksets and vectorclocks.
        tsan.thread = make([]Vectorclock, n+1)
        tsan.ls = make([]Set, n+1)

        for i, _ := range tsan.thread {
            tsan.thread[i] = initVC(n+1, i)
            tsan.ls[i] = mkSet()
        }

        // Make maps.
        tsan.writes = make(map[string]([]EvtInfo))
        tsan.reads = make(map[string]([]EvtInfo))

    }

    // Acquire adds lock name to lockset.
    func (tsan *LS) acquire(e Event) {
        s := *tsan
        tid := e.thread()
        s.ls[tid] = s.ls[tid].add(e.name())
        s.thread[tid] = s.thread[tid].inc(tid)
    }

    // Release removes lock name from lockset.
    func (tsan *LS) release(e Event) {
        s := *tsan
        tid := e.thread()
        s.ls[tid] = s.ls[tid].remove(e.name())
        s.thread[tid] = s.thread[tid].inc(tid)
    }

    // Sync forked thread with current thread.
    func (tsan *LS) fork(e Event) {
        tid := e.thread()
        fork_tid := e.forkedJoined()
        tsan.thread[fork_tid] = tsan.thread[fork_tid].sync(tsan.thread[tid])
        tsan.thread[tid] = tsan.thread[tid].inc(tid)
    }

    // Sync current thread with to be joined thread.
    func (tsan *LS) join(e Event) {
        tid := e.thread()
        join_tid := e.forkedJoined()
        tsan.thread[tid] = tsan.thread[tid].sync(tsan.thread[join_tid])
        tsan.thread[tid] = tsan.thread[tid].inc(tid)
    }

    // 1. Select all reads/writes that are concurrent wrt the write.
    // 2. Check if any of the locksets is disjoint wrt the write.
    //    If yes build a new race pair.
    // 3. Adjust concurrent reads/writes. Add write to concurrent writes.
    // 4. Report new races.
    func (tsan *LS) write(e Event) []RacePair {
        tid := e.thread()

        concWrites := selConc(e, tsan.thread[tid], tsan.writes[e.name()])
        concReads := selConc(e, tsan.thread[tid], tsan.reads[e.name()])

        // Clone the event's vector clock and lockset when reporting races.
        newElem := mkEvtInfoLS(e, tsan.thread[tid], tsan.ls[tid])

        newRaces := make([]RacePair, 0, len(concWrites)+len(concReads))
        for _, elem := range concWrites {
            if tsan.ls[tid].disjoint(elem.ls) {
                newRaces = append(newRaces, RacePair{elem, newElem})
            }
        }

        for _, elem := range concReads {
            if tsan.ls[tid].disjoint(elem.ls) {
                newRaces = append(newRaces, RacePair{elem, newElem})
            }
        }

        tsan.writes[e.name()] = append(concWrites, newElem)
        tsan.reads[e.name()] = concReads

        tsan.thread[tid] = tsan.thread[tid].inc(tid)

        return newRaces

    }

    // Similar to write but don't consider read-read races (obviously).
    func (tsan *LS) read(e Event) []RacePair {
        tid := e.thread()

        concWrites := selConc(e, tsan.thread[tid], tsan.writes[e.name()])
        concReads := selConc(e, tsan.thread[tid], tsan.reads[e.name()])

        newElem := mkEvtInfoLS(e, tsan.thread[tid], tsan.ls[tid])

        newRaces := make([]RacePair, 0, len(concWrites))
        for _, elem := range concWrites {
            if tsan.ls[tid].disjoint(elem.ls) {
                newRaces = append(newRaces, RacePair{elem, newElem})
            }
        }

        tsan.writes[e.name()] = concWrites
        tsan.reads[e.name()] = append(concReads, newElem)

        tsan.thread[tid] = tsan.thread[tid].inc(tid)

        return newRaces
    }

    ////////////////////////////////////////////////////////////////////////////////////////////////////////
    // HB (happens-before with program order and critical section order) race predictor (similar to TSan V2)
    //
    // we compute happens-before relations via vector clocks.

    // Don't care about lockset entry for HB.
    func mkEvtInfoHB(e Event, v Vectorclock) EvtInfo {
        v_ := v.copy()
        return EvtInfo{evt: e, vc: v_}
    }

    type HB struct {
        namesRW     Set                    // names of shared variables
        namesLock   Set                    // names of lock variables
        ls          []Set                  // each thread has its lockset
        thread      []Vectorclock          // each thread has its vector clock
        lastRelease map[string]Vectorclock // vector clock of last release (for each lock variable)
        writes      map[string]([]EvtInfo) // current set of concurrent writes for each variable
        reads       map[string]([]EvtInfo) // current set of concurent reads for each variable
    }

    func (hb *HB) init(t TRACE) {
        var max_tid THREAD_ID

        hb.namesRW, hb.namesLock, max_tid = preprocess(t)
        n := (int)(max_tid)

        // Make + init vectorclocks.
        hb.thread = make([]Vectorclock, n+1)

        for i, _ := range hb.thread {
            hb.thread[i] = initVC(n+1, i)
        }

        // Make maps.
        hb.lastRelease = make(map[string]Vectorclock)
        hb.writes = make(map[string]([]EvtInfo))
        hb.reads = make(map[string]([]EvtInfo))

        for x, _ := range hb.namesLock {
            hb.lastRelease[x] = zeroVC(n + 1)

        }

    }

    func (hb *HB) acquire(e Event) {
        tid := e.thread()
        hb.thread[tid] = hb.thread[tid].sync(hb.lastRelease[e.name()])
        hb.thread[tid] = hb.thread[tid].inc(tid)
    }

    func (hb *HB) release(e Event) {
        tid := e.thread()
        hb.lastRelease[e.name()] = hb.thread[tid]
        hb.thread[tid] = hb.thread[tid].inc(tid)
    }

    // Same as for LS
    func (hb *HB) fork(e Event) {
        tid := e.thread()
        fork_tid := e.forkedJoined()
        hb.thread[fork_tid] = hb.thread[fork_tid].sync(hb.thread[tid])
        hb.thread[tid] = hb.thread[tid].inc(tid)
    }

    // Sync current thread with to be joined thread.
    func (hb *HB) join(e Event) {
        tid := e.thread()
        join_tid := e.forkedJoined()
        hb.thread[tid] = hb.thread[tid].sync(hb.thread[join_tid])
        hb.thread[tid] = hb.thread[tid].inc(tid)
    }

    func (hb *HB) write(e Event) []RacePair {
        tid := e.thread()

        concWrites := selConc(e, hb.thread[tid], hb.writes[e.name()])
        concReads := selConc(e, hb.thread[tid], hb.reads[e.name()])

        // Clone the event's vector clock when reporting races.
        newElem := mkEvtInfoHB(e, hb.thread[tid])

        newRaces := make([]RacePair, 0, len(concWrites)+len(concReads))
        for _, elem := range concWrites {
            newRaces = append(newRaces, RacePair{elem, newElem})
        }

        for _, elem := range concReads {
            newRaces = append(newRaces, RacePair{elem, newElem})
        }

        hb.writes[e.name()] = append(concWrites, newElem)
        hb.reads[e.name()] = concReads

        hb.thread[tid] = hb.thread[tid].inc(tid)

        return newRaces

    }

    func (hb *HB) read(e Event) []RacePair {
        tid := e.thread()

        concWrites := selConc(e, hb.thread[tid], hb.writes[e.name()])
        concReads := selConc(e, hb.thread[tid], hb.reads[e.name()])

        // Clone the event's vector clock when reporting races.
        newElem := mkEvtInfoHB(e, hb.thread[tid])

        newRaces := make([]RacePair, 0, len(concWrites)+len(concReads))
        for _, elem := range concWrites {
            newRaces = append(newRaces, RacePair{elem, newElem})
        }

        hb.writes[e.name()] = concWrites
        hb.reads[e.name()] = append(concReads, newElem)

        hb.thread[tid] = hb.thread[tid].inc(tid)

        return newRaces

    }

    ///////////////////////////////////////////
    // Example traces

    func trace0() TRACE {
        var t = TRACE{}
        return t
    }

    func trace1() TRACE {
        var t = TRACE{
            mkWrite(0, 1, "x"),
            mkWrite(1, 2, "x")}
        return t
    }

    func trace1b() TRACE {
        var t = TRACE{
            mkWrite(0, 1, "x"),
            mkFork(0, 2, 1),
            mkWrite(1, 3, "x"),
            mkWrite(1, 4, "x")}
        return t
    }

    func trace1c() TRACE {
        var t = TRACE{
            mkWrite(0, 1, "x"),
            //      mkFork(0, 2, 1),
            mkWrite(1, 3, "x"),
            mkWrite(1, 4, "x")}
        return t
    }

    func trace2() TRACE {
        var t = TRACE{
            // T0
            mkWrite(0, 1, "x"),
            mkAcq(0, 2, "y"),
            mkWrite(0, 3, "x"),
            mkRel(0, 4, "y"),
            // T1
            mkAcq(1, 5, "y"),
            mkWrite(1, 6, "x"),
            mkRel(1, 7, "y")}
        return t

    }

    func displayTraces() {
        out := displayTrace(trace1b())

        fmt.Printf("\n %s", out)
    }

    ///////////////////////////////////////////
    // Running tests

    func runTest(r RacePredictor, t TRACE) {
        fmt.Printf("%s", displayTrace(t))
        ps := run(r, t)
        printRaces(ps)
    }

    ///////////////////////////
    // Lockset tests

    func testLS(t TRACE) {
        var ls LS
        runTest(&ls, t)
    }

    ///////////////////////////
    // HB tests

    func testHB(t TRACE) {
        var hb HB
        runTest(&hb, t)
    }

    func main() {

        // displayTraces()
        //  testLS(trace1())
        // No race, trivial example.

        // testLS(trace1b())
        // No race, no race reported.
        // lockset algorithm combined with fork-join happens-before.

        //        testLS(trace1c())
        // Race reported.

        //        testLS(trace2())
        // No race reported cause we only keep track of the latest write.

        //  testHB(trace1())
        // No race, trivial example.

        // testHB(trace1b())

        // testHB(trace1c())
        // Race reported.

        //  testHB(trace2())
        // No race reported because critical sections are ordered

        fmt.Printf("\n done")
    }
