---
title: Futures and Promises
description: Martin Sulzmann 
---

## Overview

Futures and promises are a high-level concurrency construct to
support asynchronous programming. A future can be viewed as a
placeholder for a computation that will eventually become available. The
term promise is often referred to a form of future where the result can
be explicitly provided by the programmer. For a high-level overview, see
[here](https://en.wikipedia.org/wiki/Futures_and_promises).


1. We will first implement futures via channels. We use
`interface{}’ (similar to Object in Java) to represent any
type.
2. Next, we make use of generics. We no longer require type
assertions.
3. We improve the implementation by reducing the number of
goroutines. This leads to the concept of a promise.



## Channel-based futures


```go
type Comp struct {
 val interface{}
 status bool
}

type Future chan Comp

func future(f func() (interface{}, bool)) Future {
 ch := make(chan Comp)
 go func() {
 r, s := f()
 v := Comp{r, s}
 for {
 ch <- v
 }
 }()
 return ch

}

func (f Future) get() (interface{}, bool) {
 v := <-f
 return v.val, v.status
}

func (ft Future) onSuccess(cb func(interface{})) {
 go func() {
 v, o := ft.get()
 if o {
 cb(v)
 }
 }()

}

func (ft Future) onFailure(cb func()) {
 go func() {
 \_, o := ft.get()
 if !o {
 cb()
 }
 }()

}
```

* We use `interface{}` to represent any type.


	+ We will shortly introduce generics.
* We use a Boolean value to indicate success or failure of a
computation. Hence, the type `Comp` to represent the result
of a (future) computation.
* A value of type `Future` is an initially empty program
variable. We represent this via an unbuffered channel of type
`Comp`.
* Function `future` carries out the computation
asynchronously (in its own thread).
* The result of the computation will be transmitted via the
channel.
* We repeatedly transmit the value (in an infinite loop) to
retrieve the value of a `Future`an arbitrary number of times
(multiple `get`, `onSuccess`, `onFail`
calls).
* We can access the value via `get` by performing a
receive operation on the channel. This operation blocks if no value is
available yet.
* We can asynchronously access the value via methods
`onSuccess` and `onFailure`.
* Both methods take as arguments a callback functions. Callbacks
will be applied once the computation has finished.


Example
-------


Here is an example application where we asynchronously execute some
http request. While waiting for the request, we can “do something
else”.



```go
func getSite(url string) Future {
 return future(func() (interface{}, bool) {
 resp, err := http.Get(url)
 if err == nil {
 return resp, true
 }
 return err, false
 })
}

func printResponse(response \*http.Response) {
 fmt.Println(response.Request.URL)
 header := response.Header
 // fmt.Println(header)
 date := header.Get("Date")
 fmt.Println(date)

}

func example1() {

 stern := getSite("http://www.stern.de")

 stern.onSuccess(func(result interface{}) {
 response := result.(\*http.Response)
 printResponse(response)

 })

 stern.onFailure(func() {
 fmt.Printf("failure \n")
 })

 fmt.Printf("do something else \n")

 time.Sleep(2 \* time.Second)

}
```


## More expressive functionality for futures

Suppose we fire up several http requests (say stern and spiegel) and
would like to retrieve the first available request. How can this be
implemented?


A naive (inefficient) solution would check for each result one after
the other (via `get`). Can we be more efficient? Yes, we can
make use of `select` to check for the first available future
result.


`first` and
`firstSucc`
-----------------------



```go
// Pick first available future
func (ft Future) first(ft2 Future) Future {

 return future(func() (interface{}, bool) {

 var v interface{}
 var o bool

 // check for any result to become available
 select {
 case x := <-ft:
 v = x.val
 o = x.status

 case x2 := <-ft2:
 v = x2.val
 o = x2.status

 }

 return v, o
 })
}

// Pick first successful future
func (ft Future) firstSucc(ft2 Future) Future {

 return future(func() (interface{}, bool) {

 var v interface{}
 var o bool

 select {
 case x := <-ft:
 if x.status {
 v = x.val
 o = x.status
 } else {
 v, o = ft2.get()
 }

 case x2 := <-ft2:
 if x2.status {
 v = x2.val
 o = x2.status
 } else {
 v, o = ft.get()
 }

 }

 return v, o
 })
}
```

Example
-------


Our example with three http requests where we are only interested in
the first available request.



```go
 spiegel := getSite("http://www.spiegel.de")
 stern := getSite("http://www.stern.de")
 welt := getSite("http://www.welt.com")

 req := spiegel.first(stern.first(welt))

 req.onSuccess(func(result interface{}) {
 response := result.(\*http.Response)
 printResponse(response)

 })

 req.onFailure(func() {
 fmt.Printf("failure \n")
 })

 fmt.Printf("do something else \n")

 time.Sleep(2 \* time.Second)
```

Another example (holiday
booking)
---------------------------------



```go
// Holiday booking
func example3() {

 // Book some Hotel. Report price (int) and some poential failure (bool).
 booking := func() (int, bool) {
 time.Sleep((time.Duration)(rand.Intn(999)) \* time.Millisecond)
 return rand.Intn(50), true
 }

 // Yikes!
 // f1 := future(booking)
 f1 := future(func() (interface{}, bool) {
 return booking()
 })

 // Another booking request.
 f2 := future(func() (interface{}, bool) {
 return booking()
 })

 f3 := f1.firstSucc(f2)

 f3.onSuccess(func(result interface{}) {

 quote := result.(int) // Yikes!
 fmt.Printf("\n Hotel asks for %d Euros", quote)
 })

 time.Sleep(2 \* time.Second)
}
```

We require type assertions to due our use of `interface{}’ to
represent any type.


Channel-based
futures - complete source code
--------------------------------------------



```go
package main

import "fmt"
import "time"
import "net/http"
import "math/rand"

////////////////////
// Simple futures

// A future, once available, will be transmitted via a channel.
// The Boolean parameter indicates if the (future) computation succeeded or failed.

type Comp struct {
 val interface{}
 status bool
}

type Future chan Comp

// "Server-side" approach
func future(f func() (interface{}, bool)) Future {
 ch := make(chan Comp)
 go func() {
 r, s := f()
 v := Comp{r, s}
 for {
 ch <- v
 }
 }()
 return ch

}

func (f Future) get() (interface{}, bool) {
 v := <-f
 return v.val, v.status
}

func (ft Future) onSuccess(cb func(interface{})) {
 go func() {
 v, o := ft.get()
 if o {
 cb(v)
 }
 }()

}

func (ft Future) onFailure(cb func()) {
 go func() {
 \_, o := ft.get()
 if !o {
 cb()
 }
 }()

}

///////////////////////////////
// Adding more functionality

// Pick first available future
func (ft Future) first(ft2 Future) Future {

 return future(func() (interface{}, bool) {

 var v interface{}
 var o bool

 // check for any result to become available
 select {
 case x := <-ft:
 v = x.val
 o = x.status

 case x2 := <-ft2:
 v = x2.val
 o = x2.status

 }

 return v, o
 })
}

// Pick first successful future
func (ft Future) firstSucc(ft2 Future) Future {

 return future(func() (interface{}, bool) {

 var v interface{}
 var o bool

 select {
 case x := <-ft:
 if x.status {
 v = x.val
 o = x.status
 } else {
 v, o = ft2.get()
 }

 case x2 := <-ft2:
 if x2.status {
 v = x2.val
 o = x2.status
 } else {
 v, o = ft.get()
 }

 }

 return v, o
 })
}

///////////////////////
// Examples

func getSite(url string) Future {
 return future(func() (interface{}, bool) {
 resp, err := http.Get(url)
 if err == nil {
 return resp, true
 }
 return err, false
 })
}

func printResponse(response \*http.Response) {
 fmt.Println(response.Request.URL)
 header := response.Header
 // fmt.Println(header)
 date := header.Get("Date")
 fmt.Println(date)

}

func example1() {

 stern := getSite("http://www.stern.de")

 stern.onSuccess(func(result interface{}) {
 response := result.(\*http.Response)
 printResponse(response)

 })

 stern.onFailure(func() {
 fmt.Printf("failure \n")
 })

 fmt.Printf("do something else \n")

 time.Sleep(2 \* time.Second)

}

func example2() {

 spiegel := getSite("http://www.spiegel.de")
 stern := getSite("http://www.stern.de")
 welt := getSite("http://www.welt.com")

 req := spiegel.first(stern.first(welt))

 req.onSuccess(func(result interface{}) {
 response := result.(\*http.Response)
 printResponse(response)

 })

 req.onFailure(func() {
 fmt.Printf("failure \n")
 })

 fmt.Printf("do something else \n")

 time.Sleep(2 \* time.Second)

}

// Holiday booking
func example3() {

 // Book some Hotel. Report price (int) and some poential failure (bool).
 booking := func() (int, bool) {
 time.Sleep((time.Duration)(rand.Intn(999)) \* time.Millisecond)
 return rand.Intn(50), true
 }

 // Yikes!
 // f1 := future(booking)
 f1 := future(func() (interface{}, bool) {
 return booking()
 })

 // Another booking request.
 f2 := future(func() (interface{}, bool) {
 return booking()
 })

 f3 := f1.firstSucc(f2)

 f3.onSuccess(func(result interface{}) {

 quote := result.(int) // Yikes!
 fmt.Printf("\n Hotel asks for %d Euros", quote)
 })

 time.Sleep(2 \* time.Second)
}

func main() {

 // example1()

 // example2()

 example3()
}
```


## Generics to the rescue


```go
type Comp[T any] struct {
 val T
 status bool
}

type Future[T any] chan Comp[T]
```

Holiday booking again
---------------------



```go
func example3() {

 // Book some Hotel. Report price (int) and some poential failure (bool).
 booking := func() (int, bool) {
 time.Sleep((time.Duration)(rand.Intn(999)) \* time.Millisecond)
 return rand.Intn(50), true
 }

 f1 := future[int](booking)

 // Another booking request.
 f2 := future[int](booking)

 f3 := f1.firstSucc(f2)

 f3.onSuccess(func(quote int) {

 fmt.Printf("\n Hotel asks for %d Euros", quote)
 })

 time.Sleep(2 \* time.Second)
}
```

Complete source code
--------------------



```go
package main

import "fmt"
import "time"
import "net/http"
import "math/rand"

////////////////////
// Simple futures with generics

// A future, once available, will be transmitted via a channel.
// The Boolean parameter indicates if the (future) computation succeeded or failed.

type Comp[T any] struct {
 val T
 status bool
}

type Future[T any] chan Comp[T]




// "Server-side" approach
func future[T any](f func() (T, bool)) Future[T] {
 ch := make(chan Comp[T])
 go func() {
 r, s := f()
 v := Comp[T]{r, s}
 for {
 ch <- v
 }
 }()
 return ch

}

func (f Future[T]) get() (T, bool) {
 v := <-f
 return v.val, v.status
}

func (ft Future[T]) onSuccess(cb func(T)) {
 go func() {
 v, o := ft.get()
 if o {
 cb(v)
 }
 }()

}

func (ft Future[T]) onFailure(cb func()) {
 go func() {
 \_, o := ft.get()
 if !o {
 cb()
 }
 }()

}

///////////////////////////////
// Adding more functionality

// Pick first available future
func (ft Future[T]) first(ft2 Future[T]) Future[T] {

 return future(func() (T, bool) {

 var v T
 var o bool

 // check for any result to become available
 select {
 case x := <-ft:
 v = x.val
 o = x.status

 case x2 := <-ft2:
 v = x2.val
 o = x2.status

 }

 return v, o
 })
}

// Pick first successful future
func (ft Future[T]) firstSucc(ft2 Future[T]) Future[T] {

 return future(func() (T, bool) {

 var v T
 var o bool

 select {
 case x := <-ft:
 if x.status {
 v = x.val
 o = x.status
 } else {
 v, o = ft2.get()
 }

 case x2 := <-ft2:
 if x2.status {
 v = x2.val
 o = x2.status
 } else {
 v, o = ft.get()
 }

 }

 return v, o
 })
}

///////////////////////
// Examples


func getSite(url string) Future[\*http.Response] {
 return future(func() (\*http.Response, bool) {
 resp, err := http.Get(url)
 if err == nil {
 return resp, true
 }
 return resp, false // ignore err, we only report "false"
 })
}

func printResponse(response \*http.Response) {
 fmt.Println(response.Request.URL)
 header := response.Header
 // fmt.Println(header)
 date := header.Get("Date")
 fmt.Println(date)

}

func example1() {

 stern := getSite("http://www.stern.de")

 stern.onSuccess(func(response \*http.Response) {
 printResponse(response)

 })

 stern.onFailure(func() {
 fmt.Printf("failure \n")
 })

 fmt.Printf("do something else \n")

 time.Sleep(2 \* time.Second)

}

func example2() {

 spiegel := getSite("http://www.spiegel.de")
 stern := getSite("http://www.stern.de")
 welt := getSite("http://www.welt.com")

 req := spiegel.first(stern.first(welt))

 req.onSuccess(func(response \*http.Response) {
 printResponse(response)

 })

 req.onFailure(func() {
 fmt.Printf("failure \n")
 })

 fmt.Printf("do something else \n")

 time.Sleep(2 \* time.Second)

}


// Holiday booking
func example3() {

 // Book some Hotel. Report price (int) and some poential failure (bool).
 booking := func() (int, bool) {
 time.Sleep((time.Duration)(rand.Intn(999)) \* time.Millisecond)
 return rand.Intn(50), true
 }

 f1 := future[int](booking)

 // Another booking request.
 f2 := future[int](booking)

 f3 := f1.firstSucc(f2)

 f3.onSuccess(func(quote int) {

 fmt.Printf("\n Hotel asks for %d Euros", quote)
 })

 time.Sleep(2 \* time.Second)
}


func main() {

 // example1()

 // example2()

 // example3()
}
```


## Discussion

* Each future implies a goroutine.
* Each onSuccess/onFailure call implies a goroutine.
* Combinators first/firstSucc rely on the `future’ primitive and
therefore imply a goroutine.


Goroutines in Go are cheap (compared to threads in Java).


However, we should avoid them if possible.


Idea:


* Each future maintains a list of callback functions.


	+ One list for the success case.
	+ Another list for the failiure case.
* Each onSuccess/onFailure call adds the callback to the respective
list.
* What if the “future” value is already present?


	+ Then, there’s no need to register the callback.
	+ We can immediately apply the “future” value and process the
	callback.



## Futures via Promises


```go
type Promise[T any] struct {
 val T
 status bool
 m chan int
 succCallBacks []func(T)
 failCallBacks []func()
 empty bool
}

func newPromise[T any]() \*Promise[T] {
 p := Promise[T]{empty: true, m: make(chan int, 1), succCallBacks: make([]func(T), 0), failCallBacks: make([]func(), 0)}
 return &p
}
```

* Promises are initialy empty
* We use a buffered channel to simulate a mutex (as we need to
avoid races if goroutines concurrently access the same promise)
* We use slices to register succ/fail callbacks
* Maintain a reference to a promise to ensure that promises are
copied automatically


Complete source code
--------------------



```go
package main

import "fmt"
import "time"
import "math/rand"

////////////////////
// Reducing the number of gourtines.
// Internally, we use a promise as we might want to explicitly provide the (future) value.

// A promise is a form of a future where the result can be provided explicitely via some setSucc/setFail primitives.
// A promise can only be completed once.
// We keep of the completion status via the boolean flag empy.
// If empty any callback will be registered and executed once the promise is completed.

type Promise[T any] struct {
 val T
 status bool
 m chan int
 succCallBacks []func(T)
 failCallBacks []func()
 empty bool
}

func newPromise[T any]() \*Promise[T] {
 p := Promise[T]{empty: true, m: make(chan int, 1), succCallBacks: make([]func(T), 0), failCallBacks: make([]func(), 0)}
 return &p
}

// Check if still empty.
// If yes, call all registered callbacks within one goroutine.
// Otherwise, do nothing.
func (p \*Promise[T]) setSucc(v T) {
 p.m <- 1
 if p.empty {
 p.val = v
 p.status = true
 p.empty = false
 succs := p.succCallBacks
 p.succCallBacks = make([]func(T), 0)
 <-p.m
 go func() {
 for \_, cb := range succs {
 cb(v)
 }
 }()
 } else {
 <-p.m
 }

}

func (p \*Promise[T]) setFail() {
 p.m <- 1
 if p.empty {
 p.status = false
 p.empty = false
 fails := p.failCallBacks
 p.failCallBacks = make([]func(), 0)
 <-p.m
 go func() {
 for \_, cb := range fails {
 cb()
 }
 }()
 } else {
 <-p.m
 }

}

func future[T any](f func() (T, bool)) \*Promise[T] {
 p := newPromise[T]()
 go func() {
 r, s := f()
 if s {
 p.setSucc(r)
 } else {
 p.setFail()
 }
 }()
 return p
}

func (p \*Promise[T]) complete(f func() (T, bool)) {
 go func() {
 r, s := f()
 if s {
 p.setSucc(r)
 } else {
 p.setFail()
 }
 }()

}

func (p \*Promise[T]) onSuccess(cb func(T)) {
 p.m <- 1
 switch {
 case p.empty:
 p.succCallBacks = append(p.succCallBacks, cb)
 case !p.empty && p.status:
 go cb(p.val)
 default: // drop cb, will never be called

 }
 <-p.m

}

func (p \*Promise[T]) onFailure(cb func()) {
 p.m <- 1
 switch {
 case p.empty:
 p.failCallBacks = append(p.failCallBacks, cb)
 case !p.empty && !p.status:
 go cb()
 default: // drop cb, will never be called

 }
 <-p.m

}

///////////////////////////////
// Adding more functionality

// Try to complete p with p2.
// We only consider the successful case.
func (p \*Promise[T]) tryCompleteWith(p2 \*Promise[T]) {
 p2.onSuccess(func(v T) {
 p.setSucc(v)
 })

}

// Pick first successful future
func (p \*Promise[T]) firstSucc(p2 \*Promise[T]) \*Promise[T] {
 p3 := newPromise[T]()
 p3.tryCompleteWith(p)
 p3.tryCompleteWith(p2)
 return p3
}

///////////////////////
// Examples

// Holiday booking
func example1() {

 // Book some Hotel. Report price (int) and some poential failure (bool).
 booking := func() (int, bool) {
 // time.Sleep((time.Duration)(rand.Intn(999)) \* time.Millisecond)
 return rand.Intn(50), true
 }

 f1 := newPromise[int]()
 f1.complete(booking)

 f2 := newPromise[int]()
 f2.complete(booking)

 f3 := f1.firstSucc(f2)

 f3.onSuccess(func(quote int) {

 fmt.Printf("\n Hotel asks for %d Euros", quote)
 })

 time.Sleep(2 \* time.Second)
}

func example2() {

 // Book some Hotel. Report price (int) and some poential failure (bool).
 booking := func() (int, bool) {
 // time.Sleep((time.Duration)(rand.Intn(999)) \* time.Millisecond)
 return rand.Intn(50), true
 }

 f1 := future[int](booking)

 f2 := future[int](booking)

 f3 := f1.firstSucc(f2)

 f3.onSuccess(func(quote int) {

 fmt.Printf("\n Hotel asks for %d Euros", quote)
 })

 time.Sleep(2 \* time.Second)
}

func main() {

 example2()
}
```

