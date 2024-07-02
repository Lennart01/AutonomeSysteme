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
then we say that (*e*, *f*) is a *Lockset data race pair*.

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
(*i*\##*a**c**q*(*y*)<sub>*k*</sub>, *j*\##*r**e**l*(*y*)<sub>*l*</sub>)
is a *matching acquire/release pair* if

1.  *i* = *j*, and

2.  *k* &lt; *l* and there is no *i*\##*r**e**l*(*y*)<sub>*m*</sub> where
    *k* &lt; *m* &lt; *l*.

The first condition states that *a**c**q*(*y*) and *r**e**l*(*y*) belong
to the same thread. The second condition states that inbetween
*a**c**q*(*y*) and *r**e**l*(*y*) there is no other *r**e**l*(*y*).

We write
*C**S*(*i*\##*a**c**q*(*y*)<sub>*k*</sub>, *i*\##*r**e**l*(*y*)<sub>*l*</sub>)
to denote the set of events that are part of the *critical section* for
a matching acquire/release pair
(*i*\##*a**c**q*(*y*)<sub>*k*</sub>, *i*\##*r**e**l*(*y*)<sub>*l*</sub>).

An event *j*\##*e*<sub>*m*</sub> is part of
*C**S*(*i*\##*a**c**q*(*y*)<sub>*k*</sub>, *i*\##*r**e**l*(*y*)<sub>*l*</sub>),
written
*j*\##*e*<sub>*m*</sub> ∈ *C**S*(*i*\##*a**c**q*(*y*)<sub>*k*</sub>, *i*\##*r**e**l*(*y*)<sub>*l*</sub>)
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
*L**S*(*e*) = {*y* ∣ ∃*a*, *r*.*e* ∈ *C**S*(*a*, *r*)}.

∃*a*, *r*. means that we find *a* = *i*\##*a**c**q*(*y*)<sub>*k*</sub>
and *r* = *i*\##*r**e**l*(*y*)<sub>*l*</sub> where (*a*, *r*) is matching
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
*C**S*(*T*1\##*a**c**q*(*y*)<sub>2</sub>, *T*1\##*r**e**l*(*y*)<sub>3</sub>).

In thread T2, we have the critical section
*C**S*(*T*2\##*a**c**q*(*y*)<sub>4</sub>, *T*2\##*r**e**l*(*y*)<sub>6</sub>).

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

The following examples are automatically generated. Traces are annotated
with lockset information (for reads/writes only).

## Example 1

       T0          T1          Lockset
    e1. fork(T1)
    e2. acq(L1)
    e3. wr(V2)                 {L1}
    e4. rel(L1)
    e5.             acq(L1)
    e6.             rel(L1)
    e7.             wr(V2)     {}

Locksets of the writes are disjoint. Hence, we issue a data race
warning. This is a true positive.

## Example 2

       T0          T1          Lockset
    e1. fork(T1)
    e2. acq(L1)
    e3. wr(V2)                 {L1}
    e4. rel(L1)
    e5.             wr(V2)     {}
    e6.             acq(L1)
    e7.             rel(L1)

Locksets of the writes are disjoint. Hence, we issue a data race
warning. This is a true positive.

## Example 2b

       T0          T1          Lockset
    e1. fork(T1)
    e2. acq(L1)
    e3. wr(V2)                 {L1}
    e4. wr(V2)                 {L1}
    e5. rel(L1)
    e6.             wr(V2)     {}
    e7.             acq(L1)
    e8.             rel(L1)

Each write in thread T0 is in a race with the write in thread T1
(because their locksets are disjoint).

## Example 3

       T0          T1          T2          Lockset
    e1. wr(V2)                             {}
    e2. fork(T1)
    e3. fork(T2)
    e4. rd(V2)                             {}
    e5.             rd(V2)                 {}
    e6.                         acq(L1)
    e7.                         wr(V2)     {L1}
    e8.                         rel(L1)

Each read (in thread T0 and thread T1) is in a race with the write in
thread T2 (because their locksets are disjoint).

## Example 3b

       T0          T1          T2          Lockset
    e1. fork(T1)
    e2. fork(T2)
    e3. wr(V2)                             {}
    e4. rd(V2)                             {}
    e5.             rd(V2)                 {}
    e6.                         acq(L1)
    e7.                         wr(V2)     {L1}
    e8.                         rel(L1)

The locksets of the write and read in thread T0 are disjoint. This is
not a race because the write and read take place in the same thread.
Recall that we only consider pairs of conflicting events where events
take place in distinct threads and at least one event is a write.

## Example 4

       T0          T1          Lockset
    e1. fork(T1)
    e2. acq(L1)
    e3. acq(L2)
    e4. wr(V2)                 {L1,L2}
    e5. rel(L2)
    e6. wr(V2)                 {L1}
    e7. rel(L1)
    e8.             acq(L2)
    e9.             wr(V2)     {L2}
    e10.             rel(L2)

The write e4 in thread T0 is protected by locks L1 and L2. Hence, e4 is
not in a race with the write e9 (their locksets share the common lock
L2). On the other hand, write e6 is in a race with e9 (there is no
common lock).

## Example 5

      T0          T1          Lockset
    e1. fork(T1)
    e2. acq(L1)
    e3.             wr(V2)     {}
    e4. wr(V2)                 {L1}
    e5. rel(L1)
    e6.             acq(L1)
    e7.             wr(V2)     {L1}
    e8.             rel(L1)

Write e3 takes place in thread T1 whereas the acquire and release take
place in thread T0. There is no synchronization between thread T0 and
thread T1. Hence, the lockset of write e3 is empty. Hence, the write e3
is in a race with the write e4 (because their locksets are disjoint).

## Example 6

      T0          T1          T2          Lockset
    e1. fork(T1)
    e2. wr(V2)                             {}
    e3. fork(T2)
    e4.                         wr(V2)     {}
    e5.             join(T0)
    e6.             wr(V2)                 {}

The locksets of all writes are empty. Hence, we would issue the
following data race warnings.

-   e2 is in a race with e4

-   e2 is in a race with e6

-   e4 is in a race with e6

The race warning “e2 is in a race with e4” is a false positive. Due to
the fork event e3, event e2 will always happen before event e4.

The race warning “e2 is in a race with e6” is a false positive as well.
Due to the join event e5, event e2 will always happen before e6.

The only true positive is “e4 is in a race with e6”.

## Lockset implementation

[Go playground](https://go.dev/play/p/AqXqUdS1muv)

Check out main and the examples.

    package main

    // Lockset-based race predictor

    import "fmt"
    import "strconv"
    import "strings"

    // Example traces.

    // Traces are assumed to be well-formed.
    // For example, if we fork(ti) we assume that thread ti exists.

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

    func trace_4() []Event {
        t0 := mainThread()
        t1 := nextThread(t0)
        x := 1
        y := 2
        z := 2
        return []Event{
            fork(t0, t1),
            acq(t0, x),
            acq(t0, y),
            wr(t0, z),
            rel(t0, y),
            wr(t0, z),
            rel(t0, x),
            acq(t1, y),
            wr(t1, z),
            rel(t1, y)}

    }

    func trace_5() []Event {
        t0 := mainThread()
        t1 := nextThread(t0)
        x := 1
        z := 2
        return []Event{
            fork(t0, t1),
            acq(t0, x),
            wr(t1, z),
            wr(t0, z),
            rel(t0, x),
            acq(t1, x),
            wr(t1, z),
            rel(t1, x)}
    }

    func trace_6() []Event {
        t0 := mainThread()
        t1 := nextThread(t0)
        t2 := nextThread(t1)
        z := 2
        return []Event{
            fork(t0, t1),
            wr(t0, z),
            fork(t0, t2),
            wr(t2, z),
            join(t1, t0),
            wr(t1, z)}
    }

    func main() {

        run(trace_1())

        run(trace_2())

        run(trace_2b())

        run(trace_3())

        run(trace_3b())

        run(trace_4())

        run(trace_5())

        run(trace_6())

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
    func displayEvtSimple(e Event) string {
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
    func displayTraceWithLS(m int, es []Event, evt_ls map[int]LS, row_offset int) string {
        s := ""
        for i, e := range es {
            ls_info := "     "
            _, ok := evt_ls[i]
            if ok {
                ls_info += evt_ls[i].display()
            }
            row := "\n" + "e" + strconv.Itoa(i+1) + ". " + colOffset(e.thread(), row_offset) + displayEvtSimple(e) + colOffset(m-e.thread(), row_offset) + ls_info
            s = s + row
        }
        // Add column headings.
        heading := "   "
        for i := 0; i <= m; i++ {
            heading += "T" + strconv.Itoa(i) + strings.Repeat(" ", row_offset-2)
        }
        heading += "Lockset"
        s = heading + s

        return s
    }

    ///////////////////////////////////////////////////////////////
    // Lock sets

    type LS map[int]bool //

    func (ls LS) add(x int) {
        ls[x] = true
    }

    func (ls LS) remove(x int) {
        delete(ls, x)
    }

    func (ls LS) display() string {
        var s string
        i := len(ls)
        s = "{"
        for lock, _ := range ls {

            if i > 1 {
                s = s + "L" + strconv.Itoa(lock) + ","

            }
            if i == 1 {
                s = s + "L" + strconv.Itoa(lock)
            }
            i--
        }
        return s + "}"
    }

    func copyLS(ls LS) LS {
        new := make(map[int]bool)
        for lock, _ := range ls {
            new[lock] = true
        }

        return new
    }

    ///////////////////////////////////////////////////////////////

    type State struct {
        th_lockset  map[int]LS // key = thread id
        evt_lockset map[int]LS // key = trace position
    }

    func run(es []Event) {

        var s State

        s.th_lockset = make(map[int]LS)
        s.evt_lockset = make(map[int]LS)

        max_tid := 0

        for _, e := range es {
            max_tid = max(max_tid, e.thread())
        }

        for i := 0; i <= max_tid; i++ {
            s.th_lockset[i] = make(map[int]bool)
        }

        exec := func(e Event) {
            switch {
            case e.kind() == AcquireEvt:
                s.acquire(e)
            case e.kind() == ReleaseEvt:
                s.release(e)
            case e.kind() == ForkEvt:
                s.fork(e)
            case e.kind() == JoinEvt:
                s.join(e)
            case e.kind() == WriteEvt:
                s.write(e)
            case e.kind() == ReadEvt:
                s.read(e)
            }

        }

        for i, e := range es {
            exec(e)
            if e.kind() == WriteEvt {
                s.evt_lockset[i] = copyLS(s.th_lockset[e.thread()])
            }
            if e.kind() == ReadEvt {
                s.evt_lockset[i] = copyLS(s.th_lockset[e.thread()])
            }
        }

        fmt.Printf("\n%s\n", displayTraceWithLS(max_tid, es, s.evt_lockset, 12))

    }

    func (s *State) acquire(e Event) {
        t := e.thread()
        y := e.arg()

        s.th_lockset[t].add(y)

    }

    func (s *State) release(e Event) {
        t := e.thread()
        y := e.arg()
        s.th_lockset[t].remove(y)
    }

    func (s *State) fork(e Event) {

    }

    func (s *State) join(e Event) {

    }

    func (s *State) write(e Event) {

    }

    func (s *State) read(e Event) {

    }
