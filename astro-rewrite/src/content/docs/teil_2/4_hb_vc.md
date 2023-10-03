---
title: Dynamic data race prediction - Happens-before and vector clocks
description: Martin Sulzmann 
---

Data race prediction
--------------------


We say that two read/write operations on some shared variable are
*conflicting* if both operations arise in different threads and
at least one of the operations is a write.


Dynamic analysis method
-----------------------


We consider a specific program run represented as a trace. The trace
contains the sequence of events as they took place during program
execution. Based on this trace, we carry out the analysis.


Exhaustive
versus efficient and approximative methods
-----------------------------------------------------


To identify conflicting events that are in a race, we could check if
there is a valid reordering of the trace under which both events occur
right next to each other. In general, this requires to exhaustively
compute all reordering which is not efficient.


Efficient methods approximate by only considering certain
reorderings.


Happens-before
--------------


Some partial order relation to identify if one event happens before
another event.


In case of of unordered events, we can assume that these events may
happen concurrently.


The happens-before (partial) order approximates the *must*
happen relations. Hence, we may encounter false positives and false
negatives.


Vector clocks
-------------


Some efficient representation for the happens-before relation.


If two conflicting operations are unordered under the happens-before
relation, then we report that these operations are in a (data) race.



## Trace and event notation

We write
j#eij\#e\_i
to denote event
ee
at trace position
ii
in thread
jj.


In plain text notation, we sometimes write `j#e_i`.


We assume the following events.



```go
e ::=  acq(y)         -- acquire of lock y
   |   rel(y)         -- release of lock y
   |   w(x)           -- write of shared variable x
   |   r(x)           -- read of shared variable x

```

Consider the trace


