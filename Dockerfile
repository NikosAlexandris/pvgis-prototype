# Build stage

# Use following Docker image
FROM quay.apps.ocpt.jrc.ec.europa.eu/public/dockerhub/python:3.11 as build

# Set environment variables
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8
ENV COLUMNS=160
ENV FORCE_COLOR=1

# Set the working directory
# WORKDIR /build

# Copy project files to the container ?
COPY ../ .

# Who is user 0 ? ------------------------------------------------------------
USER 0

# Install dependencies and build the project
# RUN apt-get update && apt-get install -y locales
RUN pip install --upgrade pip \
    && pip install pdm \
    && pdm install \
    && pdm run mkdocs build --verbose --site-dir public

# Final Stage
FROM quay.apps.ocpt.jrc.ec.europa.eu/public/redhat/ubi9/nginx-122

# Copy the built project from the build stage
COPY --from=build /build/public /opt/app-root/src

# Set ownership and permissions
RUN chown -R nginx:nginx /opt/app-root/src

# run Nginx
CMD /usr/libexec/s2i/run
