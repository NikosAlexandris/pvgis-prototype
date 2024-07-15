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

# Set non-interactive installation to avoid debconf and other prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies and configure locale/s as root
USER 0
RUN apt-get update \
    && apt-get install -y locales \
    && echo "LC_ALL=en_US.UTF-8" >> /etc/environment \
    && echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen \
    && echo "LANG=en_US.UTF-8" >> /etc/locale.conf \
    && locale-gen en_US.UTF-8 \
    && dpkg-reconfigure --frontend=noninteractive locales \
    && update-locale LANG=en_US.UTF-8 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Add new user for non-root level operations
RUN useradd -m pvgis-user
USER pvgis-user

# Set environment variables after locales are configured
ENV LANG=en_US.UTF-8 \
    LC_ALL=en_US.UTF-8 \
    FORCE_COLOR=1 \
    PATH="/home/pvgis-user/.local/bin:${PATH}"
    ENV COLUMNS=200

WORKDIR /home/pvgis-user/
COPY --chown=pvgis-user:pvgis-user ./ /home/pvgis-user/
RUN pip install --upgrade pip \
    && pip install --user pdm  \
    && pip install .[docs] \
    && pdm install \
    && pdm run mkdocs build --verbose --site-dir public \
    && pip cache purge

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
COPY --from=build /home/pvgis-user/public /opt/app-root/src

# run Nginx
CMD ["/usr/libexec/s2i/run"]
