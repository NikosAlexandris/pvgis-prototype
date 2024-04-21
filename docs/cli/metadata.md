---
icon: material/identifier
title: Metadata
description: Command metadata
tags:
  - How-To
  - CLI
  - Metadata
---

Each and every command
produces a unique [_fingerprinted_-output](fingerprint.md).
What about the inputs
and the state of the software that generated this unique output ?
PVGIS can return the **metadata of the executed command**
which serves to verify where, when and how the output has been produced.
Something like a detailed purchase receipt. And it's all one option away.

``` bash exec="true" result="ansi" source="material-block"
pvgis-prototype power broadband 8 45 214 -v --metadata
```
