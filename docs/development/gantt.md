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

!!! info "On-line Pan-&-Zoom version"

    [![](https://mermaid.ink/img/pako:eNqNVttu4zYQ_RVCBRYNVkp0sexYL0Uu7a6BuDEaI4sWBrqMRNusJVKgqCRukH_vkBR1ieNshTw4w5kzw7kczouT8ow4ibPBTMoVQ_BJKnOC5iAXDC3uv8zujDzDkvzGRYElQn_C583n3vV1Y8MzvJ9jsSMCVVLwHfGeaCa3SVw-u0aQ_OSvfZeXOKVyn_in8YoZ24qkknKG5jQnleSMVEpqzloZ-vwZJQiD5iNxUWHFbqfxd-yi0A9Hnj_1_MBFkZ8dYKAfYYwsxniIMWMSsoFz9I08oIvFDP282HLJH3kuMU1RScRaZYal5ORHLiLrIvaCuOdiIThfe_B3xQGmlK2rBGUaIhVUHsEMXYTXEGFPFGg3kRcEXjA2HiwwhbLu5ZZrofr-hwcLB1GH5_b3FG5goC_JhjJG2eYNVmfzttq3paQFrbD6p03AmuYKA9L7O0fQa-iG87JSKW3hRl4Q6tqE2wOzmYtmGWGSrvfogUtoY0bSXdWat6oqYaYIgRfC78AW4RpLrBq4TmUtCIRBdydtkmxZDZhSvbOaXbJVaGMLd1vLspaoFJRJlOI8rzSki359lh3uQh27thhNYKEXTAC1Abrhm4264oG1sm8O3XfsI3sv8lAfRTAorYp7FOUe5zTDpnzs7Ha9HiRIo3Qqbodikhw3KFc43dpIhkG0KI2K7eo-aFuqi2rP0q3gjNcV4jCBWqHqYJOByjtY3VTUQkDbvIuiw2lVjqIssIDykvwIhi5zo3IU4yvdbL1FRyXesmaDRNk-Voo9PQvYOdCkMpy3JQwygDV3np1dXQ9Tbivl9yo1K8qcFCozEqyrt2otdQ09XeQbDmFuCyBGaGyygX_2RuWO51iop6WGF2ZJc4k-oVtBwYPpKt4jhaZTlwJTRjStGt-RHrG4MIh_kEdKnpCt4AGJmtx1s7vgVz1inLjvXeCap3VhY2pJ5h84Pbsoy5ymzQg8EqGdd-gGWPOTfTcqCTUxBgM9nUVLn8taQspwXvV0mi63yazQL91hc6Yfh0NM29g3Hx53z8tRlTtei5RA-2cEfS92GU-BGqGJqu9tXg3ZN4_PDjIHgxZktjZrAlVJSfW2DA0p9fOMCAPyAcqtS7VoAOn3mKqLse_pI5SKyLo8saNj47QR2gYI_S6U5moIpgpV5uJqNxoQZu8Cw5ZZ4HSHNb9-QvdEVCDrho2rMdJqB8MGnRyMmnRd1jTPEIZWKPoD0CTA8rEfNJ3RuEEB-gb9AbFqLwRGTj05mXrIgB3wxgywomZj0N8MBjuOBQzRkwLEWUZVGLD0SJJuGc_5hprdzHJ9A9g-pqMhYI-ikCAlFxJ99CVowGlv9jDHdQoCZzSDbfVFOVg5cguXWzkJ_Mxg91w5biNXG-ySl7CQQk2UQhj3jy5hN-BFdxr7zekDFl8JkKvUNj3pF1wq0cii8HKh8gMlBunEglc0IwP5ir2uGESuinoHb5GTwMJAXMf0-DXFG4ELKywxc5IX59lJwvHpJAymcTANwzCK_WnkOnsnic5Pg3F4Hk7iyTSahufjV9f5l3MACE6DcBJNovMoHI9G0_E4dh0C5eNibtZ7veVrF39pA-Xx9T-2fZRL?type=png)](https://mermaid.live/edit#pako:eNqNVttu4zYQ_RVCBRYNVkp0sexYL0Uu7a6BuDEaI4sWBrqMRNusJVKgqCRukH_vkBR1ieNshTw4w5kzw7kczouT8ow4ibPBTMoVQ_BJKnOC5iAXDC3uv8zujDzDkvzGRYElQn_C583n3vV1Y8MzvJ9jsSMCVVLwHfGeaCa3SVw-u0aQ_OSvfZeXOKVyn_in8YoZ24qkknKG5jQnleSMVEpqzloZ-vwZJQiD5iNxUWHFbqfxd-yi0A9Hnj_1_MBFkZ8dYKAfYYwsxniIMWMSsoFz9I08oIvFDP282HLJH3kuMU1RScRaZYal5ORHLiLrIvaCuOdiIThfe_B3xQGmlK2rBGUaIhVUHsEMXYTXEGFPFGg3kRcEXjA2HiwwhbLu5ZZrofr-hwcLB1GH5_b3FG5goC_JhjJG2eYNVmfzttq3paQFrbD6p03AmuYKA9L7O0fQa-iG87JSKW3hRl4Q6tqE2wOzmYtmGWGSrvfogUtoY0bSXdWat6oqYaYIgRfC78AW4RpLrBq4TmUtCIRBdydtkmxZDZhSvbOaXbJVaGMLd1vLspaoFJRJlOI8rzSki359lh3uQh27thhNYKEXTAC1Abrhm4264oG1sm8O3XfsI3sv8lAfRTAorYp7FOUe5zTDpnzs7Ha9HiRIo3Qqbodikhw3KFc43dpIhkG0KI2K7eo-aFuqi2rP0q3gjNcV4jCBWqHqYJOByjtY3VTUQkDbvIuiw2lVjqIssIDykvwIhi5zo3IU4yvdbL1FRyXesmaDRNk-Voo9PQvYOdCkMpy3JQwygDV3np1dXQ9Tbivl9yo1K8qcFCozEqyrt2otdQ09XeQbDmFuCyBGaGyygX_2RuWO51iop6WGF2ZJc4k-oVtBwYPpKt4jhaZTlwJTRjStGt-RHrG4MIh_kEdKnpCt4AGJmtx1s7vgVz1inLjvXeCap3VhY2pJ5h84Pbsoy5ymzQg8EqGdd-gGWPOTfTcqCTUxBgM9nUVLn8taQspwXvV0mi63yazQL91hc6Yfh0NM29g3Hx53z8tRlTtei5RA-2cEfS92GU-BGqGJqu9tXg3ZN4_PDjIHgxZktjZrAlVJSfW2DA0p9fOMCAPyAcqtS7VoAOn3mKqLse_pI5SKyLo8saNj47QR2gYI_S6U5moIpgpV5uJqNxoQZu8Cw5ZZ4HSHNb9-QvdEVCDrho2rMdJqB8MGnRyMmnRd1jTPEIZWKPoD0CTA8rEfNJ3RuEEB-gb9AbFqLwRGTj05mXrIgB3wxgywomZj0N8MBjuOBQzRkwLEWUZVGLD0SJJuGc_5hprdzHJ9A9g-pqMhYI-ikCAlFxJ99CVowGlv9jDHdQoCZzSDbfVFOVg5cguXWzkJ_Mxg91w5biNXG-ySl7CQQk2UQhj3jy5hN-BFdxr7zekDFl8JkKvUNj3pF1wq0cii8HKh8gMlBunEglc0IwP5ir2uGESuinoHb5GTwMJAXMf0-DXFG4ELKywxc5IX59lJwvHpJAymcTANwzCK_WnkOnsnic5Pg3F4Hk7iyTSahufjV9f5l3MACE6DcBJNovMoHI9G0_E4dh0C5eNibtZ7veVrF39pA-Xx9T-2fZRL)

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
