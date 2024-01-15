---
title: Dynamic data race prediction - Locksets
description: Martin Sulzmann
---



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

## Critical section

We assume that critical sections are always identified by pairs of
*a**c**q*(*y*) and *r**e**l*(*y*) events.

To define matching acquire/release pairs, we attach thread ids and trace
positions to events. We write *i*\##*e*<sub>*k*</sub> to denote some
event *e* in thread *i* at trace position *k*. Recall [Trace and event
notation](./lec-hb-vc.html##(3)).

Consider acquire event *i*\##*a**c**q*(*y*)<sub>*k*</sub> and release
event *j*\##*r**e**l*(*y*)<sub>*l*</sub>.

We say that
(*i*\##*a**c**q*(*y*)<sub>*k*</sub>,*j*\##*r**e**l*(*y*)<sub>*l*</sub>) is
a *matching acquire/release pair* if

1.  *i* = *j*, and

2.  *k* &lt; *l* and there is no *i*\##*r**e**l*(*y*)<sub>*m*</sub> where
    *k* &lt; *m* &lt; *l*.

The first condition states that *a**c**q*(*y*) and *r**e**l*(*y*) belong
to the same thread. The second condition states that inbetween
*a**c**q*(*y*) and *r**e**l*(*y*) there is no other *r**e**l*(*y*).

We write
*C**S*(*i*\##*a**c**q*(*y*)<sub>*k*</sub>,*i*\##*r**e**l*(*y*)<sub>*l*</sub>)
to denote the set of events that are part of the *critical section* for
a matching acquire/release pair
(*i*\##*a**c**q*(*y*)<sub>*k*</sub>,*i*\##*r**e**l*(*y*)<sub>*l*</sub>).

An event *j*\##*e*<sub>*m*</sub> is part of
*C**S*(*i*\##*a**c**q*(*y*)<sub>*k*</sub>,*i*\##*r**e**l*(*y*)<sub>*l*</sub>),
written
*j*\##*e*<sub>*m*</sub> ∈ *C**S*(*i*\##*a**c**q*(*y*)<sub>*k*</sub>,*i*\##*r**e**l*(*y*)<sub>*l*</sub>)
if

1.  *j*\##*e*<sub>*m*</sub> = *i*\##*a**c**q*(*y*)<sub>*k*</sub>, or
    *e*=,*j*\##*r**e**l*(*y*)<sub>*l*</sub>, or

2.  *j* = *i* and *k* &lt; *m* &lt; *l*.

The first condition states that *a**c**q*(*y*) and *r**e**l*(*y*) are
part of the critical section. The second condition states that any event
inbetween that is in the same thread is also part of this critical
section.

## Lockset

Let *e* an event. Then, the lockset of *e*, written *L**S*(*e*),
consists of all *y*s where *e* appears within a critical section
belonging to lock *y*. More formally, we define
*L**S*(*e*) = {*y* ∣ ∃*a*, *r*.*e* ∈ *C**S*(*a*,*r*)}.

∃*a*, *r*. means that we find *a* = *i*\##*a**c**q*(*y*)<sub>*k*</sub>
and *r* = *i*\##*r**e**l*(*y*)<sub>*l*</sub> where (*a*,*r*) is matching
pair acquire/release pair.

## Example

Recall the earlier trace.

    Trace A:

         T1          T2

    1.   w(x)
    2.   acq(y)
    3.   rel(y)
    4.               acq(y)
    5.               w(x)
    6.               rel(y)

We find two critical sections for lock variable *y*.

In thread T1, we have the critical section
*C**S*(*T*1\##*a**c**q*(*y*)<sub>2</sub>,*T*1\##*r**e**l*(*y*)<sub>3</sub>).

In thread T2, we have the critical section
*C**S*(*T*2\##*a**c**q*(*y*)<sub>4</sub>,*T*2\##*r**e**l*(*y*)<sub>6</sub>).

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

## Lockset computation

We maintain the following state variables.

    ls(t)

      The set of locks hold by thread t at a certain time.

    LS

      A mapping that records for each event e its lockset.

We write `e@operation` to denote that event `e` will be processed by
`operation`.

    e@acq(t,y) {
       ls(t) = ls(t) cup {y}
    }

    e@rel(t,y) {
     ls(t) = ls(t) - {y}

    e@fork(t1,t2) {
    }

    e@join(t1,t2) {
    }

    e@write(t,x) {
      LS(e) = ls(t)
    }

    e@read(t,x) {
      LS(e) = ls(t)
    }

In the above, we write `cup` to denote set union ∪. For sets S1 and S2
we write S1 - S2 to denote the set that contains all elements in S1 that
are not in S2.

We only record the lockset for write and read events.

We also cover fork and join events. As we can see, the computation of
locksets is agnostic to the presence of fork and join events.

## Observation

Unlike the Lamport’s happens-before that is sensitive to the order of
critical sections, the computation of locksets is not affected if we
reorder critical sections.

Consider trace A.

         T1          T2

    e1.   w(x)
    e2.   acq(y)
    e3.   rel(y)
    e4.               acq(y)
    e5.               w(x)
    e6.               rel(y)

We find that *L**S*(*e*1) = {} and *L**S*(*e*5) = {*y*}.

For the following (valid) reordering

         T1          T2
    e4.               acq(y)
    e5.               w(x)
    e6.               rel(y)
    e1.   w(x)
    e2.   acq(y)
    e3.   rel(y)

we again find that *L**S*(*e*1) = {} and *L**S*(*e*5) = {*y*}.

## Further examples

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
the lockset method reports that there’s a data race.

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

This “fork” information is not recorded in the trace. As we only compare
locksets, we encounter here another case of a false positive.

## Example 4

          T0      T1      T2        Lockset
    1.   acq(y)
    2.           w(x)              {}
    3.   rel(y)
    4.                   acq(y)
    5.                   w(x)      {y}
    6.                   rel(y)

Shouldn’t the lockset at trace position 2 include lock variable y!?

No!

-   The write at trace position 2 seems to be protected by lock variable
    y.

-   However, thread T1 does not “own” this lock variable!
