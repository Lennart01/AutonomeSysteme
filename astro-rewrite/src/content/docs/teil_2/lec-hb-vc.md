---
title: Dynamic data race prediction - Happens-before and vector clocks
description: Martin Sulzmann
---



## Overview

## Data race prediction

We say that two read/write operations on some shared variable are
*conflicting* if both operations arise in different threads and at least
one of the operations is a write.

## Dynamic analysis method

We consider a specific program run represented as a trace. The trace
contains the sequence of events as they took place during program
execution. Based on this trace, we carry out the analysis.

## Exhaustive versus efficient and approximative methods

To identify conflicting events that are in a race, we could check if
there is a valid reordering of the trace under which both events occur
right next to each other. In general, this requires to exhaustively
compute all reordering which is not efficient.

Efficient methods approximate by only considering certain reorderings.

## Happens-before

Some partial order relation to identify if one event happens before
another event.

In case of of unordered events, we can assume that these events may
happen concurrently.

The happens-before (partial) order approximates the *must* happen
relations. Hence, we may encounter false positives and false negatives.

## Vector clocks

Some efficient representation for the happens-before relation.

If two conflicting operations are unordered under the happens-before
relation, then we report that these operations are in a (data) race.

## Trace and event notation

We write *j*\##*e*<sub>*i*</sub> to denote event *e* at trace position
*i* in thread *j*.

In plain text notation, we sometimes write `j##e_i`.

We assume the following events.

    e ::=  acq(y)         -- acquire of lock y
       |   rel(y)         -- release of lock y
       |   w(x)           -- write of shared variable x
       |   r(x)           -- read of shared variable x

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

## Trace reordering

To predict if two conflicting operations are in a race we could
*reorder* the trace. Reordering the trace means that we simply permute
the elements.

Consider the example trace.

         T1          T2

    1.   w(x)
    2.   acq(y)
    3.   rel(y)
    4.               acq(y)
    5.               w(x)
    6.               rel(y)

Here is a possible reordering.

         T1          T2

    4.               acq(y)
    1.   w(x)
    2.   acq(y)
    3.   rel(y)
    5.               w(x)
    6.               rel(y)

This reordering is *not valid* because it violates the lock semantics.
Thread T2 holds locks y. Hence, its not possible for thread T1 to
acquire lock y as well.

Here is another invalid reordering.

         T1          T2

    2.   acq(y)
    3.   rel(y)
    4.               acq(y)
    1.   w(x)
    5.               w(x)
    6.               rel(y)

The order among elements in trace has changed. This is not allowed.

## Valid trace reordering

For a reordering to be valid the following rules must hold:

1.  The elements in the reordered trace must be part of the original
    trace.

2.  The order among elements for a given trace cannot be changed. See
    The Program Order Condition.

3.  For each release event rel(y) there must exist an earlier acquire
    event acq(y) such there is no event rel(y) in between. See the Lock
    Semantics Condition.

4.  Each read must have the same *last writer*. See the Last Writer
    Condition.

A valid reordering only needs to include a subset of the events of the
original trace.

Consider the following (valid) reordering.

         T1          T2

    4.               acq(y)
    5.               w(x)
    1.   w(x)

This reordering shows that the two conflicting events are in a data
race. We only consider a prefix of the events in thread T1 and thread
T2.

## Exhaustive data race prediction methods

A “simple” data race prediction method seems to compute all possible
(valid) reordering and check if they contain any data race. Such
*exhaustive* methods generally do not scale to real-world settings where
resulting traces may be large and considering all possible reorderings
generally leads to an exponential blow up.

## Approximative data race prediction methods

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

We consider here Lamport’s happens-before (HB) relation that
approximates the possible reorderings. The HB relation can be computed
efficiently but may lead to false positives and false negatives.

## Lamport’s happens-before (HB) relation

