---
title: Dynamic deadlock prediction
description: Martin Sulzmann
---



# Overview

Our assumptions are:

-   Concurrent programs making use of acquire and release (mutex
    operations).

-   A single program run where events that took place are recorded in
    some trace.

Goal:

-   Analyze the trace to check if we might run into a deadlock.

The literature distinguishes between *resource* and *communication*
deadlocks.

A **resource deadlock** arises if

-   a set of threads are blocked, and

-   each thread in the set is waiting to acquire a lock held by another
    thread in the set.

Communication deadlocks arise if threads are blocked due to (missing)
channel events such as send and receive.

Here, we only consider resource deadlocks. Whenever we say deadlock we
refer to a resource deadlock.

## Lock graphs

We introduce a well-established deadlock prediction method based on
*lock graphs*. The basic idea is as follows:

-   Locks are nodes.

-   There is an edge from lock x to lock y if a thread holds locks x and
    acquires lock y. This can be calculated based on lock sets.

-   Check for cycles in the lock graph.

-   If there is a cycle, we report that there is a potential deadlock.

In the below, we consider some examples and consider a simple
implementation of the lock graph method in Go for the analysis of
programs making use of acquire/release operations.

## Literature

-   [Using Runtime Analysis to Guide Model Checking of Java
    Programs](https://spinroot.com/spin/symposia/ws00/18850248.pdf)

Introduces lock trees. Each thread maintains its own sequence of locking
steps. This approach is known under the name the *Goodlock* approach.
Goodlock can only deal with two threads.

-   [Detecting Potential Deadlocks with Static Analysis and Run-Time
    Monitoring](https://www.research.ibm.com/haifa/Workshops/PADTAD2005/papers/article.pdf)

Introduces lock graphs, a generalization of lock trees. Lock graphs are
capable of checking for deadlocks among three threads and more.

# Examples

We explain the idea of dynamic deadlock predication based on lock graphs
via several examples. The lock graph construction is as follows.

-   Locks are nodes.

-   There is an edge from lock x to lock y if a thread holds locks x and
    acquires lock y.

Consider the example.

        T1         T2

    1.  acq(y)
    2.  acq(x)
    3.  rel(x)
    4.  rel(y)
    5.             acq(x)
    6.             acq(y)
    7.             rel(y)
    8.             rel(x)

Based on the above trace, the program runs through without any apparent
problem.

For the above trace, we find the following lock graph.

      y -> x
      x -> y

That is, we may run into a situation where

-   some thread holds lock y and acquires lock x,

-   some thread holds lock x and acquires lock y.

This may lead to a deadlock!

Consider the following reordering of the above trace.

        T1         T2

    1.  acq(y)
    5.             acq(x)
    2.  B-acq(x)
    6.             B-acq(y)

We write `B-acq` to denote that the acquire is blocked.

As we can see, all threads are blocked =&gt; deadlock!

**Deadlock lock graph criteria**:

If there’s a cycle in the lock graph, there’s a potential deadlock.

# Precision

How *precise* is the analysis method based on lockgraphs?

## False positives

Consider the example.

        T1         T2

    1.  acq(y)
    2.  acq(x)
    3.  rel(x)
    4.  rel(y)
    5.  acq(x)
    6.  acq(y)
    7.  rel(y)
    8.  rel(x)

We encounter the same (cyclic) lock graph as shown above.

      y -> x
      x -> y

This is a false positives as all events take place in the same thread.

## False negatives

We consider the addition of fork/join events. Fork corresponds to `go`.
We can emulate a join via channel synchronization.

         T1         T2        T3

    1.  acq(x)
    2.  fork(T2)
    3.             acq(y)
    4.             rel(y)
    5.  join(T2)
    6.  rel(x)
    7.                       acq(y)
    8.                       acq(x)
    9.                       rel(x)
    10.                      rel(y)

We find the following lock graph.

     y -> x

There appears to be no deadlock (no cycle) but there’s a trace
reordering under which we run into a deadlock.

         T1         T2        T3

    1.  acq(x)
    2.  fork(T2)
    7.                       acq(y)
    8.                       B-acq(x)
    3.             B-acq(y)
    5.  B-join(T2)

The above is an example of a *cross-thread* critical section that
includes several events.

# Go-style mutexes behave like semaphores

So far, we assumed that a thread that acquires lock x must also release
x. This assumption holds for Java and C++. However, Go-style mutexes
behave differently as they act more like semaphores. In Go, the acquire
and release of a lock is not tied to a single thread.

Consider the following example.

        T1       T2        T3

    1. acq(x)
    2.          rel(x)
    3.          acq(y)
    4.                    rel(y)

Thread T1 acquires lock x but this lock is released by thread T2. A
similar observation applies to lock y and threads T2 and T3.

Go-style mutexes pose new challenges for lockgraph based deadlock
prediction.

Consider the following example.

        T1         T2        T3

    1.  acq(y)
    2.  acq(x)
    3.            rel(y)
    4.            rel(x)
    5.                      acq(x)
    6.                      acq(y)
    7.                      rel(y)
    8.                      rel(x)

If we apply the lockgraph method we find the following graph

    y -> x

    x -> y

There is a cyclic dependency and therefore we issue a deadlock warning.
This is a false positive as there is no valid reordering under which
threads T1 and T3 remain stuck.

For example, consider the following reordering.

        T1         T2        T3

    1.  acq(y)
    5.                      acq(x)

    At this point we are not stuck, because thread T2 can continue

    3.            rel(y)

    and therefore thread T3 continues

    6.                      acq(y)

    and so on.

Similar arguments apply to the other reorderings.

We conclude:

-   Go-style mutexes behave like semaphores

-   Deadlock prediction based on lockgraph results then in further false
    positives

# [ThreadSanitizer (TSan)](https://github.com/google/sanitizers/wiki/ThreadSanitizerDeadlockDetector)

Lock graph based deadlock detector. Not much is known about what has
been implemented. Certainly a fairly naive implementation.

    void foo() {
        mutexA.lock();
        mutexB.lock();
        mutexB.unlock();
        mutexA.unlock();
    }

    void bar() {
        mutexB.lock();
        mutexA.lock();
        mutexA.unlock();
        mutexB.unlock();
        foo();
    }

    int main() {
        bar();
    }

TSan reports a deadlock but this is a clear false positive.

# Summary

-   Dynamic deadlock prediction based on lock graphs.

-   Various extensions exist to deal with false positives and false
    negatives.

-   False positives and false negatives remain an issue (see
    cross-thread critical sections).

-   Go-style mutexes pose further challenges (false positives).

-   On-going research to reduce the amount of false positives and false
    negatives.

# Appendix: Some implementation in Go

Here comes a simple implementation for dynamic deadlock prediction based
on lock graphs.

We consider “standard” mutex operations where we assume the thread that
acquires a lock also must release the lock.

    package main

    import "fmt"
    import "time"



    // Set of integers.
    // We use map[int]bool to emulate sets of integers.
    // The default value for bool is true.
    // Hence, if the (integer) key doesn't exist, we obtain false = element not part of the set.
    // In case of add and remove, we use pointers to emulate call-by-reference.

    type Set map[int]bool

    func mkSet() Set {
        return make(map[int]bool)
    }

    func empty(set Set) bool {
        return len(set) == 0
    }

    func elem(set Set, n int) bool {
        return set[n]
    }

    func add(set Set, n int) Set {
        s := set
        s[n] = true
        return s
    }

    //  union(a,b) ==> c,true
    //    if there's some element in b that is not an element in a
    //  union(a,b) ==> c,false
    //    if all elements in b are elements in a
    func union(a Set, b Set) (Set, bool) {
        r := true
        for x, _ := range b {
            if !elem(a, x) {
                r = false
                a = add(a, x)
            }
        }
        return a, r

    }

    func remove(set Set, n int) Set {
        s := set
        s[n] = false
        return s
    }

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

    // User interface
    type M interface {
        init()
        acquire(tid int, n int)
        release(tid int, n int)
        check() bool
        info()
    }

    // Each mutex is identified via a natural number starting with 0.
    // We support MAX_MUTEX number of mutexes.
    const MAX_MUTEX = 3

    // Each thread is identified via natural number starting with 0.
    // We support MAX_TID number of threads.
    const MAX_TID = 4

    // We represent the lock graph via an adjacency matrix.
    // Edge x --> y is represented via edge[x][y] = true.
    // Thread i adds the edge x --> y if
    // thread i holds the lock x while acquiring the lock y.
    type LG struct {
        lockset [MAX_TID]Set
        edge    [MAX_MUTEX][MAX_MUTEX]bool
        mutex   [MAX_MUTEX]Mutex
        g       Mutex
    }

    // We use pointer receivers as we update some of the internal structs.
    // Interface M is implemented by *LG.

    func (m *LG) init() {
        for i := 0; i < MAX_TID; i++ {
            m.lockset[i] = mkSet()
        }

        for i := 0; i < MAX_MUTEX; i++ {
            for j := 0; j < MAX_MUTEX; j++ {
                m.edge[i][j] = false
            }

        }

        for i := 0; i < MAX_MUTEX; i++ {
            m.mutex[i] = newMutex()

        }

        m.g = newMutex()

    }

    func (m *LG) info() {

        fmt.Printf("\n *** INFO ***")
        lock(m.g)

        for i := 0; i < MAX_TID; i++ {
            fmt.Printf("\n Thread %d holds the following locks:", i)
            for j := 0; j < MAX_MUTEX; j++ {
                if elem(m.lockset[i], j) {
                    fmt.Printf(" %d", j)
                }
            }
        }

        fmt.Printf("\n Lock graph:")
        for i := 0; i < MAX_MUTEX; i++ {
            for j := 0; j < MAX_MUTEX; j++ {
                if m.edge[i][j] {
                    fmt.Printf("\n  %d --> %d", i, j)
                }
            }

        }

        unlock(m.g)

    }

    // 1. Acquire the actual lock.
    // 2. Update the lock graph.
    // 3. Update the lockset.
    // Optimization note:
    //   There's no need to iterate over all the elements in the lockset.
    //   It's sufficient to add an edge x -> n where
    //   x is the 'most recent' lock added.
    ///  Example:
    //    Consider the lock graph x -> y, y -> z where
    //    via the transitive closure we obtain x -> z.
    //    Hence, there's no need to add the edge x -> z.
    func (m *LG) acquire(tid int, n int) {
        lock(m.mutex[n])

        lock(m.g)
        for i := 0; i < MAX_MUTEX; i++ {
            if elem(m.lockset[tid], i) {
                m.edge[i][n] = true
            }
        }

        m.lockset[tid] = add(m.lockset[tid], n)

        unlock(m.g)
    }

    // 1. Update the lockset.
    // 2. Release the actual lock.
    func (m *LG) release(tid int, n int) {

        lock(m.g)
        m.lockset[tid] = remove(m.lockset[tid], n)
        unlock(m.g)

        unlock(m.mutex[n])

    }

    // Check for cycles in the lock graph.
    func (m *LG) check() bool {

        directNeighbors := func(m LG, x int) Set {
            next := mkSet()

            for y := 0; y < MAX_MUTEX; y++ {
                if m.edge[x][y] {
                    next = add(next, y)
                }
            }
            return next
        }

        // Cycle check for a specific node x by breadth-first traversal.
        // 1. Builds the set of all neighbors of neighbors and so on starting
        // with a specific node x.
        // 2. Check if we encounter/visit x.
        checkCycle := func(m LG, x int) bool {
            visited := mkSet()
            goal := directNeighbors(m, x)
            stop := false

            for !stop {
                new_goal := mkSet()
                for y, _ := range goal {
                    new_goal, _ = union(new_goal, directNeighbors(m, y))
                }

                visited, stop = union(visited, goal)
                goal = new_goal

            }

            if elem(visited, x) {
                return true
            }
            return false
        }

        // Cycle check for each node.
        r := false

        lock(m.g)

        for x := 0; x < MAX_MUTEX; x++ {
            r = r || checkCycle(*m, x)

        }

        unlock(m.g)

        if r {
            fmt.Printf("\n *** cycle => potential deadlock !!! ***")
        }

        return r

    } // check

    // Examples

    // Program with a potential deadlock.
    func example1(m M) {
        // Introduce some short-hands.
        x := 0
        y := 1
        t0 := 0
        t1 := 1
        // MUST call init at the start!
        m.init()

        // If we include the command below, it appears that often
        // the deadlock won't be detected.
        // m.info()

        // Helper
        // acq(a);acq(b);rel(b);rel(a)
        acqRel2 := func(t int, a int, b int) {
            m.acquire(t, a)
            m.acquire(t, b)
            m.release(t, b)
            m.release(t, a)

        }

        // T0
        go acqRel2(t0, x, y)

        // T1
        acqRel2(t1, y, x)

        m.info()
        m.check()

        // m.info()

    }

    // Program with no deadlock
    // but our deadlock detector may signal "potential deadlock".
    func example2(m M) {
        x := 0
        y := 1
        t0 := 0
        t1 := 1
        m.init()
        ch := make(chan int)

        acqRel2 := func(t int, a int, b int) {
            m.acquire(t, a)
            m.acquire(t, b)
            m.release(t, b)
            m.release(t, a)

        }
        // T0
        go func() {
            acqRel2(t0, x, y)
            ch <- 1
        }()

        // T1
        <-ch
        acqRel2(t1, y, x)

        m.info()
        m.check()

        // m.info()

    }

    // Program with a potential deadlock where three threads are involved in.
    func example3(m M) {
        x := 0
        y := 1
        z := 2

        t0 := 0
        t1 := 1
        t2 := 2

        m.init()

        acqRel2 := func(t int, a int, b int) {
            m.acquire(t, a)
            m.acquire(t, b)
            m.release(t, b)
            m.release(t, a)
        }

        // T0
        go acqRel2(t0, x, y)

        // T1
        go acqRel2(t1, y, z)

        // T2
        acqRel2(t2, z, x)

        m.info()
        m.check()
        time.Sleep(1 * time.Second)

    }

    // Program with a potential deadlock.
    // There are two threads and three locks.
    // The deadlock involves only two of the three locks.
    func example4(m M) {
        x := 0
        y := 1
        z := 2

        t0 := 0
        t1 := 1

        m.init()

        // T0
        go func() {
            m.acquire(t0, x)
            m.acquire(t0, y)
            m.acquire(t0, z)
            m.release(t0, z)
            m.release(t0, y)
            m.release(t0, x)
        }()

        // T1
        m.acquire(t1, z)
        m.acquire(t1, x)
        m.release(t1, x)
        m.release(t1, z)

        m.info()
        m.check()
        time.Sleep(1 * time.Second)

    }

    // Program with no deadlock
    // but our deadlock detector may signal "potential deadlock".
    func example5(m M) {
        x := 0
        y := 1
        z := 2

        t0 := 0
        t1 := 1

        m.init()

        // T0
        go func() {
            m.acquire(t0, x)
            m.acquire(t0, y)
            m.acquire(t0, z)
            m.release(t0, z)
            m.release(t0, y)
            m.release(t0, x)
        }()

        // T1
        m.acquire(t1, x)
        m.acquire(t1, z)
        m.acquire(t1, y)
        m.release(t1, y)
        m.release(t1, z)
        m.release(t1, x)

        m.info()
        m.check()
        time.Sleep(1 * time.Second)

    }

    func main() {
        var lg LG

        // example1(&lg)
        // example2(&lg)
        // example3(&lg)
        // example4(&lg)
        example5(&lg)

    }

    // NOTES

    /*

     Require a (global) lock to avoid data races during tracing and checking.
     For example,

      acquires "writes" to the lockgraph, and
      check "reads" from the lockgraph

      releases "writes" to the lockset, and
      info "reads" from the lockset.


     If check and info won't happen concurrently to tracing the program,
     we can simplify the instrumentation for acquire and release.
     There's no need for lock(m.g) and unlock(m.g) instructions for the following reasons.

     Consider acquire for thread tid and lock n.
      1. We first acquire its actual lock.
      2. Hence, there can't be any concurrent access to m.lockset[tid] and m.edge[i][n].

     Consider release for thread tid and lock n.
      1. We first update m.lockset[tid] before
      2. releasing the actual lock.
      Hence, there can't be any concurrent access to m.lockset[tid].


    */

    // Further Observations

    // -- race for example1 sometimes leads to a stalled program run
