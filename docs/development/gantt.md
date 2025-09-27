---
icon: material/chart-gantt
hide:
  - navigation
  - toc
tags:
  - pvgisprototype
  - Development
  - Gantt diagram
---

# State & Future of PVGIS


**Chart**

``` mermaid
    gantt
        title Modern PVGIS : Research, Review, Conception
        dateFormat  YYYY-MM-DD
        todayMarker Off
        excludes    weekends

        section Milestones
        Conception : milestone, done, after RR, 2023-05-28,
        Research & Review : done, RR, after Beginning,
        Beginning : milestone, done, crit, Beginning, 2023-05-01,

        section Conception
        Web API: done, 2023-06-05, 2023-06-15
        CLI: crit, done, 2023-06-01, 2023-06-10
        
        section Review
        Web API frameworks: crit, done, 2023-06-01, 2023-06-10
        CLI frameworks: crit, done, 2023-05-01, 2023-05-28
        Software for scientific computation: done, 2023-05-01, 2023-05-31
        Relevant tools : done, active, 2023-05-01

        section Research
        Best programming practices: active, done, 2023-05-01, 2023-05-31
        Understand solar geometry : crit, done, 2023-05-01
```

!!! info "Supporting document"

    [State and Future of PVGIS](state_and_future_of_pvgis.md)

# Research, Review, Conception

``` mermaid
    gantt
        title Modern PVGIS : Research, Review, Conception
        dateFormat  YYYY-MM-DD
        todayMarker Off
        excludes    weekends

        section Milestones
        Conception : milestone, done, after RR, 2023-05-28,
        Research & Review : done, RR, after Beginning,
        Beginning : milestone, done, crit, Beginning, 2023-05-01,

        section Conception
        Web API: done, 2023-06-05, 2023-06-15
        CLI: crit, done, 2023-06-01, 2023-06-10
        
        section Review
        Web API frameworks: crit, done, 2023-06-01, 2023-06-10
        CLI frameworks: crit, done, 2023-05-01, 2023-05-28
        Software for scientific computation: done, 2023-05-01, 2023-05-31
        Relevant tools : done, active, 2023-05-01

        section Research
        Best programming practices: active, done, 2023-05-01, 2023-05-31
        Understand solar geometry : crit, done, 2023-05-01
```

# Prototyping

``` mermaid
gantt
    title Modern PVGIS : Prototyping
    dateFormat  YYYY-MM-DD
    todayMarker Off
    excludes weekends
    tickInterval 1week

    section Milestones
    Developer's Proof-of-Concept : milestone, crit, done, Concept-in-Python, 2023-09-15,
    Short-term progress presentation : milestone, crit, done, 2023-07-15,
    Beginning : milestone, done, crit, Beginning, 2023-05-28,

    section Testing
    NOAA : after Pytests,
    Automated examples using Pytest : crit, Pytests, after NOAA,

    section Documentation
    NumPy-style for Python docstrings (Nik, Ext)  : active,

    section Prototyping
    Simple solar geometry function : done, after WebAPI, 2023-07-15
    Interactive solar declination plot : done, after WebAPI, 2023-07-15
    Web API prototype based on FastAPI: crit, done, WebAPI, after CLI, 2023-07-01
    CLI prototype based on Typer : crit, done, CLI, after Beginning, 2023-06-15
    Effective inclined irradince : crit, done, after Global-Inclined,
    Solar irradiance components for a location & moment : done, after Global-Inclined,
    Global irradiance : crit, done, Global-Inclined, after Reflected-Inclined,
    Reflected irradince : crit, done, Reflected-Inclined, after NOAA,
    Diffuse irradince : crit, done, Diffuse-Inclined, after NOAA,
    Direct irradiance for a location & moment : crit, done, Direct-Inclined, 2023-06-10, 2023-07-15
    Solar geometry (Skyfield, pvlib, pysolar): crit, done, after NOAA, 2023-07-15
    Solar geometry (NOAA): crit, done, NOAA, 2023-06-15,
```

# Packaging & Documentation

# Optimisation

