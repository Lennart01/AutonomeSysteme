---
title: Dynamic versus static analysis methods
description: Martin Sulzmann
---



## Overview

Dynamic analysis:

-   Run the program

-   Check for any bad behavior

Static analysis:

-   Build an approximation of the program’s behaviour

-   Check that the approximation satisfies some properties

*Dynamic* because the analysis runs the actual program. Sometimes,
dynamic analysis is also referred to as run-time analysis.

*Static* because the analysis does not run the program. Rather, the
program is analysed at compile-time.

## Selection of dynamic and static analysis methods

For each type of analysis, there exist many refinements.

## Static program analysis

1.  Type systems

2.  Data-flow analysis

3.  Control-flow analysis

4.  Modelchecking

…

## Dynamic program analysis

1.  Testing

    -   User Tests

    -   Unit Tests

    -   Invariants/Assertions

    -   Property-based testing

2.  Trace-based analysis (see Data Race and Deadlock Prediction)

…

## Program analysis examples

## Type checking

Consider the following program written in a C-like language.

    int x;
    if(some_condition) {
      x = 1;
    } else {
      int y = x[1];
    }

Assuming we apply *static* type checking we obtain a type error (before
running the program).

Integer variable `x` is not an array.

In a language like Python where we apply dynamic type checking such type
errors (if at all) only show up at run-time.

## Data race analysis

Consider the following Go program.

    package main

    import "fmt"

    var x int

    func f(n int) {
        switch {
        case n > 1:
            fmt.Printf("%d", x)
            f(n - 1)
        case n == 1:
            fmt.Printf("%d", x)
        default: // n < 1
            x = 0
        }

    }

    func main() {
        x = 1
        // Thread T
        go func() {
            fmt.Printf("%d", x)
        }()
        f(3)
        fmt.Printf("%d", x)
    }

There is no data race here because the `default` case never applies.

Some static analysis might approximate the program as follows.

     F -> r(x) F
     F -> r(x)
     F -> w(x)

     T -> r(x)

In the above, we make use of context-free grammars to approximate the
behavior of each thread.

The interleaving of `F` and `T` yields a trace where we encounter the
following subtrace: `w(x) r(x)`.

Hence, the static analysis issues (falsely) a data race warning.

To remove this false positive, the static analysis needs to apply some
more involved reasoning to infer that the `default` case will never be
reached. In general, such reasoning might not be decidable. Hence,
static analysis methods overrapproximate the program’s behavior.

## Summary

-   Static analysis methods generally overapproximate the behavior of
    the program and therefore suffer from false positives.

-   Static analysis methods might also have scalability issues when
    considering large programs (applies to modelchecking).

-   Dynamic analysis methods generally suffer from false negatives. We
    need to find the “right” inputs so that we can uncover the bug.

-   The advantage is that dynamic analysis methods generally scale for
    larger programs.

-   There are also hybrid methods. For example, in case of trace-based
    program analysis (we run the program to obtain some trace), we could
    apply modelchecking to obtain all valid reorderings.
