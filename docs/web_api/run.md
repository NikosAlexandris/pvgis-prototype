---
icon: material/unicorn-variant
title: Run
tags:
  - How-To
  - Web API
  - Run
  - uvicorn
---

Run the server

  <div class="termy">

    ``` console
    $ cd pvgisprototype
    $ uvicorn pvgisprototype.webapi:app --reload
    INFO:     Will watch for changes in these directories: ['pvgis-prototype']
    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [134186] using StatReload
    INFO:     Started server process [134188]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

  </div>

  By default, the server will run on http://127.0.0.1:8000.
  We can run on another address, like so :

  <div class="termy">

    ``` console
    $ cd pvgisprototype
    $ uvicorn pvgisprototype.webapi:app --reload --host 127.0.0.2
    INFO:     Will watch for changes in these directories: ['pvgis-prototype']
    INFO:     Uvicorn running on http://127.0.0.2:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [134186] using StatReload
    INFO:     Started server process [134188]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```

  </div>

  Click on the URL and you should be landing in a page like

  <!-- <figure markdown> -->
  ![PVGIS Web API](../images/pvgis-prototype_web_api_uvicorn_2024-01-26.png)
  <!-- <figcaption>Image caption</figcaption> -->
  <!-- </figure> -->
