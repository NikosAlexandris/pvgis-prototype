---
icon: simple/conventionalcommits
title: Conventions
tags:
  - Development
  - Convention
  - Git
  - Branch
  - Git Host
  - GitLab
  - GitLab Issues
---

# Docstrings

PVGIS adheres to the [NumPy Style Guide][numpy-style-guide]
for the syntax and best practices for docstrings.
The NumPy Style itself follows the standard Python style conventions[^0][^1].

!!! seealso "Example of best docstrings practices for a Python module"

    See [example.py](https://numpydoc.readthedocs.io/en/latest/example.html#example).

[numpy-style-guide]: https://numpydoc.readthedocs.io/en/latest/format.html#

[^0]: https://peps.python.org/pep-0008/

[^1]: https://peps.python.org/pep-0257/

# Git Commit Message

``` mermaid
    gitGraph
       commit
       commit
```

## Messages

Meaningful git commit messages are _important_!
Please have a read at [cbea.ms/git-commit](https://cbea.ms/git-commit/)

## Convention

Our commit messages should be both human and machine readable.
To this end, we follow the lightweight convention on top of commit messages
specified in [conventionalcommits.org][conventionalcommits].
The convention follows simple rules to create an explicit commit history.

[conventionalcommits]: https://www.conventionalcommits.org/en/v1.0.0/

# Branch Naming

## Overview

Branches are a fundamental component of version control with Git. They allow for development of features, fixes, and experiments in isolated environments. While Git-based services like [GitLab](https://gitlab.com) and [GitHub](https://github.com) are essentially feature-full repository and software project management tool, branches are, nonetheless, a feature of Git itself, not these hosting services. This distinction becomes particularly important when considering repository portability between different Git-based services.

## Convention

To ensure clarity, consistency, and ease of navigation across different platforms, we agreed on a branch naming convention that emphasizes readability, understandability, and practicality. The approach aids in the quick identification of branches, their purposes, and associated issues or features.

### Format

```
<issue number>-gitlab-<describe issue>
```

- **Issue Number**: Prefixing the branch name with the issue number directly links the branch to its corresponding issue. This practice facilitates automatic referencing in GitLab and aids developers in quickly locating and associating branches with their respective issues.

- **Git Host Name**: Including a service-specific name (e.g., `gitlab`) after the issue number, references the Git-based hosting platform of the issue. This is useful in case of migrating repositories between services, such as from GitLab to GitHub.

- **Issue Description**: Following the _issue number_ and _git host name_ with a short keyword-style description of the issue, should give an insight into the purpose of the branch.

### Examples

- [129-add-different-panel-orientation-tilt](https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/compare/main...129-add-different-panel-orientation-tilt)`
- ..

``` mermaid
    gitGraph
       commit
       branch 129-add-different-panel-orientation-tilt
       commit
```

## Rationale

The adopted naming convention offers :

- **Readability and Understandability**: Clear and descriptive branch names improve navigation and comprehension for all team members, regardless of their familiarity with the issue tracker.

- **Efficiency**: Prefixing branches with issue numbers makes use of GitLab's automatic issue referencing, streamlining the development workflow.

- **Portability**: Including a service-specific prefix mitigates confusion when migrating projects between Git-based platforms, preserving the context of issue tracking.

## Discussion

Dialogue on branch naming practices,
as in just about every aspect of our software project, is encouraged.
A flexible yet structured approach to branch naming
will support our collective effort,
even more so ahead of a potential transition to other Git Hosts.
