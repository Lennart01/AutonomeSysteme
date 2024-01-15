---
title: Dynamic data race prediction - Summary
description: Martin Sulzmann
---



## Summary

**Dynamic program analysis**

-   Execute the program

-   Observe if there is any potential bad behavior based on this
    specific program run represented as a program **trace**

**Exhaustive methods**

-   Consider all trace reorderings

-   Scalability issues

**Efficient methods**

*Underapproximate:*

-   Consider only certain reordering

-   See Lamport’s happens-before method

-   Generally no false positives but false negatives

*Overapproximate:*

-   Consider possibly too many reorderings

-   See the Lockset method

-   Generally no false negatives but false positives

**Happens-before versus vector clocks**

-   Correct by construction data race prediction algorithm based on
    events sets

-   More efficient vector clock algorithm by establishing an isomorphism
    between event sets and vector clocks

-   TSan

    -   Highly optimized implementation of the algorithm

    -   Only record some of the most recent reads

    -   Only keep track of at most 256 threads at a time

    -   Leads to false negatives
