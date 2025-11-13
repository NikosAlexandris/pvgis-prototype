---
tags:
  - How-To
  - CLI
  - Solar Incidence Angle
hide:
  - toc
---

# Solar incidence angle

`#!bash pvgis-prototype`
can calculate the solar incidence angle
for a givel location and moment in time.

``` bash exec="true" result="ansi" source="above"
pvgis-prototype position incidence 8.627626 45.812233 180 45 '2020-01-01 15:00:00' -v
```

Let's ask for a day

``` bash exec="true" result="ansi" source="above"
pvgis-prototype position incidence \
8.628 45.812 180 0.1 \
--start-time '2010-01-01' \
--end-time '2010-01-02' \
-v
```

Now, let's ask for a different (geometrucal) definition of the solar incidence
angle

``` bash exec="true" result="ansi" source="above" hl_lines="6"
pvgis-prototype position incidence \
8.628 45.812 180 0.1 \
--start-time '2010-01-01' \
--end-time '2010-01-02' \
-v \
--sun-vector-to-surface-plane
```

See the difference ?  Check out the metadata panels as well !
