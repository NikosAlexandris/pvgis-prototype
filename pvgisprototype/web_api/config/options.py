from enum import StrEnum

class LogLevel(StrEnum):
    debug = "DEBUG"
    info = "INFO"
    warning = "WARNING"
    error = "ERROR"
    critical = "CRITICAL"

class LogFormat(StrEnum):
    plain = "plain"
    json = "json"
    uvicorn = "uvicorn"

class Environment(StrEnum):
    production = "PRODUCTION"
    development = "DEVELOPMENT"

class Profiler(StrEnum):
    scalene = "SCALENE"
    pyinstrument = "PYINSTRUMENT"
    yappi = "YAPPI"

class ProfileOutput(StrEnum):
    json = "JSON"
    html = "HTML"
    pstat = "PSTAT"
    callgrind = "CALLGRIND"