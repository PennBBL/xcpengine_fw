#flywheel/xcpengine

############################
# Get the xcpengine algorithm from DockerHub
FROM pennbbl/xcpengine:latest

MAINTAINER Ted Satterthwaite <sattertt@upenn.edu>

ENV XCPENGINE_VERSION 1.0 
RUN apt-get update && apt-get -y install \
  jq \
  tar \
  zip \
  build-essential

############################
# Install the Flywheel SDK
RUN pip install flywheel-sdk

############################
# Install the Flywheel BIDS client
RUN pip install flywheel_bids

############################
# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
RUN mkdir -p ${FLYWHEEL}
COPY run ${FLYWHEEL}/run
COPY manifest.json ${FLYWHEEL}/manifest.json

# Set the entrypoint
ENTRYPOINT ["/flywheel/v0/run"]
ADD https://raw.githubusercontent.com/PennBBL/xcpEngine/master/Dockerfile  ${FLYWHEEL}/xcpemgine_${XCPENGINE_VERSION}_Dockerfile
RUN chmod +x ${FLYWHEEL}/*
############################
# ENV preservation for Flywheel Engine
RUN env -u HOSTNAME -u PWD | \
  awk -F = '{ print "export " $1 "=\"" $2 "\"" }' > ${FLYWHEEL}/docker-env.sh

WORKDIR /flywheel/v0
