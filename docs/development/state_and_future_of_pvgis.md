---
author: Nikos Alexandris 
title: State and Future of PVGIS
---

## Summary

After almost 9 months of working in and for the PVGIS team,
on programmatic issues and matters of data processing,
I gained an appreciation
for the amount of good work put into PVGIS by several people.
Notably,
high quality work has been delivered by external contributors
on the software side of PVGIS.
Notwithstanding,
from a modern world's software and user experience perspective,
and after a holistic assessment,
my recommendation is that PVGIS deserves an overhaul. 

I presented my findings and recommendations on September 2022
in the members of the PVGIS team.

!!! info "Presentation of findings and recommendations"

    [State & Future of PVGIS](https://eceuropaeu.sharepoint.com/:p:/r/teams/GRP-PVGIS/Shared%20Documents/General/Presentations/State%20and%20future%20of%20PVGIS.pptx?d=w2c9d36bb03fb4fe091f4c02cf4d058fa&csf=1&web=1&e=kar8Dh)

On April 2023,
the recommendations were re-assessed and it was decided to launch a research &
conception effort in order to showcase the potential for a modern version of
PVGIS based on Python and modern technologies for scientific and high
performance computations.


## State 

At the moment, 

- The software, written in C/C++, is practically opaque because it 

    - does not adhere to coding standards 
    - contains repetitive duplication of code snippets 
    - lacks automated tests 

- The custom and proprietary PVGIS data format 

    - is not readable by modern and well known software 
    - is difficult to work with from a modern perspective 
    - forcedly adds extra processing steps, at times of re-processing or
      updating the raw data, which increases the possibilities of computing
      errors 

- The manual for PVGIS software and data written previously
has been converted in a modern website based on Jupyter Book.
But there is still no answer after 2 requests
(one in the JEODPP/BDAP team, one in the HelpDesk)
for a space to host it. UPDATE-ME 

- The user experience is not in par with today's web mapping standards
(for example no full screen maps) 

- The functional mailbox serves users to get in contact with the PVGIS team
and ask questions or communicate feature requests.
Naturally, there is repetition of questions.
The lack of a proper Question & Answer system
requires valuable time to be put into responding to users. 


## Future 

Given the JRC wants to
continue providing PVGIS as a cost-free and publicly accessible service
for the years to come,
a complete re-design of the software is necessary. 


## What to do? 
 
-   Re-design PVGIS by following good practices recommended by open scientific and programming communities (e.g. the pangeo community) 
-   Rewrite the core of the code in a modern high level language like Python. 
    - Most of the code deals with reading time series over a specific location. The amount of code can be reduced substantially. Using Numba, for example, would also make up for speed in retrieving time series. 
-   Write automated tests to help eliminating bugs, ease off maintenance, etc. 
-   Use directly the NetCDF files or Zarr stores or even adopt a spatial database. 
-   Serve the manual accessible internally for the JRC community 
-   Set up a modern Question & Answer platform 

### Good practices to learn from 

For example,
https://pangeo.io/# is such a project.
Pangeo is a community of people working collaboratively
to develop software and infrastructure to enable Big Data geoscience research. 


## Software 

We distinguish between the front-end and the back-end 

### The front-end 

The front-end is all what users see and interact with via a web browser.
Though there are many good elements currently in-place,
the user experience can be improved significantly.
For example, modern web-mapping applications enjoy full screen display of maps.
Another example is the format of the output data a user can acquire through PVGIS.
The CSV files, for example,
are inconsistent with the very definition of what makes a CSV file.
One more problem is the generation of PDF reports
– it depends on the user's browser and often, such reports,
contain overlapping text which makes the report partly unreadable.
Yet another problem,
in the programmatic part of the front-end is the need to repeat a set of files
for each and every language version of the PVGIS tools.
All these are obstacles in maintaining a software. 

### The back-end 

The back-end includes 

-   the core C/C++ programs 
-   the web server back-end software that links the front-end with the core PVGIS programs 

The core of PVGIS is a collection of programs written in C/C++.
They are not easy to read and understand.
Hence, it is difficult to identify errors and make modifications.
It takes substantial effort to perform any or some or all of the aforementioned actions
(see some issues tagged with the BUG label in our internal gitlab repository:
https://jeodpp.jrc.ec.europa.eu/apps/gitlab/use_cases/pvgis/rsun3/-/issues?sort=updated_desc&state=opened&label_name[]=BUG).

For example,
there is an important bug in how a pixel is selected based
on a pair of coordinates defined by the user
(see https://jeodpp.jrc.ec.europa.eu/apps/gitlab/use_cases/pvgis/rsun3/-/issues/57).
There is a workaround to make up for the buggy pixel retrieval algorithm
that increases the spatial resolution of the data,
which in turn require more disk storage space.
Note,
a correct implementation of this very pixel selection algorithm
is implemented in Python in the PVGIS Python tools
(developed by an external contractor)
which are used to generate PVGIS time series in the desired custom data format. 

The web server back-end software is of high quality,
written in Python based on the Flask web framework.  


## What to do? 

The core of PVGIS software needs to be rewritten and accompanied with unit tests,
coverage tests and more.
Re-designing the core of PVGIS,
however, will require to redesign the web server back-end too. 

### Why? 

- To ease off technical works and focus on science. 
- To enable the software to be open-sourced 


## Good practice examples 

- In this notebook
https://colab.research.google.com/drive/1ba_guD2cDFlT0kppXz_CkoXPGeNwzzjk?pli=1#scrollTo=EuoUzhJocwj_
the pvlib people show how with a few lines of code they query PVGIS' API.
PVGIS should provide itself a library with a simple interface and examples,
tutorials, etc. 

- The GUI should support deep-linking,
in example links directly to content instead of only a tool.
For example,
someone can set the location and all required parameters for a PV-related calculation
and share this link to the result.
This would save the time from re-fillling the parameters for the same query.
At the moment, PVGIS supports for pre-setting the location. 


## How long will it take? 

An rough estimation for producing a modern Proof-of-Concept version (excluding
work on the Front-end),
would be one skillful person with some additional help,
working over a 1-year period.
This would be more or less
the amount of time put by the previous two external consultants,
plus some extra time.

## Data format 

### Status 

- PVGIS splits the world map in 7774 tiles (54 rows x 144 columns) out of which 3452 tiles cover land. For each variable and every one of the 3452 tiles, time series data are stored in a single files. Thus, we have as many "sets of tiles" as the number of variables we require to run PVGIS. For example, we have 3452 single files for temperature, 3452 single files for wind speed and so on. 

- Essentially, a "PVGIS tile" contains a time series for a specific variable. The "traditional" data format for a PVGIS tile is a custom one designed years ago by Thomas Huld. At the time it served fast and "on-the-fly" the calculations needed for the PVGIS queries. This format, however, is not compatible with modern data structures and software. Work has been done by previous developers to ensure reading and writing data from and to this format. The conversion, however, is not straightforward as it includes more than 1 step. 

### Spatial resolution? 

- A PVGIS tile covers an area of 2.5 degrees.
Therefore, the number of pixels in a PVGIS tile
depend on the spatial resolution of the input data.
For example CMSAF data features pixels of 0.05 degrees
in which case a PVGIS tile will feature 50 pixels.
For ERA5-Land and ERA5 the number of pixels are respectively 25 and 10. 

### Drawbacks 

Example, to get data in to the PVGIS format, we need to: 

1. get ERA5 temperature data as yearly NetCDF files (each year is a multi-GB file) 
2. convert them in a Zarr store that packs all "years" together 
3. create PVGIS tiles from the Zarr store 

Thinking of the multiple variables we deal with in PVGIS,
this processing chain involves a lot of TBs (size of files),
3 different data file formats and requires substantial time.
Noteworthy is that in the case of an error identified in a PVGIS tile,
for example extreme outliers or data corruption,
the whole processing chain has to run again! 

### What to do? 

Deprecate the custom proprietary format
and use either the raw NetCDF files directly
or the Zarr storage data format.
Alternatively, adopt a modern spatial database.
Current data and software technologies
can provide the same or even better calculation speeds
– this is of course a subject to test and verify. 

### Why? 

- For... 
    - modern, fast and interoperable data format 
    - simpler to query and check 
    - easier to share with the outer world 

- To support and supported by the Commission's Open source software strategy 2020-2023 
- more... 

## Hardware 

We currently have access to virtual desktops
provided by the JEODPP/BDAP supercomputing cluster in the JRC.
These virtual containers are convenient in many ways.
However,
the High-Throughput-Cluster is primarily designed
to do parallel processing of large, massive and big datasets.
Therefore, it uses a clustered file-system name EOS.
EOS is not fit for purpose when working with many small files,
as we are used to work in our personal desktops, laptops or workstations.
The task to read and write files quickly, is not one of its strengths. 

There are several open/closed issues reported in the internal gitlab instance,
in the JEODPP/BDAP which clearly show the difficulties we have to deal with
in day-to-day work. Example: 

- https://jeodpp.jrc.ec.europa.eu/apps/gitlab/jeodpp-services/data-access/-/issues/48 
- https://jeodpp.jrc.ec.europa.eu/apps/gitlab/for-everyone/support/-/issues/367 
- https://jeodpp.jrc.ec.europa.eu/apps/gitlab/for-everyone/support/-/issues/906 

## Outer world 

PVGIS is known to be used widely out there,
by private individuals as well as professionals.
PVGIS has been advertised recently through various internet media
(like LinkedIn and Twitter).
And all this is great.
However,
I would like to express my concern that it is important to modernise PVGIS.
If PVGIS is to remain in its current state,
the increasing workload will not help us focus on the science of it. 

## Open Source 

### What is it? 

To start with,
open source is a software and a business development model.
Open source isn't just opening the source code of a software to the world.
The central idea is to encourage collaboration through peer production.
And this without excluding nor discouraging
commercialisation of services, training, support and consulting. 

!!! info

    What is Open Source? https://commons.wikimedia.org/wiki/File:121212_2_OpenSwissKnife.png#/media/File:121212_2_OpenSwissKnife.png 

### Is PVGIS open source? 

At PVGIS we are offering cost-free and publicly accessible a service,
that is developed and maintained by the European Commission.
It is essentially public money that fund this service.
_The software that powers this service is not open-source_.

However,
the core PVGIS has been actually open-sourced, years ago,
in the form of GRASS GIS modules
-- see https://publications.jrc.ec.europa.eu/repository/handle/JRC43644.
Since no-one is working on updating this set of modules
(I am an active member of the GRASS GIS community),
there is the additional "task" to sync our internal PVGIS version with the GRASS GIS modules.
This will be easier if PVGIS will be open-sourced.
GRASS GIS and any other software project,
will greatly benefit from a PVGIS library.
In turn,
such projects, will bring in more exposure of the Commission's work
coupling research in photovoltaics and open-sourcing its software. 

### Does open-source mean automatically success? 

No!
There is a lot of work to do for an an open-source project to become successful.
What is important in the case of PVGIS, is its very wide user-base. 

### In the Commission 

+ Example of proprietary software migration to Open Source 

During 2007-2010,
the European Commission's activities have lead to the delivery of OSS tools
in support of e-Government processes, such as e-Prior,
a procurement tool for the exchange of standardised electronic documents
that supports purchase orders and service catalogues,
developed by the European Commission's DG Informatics
and shared under EUPL on OSOR.eu. 

In addition,
a study on the impact of Open Source on the European economy
published by the Commission,
predicts that an increase of 10% in contributions to Open Source Software code
would annually generate an additional 0.4% to 0.6% GDP,
as well as more than 600 additional ICT start-ups in the EU. 

## To Do 

- Design the architecture 
- Why select one tech over another? Overview –es and +es 
- Clean separation of Core/Back-end and Front-end 
- Work slowly, publish early (alpha, beta, …) 
- ... 
