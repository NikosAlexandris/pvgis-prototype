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

- print statements for output and support debugging _which is slowing down_ a programs runtime [^0]
- debugging calls, specifically `debug(locals())` from [`devtools`][devtools]
- input data validation using [Pydantic][Pydantic]
- in-function manual output data validation
- custom data classes/[Pydantic models][Pydantic models]
- frequently requested/repeated calculations
- complete lack of caching/memoization
- if and wherever possible, complete lack of :
    - asynchronous executions,
    - concurrent executions,
    - parallel executions
        - no parallel processing beyond NumPy's own internals (?)
- using Pandas' DateTimeIndex which is _not hashable_

!!! quote ""

    Hence,
    the margin for optimisation is quite large.

## Profiling

Before optimising,
however,
it is important to quantify performance bottlenecks.

Using profiling tools like `cProfile` for Python
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

## Load Balancing

!!! note

    A task mainly for and to work collaboratively with the IT support team

- Implement load balancing
- Distribute API requests evenly across multiple servers
- Enhance scalability and reliability

- Collaborate with the IT support team for implementing load balancing. This includes distributing API requests across servers and enhancing system scalability and reliability.

[^0]: https://www.codeease.net/programming/python/python-slow-print

[NumPy]: https://numpy.org/

[SciPy]: https://scipy.org/

[ForLoop]: https://wiki.python.org/moin/ForLoop

[5cca629ea186ff3c7711fbdbd8219841caf4d6b]: https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/commit/5cca629ea186ff3c7711fbdbd8219841caf4d6b

[devtools]: https://python-devtools.helpmanual.io/usage/#debug

[Pydantic]: https://docs.pydantic.dev/latest/

[Pydantic models]: https://docs.pydantic.dev/latest/concepts/models/

[structlog]: https://www.structlog.org/en/stable/index.html

[Redis]: https://redis.io/

[Memcached]: https://www.memcached.org/
