def generate_citation_text():
    citation = {
        "title": "PVGIS",
        "subtitle": "Photovoltaic Geographic Information System",
        "tags": ["PVGIS", "Overview"],
        "contact": {
            "name": "European Commission, Joint Research Centre",
            "email": "JRC-PVGIS@ec.europa.eu",
            "address": {
                "line1": "via E. Fermi 2749, TP 450",
                "line2": "I-21027 Ispra (VA)",
                "country": "Italy",
            },
        },
        "description": "PVGIS is an open web application of the European Commission, developed and maintained by the Joint Research Centre (JRC) for over two decades by the Energy Efficiency and Renewables Unit (Ispra) of the Energy, Transport and Climate directorate.",
        "features": [
            "Various technologies: Grid-connected, Stand-alone",
            "Reproducible calculations",
            "Shareable results via QR-Code",
            "Time Series: PV Performance, Solar Radiation, Temperature, Wind Speed, Meteorological data",
            "Coverage: Europe, Africa, Asia, America, Regional maps",
            "Supported by the European Commission, cost-free and open access",
            "Languages: English, French, German, Spanish, Italian",
        ],
        "components": [
            {
                "name": "Web API",
                "description": "Entry level guide to get up and running quickly.",
            },
            {
                "name": "CLI",
                "description": "Collection of command line tools for interactive use.",
            },
            {
                "name": "Python API",
                "description": "For advanced users and programmers with examples and source code documentation.",
            },
            {
                "name": "Development",
                "description": "Contribution guidelines, adding new features, and testing.",
            },
        ],
        "support": {
            "community_forum": "https://example.com/support/forum",
            "faq": "https://example.com/support/faq",
        },
        "links": {
            "PVGIS": "https://joint-research-centre.ec.europa.eu/photovoltaic-geographical-information-system-pvgis_en",
            "PVGIS Web Application": "https://re.jrc.ec.europa.eu/pvg_tools/en/",
        },
        "badges": [
            {
                "name": "pipeline status",
                "url": "https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/badges/mkdocs/pipeline.svg",
            },
            {
                "name": "coverage report",
                "url": "https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/badges/mkdocs/coverage.svg",
            },
            {
                "name": "latest release",
                "url": "https://gitlab.jrc.ec.europa.eu/jrc-projects/pvgis/pvis-be-prototype/-/badges/release.svg",
            },
        ],
    }
    return citation
