FROM quay.apps.ocpt.jrc.ec.europa.eu/public/dockerhub/python:3.11 as build
ARG LANG="en_US.UTF-8"
ARG LC_ALL="en_US.UTF-8"
ARG COLUMNS=160
WORKDIR /build
COPY ../ .
# RUN apt-get update && apt-get install -y locales
USER 0
RUN pip install --upgrade pip ; \
 pip install pdm mkdocs-jupyter ; \
 pip install -r requirements.txt ; \
 pdm run mkdocs build --verbose --site-dir public

FROM quay.apps.ocpt.jrc.ec.europa.eu/public/redhat/ubi9/nginx-122
COPY --from=build /build/public /opt/app-root/src
CMD /usr/libexec/s2i/run