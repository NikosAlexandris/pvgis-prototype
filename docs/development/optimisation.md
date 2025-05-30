---
icon: material/rocket-launch
tags:
  - Development
  - Roadmap
  - Progress
  - Optimisation
  - Performance
  - Data Structure
---

!!! danger "Unsorted content"

    Following content needs a review and consolidation.

This page overviews some key areas for optimization.

!!! abstract "Performance Optimisation"

    The goal is to improve the efficiency of PVGIS
    by optimizing data structures,
    refining algorithms,
    and implementing modern Python practices
    for asynchronous, concurrent, and parallel executions.
    Additionally,
    caching strategies and load balancing
    are essential for enhancing performance and scalability.


## Status

The current Proof-of-Concept,
(see commit : 
[5cca629ea186ff3c7711fbdbd8219841caf4d6b][5cca629ea186ff3c7711fbdbd8219841caf4d6b]
)
==includes== among other elements :

- quite some constants (see [constants.py][constants.py-commit-5cca629ea186ff3c7711fbdbd8219841caf4d6b1])
- [`print()`][print()] statements for output and support debugging _which is slowing down_ a programs runtime [^0]
- debugging calls, specifically `debug(locals())` from [`devtools`][devtools]
- input data validation using [Pydantic][Pydantic]
- in-function output data validation
- custom data classes/[Pydantic models][Pydantic models]
- use of lists and list comprehensions
- frequently requested/repeated calculations
- lack of caching/memoization practices
- lack of :
    - asynchronous executions,
    - concurrent executions,
    - parallel executions
        - no parallel processing beyond NumPy's own internals (?)
- using Pandas' [DatetimeIndex][DatetimeIndex] which is _not hashable_
- no use of any external compiler or library for High-Performance Computing

!!! quote ""

    Hence,
    the margin for optimisation is quite large.


## Profiling

Before optimising,
however,
it is important to quantify performance bottlenecks.

Using profiling tools like `cProfile`, `scalene`, `pyinstrument` and more for Python
we can analyse and understand
which parts of the code are consuming the most resources.


## Areas for improvement

Out of common/public programmatic experience,
documented in books, articles, software projects,
publicly accessible wikis and fora,
we can list ahead some areas for improvement
and discuss possible optimisation actions.


## Logging
  
1. Replace print statements and `debug(locals())`
   with a structured logging framework like :

    - Python's `logging` module
    - `loguru`
    - [`structlog`][structlog]

2. Remove print statements completely
   and return only JSON or other structured
   output through the Web API in the production version ?


## Debugging

The `debug(locals())` calls from [`devtools`][devtools]
can be optimised (?)
or removed completely in the production version to reduce overhead.


## Data Validation

  - Avoid redundant checks

  - Consider removing/switching off the input data validation
    for the efficient Web API module(s).
    Albeit,
    after extensive validation of the fundamental algorithms,
    the core API and the CLI
    which can ensure quality and reproducibility of operations.

??? example "Example : Efficient Data Validation with Pydantic"

    ```python
    from pydantic import BaseModel

    class ExampleModel(BaseModel):
        attribute1: int
        attribute2: str

    # Using Pydantic for validation
    example = ExampleModel(attribute1=123, attribute2="test")
    ```

## Use libraries developed in C/C++

There are numerous libraries/packages developed in C/C++
that can be integrated into Python programs. 
[Numpy][NumPy] and [Scipy][] are prominent examples,
known for their effectiveness in handling large datasets.

Use such libraries to speed-up operations. 

### NumPy Arrays

[NumPy][NumPy] is the golden standard
for scientific and high-performance computing with Python.
NumPy arrays outpace significantly common Python lists
in processing massive data and performing numerical computations.
consuming less memory than lists.


## Do Not Use .dot Operation

Dot operations may be time-consuming!

Function with a `.` (dot)
first call `__getattribute()__` or `__getattr()__`,
which then uses a dictionary operation.
This adds some overhead.
It is recommended to import functions for optimizing Python code for speed.


