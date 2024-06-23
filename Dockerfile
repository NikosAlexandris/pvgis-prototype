# Build stage

# Docker image
FROM quay.apps.ocpt.jrc.ec.europa.eu/public/dockerhub/python:3.11 as build

# Build arguments
ARG BUILD_DATE
ARG VERSION
ARG REVISION

# Docker image metadata
LABEL org.opencontainers.image.created=$BUILD_DATE \
      org.opencontainers.image.authors='Alessandro Parodi <Alessandro.Parodi@ext.ec.europa.eu>, Nikos Alexandris <Nikos.Alexandris@ec.europa.eu>' \
      org.opencontainers.image.url='quay.apps.ocpt.jrc.ec.europa.eu/public/dockerhub/python:3.11' \
      org.opencontainers.image.source='?' \
      org.opencontainers.image.documentation='?' \
      org.opencontainers.image.version=$VERSION \
      org.opencontainers.image.revision=$REVISION \
      org.opencontainers.image.vendor='JRC' \
      org.opencontainers.image.licenses='EUPL-1.2' \
      org.opencontainers.image.ref.name='PVGIS 6 Documentation'

# Environment variables
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV COLUMNS=160
ENV FORCE_COLOR=1

# Set the working directory ?
WORKDIR /build

# Copy project files to the container ?
COPY ../ .

# Who is user 0 ? ------------------------------------------------------------
USER 0

# Install dependencies and build the documentation

# RUN apt-get update && apt-get install -y locales
RUN pip install --upgrade pip \
    && pip install pdm \
    && pdm install \
    && pdm run mkdocs build --verbose --site-dir public

# Final Stage
FROM quay.apps.ocpt.jrc.ec.europa.eu/public/redhat/ubi9/nginx-122

# Add image metadata
LABEL org.opencontainers.image.created=$BUILD_DATE \
      org.opencontainers.image.authors='Alessandro Parodi <Alessandro.Parodi@ext.ec.europa.eu>, Nikos Alexandris <Nikos.Alexandris@ec.europa.eu>' \
      org.opencontainers.image.url='quay.apps.ocpt.jrc.ec.europa.eu/public/dockerhub/python:3.11' \
      org.opencontainers.image.source='?' \
      org.opencontainers.image.documentation='?' \
      org.opencontainers.image.version=$VERSION \
      org.opencontainers.image.revision=$REVISION \
      org.opencontainers.image.vendor='JRC' \
      org.opencontainers.image.licenses='EUPL-1.2' \
      org.opencontainers.image.ref.name='PVGIS 6 Documentation'

# Copy the built project from the build stage
COPY --from=build /build/public /opt/app-root/src

# run Nginx
CMD ["/usr/libexec/s2i/run"]
