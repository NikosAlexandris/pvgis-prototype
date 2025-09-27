---
icon: material/qrcode-scan
description: Quick Response Code
title: QR Code
subtitle: Share PVGIS results via QR Codes
tags:
  - How-To
  - CLI
  - QR-Code
---

You can share PVGIS results easily using your portable device's camera and a
QR-Code enabled scanner application!

``` bash exec="true" result="ansi" source="material-block" hl_lines="5"
pvgis-prototype power broadband \
    8 45 214 167 \
    --start-time '2000-01-01' \
    --end-time '2020-12-31' \
    --qr Image
```
