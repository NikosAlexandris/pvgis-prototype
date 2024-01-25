---
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

## Profiling

Profile the source code to identify performance bottlenecks and areas for improvement.

## Performance Optimization

Optimizing the performance of PVGIS'
algorithmic foundation
and core API
is crucial for handling
large datasets,
complex calculations,
and ensuring efficiency of operation.

## Status

The Proof-of-Concept,
as it stands today
(see commit : 
[5cca629ea186ff3c7711fbdbd8219841caf4d6b](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/commit/5cca629ea186ff3c7711fbdbd8219841caf4d6b)
)
==includes== amomng other elements :

- print statements
- debugging calls, specifically `debug(locals())` from `devtools`
- input data validation using Pydantic
- in-function manual output data validation
- custom data classes
- frequently requested/repeated calculations
- complete lack of caching/memoization
- if and wherever possible, complete lack of :
  - asynchronous executions,
  - concurrent executions,
  - parallel executions
- no parallel processing beyond NumPy's own internals (?)
- using Pandas' DateTimeIndex which is _not hashable_

Hence,
the margin for optimisation is large.

## Caching Strategies

Caching the output of frequently requested functions
can significantly reduce response times and server load.

### Caching intermediate outputs

Some core API functions,
though the mean to output different calculated quantities,
may depend on the same intermediate algorithmic components.

Caching the output of such frequently requested intermediate functions
at the core API level, will speed up the tha overall calculations.

### Caching final output

Caching repeatedly requested final output calls at the Web API lebel

- **Local Caching**: Implement local caching mechanisms to store frequently accessed data.
- **Distributed Caching**: For distributed systems, consider using a distributed cache like Redis or Memcached.

## Data structure Optimization

- Massive time series
    - Contiguous in time
    - Small chunks of data in space

## Algorithmic Efficiency

- Review and optimize algorithms for key calculations to reduce complexity.

## Parallel Processing

- Utilize parallel processing techniques to handle intensive computational tasks.

## Load Balancing

!!! note

    A task mainly for and to work collaboratively with the IT support team

- Implement load balancing
- Distribute API requests evenly across multiple servers
- Enhance scalability and reliability
