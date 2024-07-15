---
icon: material/information-variant
title: Web Traffic
summary: Analysis of PVGIS Web Traffic Logs.
authors:
    - Nikos Alexandris
date: 2023-11
read-time: 10 min read
tags:
  - Context
  - Reference Material
  - Analysis
  - DRAFT
  - Review-Me
---

|Status|DRAFT|

<!-- ```{article-info} -->
<!-- :avatar-outline: muted -->
<!-- :avatar: https://avatars.githubusercontent.com/u/7046639?v=4 -->
<!-- :avatar-link: https://github.com/NikosAlexandris -->
<!-- :author: Nikos Alexandris -->
<!-- :date: 11. 2023 -->
<!-- :read-time: 10 min read -->
<!-- :class-container: sd-p-2 sd-outline-muted sd-rounded-1 -->
<!-- ``` -->

!!! danger

    Update the _Origing of requests table!_

!!! abstract

<div class="grid cards" markdown>

- **Origin of requests between 28 May and 4 June 2023**

    ---

    | Country | Requests |    % |
    |:-------:|---------:|-----:|
    | Ireland |    17916 | 22.3 |
    | Germany |    13244 | 16.5 |
    |  Spain  |     8253 | 10.3 |
    |  France |     7286 |  9.1 |
    |  Italy  |     4853 |  6.0 |

- **Tools popularity**

    ---

    |     Tool     |   Count |
    |:------------:|--------:|
    |    pvcalc    | 5069005 |
    |    drcalc    | 1181591 |
    |  seriescalc  |  694966 |
    | printhorizon |  484195 |
    |    mrcalc    |  267355 |
    |      tmy     |  227129 |
    | getelevation |  188357 |
    |    extent    |  184505 |
    |    shscalc   |   61093 |
    |  degreedays  |     907 |

    !!! note

        IP addresses hereafter are redacted for the obvious privacy reasons!

</div>

# Web Traffic

## Insights from Data

**Decoding PVGIS's Web Traffic Patterns and User Demographics**

PVGIS is labeled as one highest visited web applications in the Joint
Research Centre, European Commission. For a good reason so!
In the week between
**28 May 2023** 04:15:36 +0200
and **04 June 2023** 03:43:49 +0200,
PVGIS got $80445$ unique and successful requests _outside_ the JRC Intranet.
Unique means $80K$ _distinct_ IP addresses
excluding ones from the JRC intranet,
and _succesful_ means requests that were served with the data asked.
The top $5$ countries of origin were
Ireland, Germany, Spain, France and Italy.

Nonetheless,
the above figure might be misleading
as among these we can find duplicate requests or clicks on icons.
In order to gain a pragmatic appreciation of what users really look for,
we need to undergo a careful in-depth analysis of the logs.
For example,
the number of _unique_ _external_ IP addresses
that _succesfully_ requested for an _API tool_,
is $64243$.
Hence,
it is important to come up with a fair set of filtering criteria
and the right questions on the usage.

For example : 

- **Which requests are meaningful and what are they targetting ?**
- **Which tools are mostly _wanted_ and how much data is actually _downloaded_ ?**

| Requests      | Wanted          | Remarks for **exclusion**              |
|---------------|-----------------|----------------------------------------|
| External      | No              | IP addresses from the JRC intranet     |
| Unique        | Yes             | Duplicate IP addresses                 |
| Meaningful    | Yes             | Clicks on icons, buttons, help pages   |
| Duplicates    | No              | Duplicate requests, even if successful |
| Download size | Yes > Threshold | requests sized < ? bytes               |

While duplicate requests are common for a variety of reasons,
they should be excluded as they would add up to misleading figures.
We should also reject requests that aren't meaningful
such as clicking an icon, a help _tooltip_ and similar actions.
Having a clean dataset is important before diagnosing user demographics!
Let's take a detailed look at the web server logs.


!!! warning "To Do"

    This is a on-going work. Some ideas for the next steps :

    - Complete analysis for the past 6 months

      - Which tools are mostly used ?
      - What is the average size of data requested and downloaded ?

    - Set up an automatic routine to analyse logs each month ?

    - Explain technical terms : "IP", "GDPR", or "Miller". 

    - Privacy & Ethics : a note on respecting user privacy mandated by the GDPR

    - Visualization ?

    - Questions... : what does the geographical distribution of the visits imply for PVGIS?

    - Contextualize : why are these findings important ?

### How many visits ?

We all want to understand the significance of a service :
its capabilities, if it is useful and in which ways.
The obvious question is
_how much traffic does our service generate ?_
Let's dive in some log data manipulation to answer some of these questions!

#### The log files

