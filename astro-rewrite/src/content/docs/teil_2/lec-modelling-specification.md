---
title: Model-Based Specification
description: Martin Sulzmann
---



# Motivation

## Formal reasoning?

*Who cares?*

No need. We know how to program. Whatever we need we find via 'google'
...

## The need for formal reasoning

"Informatik" = Information + Automation

Goal:

-   Understand the problem (Analysis)

-   Code up a solution (Implementation)

-   Make sure that the solution is correct and matches the problem
    (Verification + Validation)

Verification:

-   "The product we have built is right"

-   No bugs, ...

-   Implementation meets the specification

Validation:

-   "We have built the right product"

-   Specification meets the problem description ("customer needs")

Terminology:

-   System: Refers to the product. As we focus on software aspects, in
    our case consists of program code. Can be rather complex as the
    program code may run on several machines, remotely, web-based etc.
    There may be interactions among sub-systems etc. Usually, it is a
    system of systems!

### Example

The problem description says:

    The increment function shall increment each value by one.

The specification given to the programmer says:

    For each int value, the function shall produce some int value.

The programmer implements.

    inc (x int) int {
         return 0
    }

So, verification succeeds but validation fails.

## Modeling

Often phrased as model-based software development.

Purpose:

-   Assist implementation and specification tasks.

-   Avoid coding errors.

-   Make use of high-level abstractions.

-   Make model easy to extend, maintain, ...

What is a (formal) model? Comes in all shapes and sizes.

**Important** We expect that for any model we find a concise semantic
description (so we actually know what a specific model means!)

Examples:

-   The programming language C is a low-level programming *model*. Great
    for low-level stuff but prune to tricky to spot programming
    mistakes.

-   Some of you find that Java is a much better, more high-level
    programming *model*. Some coding errors can't happen in the first
    place (think of memory management). Also, Java offers higher level
    of abstractions (classes, ...). This can be useful to achieve a
    solution which is easier to maintain, ...

Textual versus graphical models:

-   Any programming language serves as a text-based modeling language.
    For example, Perl is a great language for write scripts. The
    modeling focus there is on scripting tasks.

-   We will also encounter graphical modeling languages. For example,
    automata-based models. Some programing languages offer a graphical
    interface.

Logic-based models:

-   Consider Boolean expressions to describe the control-flow behavior
    in your program.

-   We will also consider temporal logics to describe the temporal
    behavior of a system.

What about UML?

-   Well, UML offers a wide range of models. My main criticism is that
    these models often lack some formal underpinnings. So we won't
    directly discuss UML here.

## Specification

-   Make use of a formal model to describe the intended behavior of your
    system.

**Important:**

-   We can use the same type of model to describe the actual working of
    the system (its implementation) and its specification.

-   Extreme case. The implementation serves as the specification! Does
    this make sense?