## Intern Strings in Python

!!! danger

    Explain.-


## Generator expressions

Use generator expressions instead of list comprehensions


## Apply multiple assignements

Instead of doing

``` python
a = 3
b = 6
c = 9
```

better do 

```python
a, b, c = 3, 6, 9
```

This approach optimizes and speeds up the code execution.


## Peephole Optimization

Code readability often comes with cost in terms of efficiency
as the language interpreter automatically calculates constant expressions.
The [peephole][Peephole] technique means to
let Python pre-compute such expressions,
replace repetitive instances with the result
and employ membership tests.
This may help to avoid performance decrease
and boost software performance.

[Peephole]: https://en.wikipedia.org/wiki/Peephole_optimization


## Data structure Optimization

Optimize in-advance massive time series data structures :

- to be contiguous time 
- small chunks of data in space

- Handle massive time series data programmatically
  by using efficient data structures like NumPy Arrays.


## Data Classes

  - Refactor PVGIS' custom Python `dataclasses` for efficiency
  - Use alternatives from well-known libraries :
    - Python's `dataclasses` or `attrs` ?

??? example "Example : Python Data Class"

    Use a Python `dataclass` as a decorator to add special methods to classes :

    ```python
    from dataclasses import dataclass

    @dataclass
    class ExampleClass:
        attribute1: int
        attribute2: str

    example = ExampleClass(123, "test")
    ```

## Caching/Memoization Strategies

### Intermediate outputs

Some core API functions,
though they produce output for different calculated quantities,
may depend on idenctical intermediate components.
Hence, it is important to experiment, understand
and apply local and distributed caching strategies.

Caching the output of frequently requested functions or data,
for example using `lru_cache` or similar mechanisms,
at the core API level,
can decrease the computation time for functions with shared dependencies
and consequently reduce response times and server load significantly.

- For local caching,
  consider Python's built-in caching tools like `functools.lru_cache`
  for caching the output of functions,
  especially for functions with expensive or repetitive computations.

    ??? example "Example : Caching/Memoization with `functools.lru_cache`"

        ```python
        from functools import lru_cache

        @lru_cache(maxsize=100)
        def expensive_function(arg):
            # Time-consuming computations
            return result
        ```

  - The non-hashable nature of Pandas' DateTimeIndex
    can be a limitation in the context of caching.
    Are there alternative data structures or methods for handling timestamps ?

    !!! danger
        
        Does not work with non-hashable data structures!

- For distributed caching,
  consider tools like [Redis][Redis] or [Memcached][Memcached].

- Caching repeatedly requested _final output_ calls at the Web API level ?


## Asynchronous operations

Asynchronous execution for I/O-bound operations
can improve
the performance of network operations,
the responsiveness
and the efficiency of I/O tasks.
It can be implemented using Python’s `asyncio` module

??? example "Example : Asynchronous Execution with `asyncio`"

    ```python
    import asyncio

    async def async_task():
        # Perform async operations
        return result

    # Running async tasks
    asyncio.run(async_task())
    ```

## Concurrent operations

For CPU-bound tasks,
explore Python’s `multiprocessing`
or `multithreading` (if tasks are I/O-bound)
to distribute computations and enhance performance.

- Many in-between calculations
  do not depend on each other
  and can, therefore, be executed independently.
  Use Python's `concurrent.futures`
  or similar libraries
  to manage concurrent tasks.

    ??? example "Example : Concurrent Executions with `concurrent.futures`"

        ```python
        from concurrent.futures import ThreadPoolExecutor

        def function_to_run_concurrently(arg):
            # Operations
            return result

        with ThreadPoolExecutor(max_workers=5) as executor:
            future = executor.submit(function_to_run_concurrently, (arg))
            return_value = future.result()
        ```

- For independent calculations
  explore libraries like `concurrent.futures`
  to manage concurrent tasks efficiently.
  

## Parallel operations

- Use parallel processing techniques and software
  to handle intensive computational tasks.