_Weekly_ log files are kept for the past 6 months,
as mandated by the [GDPR](https://gdpr.eu/).
Here a list of log files including the most recent one :

``` bash
316M Jun  4 04:43 access.log-20230604.gz
295M Jun 11 04:09 access.log-20230611.gz
240M Jun 18 04:06 access.log-20230618.gz
228M Jun 25 05:06 access.log-20230625.gz
225M Jul  2 04:21 access.log-20230702.gz
224M Jul  9 04:55 access.log-20230709.gz
196M Jul 16 04:47 access.log-20230716.gz
443M Jul 23 04:57 access.log-20230723.gz
519M Jul 30 05:25 access.log-20230730.gz
518M Aug   6 05:36 access.log-20230806.gz
585M Aug  13 04:15 access.log-20230813.gz
668M Aug  20 04:12 access.log-20230820.gz
203M Aug  27 04:39 access.log-20230827.gz
237M Sep   3 04:48 access.log-20230903.gz
237M Sep  10 04:32 access.log-20230910.gz
257M Sep  17 05:06 access.log-20230917.gz
232M Sep  24 04:40 access.log-20230924.gz
242M Oct   1 04:37 access.log-20231001.gz
577M Oct   8 04:42 access.log-20231008.gz
669M Oct  15 05:22 access.log-20231015.gz
254M Oct  22 04:13 access.log-20231022.gz
305M Oct  29 04:42 access.log-20231029.gz
245M Nov   5 04:41 access.log-20231105.gz
230M Nov  12 04:54 access.log-20231112.gz
255M Nov  19 04:22 access.log-20231119.gz
243M Nov  26 04:22 access.log-20231126.gz
185M Nov  30 12:04 access-today.log
```

??? tip "What is Miller?"

    **What is Miller ?** Head over to [_A Guide To Command-Line Data Manipulation_](https://www.smashingmagazine.com/2022/12/guide-command-line-data-manipulation-cli-miller/)
    or [Miller in 10 minutes](https://miller.readthedocs.io/en/latest/10min/).

#### Working with Miller

##### Log Format

These files are compressed. Let's use the powerfull
[Miller](https://miller.readthedocs.io/en/latest/) to work with these logs
(yes, directly with compressed files!).
For starters, let's count the total number of records in the logs

``` bash
mlr count access.log-2023*.gz
```

> This will take some time to decompress and read the log files which aren't
> that small!

which returns

``` bash
count=406581612
```

Quite a number : $~406 million$ records!

To make sense of the structure of the logs,
let's examine one such record from a log file.
We use Miller's `--nidx --ocsv` options
to split a log record on spaces
and assign integer field names starting with `1`:

``` bash
mlr --nidx --ocsv head -n 1 access.log-20230604.gz
1,2,3,4,5,6,7,8,9,10,11,12
193.189.???.???,-,-,[28/May/2023:04:15:36,+0200],"""GET",/api/pvcalc?lat=52&lon=5.4&peakpower=3.92&loss=14.00&angle=15&aspect=0&outputformat=basic,"HTTP/1.1""",200,410,"""-""","""-"""
```

or let's print it out vertically

``` bash
mlr --nidx --oxtab head -n 1 access.log-20230604.gz
1  193.189.???.???
2  -
3  -
4  [28/May/2023:04:15:36
5  +0200]
6  "GET
7  /api/pvcalc?lat=52&lon=5.4&peakpower=3.92&loss=14.00&angle=15&aspect=0&outputformat=basic
8  HTTP/1.1"
9  200
10 410
11 "-"
12 "-"
```

We can see that the record has `12` fields.
Is this the case for all records?
Querying more records, for example `-n 4`,
shows that _not all records are of equal size_.
For example :

``` bash
mlr --nidx --ocsv head -n 4 access.log-20230604.gz
1,2,3,4,5,6,7,8,9,10,11,12
193.189.???.???,-,-,[28/May/2023:04:15:36,+0200],"""GET",/api/pvcalc?lat=52&lon=5.4&peakpower=3.92&loss=14.00&angle=15&aspect=0&outputformat=basic,"HTTP/1.1""",200,410,"""-""","""-"""
34.244.???.???,-,-,[28/May/2023:04:15:36,+0200],"""GET",/api/DRcalc?lat=52.205&lon=0.143&usehorizon=1&month=0&angle=40.0&aspect=17.0&clearsky=1&outputformat=json,"HTTP/1.1""",200,13560,"""-""","""unirest-java/1.3.11"""
54.247.??.???,-,-,[28/May/2023:04:15:36,+0200],"""GET",/api/DRcalc?lat=51.071&lon=-0.324&usehorizon=1&month=0&angle=60.0&aspect=0.0&clearsky=1&outputformat=json,"HTTP/1.1""",200,13556,"""-""","""unirest-java/1.3.11"""

1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21
3.75.4.186,-,-,[28/May/2023:04:15:36,+0200],"""HEAD",/api/pvcalc?lat=47.4166285&lon=9.3546922&peakpower=0.15901&loss=12.0&angle=30&aspect=0&raddatabase=PVGIS-CMSAF&pvtechchoice=crystSi&mountingplace=free&usehorizon=1&outputformat=json,"HTTP/1.1""",204,0,"""-""","""Mozilla/5.0",(X11;,Linux,x86_64),AppleWebKit/537.36,"(KHTML,",like,Gecko),Chrome/112.0.0.0,"Safari/537.36"""
```

!!! info "Combined Log Format"
    The Combined Log Format is a standardized log format
    used by a number of web servers to keep track of accesses to websites.
    It is one of the formats available in Apache, and is similar to the
    [Common Log Format](https://en.wikipedia.org/wiki/Common_Log_Format)
    except for the addition of two more fields, the _referer_ and _user agent_.

!!! important

    **Breakdown of Log Fields**

    - **IP Address**: `193.189.???.???`, `34.244.???.???`, etc. The IP address of the client (browser or user) making the request to the server.

    - **Remote User**: Represented by a dash `-` in the logs since the requests are anonymised.

    - **User Identifier**: Another dash `-`, indicating that this information is not recorded.

    - **Timestamp**: `[28/May/2023:04:15:36 +0200]`. The date and time when the request was received. +0200 indicates the time zone offset from UTC.

    - **Request Line**: `"GET` [`/api/pvcalc?lat=52&lon=5.4&peakpower=3.92&loss=14.00&angle=15&aspect=0&outputformat=basic`](/api/pvcalc?lat=52&lon=5.4&peakpower=3.92&loss=14.00&angle=15&aspect=0&outputformat=basic)` HTTP/1.1"`. This is the **request** made by the client. It includes the method (GET), the requested resource or URL, and the HTTP protocol version.

    - **Status Code**: `0`, `200`, `204`, `400`, etc. This is the HTTP status code returned by the server. It indicates the outcome of the request.

    - **Size of Response**: `410`, `0`, `160`, etc. The size of the response body in bytes sent to the client.

    - **Referer**: `-` This field shows the page URL that referred the user to the current request. A dash `-` indicates no referer or not provided.

    - **User-Agent**: `"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"`, `"python-requests/2.25.1"`, etc. This is a string identifying the browser or tool used to make the request.

This is useful to know in further shaping the data.
Important, however, is to note the data format : they are shaped after the
[Combined Log Format](https://httpd.apache.org/docs/2.2/logs.html#combined).


##### Reshaping the data

Using Miller after some trial and error,
we can re-shape the data to a _proper_ CSV like so
(example for the first `4` records) :

!!! warning

    Explain the `sed` commands

``` bash
mlr head -n 4 access.log-20230604.gz \
  |sed 's/.*} //' \
  |sed 's/1=//' \
  |mlr --nidx --oxtab \
    then put -f convert_nginx_to_csv.mlr \
    then cut -f ip,status,size
```

which returns

``` bash
ip     193.189.???.???
status 200
size   410

ip     34.244.???.???
status 200
size   13560

ip     54.247.??.???
status 200
size   13556

ip     3.75.?.???
status 204
size   0
```

where the Miller domain specific language set of instructions contained in
`convert_nginx_to_csv.mlr` is :

``` bash
$ip=$1;
$id=$2;
$user=$3;
$timestamp=strftime(strptime($4 . " " . $5, "[%d/%b/%Y:%H:%M:%S %z]"), "%FT%TZ");
$request=$6 . " " . $7 . " " . $8;
$status=$9;
$size=$10;
$referrer=$11;
$agent=$12;
$merged = "";
```

#### Filter the data

At this point, we can filter the records to _exlude_

  1. IP adresses that belong to the JRC intranet `139.191.*`
  2. non-successful requests
  3. non-API requests [^*]

[^*]: We will need to take another detailed look for non-API requests

Let's do 1 :

``` bash
mlr head -n 4 access.log-20230604.gz \
  | sed 's/.*} //' \
  | sed 's/1=//' \
  | mlr --nidx --ocsv \
    then put -f test/convert_nginx_to_csv.mlr \
    then filter '!contains($ip, "139.191.")' \
    then cut -f ip,status,size
```

which returns

``` bash
ip,status,size
193.189.???.???,200,410
34.244.???.???,200,13560
54.247.??.???,200,13556
3.75.4.???,???,0
```

and then add filter # 2 :

``` bash
mlr head -n 4 access.log-20230604.gz \
  |sed 's/.*} //' \
  |sed 's/1=//' \
  |mlr --nidx --ocsv \
    then put -f test/convert_nginx_to_csv.mlr \
    then filter '!contains($ip, "139.191.")' \
    then filter '$status == 200' \
    then cut -f ip,status,size 
```

which returns
``` bash
ip,status,size
193.189.???.???,200,410
34.244.???.???,200,13560
54.247.??.???,200,13556
```

Seems it works!  The 4rth record with status `0` is now gone.

Let's do something more : keep only _unique_ IPs
and calculate the size of downloaded data for each for 10 records from the
input log file :


``` bash
mlr head -n 10 access.log-20230604.gz \
  |sed 's/.*} //' \
  |sed 's/1=//' \
  |mlr --nidx --ocsv \
    then put -f test/convert_nginx_to_csv.mlr \
    then filter '!contains($ip, "139.191.")' \
    then filter '$status == 200' \
    then cut -f ip,status,size \
    then stats1 -a sum -f size -g ip 
```

which returns

``` bash
ip,size_sum
193.189.???.???,410
34.244.???.???,13560
54.247.??.???,13556
139.191.???.??,5211
141.52.???.1,5228
34.244.???.???,13574
3.253.??.???,13546
18.203.??.???,13561
```

<!-- ::::{margin} -->
!!! hint

    For clarity,
    the filter instructions in this example are layed out line-by-line.
    We can, of course, combine them using logical operators,
    in which case we could use the logical `AND` represented by `&&`.
<!-- :::: -->

The following result is $8$ lines. So, it should work, right ?
Finally, we add filter # 3 and massively redact the logs in question
and export the output in to a proper CSV file :

```bash
mlr cat access.log-20230604.gz \
  |sed 's/.*} //' \
  |sed 's/1=//' \
  |mlr --nidx --ocsv \
    then put -f test/convert_nginx_to_csv.mlr \
    then filter '!contains($ip, "139.191.")' \
    then filter '$status == 200' \
    then filter 'contains($request, "/api/")' \
    then cut -f ip,request,size \
    > access.log-20230604_Filter_external_successful_api_Output_ip_request_size
```

From now on, we can manipulate this new _filtered_ set or log records.


**How many log records ?**

The original log file `access.log-20230604.gz`

``` bash
mlr count access.log-20230604.gz
```
contains

``` bash
count=18443910
```

The _filtered_ dataset, however,

``` bash
mlr count access.log-20230604_Filter_external_successful_api_Output_ip_request_size
```
contains

``` bash
count=8359104
```

$8.36$ million records is about $45%$ of original log records
for the week in question.

**How many unique extrnal IP addresses requested API tools ?**

<!-- ::::{margin} -->
!!! danger
    Be careful **not** to do 

    ``` bash
    filter '!contains($ip, "139.191."); $status == 200; contains($request, "/api/")'
    ```

    This would _include all_ requests containing the `/api/` string!
    To combine instructions in one `filter` call,
    we may use the logical AND operator `&&`, i.e.

    ``` bash
    filter '!contains($ip, "139.191.") && $status == 200 && contains($request, "/api/")'
    ```
<!-- :::: -->

We count distinct IP addresses in the filtered dataset :

``` bash
mlr --icsv count-distinct -f ip -n access.log-20230604_Filter_external_successful_api_Output_ip_request_size
```

returns

``` bash
count=64243
```

(pvgis-web-traffic:which-tools-are-mostly-used)=
### Which tools are mostly used ?

!!! danger

    Update Me

To better understand which functions are mostly wanted,
we need to massage our log records to enable easy counting of tools used.

We can split the `path` in
part 1 to state the version of PVGIS
and part 2 to refernce the actual tool.

<!-- ::::{margin} -->
!!! hint

    The same tools are called sometimes as mentioned in the help page,
    i.e. `PVcalc` and sometimes all lower case letter, i.e. `pvcalc`.
    To avoid confusions in counting, we convert all tool names to lower case
    letters by using Miller's built-in
    [`tolower`](https://miller.readthedocs.io/en/6.9.0/reference-dsl-builtin-functions/#tolower)
    function.
<!-- :::: -->

Let's put the instructions straight in an `.mlr` file
named `reshape_to_ip_tool_version_size.mlr` :

``` bash
$path = gsub($request, ".*?/api/([^?]+).*", "\1");
$tools = splita($path, "/");
$Version = $tools[1];
if (is_absent($tools[2])) {
    $Version = "v5_1";
    $Tool = tolower($tools[1]);
} else {
    $Version = $tools[1];
    $Tool = tolower($tools[2]);
};
```

and run our query via

``` bash
mlr --icsv cat access.log-20230604_Filter_external_successful_api_Output_ip_request_size \
|mlr put -f ../scripts/reshape_to_ip_tool_version_size.mlr \
  then count-distinct -f Tool \
  then sort -nr count
```

returns a longer list which needs further clean-up! Here the Top 5 :

``` bash
Tool=pvcalc,count=5069005
Tool=drcalc,count=1181591
Tool=seriescalc,count=694966
Tool=printhorizon,count=484195
Tool=mrcalc,count=267355
Tool=tmy,count=227129
Tool=getelevation,count=188357
Tool=extent,count=184505
Tool=shscalc,count=61093
Tool=degreedays,count=907
```

`PVcalc` is by far the most wanted tool.

(pvgis-web-traffic-part-2)=
## Getting information from IP addresses

<!-- :::{margin} -->
!!! info

    [What information can I get from an IP address ?](https://ipinfo.io/ip-address-information)
<!-- ::: -->

We can easily get an interesting summary for the filtered data
using [`ipinfo`](https://ipinfo.io/) :

``` bash
mlr --csv cut -f ip access.log-20230604_external_successful_unique_ip_and_size \
|ipinfo summarize
```

which returns

```
Summary
- Total   80445
- Unique  80445
- Anycast 1
- Bogon   12
- Mobile  10424
- VPN     4526
- Proxy   131
- Hosting 26576
- Tor     0
- Relay   394

Top ASNs
- AS16509 Amazon.com, Inc.           22108 (27.5%)
- AS3320 Deutsche Telekom AG         4039 (5.0%)
- AS3352 TELEFONICA DE ESPANA S.A.U. 2551 (3.2%)
- AS3215 Orange S.A.                 1972 (2.5%)
- AS3209 Vodafone GmbH               912 (1.1%)

Top Usage Types
- ISP       46859 (58.2%)
- Hosting   26576 (33.0%)
- Business  5571 (6.9%)
- Education 1207 (1.5%)

Top Routes
- 3.248.0.0/13 (AS16509)  4364 (5.4%)
- 34.240.0.0/13 (AS16509) 3689 (4.6%)
- 34.248.0.0/13 (AS16509) 1422 (1.8%)
- 52.208.0.0/13 (AS16509) 762 (0.9%)
- 3.24.0.0/14 (AS16509)   368 (0.5%)

Top Countries
- Ireland 17916 (22.3%)
- Germany 13244 (16.5%)
- Spain   8253 (10.3%)
- France  7286 (9.1%)
- Italy   4853 (6.0%)

Top Cities
- Dublin, Leinster, IE         17673 (22.0%)
- Frankfurt am Main, Hesse, DE 2880 (3.6%)
- Paris, Île-de-France, FR     2617 (3.3%)
- Madrid, Madrid, ES           2601 (3.2%)
- Sydney, New South Wales, AU  1626 (2.0%)

Top Regions
- Leinster, IE               17824 (22.2%)
- Hesse, DE                  3593 (4.5%)
- Île-de-France, FR          3135 (3.9%)
- Madrid, ES                 2767 (3.4%)
- North Rhine-Westphalia, DE 1761 (2.2%)

Top Carriers
- Vodafone 1218 (1.5%)
- Orange   1166 (1.4%)
- Telekom  342 (0.4%)
- O2       316 (0.4%)
- Yoigo    298 (0.4%)

Top Privacy Services
- Apple Private Relay 354 (0.4%)
- ExpressVPN          145 (0.2%)
- NordVPN             69 (0.1%)
- Surfshark           45 (0.1%)
- ProtonVPN           42 (0.1%)

Top Domains
- t-ipconnect.de 3382 (4.2%)
- rima-tde.net   2328 (2.9%)
- wanadoo.fr     1287 (1.6%)
- vodafone-ip.de 884 (1.1%)
```

## Parallel processing of log files

The weekly log file for comprises 
Working out a single log file takes some time,
obviously due to the large number of records.
Modern hardware and software enable us to perform parallel processing.
We can use [GNU Parallel](https://www.gnu.org/software/parallel/)
to run the same analysis for all log files with a single command!
`parallel` will take care to utilise the many processors of a computer
and will even track how much time took each of the processes.

Let's explore if this works with our log files
by _echoing_ (in contrast to really executing!)
the command `mlr head -n 1`
which _would be_ asking for the first line from each log file
whose name starts with `access.log`,
has then any series of characters in its name
and ends with the extentions `.gz` :

``` bash
parallel echo mlr head -n 1 ::: access.log*.gz
```

this command one-liner returns

```
mlr head -n 1 access.log-20230604.gz
mlr head -n 1 access.log-20230611.gz
mlr head -n 1 access.log-20230618.gz
mlr head -n 1 access.log-20230625.gz
mlr head -n 1 access.log-20230702.gz
mlr head -n 1 access.log-20230709.gz
mlr head -n 1 access.log-20230716.gz
mlr head -n 1 access.log-20230723.gz
mlr head -n 1 access.log-20230730.gz
mlr head -n 1 access.log-20230806.gz
mlr head -n 1 access.log-20230813.gz
mlr head -n 1 access.log-20230820.gz
mlr head -n 1 access.log-20230827.gz
mlr head -n 1 access.log-20230903.gz
mlr head -n 1 access.log-20230910.gz
mlr head -n 1 access.log-20230917.gz
mlr head -n 1 access.log-20230924.gz
mlr head -n 1 access.log-20231001.gz
mlr head -n 1 access.log-20231008.gz
mlr head -n 1 access.log-20231015.gz
mlr head -n 1 access.log-20231022.gz
mlr head -n 1 access.log-20231029.gz
mlr head -n 1 access.log-20231105.gz
mlr head -n 1 access.log-20231112.gz
mlr head -n 1 access.log-20231119.gz
mlr head -n 1 access.log-20231126.gz
```

Great!  If we remove the `echo` command, `Parallel` will indeed execute the
`mlr head` command along with the option `-n 1` for each filename that matches
the desired filename pattern :

``` bash
❯ parallel mlr head -n 1 ::: access.log*.gz
3.249.???.??? - - [04/Jun/2023:03:43:49 +0200] "GET /api/DRcalc?lat=50.854&lon=-0.986&usehorizon=1&month=0&angle=40.0&aspect=2.0&clearsky=1&outputformat=json HTTP/1.1" 200 13561 "-" "unirest-java/1.3.11"
189.6.???.??? - - [11/Jun/2023:03:09:37 +0200] "GET /api/v5_2/MRcalc?lat=-22.178&lon=-56.193&startyear=2017&endyear=2020&raddatabase=PVGIS-SARAH2&angle=&browser=1&outputformat=csv&userhorizon=&usehorizon=1&js=1&select_database_month=PVGIS-SARAH2&mstartyear=2017&mendyear=2020&horirrad=1&mr_dni=1&optrad=1&avtemp=1 HTTP/1.1" 200 2439 "-" "python-requests/2.31.0"
193.189.???.??? - - [28/May/2023:04:15:36 +0200] "GET /api/pvcalc?lat=52&lon=5.4&peakpower=3.92&loss=14.00&angle=15&aspect=0&outputformat=basic HTTP/1.1" 200 410 "-" "-"
185.250.???.??? - - [18/Jun/2023:03:06:25 +0200] "GET /api/v5_2/MRcalc?lat=28.20252&lon=-16.83029&startyear=2020&endyear=2020&mr_dni=1&outputformat=json&horirrad=1 HTTP/1.1" 200 2325 "-" "python-requests/2.28.1"
34.254.??.??? - - [25/Jun/2023:04:07:01 +0200] "GET /api/DRcalc?lat=53.789&lon=-1.751&usehorizon=1&month=0&angle=40.0&aspect=92.0&clearsky=1&outputformat=json HTTP/1.1" 200 13546 "-" "unirest-java/1.3.11"
52.31.??.??? - - [02/Jul/2023:03:21:40 +0200] "GET /api/DRcalc?lat=51.467&lon=-0.353&usehorizon=1&month=0&angle=40.0&aspect=-17.0&clearsky=1&outputformat=json HTTP/1.1" 200 13571 "-" "unirest-java/1.3.11"
54.216.???.??? - - [09/Jul/2023:03:55:36 +0200] "GET /api/DRcalc?lat=51.486&lon=-2.498&usehorizon=1&month=0&angle=40.0&aspect=1.0&clearsky=1&outputformat=json HTTP/1.1" 200 13569 "-" "unirest-java/1.3.11"
3.249.??.??? - - [16/Jul/2023:03:47:44 +0200] "GET /api/DRcalc?lat=51.54&lon=0.14&usehorizon=1&month=0&angle=40.0&aspect=90.0&clearsky=1&outputformat=json HTTP/1.1" 200 13542 "-" "unirest-java/1.3.11"
82.144.???.? - - [23/Jul/2023:03:57:58 +0200] "GET /pvgis5/PVcalc.php?raddatabase=PVGIS-CMSAF&pvtechchoice=crystSi&peakpower=2.84375&mountingplace=building&angle=35&aspect=-60&outputformat=csv&lat=47.60681&lon=18.50642&loss=11 HTTP/1.1" 301 5 "-" "Apache-HttpClient/4.5.7 (Java/11.0.8)"
63.32.??.??? - - [30/Jul/2023:04:25:28 +0200] "GET /api/DRcalc?lat=56.112&lon=-3.795&usehorizon=1&month=0&angle=40.0&aspect=90.0&clearsky=1&outputformat=json HTTP/1.1" 200 13542 "-" "unirest-java/1.3.11"
34.252.???.?? - - [06/Aug/2023:04:36:03 +0200] "GET /api/DRcalc?lat=53.192&lon=-2.892&usehorizon=1&month=0&angle=60.0&aspect=0.0&clearsky=1&outputformat=json HTTP/1.1" 200 13566 "-" "unirest-java/1.3.11"
167.179.???.?? - - [13/Aug/2023:03:15:27 +0200] "GET /pvg_scripts/v3.16.0/css/ol.css HTTP/1.1" 200 3554 "https://re.jrc.ec.europa.eu/pvg_tools/en/tools.html" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML,2= like Gecko) Chrome/115.0.0.0 Safari/537.36"
52.214.???.??? - - [20/Aug/2023:03:12:33 +0200] "GET /api/DRcalc?lat=54.991863&lon=-1.52342&usehorizon=1&month=0&angle=25.0&aspect=137.0&clearsky=1&outputformat=json HTTP/1.1" 200 13542 "-" "unirest-java/1.3.11"
3.250.???.??? - - [27/Aug/2023:03:39:32 +0200] "GET /api/DRcalc?lat=51.428202&lon=-0.342223&usehorizon=1&month=0&angle=40.0&aspect=54.0&clearsky=1&outputformat=json HTTP/1.1" 200 13565 "-" "unirest-java/1.3.11"
34.248.???.?? - - [10/Sep/2023:03:32:56 +0200] "GET /api/DRcalc?lat=53.441926&lon=-2.925451&usehorizon=1&month=0&angle=76.0&aspect=25.0&clearsky=1&outputformat=json HTTP/1.1" 200 13557 "-" "unirest-java/1.3.11"
34.243.?.??? - - [03/Sep/2023:03:48:26 +0200] "GET /api/DRcalc?lat=55.994591&lon=-3.806948&usehorizon=1&month=0&angle=40.0&aspect=56.0&clearsky=1&outputformat=json HTTP/1.1" 200 13550 "-" "unirest-java/1.3.11"
34.253.???.??? - - [17/Sep/2023:04:06:05 +0200] "GET /api/DRcalc?lat=51.211537&lon=0.294486&usehorizon=1&month=0&angle=40.0&aspect=39.0&clearsky=1&outputformat=json HTTP/1.1" 200 13568 "-" "unirest-java/1.3.11"
80.65.???.??? - - [24/Sep/2023:03:40:41 +0200] "GET /api/v5_2/printhorizon?lat=-21.31244&lon=55.45565&outputformat=json HTTP/1.1" 200 5845 "-" "python-requests/2.31.0"
54.170.??.??? - - [01/Oct/2023:03:37:26 +0200] "GET /api/DRcalc?lat=53.713086&lon=-2.634226&usehorizon=1&month=0&angle=40.0&aspect=135.0&clearsky=1&outputformat=json HTTP/1.1" 200 13513 "-" "unirest-java/1.3.11"
80.65.???.??? - - [08/Oct/2023:03:42:29 +0200] "GET /api/v5_2/printhorizon?lat=46.22231&lon=6.10786&outputformat=json HTTP/1.1" 200 5837 "-" "python-requests/2.31.0"
152.206.???.?? - - [22/Oct/2023:03:13:26 +0200] "GET /pvg_scripts/jqueryvalidation/dist/jquery.validate.min.js HTTP/1.1" 200 22691 "https://re.jrc.ec.europa.eu/pvg_tools/en/" "Mozilla/5.0 (Linux; Android 8.1.0; SM-J260M Build/M1AJB) AppleWebKit/537.36 (KHTML,2= like Gecko) Chrome/70.0.3538.110 Mobile Safari/537.36"
3.253.???.?? - - [15/Oct/2023:04:22:52 +0200] "GET /api/DRcalc?lat=54.563933&lon=-1.152292&usehorizon=1&month=0&angle=40.0&aspect=-1.0&clearsky=1&outputformat=json HTTP/1.1" 200 13567 "-" "unirest-java/1.3.11"
34.240.9.126 - - [29/Oct/2023:03:42:51 +0100] "GET /api/DRcalc?lat=51.085&lon=1.161&usehorizon=1&month=0&angle=40.0&aspect=-17.0&clearsky=1&outputformat=json HTTP/1.1" 200 13562 "-" "unirest-java/1.3.11"
34.242.???.? - - [05/Nov/2023:03:41:22 +0100] "GET /api/DRcalc?lat=51.709536&lon=-0.032412&usehorizon=1&month=0&angle=40.0&aspect=19.0&clearsky=1&outputformat=json HTTP/1.1" 200 13561 "-" "unirest-java/1.3.11"
190.239.???.??? - - [12/Nov/2023:03:54:16 +0100] "GET /api/v5_2/extent?lat=-11.960&lon=-68.660&js=1&database=PVGIS-SARAH2,2=PVGIS-SARAH,3=PVGIS-NSRDB,4=PVGIS-ERA5,5= HTTP/1.1" 200 8 "https://re.jrc.ec.europa.eu/pvg_tools/en/tools.html" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML,6= like Gecko) Chrome/119.0.0.0 Safari/537.36"
34.240.???.??? - - [19/Nov/2023:03:22:32 +0100] "GET /api/DRcalc?lat=52.093131&lon=-0.416969&usehorizon=1&month=0&angle=40.0&aspect=125.0&clearsky=1&outputformat=json HTTP/1.1" 200 13536 "-" "unirest-java/1.3.11"
```

All we need to do is to figure out _how_ to pass the full Miller command
in order to extract the information in question :
unique external IP adresses and download size.

<!-- :::{margin} -->
!!! question

    What is a [Shell Function](https://www.gnu.org/software/bash/manual/html_node/Shell-Functions.html) ?
<!-- ::: -->

!!! tip
    It's _good practice_ to
    encapsulate the series of `sed` commands
    plus the long Miller command
    in a shell function.

``` bash
function analyse_pvgis_web_traffic_log () {
    mlr head -n 3 $1 \
    |sed 's/.*} //' \
    |sed 's/1=//' \
    |mlr --nidx --ocsv \
      then put -f test/convert_nginx_to_csv.mlr \
      then filter '!contains($ip, "139.191."); $status == 200' \
      then cut -f ip,status,size then stats1 -a sum -f size -g ip && echo ;
}
```

The above _function_ `analyse_pvgis_web_traffic_log` will process only the
first 3 lines from each input log file (note the `head -n 3` command).
Before we ask from Parallel to run all this,
we need to _export_ this function to make it visible to Parallel's
individual processes (you can read more at .. ) :

``` bash
export -f analyse_pvgis_web_traffic_log
```

Now we can run parallel processes and ask for a new _log_ file
which will collect some metadata on the parallel processes themselves,
such as how long it took for each process to complete :

``` bash
parallel --joblog analyse_pvgis_logs.log analyse_pvgis_web_traffic_log ::: access.log*.gz
```

??? example "Analysis result on the first 3 records of each log file"
    ``` bash
    parallel --joblog analyse_pvgis_web_traffic_logs.log analyse_pvgis_web_traffic_log ::: access.log*.gz
    ip,size_sum
    3.249.???.???,13561
    54.154.???.??,13567
    3.251.???.??,13563

    ip,size_sum
    189.6.???.???,2439
    80.65.???.???,5832

    ip,size_sum
    193.189.???.???,410
    34.244.???.???,13560
    54.247.??.???,13556

    ip,size_sum
    34.254.??.???,13546
    34.246.???.???,13544
    54.171.??.???,13565

    ip,size_sum
    54.216.???.???,13569
    3.250.???.???,13503
    3.249.???.??,13568

    ip,size_sum
    52.31.??.???,13571
    54.170.???.???,13566
    34.246.???.???,13560

    ip,size_sum
    185.250.???.???,4649
    212.194.???.??,1441

    ip,size_sum
    34.241.???.??,13564
    54.217.???.??,13559

    ip,size_sum
    3.249.??.???,13542
    3.253.??.???,13564
    63.32.??.???,13549

    ip,size_sum
    63.32.??.???,13542
    54.78.??.??,13557
    66.249.??.??,461

    ip,size_sum
    34.252.???.??,13566
    66.249.??.??,462
    109.62.??.???,506

    ip,size_sum
    167.179.???.??,558343
    52.30.???.???,13515

    ip,size_sum
    3.250.???.???,13565
    54.195.??.??,13565
    54.154.???.??,13567

    ip,size_sum
    52.214.???.???,13542
    80.65.???.???,5832
    52.213.??.???,13552

    ip,size_sum
    34.243.?.???,13550
    35.195.???.???,9077983
    52.30.???.???,13571

    ip,size_sum
    34.248.???.??,13557
    34.244.???.???,13562
    54.78.??.??,13545

    ip,size_sum
    34.253.???.???,13568
    54.217.???.???,13555
    3.248.???.??,13532

    ip,size_sum
    80.65.???.???,5845
    52.212.???.???,13577
    34.244.??.??,13549

    ip,size_sum
    54.170.??.???,13513

    ip,size_sum
    3.253.???.??,13567
    54.247.??.???,13558
    3.126.???.???,5241

    ip,size_sum
    80.65.???.???,5837
    3.249.??.???,13562
    46.137.???.???,13569

    ip,size_sum
    152.206.???.??,22691
    66.249.??.??,78681
    185.250.???.???,2321

    ip,size_sum
    34.240.?.???,13562
    3.253.??.???,13559
    34.242.??.???,13568

    ip,size_sum
    34.242.???.?,13561
    34.245.???.???,13571
    3.252.?.??,13572

    ip,size_sum
    34.240.???.???,13536
    54.170.???.???,13531
    34.251.??.???,13561

    ip,size_sum
    190.239.???.???,8
    34.245.???.???,13532
    203.173.???.???,55644
    ```

??? info "Log of parallel processes"

    ``` bash
    Seq	Host	Starttime	JobRuntime	Send	Receive	Exitval	Signal	Command
    2	:	1701549359.720	     0.053	0	72	0	0	analyse_pvgis_web_traffic_log access.log-20230611.gz
    1	:	1701549359.719	     0.064	0	74	0	0	analyse_pvgis_web_traffic_log access.log-20230604.gz
    3	:	1701549359.722	     0.063	0	51	0	0	analyse_pvgis_web_traffic_log access.log-20230618.gz
    4	:	1701549359.725	     0.060	0	54	0	0	analyse_pvgis_web_traffic_log access.log-20230625.gz
    5	:	1701549359.730	     0.063	0	74	0	0	analyse_pvgis_web_traffic_log access.log-20230702.gz
    6	:	1701549359.743	     0.052	0	74	0	0	analyse_pvgis_web_traffic_log access.log-20230709.gz
    8	:	1701549359.756	     0.049	0	70	0	0	analyse_pvgis_web_traffic_log access.log-20230723.gz
    7	:	1701549359.751	     0.082	0	73	0	0	analyse_pvgis_web_traffic_log access.log-20230716.gz
    12	:	1701549359.801	     0.059	0	55	0	0	analyse_pvgis_web_traffic_log access.log-20230820.gz
    9	:	1701549359.783	     0.088	0	53	0	0	analyse_pvgis_web_traffic_log access.log-20230730.gz
    10	:	1701549359.788	     0.082	0	67	0	0	analyse_pvgis_web_traffic_log access.log-20230806.gz
    11	:	1701549359.794	     0.078	0	68	0	0	analyse_pvgis_web_traffic_log access.log-20230813.gz
    13	:	1701549359.806	     0.072	0	73	0	0	analyse_pvgis_web_traffic_log access.log-20230827.gz
    14	:	1701549359.814	     0.077	0	72	0	0	analyse_pvgis_web_traffic_log access.log-20230903.gz
    15	:	1701549359.832	     0.059	0	75	0	0	analyse_pvgis_web_traffic_log access.log-20230910.gz
    16	:	1701549359.840	     0.093	0	72	0	0	analyse_pvgis_web_traffic_log access.log-20230917.gz
    17	:	1701549359.871	     0.069	0	74	0	0	analyse_pvgis_web_traffic_log access.log-20230924.gz
    19	:	1701549359.891	     0.065	0	33	0	0	analyse_pvgis_web_traffic_log access.log-20231008.gz
    18	:	1701549359.878	     0.101	0	72	0	0	analyse_pvgis_web_traffic_log access.log-20231001.gz
    21	:	1701549359.908	     0.074	0	71	0	0	analyse_pvgis_web_traffic_log access.log-20231022.gz
    20	:	1701549359.897	     0.092	0	72	0	0	analyse_pvgis_web_traffic_log access.log-20231015.gz
    22	:	1701549359.917	     0.082	0	74	0	0	analyse_pvgis_web_traffic_log access.log-20231029.gz
    24	:	1701549359.940	     0.060	0	70	0	0	analyse_pvgis_web_traffic_log access.log-20231112.gz
    25	:	1701549359.952	     0.061	0	74	0	0	analyse_pvgis_web_traffic_log access.log-20231119.gz
    23	:	1701549359.933	     0.080	0	71	0	0	analyse_pvgis_web_traffic_log access.log-20231105.gz
    26	:	1701549359.974	     0.045	0	75	0	0	analyse_pvgis_web_traffic_log access.log-20231126.gz
    ```

It seems we are ready to run in parallel the analysis over the complete content
of all log files !  Let's adjust the _analysing_ function to do so and let it
also export the results in a new file named after the input log and add some
meaningful suffix : 

``` bash
function analyse_pvgis_web_traffic_log () {
    mlr cat $1 \
    |sed 's/.*} //' \
    |sed 's/1=//' \
    |mlr --nidx --ocsv \
      then put -f test/convert_nginx_to_csv.mlr \
      then filter '!contains($ip, "139.191."); $status == 200' \
      then cut -f ip,status,size then stats1 -a sum -f size -g ip > ${1%.*} ;
}
```

!!! hint

    The _new_ things in the function are `mlr cat $1` and the redirection of the
    output to a file via `${1%.*}_external_unique_ip_and_size.csv`. For the latter
    _magic_, see also
    [Shell Parameter Expansion](https://www.gnu.org/software/bash/manual/html_node/Shell-Parameter-Expansion.html) on the ‘$’ character, parameter expansion and more.

!!! danger

    This will take (took!) quite some time in a laptop with x CPUs and 48GB RAM.
    Curious ? Check out the Parallel processing log file, in particular the
    `JobRuntime` column which reports timings in seconds.

    It'd be faster to run all this in a system with more CPUs.
    Then again, let us be reminded about the environmental footprint
    in using Big computing facilities!

??? info "Parallel processing log file"

    ``` bash
    Seq	Host	Starttime	JobRuntime	Send	Receive	Exitval	Signal	Command
    7	:	1701550538.009	  1149.529	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20230716.gz
    5	:	1701550537.977	  1288.844	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20230702.gz
    6	:	1701550537.989	  1301.880	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20230709.gz
    4	:	1701550537.973	  1347.269	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20230625.gz
    3	:	1701550537.970	  1429.484	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20230618.gz
    2	:	1701550537.968	  1776.205	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20230611.gz
    8	:	1701550538.020	  1907.743	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20230723.gz
    1	:	1701550537.966	  1916.812	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20230604.gz
    13	:	1701551967.465	  1340.104	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20230827.gz
    14	:	1701552314.186	  1530.186	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20230903.gz
    9	:	1701551687.546	  2227.082	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20230730.gz
    15	:	1701552445.777	  1523.345	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20230910.gz
    10	:	1701551826.826	  2221.660	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20230806.gz
    16	:	1701552454.784	  1603.147	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20230917.gz
    11	:	1701551839.896	  2371.598	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20230813.gz
    12	:	1701551885.247	  2643.483	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20230820.gz
    17	:	1701553307.582	  1502.473	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20230924.gz
    18	:	1701553844.378	  1600.421	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20231001.gz
    21	:	1701554048.493	  1587.713	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20231022.gz
    23	:	1701554211.500	  1511.329	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20231105.gz
    22	:	1701554057.936	  1762.668	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20231029.gz
    24	:	1701554528.743	  1425.480	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20231112.gz
    25	:	1701554810.069	  1364.000	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20231119.gz
    19	:	1701553914.633	  2295.756	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20231008.gz
    20	:	1701553969.136	  2339.115	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20231015.gz
    26	:	1701555444.804	   910.405	0	0	0	0	analyse_pvgis_web_traffic_log access.log-20231126.gz
    ```