Let *T* be a trace. We define the HB relation `<` as the smallest
[strict partial
order](https://en.wikipedia.org/wiki/Partially_ordered_set##Strict_and_non-strict_partial_orders)
that satisfies the following conditions:

**Program order**

Let *j*\##*e*<sub>*i*</sub>, *j*\##*f*<sub>*i* + *n*</sub> ∈ *T* where
*n* &gt; 0. Then, we find that
*j*\##*e*<sub>*i*</sub> &lt; *j*\##*f*<sub>*i* + *n*</sub>.

**Critical section order**

Let
*i*\##*r**e**l*(*x*)<sub>*k*</sub>, *j*\##*a**c**q*(*x*)<sub>*k* + *n*</sub> ∈ *T*
where *i*! = *j* and *n* &gt; 0. Then, we find that
*i*\##*r**e**l*(*x*)<sub>*k*</sub> &lt; *j*\##*a**c**q*(*x*)<sub>*k* + *n*</sub>.

-   Program order states that for a specific threads, events are ordered
    based on their trace position.

-   Critical section order states that critical sections are ordered
    based on their trace position.

-   For each acquire the matching relase must be in the same thread.
    Hence, the critical section order only needs to consider a release
    and a later in trace appearing acquire.

## Example

Consider the trace

\[1\##*w*(*x*)<sub>1</sub>, 1\##*a**c**q*(*y*)<sub>2</sub>, 1\##*r**e**l*(*y*)<sub>3</sub>, 2\##*a**c**q*(*y*)<sub>4</sub>, 2\##*w*(*x*)<sub>5</sub>, 2\##*r**e**l*(*y*)<sub>6</sub>\].

Via program order we find that

1\##*w*(*x*)<sub>1</sub> &lt; 1\##*a**c**q*(*y*)<sub>2</sub> &lt; 1\##*r**e**l*(*y*)<sub>3</sub>

and

2\##*a**c**q*(*y*)<sub>4</sub> &lt; 2\##*w*(*x*)<sub>5</sub> &lt; 2\##*r**e**l*(*y*)<sub>6</sub>.

Via critical section order we find that

1\##*r**e**l*(*y*)<sub>3</sub> &lt; 2\##*a**c**q*(*y*)<sub>4</sub>.

Points to note.

&lt; is the smallest partial order that satisfies the above conditions.

Hence, by transitivity we can also assume that for example

1\##*w*(*x*)<sub>1</sub> &lt; 2\##*w*(*x*)<sub>5</sub>.

## Happens-before data race check

If for two conflicting events *e* and *f* we have that neither
*e* &lt; *f* nor *f* &lt; *e*, then we say that (*e*, *f*) is a *HB data
race pair*.

The argument is that if *e* &lt; *f* nor *f* &lt; *e* we are free to
reorder the trace such that *e* and *f* appear right next to each other
(in some reordered trace).

Note. If (*e*, *f*) is a *HB data race pair* then so is (*f*, *e*). In
such a situation, we consider (*e*, *f*) and (*f*, *e*) as two distinct
representative for the same data race. When reporting (and counting) HB
data races we only consider a specific representative.

## Event sets

Consider event *e*. We denote by *E**S*<sub>*e*</sub> the set of events
that happen-before *e*. We assume that *e* is also included in
*E**S*<sub>*e*</sub>. Hence,
*E**S*<sub>*e*</sub> = {*f* ∣ *f* &lt; *e*} ∪ {*e*}.

## Example - Trace annotated with event sets

We write `ei` to denote the event at trace position `i`.

         T1          T2            ES

    1.   w(x)                     ES_e1= {e1}
    2.   acq(y)                   ES_e2= {e1,e2}
    3.   rel(y)                   ES_e3 = {e1,e2,e3}
    4.               acq(y)       ES_e4 = ES_e3 cup {e4} = {e1,e2,e3,e4}
    5.               w(x)         ES_e5 = {e1,e2,e3,e4,e5}
    6.               rel(y)       ES_e6 = {e1,e2,e3,e4,e5,e6}

Observations:

To enforce the critical section order we simply need to add the event
set *E**S*<sub>*r**e**l*(*y*)</sub> of some release event to the event
set *E**S*<sub>*a**c**q*(*y*)</sub> of some later acquire event.

To enforce the program order, we keep accumulating events within one
thread (in essence, building the transitive closure).

To decide if *e* &lt; *f* we can check for
*E**S*<sub>*e*</sub> ⊂ *E**S*<sub>*f*</sub>.

Consider two conflicting events *e* and *f* where *e* appears before *f*
in the trace. To decide if *e* and *f* are in a race, we check for
*e* ∈ *E**S*<sub>*f*</sub>. If yes, then there’s no race (because
*e* &lt; *f*). Otherwise, there’s a race.

## Set-based race predictor

We maintain the following state variables.

    D(t)

      Each thread t maintains the set of events that happen before when processing events.


    R(x)

      Most recent set of concurrent reads.

    W(x)

      Most recent write.


    Rel(y)

      Critical sections are ordered as they appear in the trace.
      Rel(y) records the event set of the most recent release event on lock y.

All of the above are sets of events and assumed to be initially empty.
The exception is W(x). We assume that initially W(x) is undefined.

We write `e@operation` to denote that event `e` will be processed by
`operation`.

    e@acq(t,y) {
       D(t) = D(t) cup Rel(y) cup { e }
    }

    e@rel(t,y) {
       D(t) = D(t) cup { e }
       Rel(y) = D(t)

    e@fork(t1,t2) {
      D(t1) = D(t1) cup { e }
      D(t2) = D(t1)
    }

    e@join(t1,t2) {
      D(t1) = D(t1) cup D(t2) cup { e }
      }

    e@write(t,x) {
      If W(x) exists and W(x) not in D(t)
      then write-write race (W(x),e)

      For each r in R(x),
      if r not in D(t)
      then read-write race  (r,e)

      D(t) = D(t) cup { e }
      W(x) = e
    }

    e@read(t,x) {
      If W(x) exists and W(x) not in D(t)
      then write-read race (W(x),e)

      R(x) = {e} cup {r' | r' in R(x), r' \not\in D(t) }
      D(t) = D(t) cup { e }
    }

### Examples

### Race not detected

        T0            T1

    1.  fork(T1)
    2.  acq(y)
    3.  wr(x)
    4.  rel(y)
    5.                acq(y)
    6.                rel(y)
    7.                wr(x)

The HB relation does not reorder critical sections. Therefore, we report
there is no race. This is a false negative because there is a valid
reordering to shows the two writes on x are in a race.

Here’s the annotated trace with the information computed by the
set-based race predictor.

       T0            T1

    1.  fork(T1)
    2.  acq(y)                      D(T0) = [0:fork(T1)_1,0:acq(y)_2]
    3.  wr(x)                       W(x) = undefined
    4.  rel(y)                      Rel(y) = [0:fork(T1)_1,0:acq(y)_2,0:wr(x)_3,0:rel(y)_4]
    5.                acq(y)        D(T1) = [0:fork(T1)_1,0:acq(y)_2,0:wr(x)_3,0:rel(y)_4,1:acq(y)_5]
    6.                rel(y)        Rel(y) = [0:fork(T1)_1,0:acq(y)_2,0:wr(x)_3,0:rel(y)_4,1:acq(y)_5,1:rel(y)_6]
    7.                wr(x)         W(x) = 0:wr(x)_3

-   For each acquire in thread t we show D(t)

-   For each release on y we show Rel(y)

-   For each write on x we show the state of W(x) before processing the
    read

-   If there are any reads we also show R(x)

### Race detected

        T0            T1

    1.  fork(T1)
    2.  acq(y)
    3.  wr(x)
    4.  rel(y)
    5.                wr(x)
    6.                acq(y)
    7.                rel(y)

Under the HB relation, the two writes on x are not ordered. Hence, we
report that they are in a race.

Here’s the annotated trace.

        T0            T1

    1.  fork(T1)
    2.  acq(y)                      D(T0) = [0:fork(T1)_1,0:acq(y)_2]
    3.  wr(x)                       W(x) = undefined
    4.  rel(y)                      Rel(y) = [0:fork(T1)_1,0:acq(y)_2,0:wr(x)_3,0:rel(y)_4]
    5.                wr(x)         W(x) = 0:wr(x)_3
    6.                acq(y)        D(T1) = [0:fork(T1)_1,0:acq(y)_2,0:wr(x)_3,0:rel(y)_4,1:wr(x)_5,1:acq(y)_6]
    7.                rel(y)        Rel(y) = [0:fork(T1)_1,0:acq(y)_2,0:wr(x)_3,0:rel(y)_4,1:wr(x)_5,1:acq(y)_6,1:rel(y)_7]

### Earlier race not detected

        T0            T1

    1.  fork(T1)
    2.  acq(y)
    3.  wr(x)
    4.  wr(x)
    5.  rel(y)
    6.                wr(x)
    7.                acq(y)
    8.                rel(y)

The write at trace position 3 and the write at trace position 6 are in a
race. However, we only maintain the most recent write. Hence, we only
report that the write at trace position 4 is in a race with the write at
trace position 6.

Here’s the annotated trace.

        T0            T1

    1.  fork(T1)
    2.  acq(y)                      D(T0) = [0:fork(T1)_1,0:acq(y)_2]
    3.  wr(x)                       W(x) = undefined
    4.  wr(x)                       W(x) = 0:wr(x)_3
    5.  rel(y)                      Rel(y) = [0:fork(T1)_1,0:acq(y)_2,0:wr(x)_3,0:wr(x)_4,0:rel(y)_5]
    6.                wr(x)         W(x) = 0:wr(x)_4
    7.                acq(y)        D(T1) = [0:fork(T1)_1,0:acq(y)_2,0:wr(x)_3,0:wr(x)_4,0:rel(y)_5,1:wr(x)_6,1:acq(y)_7]
    8.                rel(y)        Rel(y) = [0:fork(T1)_1,0:acq(y)_2,0:wr(x)_3,0:wr(x)_4,0:rel(y)_5,1:wr(x)_6,1:acq(y)_7,1:rel(y)_8]

### Read-write races

        T0            T1            T2

    1.  wr(x)
    2.  fork(T1)
    3.  fork(T2)
    4.  rd(x)
    5.                rd(x)
    6.                              acq(y)
    7.                              wr(x)
    8.                              rel(y)

We find that the two reads are in a race with the write.

Here’s the annotated trace.

        T0            T1            T2

    1.  wr(x)                                     W(x) = undefined
    2.  fork(T1)
    3.  fork(T2)
    4.  rd(x)                                     W(x) = 0:wr(x)_1
    5.                rd(x)                       W(x) = 0:wr(x)_1
    6.                              acq(y)        D(T2) = [0:wr(x)_1,0:fork(T1)_2,0:fork(T2)_3,2:acq(y)_6]
    7.                              wr(x)         W(x) = 0:wr(x)_1  R(x) = [0:rd(x)_4,1:rd(x)_5]
    8.                              rel(y)        Rel(y) = [0:wr(x)_1,0:fork(T1)_2,0:fork(T2)_3,2:acq(y)_6,2:wr(x)_7,2:rel(y)_8]

Note that when processing the write in T2, we find that D(T2) contains
the earlier write.

## Can we find a more compact representation for D(t)?

The size of D(t) may grow linearly in the size of the trace.

To check for a race we check if some element is in D(t).

If there are n events, this means set-based race prediction requires
O(n\*n) time.

## From event sets to timestamps

## Timestamps

For each thread we maintain a timestamp.

We represent a timestamp as a natural number.

Each time we process an event we increase the thread’s timestamp.

Initially, the timestamp for each thread is 1.

## Example - Trace annotated with timestamps

         T1          T2      TS_T1       TS_T2

    1.   w(x)                  2
    2.   acq(y)                3
    3.   rel(y)                4
    4.               acq(y)               2
    5.               w(x)                 3
    6.               rel(y)               4

## Representing events via its thread id and timestamp

Let *e* be an event in thread *i* and *j* its timestamp.

Then, we can uniquely identify *e* via *i* and *j*.

We write *i*\##*j* to represent event *e*. In the literature, *i*\##*j* is
referred to as an *epoch*.

## Example - Trace annotated with epochs

         T1          T2           Epochs

    1.   w(x)                     1##1
    2.   acq(y)                   1##2
    3.   rel(y)                   1##3
    4.               acq(y)       2##1
    5.               w(x)         2##2
    6.               rel(y)       2##3

We use the timestamp “before” processing the event. We could also use
the timestamp “after” (but this needs to be done consistently).

## From event sets to sets of epoch

Instead of events sets we record the set of epochs.

We group together epochs belonging to the same thread. For example, in
case of {1\##1, 1\##2} we write {1\##{1, 2}}.

## Example - Trace annotated with sets of epochs

         T1          T2            Sets of epochs

    1.   w(x)                     {1##1}
    2.   acq(y)                   {1##{1,2}}
    3.   rel(y)                   {1##{1,2,3}}
    4.               acq(y)       {1##{1,2,3}, 2##1}
    5.               w(x)         {1##{1,2,3}, 2##{1,2}}
    6.               rel(y)       {1##{1,2,3}, 2##{1,2,3}}

## From sets of timestamps to vector clocks

Insight:

For each thread only keep most recent timestamp.

For example, in case of {1\##{1, 2}} we write {1\##2}

## Example - Trace annotated with most recent timestamps

         T1          T2            Sets of most recent timestamps

    1.   w(x)                     {1##1}
    2.   acq(y)                   {1##2}
    3.   rel(y)                   {1##3}
    4.               acq(y)       {1##3, 2##1}
    5.               w(x)         {1##3, 2##2}
    6.               rel(y)       {1##3, 2##3}

## Vector clocks

Instead of a set use a list (vector).

    V  ::=  [i1,...,in]    -- vector clock with n time stamps

The entry associated to each thread is identified via its position in
that list.

If there’s no entry for a thread, we assume the timestamp 0.

## Example - Trace annotated with vector clocks

         T1          T2            Vector clocks

    1.   w(x)                     [1,0]
    2.   acq(y)                   [2,0]
    3.   rel(y)                   [3,0]
    4.               acq(y)       [3,1]
    5.               w(x)         [3,2]
    6.               rel(y)       [3,3]

## Mapping event sets to vector clocks

Based on the above, each event set can be represented as the set
({1\##*E*<sub>1</sub>, ..., *n*\##*E*<sub>*n*</sub>} where sets
*E*<sub>*j*</sub> are of the form {1, ..., *k*}.

We define a mapping *Φ* from event sets to vector clocks as follows.

*Φ*({1\##*E*<sub>1</sub>, ..., *n*\##*E*<sub>*n*</sub>}) = \[*m**a**x*(*E*<sub>1</sub>), ..., *m**a**x*(*E*<sub>*n*</sub>)\]

### Properties

1.  *D*<sub>*e*</sub> ⊂ *D*<sub>*f*</sub> iff
    *ϕ*(*D*<sub>*e*</sub>) &lt; *ϕ*(*D*<sub>*f*</sub>)

2.  *ϕ*(*D*<sub>*e*</sub> ∪ *D*<sub>*f*</sub>) = *s**y**n**c*(*ϕ*(*D*<sub>*e*</sub>), *ϕ*(*D*<sub>*f*</sub>))

3.  Let *e*, *f* be two events where *e* appears before *f* and
    *e* = *i*\##*k*. Then, *e* ∉ *D*<sub>*f*</sub> iff
    *k* &gt; *Φ*(*D*<sub>*f*</sub>)(*i*).

We define &lt; and *s**y**n**c* for vector clocks as follows.

    Synchronize two vector clocks by taking the larger time stamp

         sync([i1,...,in],[j1,...,jn]) = [max(i1,j1), ..., max(in,jn)]

    Order among vector clocks

          [i1,...,in]  < [j1,...,jn])

    if ik<=jk for all k=1...n and there exists k such that ik<jk.

## Vector clock based race detector a la [FastTrack](http://dept.cs.williams.edu/~freund/papers/fasttrack-7-2016.pdf)

Further vector clock operations.

    Lookup of time stamp

       [i1,...,ik,...,in](k) = ik


    Increment the time stamp of thread i

        inc([k1,...,ki-1,ki,ki+1,...,kn],i) = [k1,...,ki-1,ki+1,ki+1,...,kn]

We maintain the following state variables.

    Th(i)

     Vector clock of thread i


    R(x)

       Vector clock for reads we have seen

    W(x)

      Epoch of most recent write


    Rel(y)

      Vector clock of the most recent release on lock y.

Initially, the timestamps in R(x), W(x) and Rel(y) are all set to zero.

In Th(i), all time stamps are set to zero but the time stamp of the
entry i which is set to one.

Event processing.

    acq(t,y) {
      Th(t) = sync(Th(t), Rel(y))
      inc(Th(t),t)
    }

    rel(t,y) {
       Rel(y) = Th(t)
       inc(Th(t),t)
    }

    fork(t1,t2) {
      Th(t2) = Th(t1)
      inc(Th(t2),t2)
      inc(Th(t1),t1)
    }

    join(t1,t2) {
      Th(t1) = Th(t2)
      inc(Th(t1),t1)
      }

    write(t,x) {
      If not (R(x) < Th(t))
      then write in a race with a read

      If W(x) exists
      then let j##k = W(x)
           if k > Th(t)(j)
           then write in a race with a write
      then write-write race (W(x),e)

      W(x) = t##Th(t)(t)
      inc(Th(t),t)
    }

    read(t,x) {
      If W(x) exists
      then let j##k = W(x)
           if k > Th(t)(j)
           then read in a race with a write
      R(x) = sync(Th(t), R(x))
    }

We follow Java’s memory semantics.

We impose last-write order only for atomic variables.

Atomic variables are protected by a lock. As we order critical sections
based on their textual occurrence, we get the last-write order for
atomic variables for free.

We include `fork` and `join` events.

## Examples (from before)

### Race not detected

        T0            T1

    1.  fork(T1)                    [1,0]
    2.  acq(x)                      [2,0]
    3.  wr(z)                       [3,0]  W(z) = undefined
    4.  rel(x)                      [4,0]
    5.                acq(x)        [1,1]
    6.                rel(x)        [4,2]
    7.                wr(z)         [4,3]  W(z) = 0##3

-   For each event we annotate its vector clock

-   For each write we show the state of W(x) before processing the read

-   If there are any reads we also show R(x)

### Race detected

        T0            T1

    1.  fork(T1)                    [1,0]
    2.  acq(x)                      [2,0]
    3.  wr(z)                       [3,0]  W(z) = undefined
    4.  rel(x)                      [4,0]
    5.                wr(z)         [1,1]  W(z) = 0##3
    6.                acq(x)        [1,2]
    7.                rel(x)        [4,3]

### Earlier race not detected

        T0            T1

    1.  fork(T1)                    [1,0]
    2.  acq(y)                      [2,0]
    3.  wr(x)                       [3,0]  W(x) = undefined
    4.  wr(x)                       [4,0]  W(x) = 0##3
    5.  rel(y)                      [5,0]
    6.                wr(x)         [1,1]  W(x) = 0##4
    7.                acq(y)        [1,2]
    8.                rel(y)        [5,3]

### Read-write races

        T0            T1            T2

    1.  wr(x)                                     [1,0,0]  W(x) = undefined
    2.  fork(T1)                                  [2,0,0]
    3.  fork(T2)                                  [3,0,0]
    4.  rd(x)                                     [4,0,0]
    5.                rd(x)                       [2,1,0]
    6.                              acq(y)        [3,0,1]
    7.                              wr(x)         [3,0,2]  W(x) = 0##1  R(x) = [0##4,1##1]
    8.                              rel(y)        [3,0,3]

## Summary

## False negatives

The HB method as *false negatives*. This is due to the fact that the
textual order among critical sections is preserved.

Consider the following trace.

         T1          T2

    1.   w(x)
    2.   acq(y)
    3.   rel(y)
    4.               acq(y)
    5.               w(x)
    6.               rel(y)

We derive the following HB relations.

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
*w*(*x*)<sub>1</sub> and *w*(*x*)<sub>5</sub> are ordered. Hence, the HB
conclude that there is no data race.

This is a false negative. Consider the following reordering.

         T1          T2

    4.               acq(y)
    5.               w(x)
    1.   w(x)

We execute first parts of thread T2. Thus, we find that the two
conflicting writes are in a data race.

## False positives

The first race reported by the HB method is an “actual” race. However,
subsequent races may be false positives.

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
(*w*(*x*)<sub>4</sub>, *w*(*x*)<sub>1</sub>).

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

## Further reading

### [What Happens-After the First Race?](https://arxiv.org/pdf/1808.00185.pdf)

Shows that the “first” race reported by Lamport’s happens-before
relation is sound.

### [ThreadSanitizer](https://github.com/google/sanitizers/wiki/ThreadSanitizerCppManual)

C/C++ implementation of Lamport’s happens-before relation (to analyze
C/C++).

### [Go’s data race detector](https://golang.org/doc/articles/race_detector)

Based on ThreadSanitizer.
