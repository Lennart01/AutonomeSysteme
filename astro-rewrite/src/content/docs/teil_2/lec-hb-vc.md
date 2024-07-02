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

*The HB relation does not enforce the last writer rule. More on this
later.*

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

          [i1,...,in]  < [j1,...,jn]

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
      then let j##k = W(x)                    -- means W(x) equals j##k
           if k > Th(t)(j)
           then write in a race with a write

      W(x) = t##Th(t)(t)
      inc(Th(t),t)
    }

    read(t,x) {
      If W(x) exists
      then let j##k = W(x)
           if k > Th(t)(j)
           then read in a race with a write
      R(x) = sync(Th(t), R(x))
      inc(Th(t),t)
    }

Points note note.

We include `fork` and `join` events.

FastTrack (like the HB relation) does not enforce the “last writer”
rule. This is in line with We Java’s “weak” memory semantics.

The last-write order is enforced for atomic variables. Atomic variables
are protected by a lock. As we order critical sections based on their
textual occurrence, we get the last-write order for atomic variables for
free.

## FastTrack Examples (from before)

The following examples are automatically generated. There is a slight
change in naming convention. Instead of lock variable “x” we write “L1”.
Similarly, we write “V0” for some shared variable “y”.

## Race not detected

Consider the following trace.

       T0            T1
    e1. fork(T1)
    e2. acq(L1)
    e3. wr(V2)
    e4. rel(L1)
    e5.               acq(L1)
    e6.               rel(L1)
    e7.               wr(V2)

We apply the FastTrack algorithm on the above trace. For each event we
annotate its vector clock before and after processing the event.

       T0                            T1
    e1. [1,0]_fork(T1)_[2,0]
    e2. [2,0]_acq(L1)_[3,0]
    e3. [3,0]_wr(V2)_[4,0]
    e4. [4,0]_rel(L1)_[5,0]
    e5.                               [1,1]_acq(L1)_[4,2]
    e6.                               [4,2]_rel(L1)_[4,3]
    e7.                               [4,3]_wr(V2)_[4,4]

Here are the individual processing steps in detail.

    ****
    Step 1: Processing event fork(T1)in thread T0
    BEFORE
    Thread VC = [1,0]
    AFTER
    Thread VC = [2,0]
    ****
    Step 2: Processing event acq(L1)in thread T0
    BEFORE
    Thread VC = [2,0]
    Rel[L1] = [0,0]
    AFTER
    Thread VC = [3,0]
    Rel[L1] = [0,0]
    ****
    Step 3: Processing event wr(V2)in thread T0
    BEFORE
    Thread VC = [3,0]
    R[V2] = [0,0]
    W[V2] = undefined
    AFTER
    Thread VC = [4,0]
    R[V2] = [0,0]
    W[V2] = 0##3
    ****
    Step 4: Processing event rel(L1)in thread T0
    BEFORE
    Thread VC = [4,0]
    Rel[L1] = [0,0]
    AFTER
    Thread VC = [5,0]
    Rel[L1] = [4,0]
    ****
    Step 5: Processing event acq(L1)in thread T1
    BEFORE
    Thread VC = [1,1]
    Rel[L1] = [4,0]
    AFTER
    Thread VC = [4,2]
    Rel[L1] = [4,0]
    ****
    Step 6: Processing event rel(L1)in thread T1
    BEFORE
    Thread VC = [4,2]
    Rel[L1] = [4,0]
    AFTER
    Thread VC = [4,3]
    Rel[L1] = [4,2]
    ****
    Step 7: Processing event wr(V2)in thread T1
    BEFORE
    Thread VC = [4,3]
    R[V2] = [0,0]
    W[V2] = 0##3
    AFTER
    Thread VC = [4,4]
    R[V2] = [0,0]
    W[V2] = 1##3

