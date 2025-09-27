---
icon: simple/numpy
title: NumPy
tags:
  - How-To
  - API
  - Core API
  - Python API
  - NumPy
  - Data Type
  - Array Backend
  - Precision
---

!!! danger "Under development"

    The backend-agnostic array system is yet incomplete!

PVGIS implements a backend-agnostic array system.
Essentially,
the algorithimc implementation is independent from the array backend.
This can benefit both end-users and developers
as it makes it easy to
target the GPU,
use sparse arrays
or perform distributed computing.

## For end-users

**Using PVGIS with the default array-backend options,
an end-user does not need to do anything.**
He can, however,
request for another array-backend
for all operations.

## For developers

Developers or scientific programmers
can write programs on top of PVGIS that are independent from the array-backend.
