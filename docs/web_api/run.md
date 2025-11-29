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
    INFO:     Will watch for changes in these directories: ['/spacetime/pvgis/pvgis-prototype-public']
    INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
    INFO:     Started reloader process [141481] using StatReload
    INFO:     Environment: Production
    INFO:     Started server process [141483]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    ```
  </div>

!!! warning

    The last line stating _Application startup complete_ might not appear !


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

  <figure markdown>
  ![PVGIS Web API](../images/pvgis6_web_api_landing_page.png)
  <figcaption>Web API landing page</figcaption>
  </figure>

## Development mode

Note in the _standard_ launch,
the default mode is set to `Environment: Production`.
When developing or experimenting with the Web API server,
it is very useful to see logging and debugging messages to better understand
errors that might occur. We can use a special environment variable to achieve
higher verbosity :


``` bash
export PVGISPROTOTYPE_WEB_API_ENVIRONMENT='Development'
```

then launch the usual way as in the examples above.


!!! seealso "More environment variables ?"


    Check out [Environment Configuration](/development/profiling/#environment-configuration) for more.