## Race detected

       T0            T1
    e1. fork(T1)
    e2. acq(L1)
    e3. wr(V2)
    e4. rel(L1)
    e5.               wr(V2)
    e6.               acq(L1)
    e7.               rel(L1)

In case of a race detected, we annotate the triggering event.

       T0                            T1
    e1. [1,0]_fork(T1)_[2,0]
    e2. [2,0]_acq(L1)_[3,0]
    e3. [3,0]_wr(V2)_[4,0]
    e4. [4,0]_rel(L1)_[5,0]
    e5.                               [1,1]_wr(V2)_[1,2]   WW
    e6.                               [1,2]_acq(L1)_[4,3]
    e7.                               [4,3]_rel(L1)_[4,4]

The annotation `WW` indicates that write event `e4` is in a race with
some earlier write.

For brevity, we omit the detailed processing steps.

### Earlier race not detected

       T0            T1
    e1. fork(T1)
    e2. acq(L1)
    e3. wr(V2)
    e4. wr(V2)
    e5. rel(L1)
    e6.               wr(V2)
    e7.               acq(L1)
    e8.               rel(L1)

Event `e6` is in a race with `e4` and `e3`. However, FastTrack only
maintains the “last” write. Hence, FastTrack only reports the race among
`e6` and `e4`.

Here is the annotated trace.

       T0                            T1
    e1. [1,0]_fork(T1)_[2,0]
    e2. [2,0]_acq(L1)_[3,0]
    e3. [4,0]_wr(V2)_[5,0]
    e4. [4,0]_wr(V2)_[5,0]
    e5. [5,0]_rel(L1)_[6,0]
    e6.                               [1,1]_wr(V2)_[1,2]   WW
    e7.                               [1,2]_acq(L1)_[5,3]
    e8.                               [5,3]_rel(L1)_[5,4]

### Read-write races

The following trace contains reads as well as writes.

       T0            T1            T2
    e1. wr(V2)
    e2. fork(T1)
    e3. fork(T2)
    e4. rd(V2)
    e5.               rd(V2)
    e6.                             acq(L1)
    e7.                             wr(V2)
    e8.                             rel(L1)

FastTrack reports that the write `e7` is in a race with a read. See the
annotation `RW` below.

       T0                            T1                            T2
    e1. [1,0,0]_wr(V2)_[2,0,0]
    e2. [2,0,0]_fork(T1)_[3,0,0]
    e3. [3,0,0]_fork(T2)_[4,0,0]
    e4. [4,0,0]_rd(V2)_[5,0,0]
    e5.                               [2,1,0]_rd(V2)_[2,2,0]
    e6.                                                             [3,0,1]_acq(L1)_[3,0,2]
    e7.                                                             [3,0,2]_wr(V2)_[3,0,3]   RW
    e8.                                                             [3,0,3]_rel(L1)_[3,0,4]

There are two read-write races: (`e4`,`e7`) and (`e5`,`e7`). In our
FastTrack implementation, we only report the triggering event.

Here is a variant of the above example where we find write-write and
write-read and read-write races.

       T0            T1            T2
    e1. fork(T1)
    e2. fork(T2)
    e3. wr(V2)
    e4. rd(V2)
    e5.               rd(V2)
    e6.                             acq(L1)
    e7.                             wr(V2)
    e8.                             rel(L1)

Here is the annotated trace.

       T0                            T1                            T2
    e1. [1,0,0]_fork(T1)_[2,0,0]
    e2. [2,0,0]_fork(T2)_[3,0,0]
    e3. [3,0,0]_wr(V2)_[4,0,0]
    e4. [4,0,0]_rd(V2)_[5,0,0]
    e5.                               [1,1,0]_rd(V2)_[1,2,0]  WR
    e6.                                                             [2,0,1]_acq(L1)_[2,0,2]
    e7.                                                             [2,0,2]_wr(V2)_[2,0,3]   RW WW
    e8.                                                             [2,0,3]_rel(L1)_[2,0,4]