[1#w(x)1,1#acq(y)2,1#rel(y)3,2#acq(y)4,2#w(x)5,2#rel(y)6][1 \# w(x)\_1, 1 \# acq(y)\_2, 1 \# rel(y)\_3, 2 \# acq(y)\_4, 2 \# w(x)\_5, 2 \# rel(y)\_6]


and its tabular representation



```go
     T1          T2

1.   w(x)
2.   acq(y)
3.   rel(y)
4.               acq(y)
5.               w(x)
6.               rel(y)
```

Instrumentation and tracing
---------------------------


We ignore the details of how to instrument programs to carry out
tracing of events. For our examples, we generally choose the tabular
notation for traces. In practice, the entire trace does not need to be
present as events can be processed *online* in a stream-based
fashion. A more detailed *offline* analysis, may get better
results if the trace in its entire form is present.



## Trace reordering

To predict if two conflicting operations are in a race we could
*reorder* the trace. Reordering the trace means that we simply
permute the elements.


Consider the example trace.



```go
     T1          T2

1.   w(x)
2.   acq(y)
3.   rel(y)
4.               acq(y)
5.               w(x)
6.               rel(y)
```

Here is a possible reordering.



```go
     T1          T2

4.               acq(y)
1.   w(x)
2.   acq(y)
3.   rel(y)
5.               w(x)
6.               rel(y)
```

This reordering is *not valid* because it violates the lock
semantics. Thread T2 holds locks y. Hence, its not possible for thread
T1 to acquire lock y as well.


Here is another invalid reordering.



```go
     T1          T2

2.   acq(y)
3.   rel(y)
4.               acq(y)
1.   w(x)
5.               w(x)
6.               rel(y)
```

The order among elements in trace has changed. This is not
allowed.


Valid trace reordering
----------------------


For a reordering to be valid the following rules must hold:


1. The elements in the reordered trace must be part of the original
trace.
2. The order among elements for a given trace cannot be
changed.
3. For each release event rel(y) there must exist an earlier acquire
event acq(y) such there is no event rel(y) in between.


A valid reordering only needs to include a subset of the events of
the original trace.


Consider the following (valid) reordering.



```go
     T1          T2

4.               acq(y)
5.               w(x)
1.   w(x)
```

This reordering shows that the two conflicting events are in a data
race. We only consider a prefix of the events in thread T1 and thread
T2.


Exhaustive data race
prediction methods
---------------------------------------


A “simple” data race prediction method seems to compute all possible
(valid) reordering and check if they contain any data race. Such
*exhaustive* methods generally do not scale to real-world
settings where resulting traces may be large and considering all
possible reorderings generally leads to an exponential blow up.


Approximative data
race prediction methods
------------------------------------------


Here, we consider **efficient** predictive methods. By efficient
we mean a run-time that is linear in terms of the size of the trace.
Because we favor efficiency over being exhaustive, we may compromise
completeness and soundness.


**Complete** means that all valid reorderings that exhibit some
race can be predicted. If incomplete, we refer to any not reported race
as a **false negative**.


**Sound** means that races reported can be observed via some
appropriate reordering of the trace. If unsound, we refer to wrongly a
classified race as a **false positive**.


We consider here Lamport’s happens-before (HB) relation that
approximates the possible reorderings. The HB relation can be computed
efficiently but may lead to false positives and false negatives.



## Lamport’s happens-before (HB) relation

Let
TT
be a trace. We define the HB relation `<` as the smallest
[strict
partial order](https://en.wikipedia.org/wiki/Partially_ordered_set#Strict_and_non-strict_partial_orders) that satisfies the following conditions:


**Program order**


Let
j#ei,j#fi+n∈Tj\#e\_i, j\#f\_{i+n} \in T
where
n>0n>0.
Then, we find that
j#ei<j#fi+nj\#e\_i < j\#f\_{i+n}.


**Critical section order**


Let
i#rel(x)k,j#acq(x)k+n∈Ti \# rel(x)\_k, j\# acq(x)\_{k+n} \in T
where
i!=ji != j
and
n>0n>0.
Then, we find that
i#rel(x)k<j#acq(x)k+ni\#rel(x)\_k < j\#acq(x)\_{k+n}.


* Program order states that for a specific threads, events are
ordered based on their trace position.
* Critical section order states that critical sections are ordered
based on their trace position.
* For each acquire the matching relase must be in the same thread.
Hence, the critical section order only needs to consider a release and a
later in trace appearing acquire.


Example
-------


Consider the trace


[1#w(x)1,1#acq(y)2,1#rel(y)3,2#acq(y)4,2#w(x)5,2#rel(y)6][1 \# w(x)\_1, 1 \# acq(y)\_2, 1 \# rel(y)\_3, 2 \# acq(y)\_4, 2 \# w(x)\_5, 2 \# rel(y)\_6].


Via program order we find that


1#w(x)1<1#acq(y)2<1#rel(y)3
1 \# w(x)\_1 < 1 \# acq(y)\_2 < 1 \# rel(y)\_3



and


2#acq(y)4<2#w(x)5<2#rel(y)6.
2 \# acq(y)\_4 < 2 \# w(x)\_5 < 2 \# rel(y)\_6.



Via critical section order we find that


1#rel(y)3<2#acq(y)4.
1 \# rel(y)\_3 < 2 \# acq(y)\_4.



Points to note.


<<
is the smallest partial order that satisfies the above conditions.


Hence, by transitivity we can also assume that for example


1#w(x)1<2#w(x)5.
1 \# w(x)\_1 < 2 \# w(x)\_5.



Happens-before data race
check
------------------------------


If for two conflicting events
ee
and
ff
we have that neither
e<fe < f
nor
f<ef < e,
then we say that
(e,f)(e,f)
is a *HB data race pair*.


The argument is that if
e<fe < f
nor
f<ef < e
we are free to reorder the trace such that
ee
and
ff
appear right next to each other (in some reordered trace).


Note. If
(e,f)(e,f)
is a *HB data race pair* then so is
(f,e)(f,e).
In such a situation, we consider
(e,f)(e,f)
and
(f,e)(f,e)
as two distinct representative for the same data race. When reporting
(and counting) HB data races we only consider a specific
representative.



## Event sets

Consider event
ee.
We denote by
ESeES\_e
the set of events that happen-before
ee.
We assume that
ee
is also included in
ESeES\_e.
Hence,
ESe={f∣f<e}∪{e}ES\_e = \{ f \mid f < e \} \cup \{ e \}.


Example - Trace
annotated with event sets
-----------------------------------------


We write `ei` to denote the event at trace position
`i`.



```go
     T1          T2            ES

1.   w(x)                     ES_e1= {e1}
2.   acq(y)                   ES_e2= {e1,e2}
3.   rel(y)                   ES_e3 = {e1,e2,e3}
4.               acq(y)       ES_e4 = ES_e3 cup {e4} = {e1,e2,e3,e4}
5.               w(x)         ES_e5 = {e1,e2,e3,e4,e5}
6.               rel(y)       ES_e6 = {e1,e2,e3,e4,e5,e6}
```

Observations:


To enforce the critical section order we simply need to add the event
set
ESrel(y)ES\_{rel(y)}
of some release event to the event set
ESacq(y)ES\_{acq(y)}
of some later acquire event.


To enforce the program order, we keep accumulating events within one
thread (in essence, building the transitive closure).


To decide if
e<fe < f
we can check for
ESe⊂ESfES\_e \subset ES\_f.


Consider two conflicting events
ee
and
ff
where
ee
appears before
ff
in the trace. To decide if
ee
and
ff
are in a race, we check for
e∈ESfe \in ES\_f.
If yes, then there’s no race (because
e<fe < f).
Otherwise, there’s a race.


Set-based race predictor
------------------------


We maintain the following state variables.



```go
D(t)

  Each thread t maintains the set of events that happen before when processing events.


R(x)

  Most recent set of concurrent reads.

W(x)

  Most recent write.


Rel(y)

  Critical sections are ordered as they appear in the trace.
  Rel(y) records the event set of the most recent release event on lock y.
```

All of the above are sets of events and assumed to be initially
empty. The exception is W(x). We assume that initially W(x) is
undefined.


We write `e@operation` to denote that event `e`
will be processed by `operation`.



```go
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
```

### Examples


#### Race not detected



```go
    T0            T1

1.  fork(T1)
2.  acq(y)
3.  wr(x)
4.  rel(y)
5.                acq(y)
6.                rel(y)
7.                wr(x)
```

The HB relation does not reorder critical sections. Therefore, we
report there is no race. This is a false negative because there is a
valid reordering to shows the two writes on x are in a race.


Here’s the annotated trace with the information computed by the
set-based race predictor.



```go
   T0            T1

1.  fork(T1)
2.  acq(y)                      D(T0) = [0:fork(T1)_1,0:acq(y)_2]
3.  wr(x)                       W(x) = undefined
4.  rel(y)                      Rel(y) = [0:fork(T1)_1,0:acq(y)_2,0:wr(x)_3,0:rel(y)_4]
5.                acq(y)        D(T1) = [0:fork(T1)_1,0:acq(y)_2,0:wr(x)_3,0:rel(y)_4,1:acq(y)_5]
6.                rel(y)        Rel(y) = [0:fork(T1)_1,0:acq(y)_2,0:wr(x)_3,0:rel(y)_4,1:acq(y)_5,1:rel(y)_6]
7.                wr(x)         W(x) = 0:wr(x)_3
```

* For each acquire in thread t we show D(t)
* For each release on y we show Rel(y)
* For each write on x we show the state of W(x) before processing
the read
* If there are any reads we also show R(x)


#### Race detected



```go
    T0            T1

1.  fork(T1)
2.  acq(y)
3.  wr(x)
4.  rel(y)
5.                wr(x)
6.                acq(y)
7.                rel(y)
```

Under the HB relation, the two writes on x are not ordered. Hence, we
report that they are in a race.


Here’s the annotated trace.



```go
    T0            T1

1.  fork(T1)
2.  acq(y)                      D(T0) = [0:fork(T1)_1,0:acq(y)_2]
3.  wr(x)                       W(x) = undefined
4.  rel(y)                      Rel(y) = [0:fork(T1)_1,0:acq(y)_2,0:wr(x)_3,0:rel(y)_4]
5.                wr(x)         W(x) = 0:wr(x)_3
6.                acq(y)        D(T1) = [0:fork(T1)_1,0:acq(y)_2,0:wr(x)_3,0:rel(y)_4,1:wr(x)_5,1:acq(y)_6]
7.                rel(y)        Rel(y) = [0:fork(T1)_1,0:acq(y)_2,0:wr(x)_3,0:rel(y)_4,1:wr(x)_5,1:acq(y)_6,1:rel(y)_7]
```

#### Earlier race not detected



```go
    T0            T1

1.  fork(T1)
2.  acq(y)
3.  wr(x)
4.  wr(x)
5.  rel(y)
6.                wr(x)
7.                acq(y)
8.                rel(y)
```

The write at trace position 3 and the write at trace position 6 are
in a race. However, we only maintain the most recent write. Hence, we
only report that the write at trace position 4 is in a race with the
write at trace position 6.


Here’s the annotated trace.



```go
    T0            T1

1.  fork(T1)
2.  acq(y)                      D(T0) = [0:fork(T1)_1,0:acq(y)_2]
3.  wr(x)                       W(x) = undefined
4.  wr(x)                       W(x) = 0:wr(x)_3
5.  rel(y)                      Rel(y) = [0:fork(T1)_1,0:acq(y)_2,0:wr(x)_3,0:wr(x)_4,0:rel(y)_5]
6.                wr(x)         W(x) = 0:wr(x)_4
7.                acq(y)        D(T1) = [0:fork(T1)_1,0:acq(y)_2,0:wr(x)_3,0:wr(x)_4,0:rel(y)_5,1:wr(x)_6,1:acq(y)_7]
8.                rel(y)        Rel(y) = [0:fork(T1)_1,0:acq(y)_2,0:wr(x)_3,0:wr(x)_4,0:rel(y)_5,1:wr(x)_6,1:acq(y)_7,1:rel(y)_8]
```

#### Read-write races



```go
    T0            T1            T2

1.  wr(x)
2.  fork(T1)
3.  fork(T2)
4.  rd(x)
5.                rd(x)
6.                              acq(y)
7.                              wr(x)
8.                              rel(y)
```

We find that the two reads are in a race with the write.


Here’s the annotated trace.



```go
    T0            T1            T2

1.  wr(x)                                     W(x) = undefined
2.  fork(T1)
3.  fork(T2)
4.  rd(x)                                     W(x) = 0:wr(x)_1
5.                rd(x)                       W(x) = 0:wr(x)_1
6.                              acq(y)        D(T2) = [0:wr(x)_1,0:fork(T1)_2,0:fork(T2)_3,2:acq(y)_6]
7.                              wr(x)         W(x) = 0:wr(x)_1  R(x) = [0:rd(x)_4,1:rd(x)_5]
8.                              rel(y)        Rel(y) = [0:wr(x)_1,0:fork(T1)_2,0:fork(T2)_3,2:acq(y)_6,2:wr(x)_7,2:rel(y)_8]
```

Note that when processing the write in T2, we find that D(T2)
contains the earlier write.


Can we find a
more compact representation for D(t)?
---------------------------------------------------


The size of D(t) may grow linearly in the size of the trace.


To check for a race we check if some element is in D(t).


If there are n events, this means set-based race prediction requires
O(n\*n) time.



## From event sets to timestamps

Timestamps
----------


For each thread we maintain a timestamp.


We represent a timestamp as a natural number.


Each time we process an event we increase the thread’s timestamp.


Initially, the timestamp for each thread is 1.


Example - Trace
annotated with timestamps
-----------------------------------------



```go
     T1          T2      TS_T1       TS_T2

1.   w(x)                  2
2.   acq(y)                3
3.   rel(y)                4
4.               acq(y)               2
5.               w(x)                 3
6.               rel(y)               4
```

Representing
events via its thread id and timestamp
---------------------------------------------------


Let
ee
be an event in thread
ii
and
jj
its timestamp.


Then, we can uniquely identify
ee
via
ii
and
jj.


We write
i#ji \# j
to represent event
ee.
In the literature,
i#ji \# j
is referred to as an *epoch*.


Example - Trace annotated
with epochs
-------------------------------------



```go
     T1          T2           Epochs

1.   w(x)                     1#1
2.   acq(y)                   1#2
3.   rel(y)                   1#3
4.               acq(y)       2#1
5.               w(x)         2#2
6.               rel(y)       2#3
```

We use the timestamp “before” processing the event. We could also use
the timestamp “after” (but this needs to be done consistently).


From event sets to sets of
epoch
--------------------------------


Instead of events sets we record the set of epochs.


We group together epochs belonging to the same thread. For example,
in case of
{1#1,1#2}\{ 1 \# 1, 1 \# 2 \}
we write
{1#{1,2}}.\{ 1 \# \{ 1, 2\} \}.


Example - Trace
annotated with sets of epochs
---------------------------------------------



```go
     T1          T2            Sets of epochs

1.   w(x)                     {1#1}
2.   acq(y)                   {1#{1,2}}
3.   rel(y)                   {1#{1,2,3}}
4.               acq(y)       {1#{1,2,3}, 2#1}
5.               w(x)         {1#{1,2,3}, 2#{1,2}}
6.               rel(y)       {1#{1,2,3}, 2#{1,2,3}}
```


## From sets of timestamps to vector clocks

Insight:


For each thread only keep most recent timestamp.


For example, in case of
{1#{1,2}}\{ 1 \# \{ 1, 2\} \}
we write
{1#2}\{ 1 \# 2 \}


Example -
Trace annotated with most recent timestamps
-----------------------------------------------------



```go
     T1          T2            Sets of most recent timestamps

1.   w(x)                     {1#1}
2.   acq(y)                   {1#2}
3.   rel(y)                   {1#3}
4.               acq(y)       {1#3, 2#1}
5.               w(x)         {1#3, 2#2}
6.               rel(y)       {1#3, 2#3}
```

Vector clocks
-------------


Instead of a set use a list (vector).



```go
V  ::=  [i1,...,in]    -- vector clock with n time stamps
```

The entry associated to each thread is identified via its position in
that list.


If there’s no entry for a thread, we assume the timestamp 0.


Example - Trace
annotated with vector clocks
--------------------------------------------



```go
     T1          T2            Vector clocks

1.   w(x)                     [1,0]
2.   acq(y)                   [2,0]
3.   rel(y)                   [3,0]
4.               acq(y)       [3,1]
5.               w(x)         [3,2]
6.               rel(y)       [3,3]
```

Mapping event sets to
vector clocks
-----------------------------------


Based on the above, each event set can be represented as the set
({1#E1,...,n#En}(\{1 \# E\_1,..., n \# E\_n\}
where sets
EjE\_j
are of the form
{1,...,k}\{1,...,k\}.


We define a mapping
Φ\Phi
from event sets to vector clocks as follows.


Φ({1#E1,...,n#En})=[max(E1),...,max(En)]\Phi(\{1 \# E\_1,..., n \# E\_n\}) = [max(E\_1),...,max(E\_n)]


### Properties


1. De⊂DfD\_e \subset D\_f
iff
ϕ(De)<ϕ(Df)\phi(D\_e) < \phi(D\_f)
2. ϕ(De∪Df)=sync(ϕ(De),ϕ(Df))\phi(D\_e \cup D\_f) = sync(\phi(D\_e),\phi(D\_f))
3. Let
e,fe, f
be two events where
ee
appears before
ff
and
e=i#ke = i\# k.
Then,
e∉Dfe \not\in D\_f
iff
k>Φ(Df)(i)k > \Phi(D\_f)(i).


We define
<<
and
syncsync
for vector clocks as follows.



```go
Synchronize two vector clocks by taking the larger time stamp

     sync([i1,...,in],[j1,...,jn]) = [max(i1,j1), ..., max(in,jn)]

Order among vector clocks

      [i1,...,in]  < [j1,...,jn])

if ik<=jk for all k=1...n and there exists k such that ik<jk.
```


## Vector clock based race detector a la <a href="http://dept.cs.williams.edu/~freund/papers/fasttrack-7-2016.pdf">FastTrack</a>

Further vector clock operations.



```go
Lookup of time stamp

   [i1,...,ik,...,in](k) = ik


Increment the time stamp of thread i

    inc([k1,...,ki-1,ki,ki+1,...,kn],i) = [k1,...,ki-1,ki+1,ki+1,...,kn]
```

We maintain the following state variables.



```go
Th(i)

 Vector clock of thread i


R(x)

   Vector clock for reads we have seen

W(x)

  Epoch of most recent write


Rel(y)

  Vector clock of the most recent release on lock y.
```

Initially, the timestamps in R(x), W(x) and Rel(y) are all set to
zero.


In Th(i), all time stamps are set to zero but the time stamp of the
entry i which is set to one.


Event processing.



```go
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
}

join(t1,t2) {
  Th(t1) = Th(t2)
  inc(Th(t1),t1)
  }

write(t,x) {
  If not (R(x) < Th(t))
  then write in a race with a read

  If W(x) exists
  then let j#k = W(x)
       if k > Th(t)(j)
       then write in a race with a write
  then write-write race (W(x),e)

  W(x) = t#Th(t)(t)
  inc(Th(t),t)
}

read(t,x) {
  If W(x) exists
  then let j#k = W(x)
       if k > Th(t)(j)
       then read in a race with a write
  R(x) = sync(Th(t), R(x))
}
```

We follow Java’s memory semantics.


We impose last-write order only for atomic variables.


Atomic variables are protected by a lock. As we order critical
sections based on their textual occurrence, we get the last-write order
for atomic variables for free.


We include `fork` and `join` events.


Examples (from before)
----------------------


#### Race not detected



```go
    T0            T1

1.  fork(T1)                    [1,0]
2.  acq(x)                      [2,0]
3.  wr(z)                       [3,0]  W(z) = undefined
4.  rel(x)                      [4,0]
5.                acq(x)        [1,1]
6.                rel(x)        [4,2]
7.                wr(z)         [4,3]  W(z) = 0#3
```

* For each event we annotate its vector clock
* For each write we show the state of W(x) before processing the
read
* If there are any reads we also show R(x)


#### Race detected



```go
    T0            T1

1.  fork(T1)                    [1,0]
2.  acq(x)                      [2,0]
3.  wr(z)                       [3,0]  W(z) = undefined
4.  rel(x)                      [4,0]
5.                wr(z)         [1,1]  W(z) = 0#3
6.                acq(x)        [1,2]
7.                rel(x)        [4,3]
```

#### Earlier race not detected



```go
    T0            T1

1.  fork(T1)                    [1,0]
2.  acq(y)                      [2,0]
3.  wr(x)                       [3,0]  W(x) = undefined
4.  wr(x)                       [4,0]  W(x) = 0#3
5.  rel(y)                      [5,0]
6.                wr(x)         [1,1]  W(x) = 0#4
7.                acq(y)        [1,2]
8.                rel(y)        [5,3]
```

#### Read-write races



```go
    T0            T1            T2

1.  wr(x)                                     [1,0,0]  W(x) = undefined
2.  fork(T1)                                  [2,0,0]
3.  fork(T2)                                  [3,0,0]
4.  rd(x)                                     [4,0,0]
5.                rd(x)                       [2,1,0]
6.                              acq(y)        [3,0,1]
7.                              wr(x)         [3,0,2]  W(x) = 0#1  R(x) = [0#4,1#1]
8.                              rel(y)        [3,0,3]
```


## Summary

False negatives
---------------


The HB method as *false negatives*. This is due to the fact
that the textual order among critical sections is preserved.


Consider the following trace.



```go
     T1          T2

1.   w(x)
2.   acq(y)
3.   rel(y)
4.               acq(y)
5.               w(x)
6.               rel(y)
```

We derive the following HB relations.


The program order condition implies the following ordering
relations:


w(x)1<acq(y)2<rel(y)3w(x)\_1 < acq(y)\_2 < rel(y)\_3


and


acq(y)4<w(x)5<rel(y)6acq(y)\_4 < w(x)\_5 < rel(y)\_6.


The critical section order condition implies


rel(y)3<acq(y)4rel(y)\_3 < acq(y)\_4.


Based on the above we can conclude that


w(x)1<w(x)5w(x)\_1 < w(x)\_5.


How? From above we find that


w(x)1<acq(y)2<rel(y)3w(x)\_1 < acq(y)\_2 < rel(y)\_3
and
rel(y)3<acq(y)4rel(y)\_3 < acq(y)\_4.


By transitivity we find that


w(x)1<acq(y)4w(x)\_1 < acq(y)\_4.


In combination with
acq(y)4<w(x)5<rel(y)6acq(y)\_4 < w(x)\_5 < rel(y)\_6
and transitivity we find that
w(x)1<w(x)5w(x)\_1 < w(x)\_5.


Because of
w(x)1<w(x)5w(x)\_1 < w(x)\_5,
the HB method concludes that there is no data race because the
conflicting events
w(x)1w(x)\_1
and
w(x)5w(x)\_5
are ordered. Hence, the HB conclude that there is no data race.


This is a false negative. Consider the following reordering.



```go
     T1          T2

4.               acq(y)
5.               w(x)
1.   w(x)
```

We execute first parts of thread T2. Thus, we find that the two
conflicting writes are in a data race.


False positives
---------------


The first race reported by the HB method is an “actual” race.
However, subsequent races may be false positives.


Consider the program



```go
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
```

We consider a specific execution run that yields the following
trace.



```go
Trace I:

     T1            T2

1.   w(x)
2.   w(y)
3.                 r(y)
4.                 w(x)
```

We encounter a write-read race because
w(y)2w(y)\_2
and
r(y)3r(y)\_3
appear right next to each other in the trace.


It seems that there is also a HB write-write data race. The HB
relations derived from the above trace are as follows:


w(x)1<w(y)2w(x)\_1 < w(y)\_2
and
r(y)3<w(x)4r(y)\_3 < w(x)\_4.


Hence,
w(x)1w(x)\_1
and
w(x)4w(x)\_4
are unordered. Hence, we find the write-write data race
(w(x)4,w(x)1)(w(x)\_4, w(x)\_1).


We reorder the above trace (while maintaining the program order HB
relations). For the reordered trace we keep the original trace
positions.



```go
Trace II:

     T1            T2

3.                 r(y)
4.                 w(x)
1.   w(x)
2.   w(y)
```

In the reordered trace II, the two writes on x appear right next to
each other. Is there a program run and that yields the above reordered
trace? No!


In the reordered trace II, we violate the write-read dependency
between
w(y)2w(y)\_2
and
r(y)3r(y)\_3.
w(y)2w(y)\_2
is the last write that takes place before
r(y)3r(y)\_3.
The read value
yy
influences the control flow. See the above program where we only enter
the if-statement if
w(y)2w(y)\_2
takes place (and sets
yy
to 2).


We conclude that the HB relation does not take into account
write-read dependencies and therefore HB data races may not correspond
to *actual* data traces.


We say *may not* because based on the trace alone we cannot
decide if the write-read dependency actually affects the control
flow.


For example, trace I could be the result of a program run where we
assume the following program.



```go
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
```

There is also a write-read dependency, see locations marked WRITE and
READ. However, the read value does not influence the control flow.
Hence, for the above program trace II would be a valid reordering of
trace I.


Further reading
---------------


### [What Happens-After the First
Race?](https://arxiv.org/pdf/1808.00185.pdf)


Shows that the “first” race reported by Lamport’s happens-before
relation is sound.


### [ThreadSanitizer](https://github.com/google/sanitizers/wiki/ThreadSanitizerCppManual)


C/C++ implementation of Lamport’s happens-before relation (to analyze
C/C++).


### [Go’s data race
detector](https://golang.org/doc/articles/race_detector)


Based on ThreadSanitizer.


