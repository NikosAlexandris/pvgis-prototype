---
icon: material/unicorn-variant
title: Run
tags:
  - How-To
  - Web API
  - Run
  - uvicorn
---

## Run the server

<div class="termy">

```console
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

By default, the server will run on [http://127.0.0.1:8000](http://127.0.0.1:8000).  
You can run it on a different address, like so:

<div class="termy">

```console
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

Click on the URL, and you should see a page like:

![PVGIS Web API](../images/pvgis-prototype_web_api_uvicorn_2025-03-18.png)

---

## PVGIS Web API Environments

PVGIS' Web API supports different environments, including **Production** and **Development** modes.

- **Production Mode** runs with minimal overhead, without logging or debugging tools. This is **intended** for deployment.
- **Development Mode** automatically enables logging, profiling, and request time measurement.

The default settings are found in:

- `pvgisprototype/web_api/config/production.py`
- `pvgisprototype/web_api/config/development.py`

---

## Environment Variables (`.env` file)

!!! tip ".env file"

    The `.env` file allows you to configure environment variables for your working setup.  
    Since `.env` files are hidden by default, you can use the `ls -a` command to display them.

    To set an environment variable, add this line to `.env`:

    ```ini
    PVGISPROTOTYPE_WEB_API_ENVIRONMENT=Development
    ```

---

## Production Settings
```python
--8<-- "pvgisprototype/web_api/config/production.py"
```

## Development Settings
```python
--8<-- "pvgisprototype/web_api/config/development.py"
```

## Configuration Options
```python
--8<-- "pvgisprototype/web_api/config/options.py"
```