-   Common approach:

    -   Use a model with an *operational* flavor to describe the
        implementation ("How does the system work?").

    -   Use a model with a *logic-based* flavor for specification ("What
        is the intended behavior?").

# State-Based Modeling

## Finite State Machines (FSM)

We consider a number of examples where FSM are useful for modeling the
system's behavior.

### "Hirte-Wolf-Kohl-Ziege"

Modeling with finite state machines

see black board

## "count"

Modeling with Mealy/Moore machines (input as well as output).

Application: Generation of test cases.

see black board

### 

-   We use the "count" finite state machine (FSA) for **validation**.

-   From the FSA we generate some C code (see below).

-   We **verify** that the C code conforms to the FSA specification.

### Zustandsbasierte Modellierung

    #include "stdio.h"

    /*

    1. Woerter in einem String zaehlen.

    Was ist ein Wort?
    Wir definieren ein Wort als eine Sequenz von
    Zeichen welche nicht getrennt ist durch Leerzeichen.

    2. Zustands-basierte Modellierung.

    Wir definieren unser Alphabet als die Menge

    Sigma = { CH, EOS, WS }

    wobei

    EOS = Nullterminator

    WS = Leerzeichen ('white space')

    CH = Zeichen ('character')


    Die Menge von Zustaenden und Transitionen ist wie folgt.

    1 -- WS --> 1

    1 -- EOS --> 2

    1 -- CH --> 3

    3 -- WS --> 1

    3 -- CH --> 3

    3 -- EOS --> 2

    Menge von Zustaenden ist {1,2,3}

    1 ist der Startzustand

    3 ist der Finalzustand

    Obiger Automat ist ein Beipsiel eines endlichen Automaten.

    3. Zaehlen von Woertern.

    Um die Woerten zu zaehlen, benoetigen wir neben einer Eingabe (Zeichen WS, CH, EOS)
    auch eine Ausgabe (Anzahl der gefunden Woerter).

    Dazu koennen wir einen Mealy/Moore Automaten verwenden.
    Z.B. im Fall eines Mealy Automaten koennen wir auf die Transition eine Ausgabe legen.

    Notation.

    Wir schreiben

    state1 -- In / Out --> state2

    Fuer einen Uebergang von Zustand state1 nach Zustand state2,
    falls das aktuelle Eingabesymbol In ist.
    Als Ausgabe finden wir Out.
    Ein Mealy Automate liefert einen Trace von Ausgabesymbolen.
    Wir benutzen zur Vereinfachung eine Zustandsvariable.


    -- / cnt=0 --> 1

    1 -- WS --> 1

    1 -- EOS --> 2

    1 -- CH / cnt++ --> 3

    3 -- WS --> 1

    3 -- CH --> 3

    3 -- EOS --> 2



     */



    // Implementierung 1

    char* scanWS(char* s) {

      while(*s == ' ') {
        s++;
      }
      return s;  
    }

    int isCH(char c) {
      return (c != ' ' && c != '\0');
    }

    char* scanCH(char* s) {

      while(isCH(*s)) {
        s++;
      }
      return s;
    }


    int countWords(char* s) {
      int cnt = 0;

      s = scanWS(s);

      while(isCH(*s)) {
        cnt++;
        s = scanCH(s);
        s = scanWS(s);
      }
      return cnt;
    }

    // Implementierung 2
    // Direkte Umsetzung des Modells.

    int countWordsModell(char* s) {
      int state = 1;
      int cnt = 0;

      while(1) {
        switch(state) {
        case 1:
           if(*s == ' ')
         state = 1;
           if(*s == '\0')
         state = 2;
           if(isCH(*s)) {
         cnt++;
         state = 3;
           }
           break;
        case 2:
          return cnt;              
        case 3:
           if(*s == ' ')
         state = 1;
           if(*s == '\0')
         state = 2;
           if(isCH(*s))
         state = 3;
           break;

        } // switch

       s++; // next symbol

      } // while
    }



    int main() {

      // Write your own tests and use cases :)
      
      return 1;
    }

## Communicating Finite State Machines (CFSM)

Communication among FSM. How?

Transitions with input and output actions.

Synchronization via hand-shake.

### Definition

    Let C be a finite alphabet of channel names.
    For each x in C, we refer to x! as an output action over channel x and
    to x? as an input action over channel x.

    Let S be a finite set of states. We generally use symbols p,q to refer to states.

    We define a CFSM = (M_1, ..., M_n) as an n-tuple of finite state machines M_i.

    Each finite state machine M consists of 

    (1) a finite set of states S where there is a designated starting state,
        written M.init, and

    (2) a finite set of transitions of the following three forms

          p ----> q     

          p -x!-> q

          p -x?-> q

    where x in C and p,q in S.

    We refer to the first kind as an "epsilon" transition
    and to the second and third kind, as output and input
    transitions respectively

    Let p_i be a state of the FSM M_i.
    We refer to (p_1, ..., p_n) as a (state) configuration of the CFSM.
    We refer to (M_1.init, ..., M_n.init) as the initial configuration of the CFSM.


    Execution proceeds by rewriting configurations which boils
    down to executing transitions of the individual FSM.
    Epsilon transitions can be executed spontaneously whereas
    input and output transititions require synchronization.



      (p_1, ..., p_i, ..., p_n) ----->   (p_1, ..., q_i, ..., p_n)


              if we find  p_i -----> q_i in M_i


      (p_1, ..., p_i, ..., p_j, ..., p_n) --x-->   (p_1, ..., q_i, ..., q_j, ..., p_n)  

              if either    p_i -x!-> q_i in M_i  and p_j -x?-> q_j in M_j
                 or        p_i -x?-> q_i in M_i  and p_j -x!-> q_j in M_j


    We refer to a path as a sequence of execution steps starting from the initial configuration.

    There may be several (alternative) paths and paths may not be finite (there are no final states).
    We can represent all possible execution steps as a tree-like structure where the
    root represents the initial configuration.

### Examples

"black-board"

### Go versus CFSM

"black-board"

# Temporal specification

## Motivation

Specify the behavior of a system over time.

-   Eventually ...

-   Always ...

-   Sometimes ...

-   If somewhen ... then from here on always ...

## Timed Computation Tree Logic (TCTL)

Specify the (expected) behavior of a CFSM in terms of the tree-like
structure which is obtained by execution of the CFSM.

### Definition

    TCTL ::=   A[] B
          |    A<> B
          |    E[] B
          |    E<> B
          |    B --> B

    B ::=  SomeAtomicProposition
      |   B and B
      |   B or B
      |   B imply B
      |   not B
      |   (B)


    B makes statements about configurations, for example

       M_1.init and M_2.exit

      M_1 is in the initial state and M_2 ist in the exist state

    Informal semantic meaning:

    A     for all paths

    E     for at least one path

    []    for all configurations

    <>    for at least one configuration


    Considering the specific cases.


    A[]B   For all paths and configurations along each path B holds.

    A<>B   For all paths there is at least one configuration for which B holds.

    E[]B   There exists a path and along that path,
           for all configurations B holds.

    E<>B   There exists a path and along that path,
           for at least one configuration B holds.


    Special case:

    B1 --> B2   = A[] (B1 imply A<> B2)

          For all paths, if we encounter a configuration for which B1 holds,
          then for all paths which continue from that configuration,
               we must find a configuration where B2 holds.

### Safety versus Liveness

Safety = Something bad never happens.

    A[] B    Invariant

    E[] B   Some "safe" path exists

Liveness = Something good will eventually happen.

    A<> B              We eventually reach "B"

    B1 --> B2          "B1" eventually leads to "B2"

### Algebraic Laws

    not A [] B = E <> not B

    not A <> B = E [] not B

    not E [] B = A <> not B

    not E <> B = A [] not B

## Linear Temporal Logic (LTL)

Specify the (expected) behavior of a CFSM in terms of the traces which
are obtained by execution of the CFSM.

### Definition

    Trace = sequence of synchronization points = channel names.

    We write "config" to denote a configuration where config_0
    represents the initial configuration.

    Consider the path

       config_0
       --x_1-->
       config_1
       --x_2-->
       ....

    Then, the trace implied by the above path consists of

       x_1 x_2 ...


    Recall that paths are infinite (and so are traces!).

LTL is a form of linear logic which states properties about the traces
which are obtained by execution of the CFSM.

    L   ::=   x               where x in C
        |   L /\ L
        |   L \/ L
        |   ! L
        |   globally L             
        |   eventually L           
        |   L until L
        |   next L
        |   (L)



    LTL infinite trace semantics.

    Let w be an infinite sequence of channel names.

    We write w^i to denote the trace obtained by dropping the first i channels.
    We write w[i] to refer to the i-th position in w.
    We start counting with 0.

    We write w |= L to denote that L satisfies w.

    w |= x            iff   w[0] = x

    w |= L1 /\ L2     iff   w |= L1 and w |= L2

    w |= L1 \/ L2     iff   w |= L1 or w |= L2

    w |= ! L          iff   w |= L does not hold

    w |= globally L   iff forall i.  w^i |= L

    w |= eventually L iff exists i. w^i |= L

    w |= L1 until L2  iff exists i>=0. w^i |= L2 and forall 0<= k < i. w^k |= L1

                          so either L2 holds immediately, or
                          at some point in the future, where L1 holds at each instant till that point

    w |= next L       iff w^1 |= L

# Model checking

Check if a model meets a specification.

For our case. Check that the CFSM meets some TCTL or LTL property,
written `CFSM |= TCTL`.

Further reading about [model
checking](https://en.wikipedia.org/wiki/Model_checking)

## Model checking applications

Verification of hardware/software systems.

### Classical uses cases

-   Get an idea about the "system's" behavior at an early stage.

-   Validate customer requirements. What do you want? Is this the
    intended behavior?

-   We sometimes can automatically generated (runnable) code out of a
    model. Assuming the model has been validated and the generated code
    reflects the behavior of the model, the code is verified by
    construction!

-   In general, the model is an abstraction of the actual system (some
    details are left out).

### Modern uses

-   Test case generation.

-   Build a model of the system.

-   Either manually (via simulation) or automatically via temporal
    properties, generate test cases

### Issues

-   Model checking is meant to complete testing and simulation (not a
    substitute!)

-   Model checking a Java program directly is not feasible in general.

-   The model we abstract away certain details (to remain decidable).
    For example, both branches ("then" and "else") are possible
    regardless of the Boolean condition.

-   Hence, model checking highly depends on how accurately the model
    abstracts the actual system behavior.

-   Failure in the model does not necessarily mean the behavior can be
    replayed in the actual system. This is known as "false positives".

-   On the other hand, an actual bug may be undetected because the model
    does not fully capture the entire system.

## Model checking algorithm

Here's a rough sketch of the model checking algorithm.

1.  CFSM |= TCTL means that all behavior (paths) in the CFSM are also
    valid in the TCTL formula.

2.  Logically, this corresponds to an implication:
    `forall path. path in CFSM implies path in TCTL`.

3.  The standard approach is to check the opposite (contradiction).

4.  `exists path. path in CFSM and path not in TCTL`.

5.  This property is checked as follows.

6.  Turn the TCTL formula into an automata A1.

7.  Build the complement of A1 which yields automata A2.

8.  Run both, CFSM and A2, simultaneously, if we reach a "final" state
    in the product automta of A1 and A2, we have found a
    counter-example!

9.  Otherwise, the property `CFSM |= TCTL` holds.

## References

[Software Model Checking Takes
Off](https://cacm.acm.org/magazines/2010/2/69362-software-model-checking-takes-off/fulltext)

[A Case Study of Toyota Unintended Acceleration and Software
Safety](https://users.ece.cmu.edu/~koopman/pubs/koopman14_toyota_ua_slides.pdf)

[Hardware model checking
(tutorial)](http://vlsi.colorado.edu/~fabio/hwmcTutorialCAV2014.pdf)

[Spin - a popular model
checker](http://spinroot.com/spin/whatispin.html)

# UPPAAL

[UPPAAL](www.uppaal.org/) is a modelchecker with a graphical language
for modeling based on Communicating Finite State Machines (CFSM) and a
temporal specification language based on the Temporal Computation Tree
Logic (TCTL). *Modelchecking* means that UPPAAL verifies if the model
satisfies the specification.

## From UPPAAL to Go

Let's consider the "coffeemachine" example (see sample solution ilias).

![Coffeemachine](data:image/png;base64,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)

Coffeemachine

![User](data:image/png;base64,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)

User

### First try

    const (
        Active    = 0
        Initial   = 1
        HasCoffee = 2
    )

    func coffeeMachine(coffee, enter, exit, payback,
        insert20, insert50, insert100 (chan int)) {
        var state int = Initial
        var acc int = 0

        for {
            switch {
            case state == Initial:
                select {
                case <-enter:
                    state = Active
                case <-exit:
                } // select
            case state == Active:
                select {
                case <-coffee:
                    if acc >= 150 {
                        acc = acc - 150
                    }
                case <-insert20:
                    acc = acc + 20
                case <-insert50:
                    acc = acc + 50
                case <-insert100:
                    acc = acc + 100
                case <-payback:
                    if acc > 0 {
                        acc = 0
                    }
                case <-exit:
                    state = Initial
                } // select

            } // switch
        } // for

    }

There's a problem.

In the UPPAAL model:

-   If `acc >= 150` *and* we synchronize via the `coffee` channel ...

In our Go implementation,

-   we first check if we can synchronize via `coffee`, and

-   then afterwards check the guard `acc >= 150`.

So, we need to check both conditions (can we synchroinze and is the
guard satisfied) atomically! How to do achieve this in Go?

### Second try (using `default`)

Recall the principle of `select` paired with `default`.

    select {
       case ch <- 1: // Action1
       default:      // Action2
    }

With out `default`, the `select` will block if we can send via channel
`ch`. With `default`, we first check all cases, if none of the cases
(such as send via channel `ch`) is available, we pick the `default`
case.

Applied to our example.

1.  Check for guard.

2.  Then, check if synchronization is possible.

3.  If we can't synchronize then "exit" via `default`.

    func coffeeMachine(coffee, enter, exit, payback,
        insert20, insert50, insert100 (chan int)) {
        var state int = Initial
        var acc int = 0

        for {
            switch {
            case state == Initial:
                select {
                case <-enter:
                    state = Active
                case <-exit:
                } // select
            case state == Active:
                select {
                case <-insert20:
                    acc = acc + 20
                case <-insert50:
                    acc = acc + 50
                case <-insert100:
                    acc = acc + 100
                case <-exit:
                    state = Initial
                default:
                    if acc >= 150 {
                        select {
                        case <-coffee:
                            acc = acc - 150
                        case <-payback:
                            acc = 0
                        default:

                        }
                    } // if

                    if acc < 150 && acc > 0 {
                        select {
                        case <-payback:
                            acc = 0
                        default:

                        }
                    }
                } // select

            } // switch
        } // for

    }

This works! But is a bit ugly cause we encounter a "busy-waiting loop".
We might repeatedly check for the guard and then the synchronization.

Unfortunately, in Go we can't impose a guard condition on the cases in a
`select` statement.

### Final try

Idea: Duplicate states by distinguishing if the guard is satisfied or
not.

So, in the state `state == Active && acc >= 150` a synchronization via
`coffee` is possible.

Here's the implementation of this idea.

    func coffeeMachine(coffee, enter, exit, payback,
        insert20, insert50, insert100 (chan int)) {
        var state int = Initial
        var acc int = 0

        for {
            switch {
            case state == Initial:
                select {
                case <-enter:
                    state = Active
                case <-exit:
                } // select
            case state == Active && acc >= 150:
                select {
                case <-coffee:
                    acc = acc - 150
                case <-insert20:
                    acc = acc + 20
                case <-insert50:
                    acc = acc + 50
                case <-insert100:
                    acc = acc + 100
                case <-payback:
                    acc = 0
                case <-exit:
                    state = Initial
                } // select

            case state == Active && 150 > acc && acc > 0:
                select {
                case <-insert20:
                    acc = acc + 20
                case <-insert50:
                    acc = acc + 50
                case <-insert100:
                    acc = acc + 100
                case <-payback:
                    acc = 0
                case <-exit:
                    state = Initial
                } // select

            case state == Active && acc <= 0:
                select {
                case <-insert20:
                    acc = acc + 20
                case <-insert50:
                    acc = acc + 50
                case <-insert100:
                    acc = acc + 100
                case <-exit:
                    state = Initial
                } // select
            } // switch
        } // for

    }

Pro: We no longer require a "busy-waiting" loop.

Cons: Codeduplication (because states are combined with guard
conditions).

#### Complete (final try) code with user

    // Translating UPPAAL to Go
    // 

    package main

    import "fmt"

    const (
        Active    = 0
        Initial   = 1
        HasCoffee = 2
    )

    func coffeeMachine(coffee, enter, exit, payback,
        insert20, insert50, insert100 (chan int)) {
        var state int = Initial
        var acc int = 0

        for {
            switch {
            case state == Initial:
                select {
                case <-enter:
                    state = Active
                case <-exit:
                } // select
            case state == Active && acc >= 150:
                select {
                case <-coffee:
                    acc = acc - 150
                case <-insert20:
                    acc = acc + 20
                case <-insert50:
                    acc = acc + 50
                case <-insert100:
                    acc = acc + 100
                case <-payback:
                    acc = 0
                case <-exit:
                    state = Initial
                } // select

            case state == Active && 150 > acc && acc > 0:
                select {
                case <-insert20:
                    acc = acc + 20
                case <-insert50:
                    acc = acc + 50
                case <-insert100:
                    acc = acc + 100
                case <-payback:
                    acc = 0
                case <-exit:
                    state = Initial
                } // select

            case state == Active && acc <= 0:
                select {
                case <-insert20:
                    acc = acc + 20
                case <-insert50:
                    acc = acc + 50
                case <-insert100:
                    acc = acc + 100
                case <-exit:
                    state = Initial
                } // select
            } // switch
        } // for

    }

    func coffeeMachineWrong(coffee, enter, exit, payback,
        insert20, insert50, insert100 (chan int)) {
        var state int = Initial
        var acc int = 0

        for {
            switch {
            case state == Initial:
                select {
                case <-enter:
                    state = Active
                case <-exit:
                } // select
            case state == Active:
                select {
                case <-coffee:
                    if acc >= 150 {
                        acc = acc - 150
                    }
                case <-insert20:
                    acc = acc + 20
                case <-insert50:
                    acc = acc + 50
                case <-insert100:
                    acc = acc + 100
                case <-payback:
                    if acc > 0 {
                        acc = 0
                    }
                case <-exit:
                    state = Initial
                } // select

            } // switch
        } // for

    }

    func coffeeMachineBusyWait(coffee, enter, exit, payback,
        insert20, insert50, insert100 (chan int)) {
        var state int = Initial
        var acc int = 0

        for {
            switch {
            case state == Initial:
                select {
                case <-enter:
                    state = Active
                case <-exit:
                } // select
            case state == Active:
                select {
                case <-insert20:
                    acc = acc + 20
                case <-insert50:
                    acc = acc + 50
                case <-insert100:
                    acc = acc + 100
                case <-exit:
                    state = Initial
                default:
                    if acc >= 150 {
                        select {
                        case <-coffee:
                            acc = acc - 150
                        case <-payback:
                            acc = 0
                        default:

                        }
                    } // if

                    if acc < 150 && acc > 0 {
                        select {
                        case <-payback:
                            acc = 0
                        default:

                        }
                    }
                } // select

            } // switch
        } // for

    }

    func user(userID string, coffee, enter, exit, payback,
        insert20, insert50, insert100 (chan int)) {
        var state int = Initial

        for {
            switch {
            case state == Initial:
                select {
                case exit <- 1:
                    // we remain in Initial
                case enter <- 1:
                    state = Active
                }
            case state == Active:
                select {
                case exit <- 1:
                    state = Initial
                case payback <- 1:
                case coffee <- 1:
                    state = HasCoffee
                case insert20 <- 1:
                case insert50 <- 1:
                case insert100 <- 1:

                }
            case state == HasCoffee:
                fmt.Printf("%s: I got coffee \n", userID)
                state = Active

            }

        }

    }

    func main() {

        var coffee = make(chan int)
        var enter = make(chan int)
        var exit = make(chan int)
        var payback = make(chan int)
        var insert20 = make(chan int)
        var insert50 = make(chan int)
        var insert100 = make(chan int)

        fmt.Print("Let's get coffee \n")

        go coffeeMachine(coffee, enter, exit, payback,
            insert20, insert50, insert100)

        go user("Max", coffee, enter, exit, payback,
            insert20, insert50, insert100)

        user("Moritz", coffee, enter, exit, payback,
            insert20, insert50, insert100)
    }

# Static versus dynamic verification

## Verification by example

Consider the program.

    int f(int n) {
      if(n == 0)
         return 1;

      if(n > 0)
         return f(n-1);

      if(n < -2)
        return f(n+1);

      return f(n-1);
    }

We observe.

    f(5) => f(4) => f(3) => f(2) => f(1) => f(0) => terminates

    f(10) => ... => f(0) => terminates

    f(-4) => f(-3) => f(-4) => f(-3) => ....

    does not seem to terminate (maybe we need to wait a bit longer?)

We verify. For all positive inputs, the function terminates. For
example, via an inductive proof.

## Dynamic verification

-   At run-time, execute the program.

-   Observe its (actual) behavior.

-   Also commonly referred to as run-time verification and testing.

## Static verification

-   Build approximation of the program's behaviour

-   Verify that the approximation satisfies some properties.

-   To remain decidable, we generally need to over-approximate.

## Selection of verification methods

### Static program analysis

1.  Data-flow analysis

2.  Control-flow analysis

3.  Type and effect systems

4.  Modelchecking

### Dynamic program analysis

1.  Testing:

    -   Unit-Tests

    -   Invariants/Assertions

    -   Oracel-based testing

2.  Run-time verification:

    -   Monitor run-time behavior

    -   Check for invalid patterns of behavior

This is just a selection

# Issues (static verification)

## False positives

To carry out the static verification, we need to **capture** the
program's behavior via some appropriate model (e.g. UPPAAL is a good
candidate model for Go programs).

In the model we typically neglect certain details so that the static
verification task becomes feasible (decidable). We say that the model
overapproximates the program's behavior.

Here's an example. Consider the program (sketch).

    ...             // S1
    if(cond) {
    ...             // S2
    }
    else {
    ...             // S3
    }

We add comments to label program points.

In the UPPAAL we could keep track of boolean conditions such as `cond`.
However, the model and the verification task becomes then rather
involved and potentially no longer decidable. Keep in mind that in
`cond` we can make use of arbitrary Go functions (some may not
terminate!).

Hence, we typically build an approximation (abstraction) where we ignore
certain details. As the model shall be a faithful representation of the
program, we simply assume that both branches of the conditional
statement are applicable.

Here's the resulting model.

    S1 ---> S2
    S2 ---> S3

We make use of labels to represents states. As can be seen, the model is
non-deterministic. We can either go from S1 to S2 or S3.

A consequence of this (over)approximation is that we may encounter
**false positives**:

1.  The static verifier reports failure.
2.  The failure is observable in the model but NOT in the program.

Recall the above example where we make the conditional statement
concrete.

    ...             // S1
    if(true) {
    ...             // S2
    }
    else {
    ...             // S3
    }

The else branch is never taken because the Boolean condition always
evaluates to true. However, in the transformation from the program to
the model, we don't inspect Boolean conditions in detail. We assume that
both Boolean results, true and false, are possible. Hence, we obtain the
following model.

    S1 ---> S2
    S2 ---> S3

Suppose there's some verification failure due to state S3. This failure
is not reproducible in the program because the else branch is never
taken. We encounter a **false positive**.

## False negatives

In the above, we assume that the model overapproximates the program's
behavior. That is, the model captures all behavior in the program but
possibly more. It could happen that we make a mistake (in the
transformation from program to model).

Consider our running example.

    ...             // S1
    if(cond) {
    ...             // S2
    }
    else {
    ...             // S3
    }

Suppose we use the following model for verification.

    S1 ---> S2

The model is faulty because we igore that from program state S1 we can
reach program state S3. Suppose there's a bug once we reach program
state S3. This bug doesn't show up in the model. Hence, the verifier
reports no failure whereas the program is faulty. We encounter a **false
negative**:

1.  The static verifier reports okay.
2.  But the program is buggy.
3.  The bug is missed because the model transformation is faulty.

# Further examples for static verification

### Type checking

Types represent a (static) model of the program's run-time behavior.
Typically, false positives arise but not false negatives.

### lint/FindBugs

These tools look for suspicious program parts by using syntax checks.
False positives as well as false negatives may arise.

# Dynamic verification

We consider

    dynamic verification = testing = run-time verification

Different words with the same intention. Observe the actual program's
behavior for a fixed number of program runs. For these fixed number of
program runs we try to identify if there is a bug or not.

### Unit-Tests

Pros:

-   Easy to understand and write

Cons:

-   Manual effort. Need to stimulate SUT (=System under Test) via
    suitable inputs and specify the expected output (result).

### Invariants/Assertions

Assertions impose conditions on program locations.

    assert(x > 0)

Invariants include more complex properties that not only involves
program locations but also functions.

    forall x. switchLowHigh(switchLowHigh(x)) == x

Assertions typically make use of Boolean conditions whereas invariants
involve more complex (predicate logic) statements.

### Oracle-based testing

Oracle = able to predict expected output for any input.

Where does the oracle come from?

1.  Independent implementation
2.  Stable release
3.  ...

# Trace-Based Runtime Verification (RV)

Special instance where we are interested in the sequence of events
(=trace) emitted by a program.

*Monitoring of the runtime behavior of programs to ensure that a given
correctness property is satisfied.*

1.  Instrumentation of a program to monitor the runtime behavior we are
    interested in.

2.  Recording of runtime behavior as a sequence of events (= program
    trace).

3.  Checking that the program trace satisfies the correctness property
    (= trace validation).

## Difference to Modelchecking (MC)

-   MC considers *all* possible program runs. In RV we consider a
    *single* program run.

-   MC operates on *infinite* traces whereas RV is restricted to
    *finite* traces.

For example, consider the UPPAAL modelchecker and the examples from the
Autonomous Systems course. A typical MC example is to guarantee that the
user eventually obtains a coffee.

In RV we can only check *safety* properties ("something bad will never
happen") whereas MC typically can also deal with *liveness* properties
("something good will eventually happen").

## RV Topics

-   Program instrumentation:

    -   **Efficiency**. As little overhead as possible (time and space).
        Also important to monitor the 'true' runtime behavior of
        programs (e.g. consider concurrent programs).

    -   Either **online** or **offline** (store trace in a log file for
        example).

    -   **Compiler** extension versus **domain-specific embedding**.

-   Trace validation:

    -   **Pattern formalisms** to specify correctness (safety)
        properties, e.g. regular expressions, LTL, ...

    -   **Efficient algorithms** to implement pattern formalisms which
        work under the offline as well as online monitoring assumption.

    -   **Explanation of results** (beyond yes/no answers).

## Simple tracer in Go

    package main

    import "fmt"
    import "time"
    import "strconv"

    /*

    Simple tracer in Go.

     Features:

    - Can be used offline and online. We only show offline use case


    Issues:

    - Tracing may be inaccurate. Tracer order may not correspond to actual program execution.

    - How to detect stuck threads? We only record events after the operation is performed.

     Limitations:

    - Naive run-time monitoring via manual inspection of the trace

     More systematic run-time monitirong methods:
        Apply regular expressions/LTL to validate trace.
        
    */

    // Events

    type Kind int

    const (
        Snd   Kind = 0
        Rcv   Kind = 1
        Write Kind = 2
        Read  Kind = 3
    )

    type Event struct {
        name     string
        threadId int
        kind     Kind
    }

    func mkEvt(n string, t int, k Kind) Event {
        return Event{name: n, threadId: t, kind: k}
    }

    func showEvt(e Event) string {
        var s string
        switch {
        case e.kind == Snd:
            s = "!"
        case e.kind == Rcv:
            s = "?"
        case e.kind == Write:
            s = "W"
        case e.kind == Read:
            s = "R"
        }
        return (strconv.Itoa(e.threadId) + "#" + e.name + s)
    }

    // Tracer

    var globalCnt int
    var logChan chan Event
    var doneSignal chan int

    func initTrace() {
        logChan = make(chan Event)
        doneSignal = make(chan int)
        globalCnt = 0

    }

    func incCnt() int {
        globalCnt++
        return globalCnt
    }

    func recordEvt(e Event) {
        go func() {
            logChan <- e
        }()
    }

    func done() {
        go func() {
            doneSignal <- 1
        }()
    }

    func retrieveEvt() (Event, bool) {
        var e Event
        var r bool
        select {
        case e = <-logChan:
            r = true
        default:
            r = false
        }
        return e, r
    }

    // Variant: Relies on doneSignal channel.
    // Doesn't seem to work very well.
    func retrieveEvt2() (Event, bool) {
        var e Event
        var r bool
        select {
        case e = <-logChan:
            r = true
        case <-doneSignal:
            r = false
        }
        return e, r
    }

    // Examples

    func example1() {
        initTrace()

        ch := make(chan int)
        t1 := incCnt()
        t2 := incCnt()
        t3 := incCnt()

        // consumer 1
        go func() {
            for i := 0; i < 10; i++ {
                <-ch
                e := mkEvt("ch", t1, Rcv)
                recordEvt(e)
            }
        }()

        // consumer 2
        go func() {
            for i := 0; i < 10; i++ {
                <-ch
                e := mkEvt("ch", t2, Rcv)
                recordEvt(e)
            }
        }()

        // producer 3
        go func() {
            for i := 0; i < 10; i++ {
                ch <- 1
                e := mkEvt("ch", t3, Snd)
                recordEvt(e)
            }
        }()

        // manual synchronization
        // wait till all threads are 'done'
        time.Sleep(3 * time.Second)
        done()

        // offline trace analysis
        // simply print trace on screen

        for {
            e, r := retrieveEvt()
            if !r {
                break
            }
            fmt.Printf("\n %s", showEvt(e))

        }
    }

    func main() {
        example1()

    }
