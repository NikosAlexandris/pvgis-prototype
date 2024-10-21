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
    Production = "Production"
    Development = "Development"


class Profiler(StrEnum):
    scalene = "Scalene"
    pyinstrument = "Pyinstrument"
    yappi = "Yappi"
    functiontrace = "FunctionTrace"


class ProfileOutput(StrEnum):
    json = "JSON"
    html = "HTML"
    pstat = "PSTAT"
    callgrind = "CALLGRIND"