## FastTrack Implementation in Go

[Go playground](https://go.dev/play/p/FJb7BDk6Tyl)

Check out main and the examples.

    package main

    // FastTrack

    import "fmt"
    import "strconv"
    import "strings"



    // Example traces.

    // Traces are assumed to be well-formed.
    // For example, if we fork(ti) we assume that thread ti exists.

    // Race not detected
    func trace_1() []Event {
        t0 := mainThread()
        t1 := nextThread(t0)
        x := 1
        z := 2
        return []Event{
            fork(t0, t1),
            acq(t0, x),
            wr(t0, z),
            rel(t0, x),
            acq(t1, x),
            rel(t1, x),
            wr(t1, z)}
    }

    // Race detected
    func trace_2() []Event {
        t0 := mainThread()
        t1 := nextThread(t0)
        x := 1
        z := 2
        return []Event{
            fork(t0, t1),
            acq(t0, x),
            wr(t0, z),
            rel(t0, x),
            wr(t1, z),
            acq(t1, x),
            rel(t1, x)}

    }

    // Earlier race not detected
    func trace_2b() []Event {
        t0 := mainThread()
        t1 := nextThread(t0)
        x := 1
        z := 2
        return []Event{
            fork(t0, t1),
            acq(t0, x),
            wr(t0, z),
            wr(t0, z),
            rel(t0, x),
            wr(t1, z),
            acq(t1, x),
            rel(t1, x)}

    }

    // Read-write races
    func trace_3() []Event {
        t0 := mainThread()
        t1 := nextThread(t0)
        t2 := nextThread(t1)
        x := 1
        z := 2
        return []Event{
            wr(t0, z),
            fork(t0, t1),
            fork(t0, t2),
            rd(t0, z),
            rd(t1, z),
            acq(t2, x),
            wr(t2, z),
            rel(t2, x)}

    }

    // Write-write and wwrite-read and read-write races
    func trace_3b() []Event {
        t0 := mainThread()
        t1 := nextThread(t0)
        t2 := nextThread(t1)
        x := 1
        z := 2
        return []Event{
            fork(t0, t1),
            fork(t0, t2),
            wr(t0, z),
            rd(t0, z),
            rd(t1, z),
            acq(t2, x),
            wr(t2, z),
            rel(t2, x)}

    }

    func main() {

        //  fmt.Printf("\n%s\n", displayTrace(trace_1()))
        //  run(trace_1(), true)

        //  fmt.Printf("\n%s\n", displayTrace(trace_2()))
        //  run(trace_2(), true)

        //  fmt.Printf("\n%s\n", displayTrace(trace_2b()))
        //  run(trace_2b(), true)

        //  fmt.Printf("\n%s\n", displayTrace(trace_3()))
        //  run(trace_3(), true)

        //      fmt.Printf("\n%s\n", displayTrace(trace_3b()))
        //      run(trace_3b(), true)

    }




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

    type Event struct {
        k_  EvtKind
        id_ int
        a_  int
    }

    func (e Event) thread() int   { return e.id_ }
    func (e Event) kind() EvtKind { return e.k_ }
    func (e Event) arg() int      { return e.a_ }

    // Some convenience functions.
    func rd(i int, a int) Event {
        return Event{ReadEvt, i, a}
    }

    func wr(i int, a int) Event {
        return Event{WriteEvt, i, a}
    }

    func acq(i int, a int) Event {
        return Event{AcquireEvt, i, a}
    }

    func rel(i int, a int) Event {
        return Event{ReleaseEvt, i, a}
    }

    func fork(i int, a int) Event {
        return Event{ForkEvt, i, a}
    }

    func join(i int, a int) Event {
        return Event{JoinEvt, i, a}
    }

    // Trace assumptions.
    // Initial thread starts with 0. Threads have ids in ascending order.

    func trace_info(es []Event) (int, map[int]bool, map[int]bool) {
        max_tid := 0
        vars := map[int]bool{}
        locks := map[int]bool{}
        for _, e := range es {
            max_tid = max(max_tid, e.thread())
            if e.kind() == WriteEvt || e.kind() == ReadEvt {
                vars[e.arg()] = true
            }
            if e.kind() == AcquireEvt { // For each rel(x) there must exists some acq(x)
                locks[e.arg()] = true
            }
        }
        return max_tid, vars, locks
    }

    func mainThread() int      { return 0 }
    func nextThread(i int) int { return i + 1 }

    const (
        ROW_OFFSET = 14
    )

    // Omit thread + loc info.
    func displayEvtSimple(e Event, i int) string {
        var s string
        arg := strconv.Itoa(e.arg())
        switch {
        case e.kind() == AcquireEvt:
            s = "acq(L" + arg + ")" // L(ock)
        case e.kind() == ReleaseEvt:
            s = "rel(L" + arg + ")"
        case e.kind() == WriteEvt:
            s = "wr(V" + arg + ")" // V(ar)
        case e.kind() == ReadEvt:
            s = "rd(V" + arg + ")"
        case e.kind() == ForkEvt:
            s = "fork(T" + arg + ")" // T(hread)
        case e.kind() == JoinEvt:
            s = "join(T" + arg + ")"
        }
        return s
    }

    func colOffset(i int, row_offset int) string {
        n := (int)(i)
        return strings.Repeat(" ", n*row_offset)
    }

    // Thread ids fully cover [0..n]
    func displayTraceHelper(es []Event, row_offset int, displayEvt func(e Event, i int) string) string {
        s := ""
        m := 0
        for i, e := range es {
            row := "\n" + "e" + strconv.Itoa(i+1) + ". " + colOffset(e.thread(), row_offset) + displayEvt(e, i)
            s = s + row
            m = max(m, e.thread())
        }
        // Add column headings.
        heading := "   "
        for i := 0; i <= m; i++ {
            heading += "T" + strconv.Itoa(i) + strings.Repeat(" ", row_offset-2)
        }
        s = heading + s

        return s
    }

    func displayTrace(es []Event) string {
        return displayTraceHelper(es, ROW_OFFSET, displayEvtSimple)
    }

    func displayTraceWithVC(es []Event, pre map[Event]VC, post map[Event]VC, races map[Event]string) string {
        displayEvt := func(e Event, i int) string {
            out := pre[e].display() + "_" + displayEvtSimple(e, i) + "_" + post[e].display()
            info, exists := races[e]
            if exists {
                out = out + "  " + info

            }
            return out

        }
        return displayTraceHelper(es, 30, displayEvt)
    }

    ///////////////////////////////////////////////////////////////
    // Vector Clocks

    type VC []int

    type Epoch struct {
        tid        int
        time_stamp int
    }

    func (e Epoch) display() string {
        return strconv.Itoa(e.tid) + "##" + strconv.Itoa(e.time_stamp)

    }

    func (v VC) display() string {
        var s string
        s = "["
        for index := 0; index < len(v)-1; index++ {
            s = s + strconv.Itoa(v[index]) + ","

        }
        if len(v) > 0 {
            s = s + strconv.Itoa(v[len(v)-1]) + "]"
        }
        return s

    }

    func copyVC(v VC) VC {
        new := make(VC, len(v))
        copy(new, v)
        return new
    }

    func sync(v VC, v2 VC) VC {
        l := max(len(v), len(v2))

        v3 := make([]int, l)

        for tid, _ := range v3 {

            v3[tid] = max(v[tid], v2[tid])
        }

        return v3
    }

    func (v VC) happensBefore(v2 VC) bool {
        b := false
        for tid := 0; tid < max(len(v), len(v2)); tid++ {
            if v[tid] > v2[tid] {
                return false
            } else if v[tid] < v2[tid] {
                b = true
            }

        }
        return b
    }

    func (e Epoch) happensBefore(v VC) bool {
        return e.time_stamp <= v[e.tid]

    }

    ///////////////////////////////////////////////////////////////
    // Vector Clocks

    type FT struct {
        Th    map[int]VC
        pre   map[Event]VC
        post  map[Event]VC
        Rel   map[int]VC
        W     map[int]Epoch
        R     map[int]VC
        races map[Event]string
        i     int
    }

    func run(es []Event, full_info bool) {

        var ft FT

        ft.Th = make(map[int]VC)
        ft.pre = make(map[Event]VC)
        ft.post = make(map[Event]VC)
        ft.Rel = make(map[int]VC)
        ft.W = make(map[int]Epoch)
        ft.R = make(map[int]VC)
        ft.races = make(map[Event]string)

        n, vars, locks := trace_info(es)
        n = n + 1

        // Initial vector clock of T0
        ft.Th[0] = make([]int, n)
        for j := 0; j < n; j++ {
            ft.Th[0][j] = 0
        }
        ft.Th[0][0] = 1

        for x, _ := range vars {
            ft.R[x] = make([]int, n) // all entries are zero
        }

        for y, _ := range locks {
            ft.Rel[y] = make([]int, n) // all entries are zero
        }

        exec := func(e Event) {
            switch {
            case e.kind() == AcquireEvt:
                ft.acquire(e)
            case e.kind() == ReleaseEvt:
                ft.release(e)
            case e.kind() == ForkEvt:
                ft.fork(e)
            case e.kind() == JoinEvt:
                ft.join(e)
            case e.kind() == WriteEvt:
                ft.write(e)
            case e.kind() == ReadEvt:
                ft.read(e)
            }

        }

        infoBefore := func(i int, e Event) {

            if full_info {

                x := strconv.Itoa(e.arg())

                    out := "\n****\nStep " + strconv.Itoa(i) + ": Processing event " + displayEvtSimple(e, i) + "in thread T" + strconv.Itoa(e.thread())
                out = out + "\nBEFORE"
                out = out + "\nThread VC = " + ft.Th[e.thread()].display()

                if e.kind() == AcquireEvt || e.kind() == ReleaseEvt {
                    out = out + "\nRel[L" + x + "] = " + ft.Rel[e.arg()].display()

                }

                if e.kind() == WriteEvt || e.kind() == ReadEvt {
                    out = out + "\nR[V" + x + "] = " + ft.R[e.arg()].display()

                    ep, exists := ft.W[e.arg()]
                    if exists {
                        out = out + "\nW[V" + x + "] = " + ep.display()
                    } else {
                        out = out + "\nW[V" + x + "] = undefined"
                    }

                }

                fmt.Printf("%s", out)
            }

        }

        infoAfter := func(e Event) {

            if full_info {

                x := strconv.Itoa(e.arg())

                out := "\nAFTER"
                out = out + "\nThread VC = " + ft.Th[e.thread()].display()

                if e.kind() == AcquireEvt || e.kind() == ReleaseEvt {
                    out = out + "\nRel[L" + x + "] = " + ft.Rel[e.arg()].display()

                }

                if e.kind() == WriteEvt || e.kind() == ReadEvt {
                    out = out + "\nR[V" + x + "] = " + ft.R[e.arg()].display()

                    ep, exists := ft.W[e.arg()]
                    if exists {
                        out = out + "\nW[V" + x + "] = " + ep.display()
                    } else {
                        out = out + "\nW[V" + x + "] = undefined"
                    }

                }

                fmt.Printf("%s", out)
            }

        }

        for i, e := range es {
            infoBefore(i+1, e)
            ft.pre[e] = copyVC(ft.Th[e.thread()])
            exec(e)
            infoAfter(e)
            ft.post[e] = copyVC(ft.Th[e.thread()])
        }

        fmt.Printf("\n%s\n", displayTraceWithVC(es, ft.pre, ft.post, ft.races))

    }

    // We only report the event that triggered the race.
    func (ft *FT) logWR(e Event) {
        ft.races[e] = "WR" // "write-read race"
    }

    // A write might be in a race with a write and a read, so must add any race message.
    func (ft *FT) logRW(e Event) {
        _, exists := ft.races[e]
        if !exists {
            ft.races[e] = ""
        }
        ft.races[e] = ft.races[e] + " " + "RW" // "read-write race"

    }

    func (ft *FT) logWW(e Event) {
        _, exists := ft.races[e]
        if !exists {
            ft.races[e] = ""
        }
        ft.races[e] = ft.races[e] + " " + "WW" // "write-write race"
    }

    func (ft *FT) inc(t int) {
        ft.Th[t][t] = ft.Th[t][t] + 1

    }

    func (ft *FT) acquire(e Event) {
        t := e.thread()
        y := e.arg()
        vc, ok := ft.Rel[y]
        if ok {
            ft.Th[t] = sync(ft.Th[t], vc)
        }
        ft.inc(t)

    }

    func (ft *FT) release(e Event) {
        t := e.thread()
        y := e.arg()
        ft.Rel[y] = copyVC(ft.Th[t])
        ft.inc(t)
    }

    func (ft *FT) fork(e Event) {
        t1 := e.thread()
        t2 := e.arg()
        ft.Th[t2] = copyVC(ft.Th[t1])
        ft.inc(t1)
        ft.inc(t2)
    }

    func (ft *FT) join(e Event) {
        t1 := e.thread()
        t2 := e.arg()
        ft.Th[t1] = sync(ft.Th[t1], ft.Th[t2])
        ft.inc(t1)

    }

    func (ft *FT) write(e Event) {
        t := e.thread()
        x := e.arg()

        if !ft.R[x].happensBefore(ft.Th[t]) {
            ft.logRW(e)
        }

        ep, exists := ft.W[x]
        if exists {
            if !ep.happensBefore(ft.Th[t]) {
                ft.logWW(e)
            }

        }

        ft.W[x] = Epoch{tid: t, time_stamp: ft.Th[t][t]}
        ft.inc(t)

    }

    func (ft *FT) read(e Event) {
        t := e.thread()
        x := e.arg()
        ep, exists := ft.W[x]
        if exists {
            if !ep.happensBefore(ft.Th[t]) {
                ft.logWR(e)
            }

            ft.R[x] = sync(ft.Th[t], ft.R[x])

        }
        ft.inc(t)

    }

## Summary

## False negatives

The HB method has *false negatives*. This is due to the fact that the
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
other. Is there a program run that yields the above reordered trace? No!

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

### Weak memory models

There are further reasons why we can argue that there is no false
positive. Consider the original trace.

    Trace I:

         T1            T2

    1.   w(x)
    2.   w(y)
    3.                 r(y)
    4.                 w(x)

The HB relation applies the program order condition. If we consider a
specific thread, then events are executed one after the other.

On today’s modern computer architecture such rules no longer apply. We
may execute events “out of order” if they do not interfere.

For example, we can argume that the read event `r(y)` and the write
event `w(x)` in thread T2 do not interfere with each other (as they
operate on distinct variables). Hence, we may process `w(x)` before
`r(y)`! There are also compiler optimizations where we speculatively
execute `w(x)` before `r(y)`. Hence, we can argue that the data race
among the writes on x is not a false positive.

## Further reading

### [What Happens-After the First Race?](https://arxiv.org/pdf/1808.00185.pdf)

Shows that the “first” race reported by Lamport’s happens-before
relation is sound.

### [ThreadSanitizer](https://github.com/google/sanitizers/wiki/ThreadSanitizerCppManual)

C/C++ implementation of Lamport’s happens-before relation (to analyze
C/C++).

### [Go’s data race detector](https://golang.org/doc/articles/race_detector)

Based on ThreadSanitizer.
