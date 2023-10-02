---
title: Dynamic deadlock prediction
description: Martin Sulzmann 
---

## Dynamic Verification - Data Races and Deadlocks

Programs may show non-deterministic behavior (e.g. see concurrency).


Issue:


* Test case successful
* But it also could happen that the test case (for the same inputs) fails


Motivating examples
-------------------


### Data races



```go
x := 0               // P1

go func() {
  lock()             // P2
  unlock()           // P3
  x = 1              // P4 
  }()

x = 2                // P5
lock()               // P6
unlock()             // P7
```

We consider a specific execution run represented as an interleaved sequence of execution steps. We refer to the interleaved sequence of execution steps as the **program trace** (or trace for short).



```go
1.   x := 0     P1
2.   x = 2      P5
3.   lock()     P6
4.   unlock()   P7
5.   lock()     P2
6.   unlock()   P3
7.   x = 1      P4
```

Looks good? What about step 1 and step 2? Statements are executed in program order (as they appear in the program text), so first P1 and then P5.


Here is another execution run.



```go
1.   x := 0     P1
2.   lock()     P2
3.   unlock()   P3
4.   x = 1      P4
5.   x = 2      P5
6.   lock()     P6
7.   unlock()   P7
```

Now, we are in trouble! Step 4 and 5 form a write/write data race. The two write statements appear right next to each other in the trace. Unlike in the earlier trace, both statements belong to distinct threads. Hence, their actual execution on some Hardware might lead to a conflict. This is commonly referred to as a data race.


Definition: 1. Two writes on the same variable belonging to two distinct threads are in a **write/write data race** if they appear right next to each other in a trace. 2. A write and a read on the same variable belonging to two distinct threads are in a **write/read data race** if they appear right next to each other in a trace.


Points to note:


* There may be a data race.
* The data race may only show up for some specific program run.


### Deadlocks


Similar observations apply to the case of deadlocks.



```go
x := make(chan int)

go func() {
    x <- 1
   }()

go func() {
    <- x
 }()

<- x
```

Dynamic data race prediction
----------------------------


### Motivation


Challenge: Based on a specific program run represented by a trace, we wish to predict if a data race may occur.


Consider the following example (variant of the above).



```go
x := 0               // P1

go func() {
  lock()             // P2
  unlock()           // P3
  x = 1              // P4 
  }()

lock()               // P5
x = 2                // P6
unlock()             // P7
```

Consider the following trace resulting from a specific execution run.



```go
1.  x := 0    P1
2.  lock()    P2
3.  unlock()  P3
4.  x = 1     P4
5.  lock()    P5
6.  x = 2     P6
7.  unlock()  P7
```

Point to note. P4 and P6 are not in race because they don't appear right next to each other in the above trace. However, it is possible to reorder the trace such P4 and P6 are in a race.


Consider



```go
1.  x := 0    P1
2.  lock()    P2
3.  unlock()  P3
4.  lock()    P5
5.  x = 1     P4
6.  x = 2     P6
7.  unlock()  P7
```

### Trace reorderings


Under what conditions are we allowed to reorder a trace?


Need to take care of write-read dependencies.


Consider



```go
var x, y int

go func() {
  y = 0               // P1
  x = 0               // P2
}()

go func() {
  if x == 0 {        // P3
     y = 1           // P4
   }
  }()
}
```

and the resulting trace



```go
1.  y = 0             P1
2.  x = 0             P2
3.  x == 0            P3
4.  y = 1             P4
```

We find that `x = 0` (write) and `x == 0` (read) are in a write-read race.


Can we reorder the trace such that P1 and P4 are in a (write-write) race? It seems possible as both operations are part of distinct threads.


No! This is not possible because there is a write-read dependency between P2 and P3. The read value affects the control-flow and the subsequent operations (like P4) in this thread.


In addition, we need to guarantee that send-receive pairs remain the same (lock/unlock is a special case).


Valid trace reordering:


* The order within a trace must remain the same.
* Each read must see the same last write.
* Send-receive pairs remain the same.


### References


[Happened-before](https://en.wikipedia.org/wiki/Happened-before)


[What Happens - After the First Race? Enhancing the Predictive Power of Happens - Before Based Dynamic Race Detection](https://arxiv.org/abs/1808.00185)


[Predicting All Data Race Pairs for a Specific Schedule](https://arxiv.org/abs/1909.03289)


[Data Race Prediction for Inaccurate Traces](https://arxiv.org/abs/1905.10855)