- Use Python’s `multiprocessing` module for CPU-bound tasks
  to distribute computations across multiple cores.

    ??? example "Example : Parallel Processing with `multiprocessing`"

        ```python
        from multiprocessing import Pool

        def function_to_run_in_parallel(arg):
            # Operations
            return result

        if __name__ == "__main__":
            with Pool(processes=4) as pool:
                results = pool.map(function_to_run_in_parallel, iterable_of_args)
        ```

## Optimizing Pandas Usage

Use vectorized operations and efficient data handling in Pandas.

??? example "Example : Vectorised operation using Pandas"

    ```python
    import pandas as pd

    # Example: Vectorized operation instead of a loop
    df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
    df['c'] = df['a'] + df['b']  # Vectorized addition
    ```

### Algorithmic Efficiency

Optimizing
the fundamental algorithms and the core API that power PVGIS,
can reduce the computational complexity,
which in turn may speed up operations significantly.
This is crucial for
handling efficiently large datasets,
and perform complex calculations.

The focus is on :

- reviewing and refactoring core algorithms to reduce complexity
- use systematically efficient libraries like [NumPy][NumPy] and [SciPy][SciPy] for numerical computations.
- best programming practices like avoiding Python's currently inefficient `for` loop


## High Performance Computation with Python ?

Explore the great potential
of using external libraries/frameworks for High Performance Computing
to boost the performance of PVGIS.

- Compilers/Just-in-Time Compilers

    - PyPy: A Just-In-Time (JIT) compiler for Python.
    - mypyc: A compiler that compiles Python to C-extension modules.
    - Pyjion: A JIT compiler for Python, using the .NET CLR.
    - [Cython][Cython]: an optimising static compiler for Python and Cython,
      allows writing C extensions for Python.

Cython gives you the combined power of Python and C to let you 

- Libraries/Frameworks

    - Jax: A library for numerical computations with auto-differentiation and GPU/TPU support.
    - GT4Py: A framework for writing stencil computations in geosciences.
    - Pythran: A compiler-like tool that converts Python to optimized C++ code, but also acts as a library.
    - Dace: An framework for data-centric parallel programming with support for Ahead-of-Time (AoT) compilation in addition to JIT.


## Load Balancing

!!! note

    A task mainly for and to work collaboratively with the IT support team

- Implement load balancing
- Distribute API requests evenly across multiple servers
- Enhance scalability and reliability

- Collaborate with the IT support team for implementing load balancing. This includes distributing API requests across servers and enhancing system scalability and reliability.

[^0]: https://www.codeease.net/programming/python/python-slow-print

[Cython]: https://cython.org/

[NumPy]: https://numpy.org/

[SciPy]: https://scipy.org/

[ForLoop]: https://wiki.python.org/moin/ForLoop

[5cca629ea186ff3c7711fbdbd8219841caf4d6b]: https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/commit/5cca629ea186ff3c7711fbdbd8219841caf4d6b

[constants.py-commit-5cca629ea186ff3c7711fbdbd8219841caf4d6b1]: https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/blob/5cca629ea186ff3c7711fbdbd8219841caf4d6b1/pvgisprototype/constants.py

[print()]: https://docs.python.org/3/library/functions.html#print

[devtools]: https://python-devtools.helpmanual.io/usage/#debug

[Pydantic]: https://docs.pydantic.dev/latest/

[Pydantic models]: https://docs.pydantic.dev/latest/concepts/models/

[structlog]: https://www.structlog.org/en/stable/index.html

[DatetimeIndex]: https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DatetimeIndex.html

[Redis]: https://redis.io/

[Memcached]: https://www.memcached.org/


# References

- [How not to lie with statistics: the correct way to summarize benchmark results](https://dl.acm.org/doi/10.1145/5666.5673)

- [25 Tips for optimising Python performance][softformance.com-how-to-speed-up-python-code]

[softformance.com-how-to-speed-up-python-code]: https://www.softformance.com/blog/how-to-speed-up-python-code/