!!! info "On-line Pan-&-Zoom version"

    [:octicons-arrow-right-24: On-line editable version of the Gantt diagram](https://mermaid.live/edit#pako:eNqNVttu4zYQ_RVCBRYNVkok2fJFL0USt7sG4sZojCxaGOgyEm2zlkiBopK4Qf69Q1LUJY6zFfLgDGfODOdyOC9OwlPixM4WMynXDMEnqcwIWoBcMLS8_zK_M_IUS_IbFzmWCP0Jn7dYeLNZbcNTfFhgsScClVLwPfGeaCp3cVQ8u0YQ_-RvfJcXOKHyEPvn0ZoZ25IkknKGFjQjpeSMlEpqzhoZ-vwZxQiD5iNxUW7Fbqvxd-Si0A-Hnj_1_MBFAz89wkA_whhajFEfY84kZANn6Bt5QJfLOfp5ueOSP_JMYpqggoiNygxLyNmPXAysi8gLoo6LpeB848HfNQeYQjauYpRqiERQeQIzdBHeQIQdUaDdDLwg8IKR8WCBKZT1IHdcC9X3PzxYOIg6nNjfU7iBgb4iW8oYZds3WK3N22rfFpLmtMTqnyYBG5opDEjv7xxBr6EbzotSpbSBG3pBqGsT7o7M5i6ap4RJujmgBy6hjRlJ9mVj3qiqhJkiBF4IvwNbhBmWWDVwlchKEAiD7s-aJNmyGjClemc122Sr0EYW7raSRSVRISiTKMFZVmpIF_36LFvcpTp2bTHqwEIvGANqDXTDt1t1xSNrZV8fuu_YD-y9yEN1EsGgNCruSZR7nNEUm_Kxi9vNppcgjdKquC2KSXJUo1zjZGcj6QfRoNQqtqu7oE2pLssDS3aCM16ViMMEaoWyhY17Ku9gtVNRCQFt8y6KDqdROYmyxALKS7ITGLrMtcpJjK90u_OWLZV4q4r1EmX7WCl29Cxg60CTSn_eVjDIAFbfeX5xPeun3FbK71RqnhcZyVVmJFiXb9Ua6up7usy2HMLc5UCM0NhkC_8cjModz7BQT0sFL8yKZhJ9QreCggfTVbxDCnWnrgSmjGhaNb4HesSi3CD-QR4peUK2gkckanLXzu6SX3eIcey-d4EZT6rcxtSQzD9wenFZFBlN6hF4JEI7b9ENsOYn-26UEmpiDHp6OouWPleVhJThrOzo1F1uk1miX9rD-kw_DseYtrFvPjxun5eTKne8EgmB9k8J-p7vU54ANUITld-bvBqyrx-fPWQOBi1IbW02BKqSkPJtGWpS6uYZEQbkA5RbFWrRANLvMFUbY9fTRyglkVVxZkfHxmkjtA0Q-m0o9dUQTBUqzcXVbtQjzM4F-i2zxMkea379hO6JKEHWDhtXY6TVjoYNOjkY1um6qmiWIgytkHcHoE6A5WM_qDujdoMC9A36A2LVXgiMnHpyUvWQATvgrRlgRc3GoLsZ9HYcCxiiJwWI05SqMGDpkSTZMZ7xLTW7meX6GrB5TId9wA5FIUEKLiT66ItRj9Pe7GGO6-QEzmgK2-qLcrB25A4ut3Zi-JmSDa4yuXbc-kgtsStewE4KZVE6YdQ9uoL1gOftaeTXpw9YfCXAr1LbdKRfcKFEQ4vCi6VKEVQZpGMLXtKU9ORr9gqhq6rewWPkxLAxENcxTT6jeCtwboUFZk784jw7cTg6H4fBNAqmYRgOIn86cJ2DEw8m58EonITjaDwdTMPJ6NV1_uUcAILzIBwPxoNJMIwmoDEcuw6B-nGxMPu9XvO1i7-0gfL4-h-YS5TA)

    [![](https://mermaid.ink/img/pako:eNqNVttu4zYQ_RVCBRYNVkok2fJFL0USt7sG4sZojCxaGOgyEm2zlkiBopK4Qf69Q1LUJY6zFfLgDGfODOdyOC9OwlPixM4WMynXDMEnqcwIWoBcMLS8_zK_M_IUS_IbFzmWCP0Jn7dYeLNZbcNTfFhgsScClVLwPfGeaCp3cVQ8u0YQ_-RvfJcXOKHyEPvn0ZoZ25IkknKGFjQjpeSMlEpqzhoZ-vwZxQiD5iNxUW7Fbqvxd-Si0A-Hnj_1_MBFAz89wkA_whhajFEfY84kZANn6Bt5QJfLOfp5ueOSP_JMYpqggoiNygxLyNmPXAysi8gLoo6LpeB848HfNQeYQjauYpRqiERQeQIzdBHeQIQdUaDdDLwg8IKR8WCBKZT1IHdcC9X3PzxYOIg6nNjfU7iBgb4iW8oYZds3WK3N22rfFpLmtMTqnyYBG5opDEjv7xxBr6EbzotSpbSBG3pBqGsT7o7M5i6ap4RJujmgBy6hjRlJ9mVj3qiqhJkiBF4IvwNbhBmWWDVwlchKEAiD7s-aJNmyGjClemc122Sr0EYW7raSRSVRISiTKMFZVmpIF_36LFvcpTp2bTHqwEIvGANqDXTDt1t1xSNrZV8fuu_YD-y9yEN1EsGgNCruSZR7nNEUm_Kxi9vNppcgjdKquC2KSXJUo1zjZGcj6QfRoNQqtqu7oE2pLssDS3aCM16ViMMEaoWyhY17Ku9gtVNRCQFt8y6KDqdROYmyxALKS7ITGLrMtcpJjK90u_OWLZV4q4r1EmX7WCl29Cxg60CTSn_eVjDIAFbfeX5xPeun3FbK71RqnhcZyVVmJFiXb9Ua6up7usy2HMLc5UCM0NhkC_8cjModz7BQT0sFL8yKZhJ9QreCggfTVbxDCnWnrgSmjGhaNb4HesSi3CD-QR4peUK2gkckanLXzu6SX3eIcey-d4EZT6rcxtSQzD9wenFZFBlN6hF4JEI7b9ENsOYn-26UEmpiDHp6OouWPleVhJThrOzo1F1uk1miX9rD-kw_DseYtrFvPjxun5eTKne8EgmB9k8J-p7vU54ANUITld-bvBqyrx-fPWQOBi1IbW02BKqSkPJtGWpS6uYZEQbkA5RbFWrRANLvMFUbY9fTRyglkVVxZkfHxmkjtA0Q-m0o9dUQTBUqzcXVbtQjzM4F-i2zxMkea379hO6JKEHWDhtXY6TVjoYNOjkY1um6qmiWIgytkHcHoE6A5WM_qDujdoMC9A36A2LVXgiMnHpyUvWQATvgrRlgRc3GoLsZ9HYcCxiiJwWI05SqMGDpkSTZMZ7xLTW7meX6GrB5TId9wA5FIUEKLiT66ItRj9Pe7GGO6-QEzmgK2-qLcrB25A4ut3Zi-JmSDa4yuXbc-kgtsStewE4KZVE6YdQ9uoL1gOftaeTXpw9YfCXAr1LbdKRfcKFEQ4vCi6VKEVQZpGMLXtKU9ORr9gqhq6rewWPkxLAxENcxTT6jeCtwboUFZk784jw7cTg6H4fBNAqmYRgOIn86cJ2DEw8m58EonITjaDwdTMPJ6NV1_uUcAILzIBwPxoNJMIwmoDEcuw6B-nGxMPu9XvO1i7-0gfL4-h-YS5TA?type=png)](https://mermaid.live/view#pako:eNqNVttu4zYQ_RVCBRYNVkok2fJFL0USt7sG4sZojCxaGOgyEm2zlkiBopK4Qf69Q1LUJY6zFfLgDGfODOdyOC9OwlPixM4WMynXDMEnqcwIWoBcMLS8_zK_M_IUS_IbFzmWCP0Jn7dYeLNZbcNTfFhgsScClVLwPfGeaCp3cVQ8u0YQ_-RvfJcXOKHyEPvn0ZoZ25IkknKGFjQjpeSMlEpqzhoZ-vwZxQiD5iNxUW7Fbqvxd-Si0A-Hnj_1_MBFAz89wkA_whhajFEfY84kZANn6Bt5QJfLOfp5ueOSP_JMYpqggoiNygxLyNmPXAysi8gLoo6LpeB848HfNQeYQjauYpRqiERQeQIzdBHeQIQdUaDdDLwg8IKR8WCBKZT1IHdcC9X3PzxYOIg6nNjfU7iBgb4iW8oYZds3WK3N22rfFpLmtMTqnyYBG5opDEjv7xxBr6EbzotSpbSBG3pBqGsT7o7M5i6ap4RJujmgBy6hjRlJ9mVj3qiqhJkiBF4IvwNbhBmWWDVwlchKEAiD7s-aJNmyGjClemc122Sr0EYW7raSRSVRISiTKMFZVmpIF_36LFvcpTp2bTHqwEIvGANqDXTDt1t1xSNrZV8fuu_YD-y9yEN1EsGgNCruSZR7nNEUm_Kxi9vNppcgjdKquC2KSXJUo1zjZGcj6QfRoNQqtqu7oE2pLssDS3aCM16ViMMEaoWyhY17Ku9gtVNRCQFt8y6KDqdROYmyxALKS7ITGLrMtcpJjK90u_OWLZV4q4r1EmX7WCl29Cxg60CTSn_eVjDIAFbfeX5xPeun3FbK71RqnhcZyVVmJFiXb9Ua6up7usy2HMLc5UCM0NhkC_8cjModz7BQT0sFL8yKZhJ9QreCggfTVbxDCnWnrgSmjGhaNb4HesSi3CD-QR4peUK2gkckanLXzu6SX3eIcey-d4EZT6rcxtSQzD9wenFZFBlN6hF4JEI7b9ENsOYn-26UEmpiDHp6OouWPleVhJThrOzo1F1uk1miX9rD-kw_DseYtrFvPjxun5eTKne8EgmB9k8J-p7vU54ANUITld-bvBqyrx-fPWQOBi1IbW02BKqSkPJtGWpS6uYZEQbkA5RbFWrRANLvMFUbY9fTRyglkVVxZkfHxmkjtA0Q-m0o9dUQTBUqzcXVbtQjzM4F-i2zxMkea379hO6JKEHWDhtXY6TVjoYNOjkY1um6qmiWIgytkHcHoE6A5WM_qDujdoMC9A36A2LVXgiMnHpyUvWQATvgrRlgRc3GoLsZ9HYcCxiiJwWI05SqMGDpkSTZMZ7xLTW7meX6GrB5TId9wA5FIUEKLiT66ItRj9Pe7GGO6-QEzmgK2-qLcrB25A4ut3Zi-JmSDa4yuXbc-kgtsStewE4KZVE6YdQ9uoL1gOftaeTXpw9YfCXAr1LbdKRfcKFEQ4vCi6VKEVQZpGMLXtKU9ORr9gqhq6rewWPkxLAxENcxTT6jeCtwboUFZk784jw7cTg6H4fBNAqmYRgOIn86cJ2DEw8m58EonITjaDwdTMPJ6NV1_uUcAILzIBwPxoNJMIwmoDEcuw6B-nGxMPu9XvO1i7-0gfL4-h-YS5TA)

    ??? seealso "Source code for the Gantt Diagram"

        ```` markdown
        ``` mermaid
        gantt
            title Modern PVGIS
            dateFormat  YYYY-MM-DD
            todayMarker stroke-width:5px,stroke:#0f0,opacity:0.5

            section Milestones    
            Milestone ++ : active, milestone, Milestone_5, 2024-09-01, 30d
            Milestone +  : active, milestone, Milestone_4, 2024-06-01, 30d
            Internal Web API (Photovoltaic performance) : active, milestone, Milestone_3, 2024-05-15, 30d
            Proof-of-Concept Web API : done, crit, milestone, Milestone_2, after Milestone_1, 2023-11-16
            Concept in Python        : done, crit, milestone, Milestone_1, 2023-05-28, 2023-09-15
            Beginning : done, crit, 2023-05-28

            section Optimisation
            Profiling I (No For Loops) : crit, 2024-12-01, 2h
            Profiling II, Identify bottlenecks : crit, Profiling_2, 2024-01-22, 10d
            Data structure (Nik)       : active, crit, DataStructure, 2023-11-01, 60d
            Output print calls (Nik, Ext)       : Print,         2024-02-17, 2d
            Logging (Nik, Ext)         : Logging,       2024-02-17, 3d
            Debugging (Nik, Ext)             : Debugging,     2024-02-17, 3d
            Validation On/Off (Nik)          : Validation,    2024-01-22, 5d
            Caching (Nik)                    : Caching, after Validation, 10d
            Asynchronous operations (Nik)    : Asynchronous, after Validation,
            Concurrent operations (Nik)      : Concurrent, after Validation,
            Parallel operations (Nik)        : Parallel, after Validation,
            High-Performance-Tuning (Nik)    : crit, HighPerformance, after Parallel, 30d

            section Testing
            CI/CD            : 2024-01-02, 5d
            Implement tests  : 2024-01-02, 30d
            
            section Algorithmic integrity
            Solar Module Tilt & Orientation optimisation (Nik, Trainee) : 2024-03-01, 5m
            Review current Proof-of-Concept (Nik) : active, PoC, 2023-11-17,
            
            section Documentation
            Project/Application Overview : active, 2023-12-01,
            Installation : active, 2024-01-15
            Tutorials : active, 
            Algorithms ? : active,
            API : active, 2024-01-15,
            CLI : active, 2024-01-15,
            Web API : active, 2024-01-15,
            Source Code `mkdocstrings` (Nik) : done, after MkDocs, 1d
            References (Nik) : active,
            Documentation engine (updates) (Nik, Ext) : active, after MkDocs
            Documentation engine (setup) (Nik)  : done, MkDocs, 2023-11-20,
            Docstrings for source code (Nik, Ext)  : active,

            section Packaging & Versioning
            Completion       : 2024-01-01, 14d
            Build automation (Nik, Ext) : 2024-02-01 
            Version 1 With complete input data management  : Version_1, 2023-11-01, 30d
            Version 2 with additional technologies         : Version_2, 2024-04-01, 30d
            Performance report                             : Performance, 2024-06-01, 30d
        ```
        ````

