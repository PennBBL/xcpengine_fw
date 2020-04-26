#flywheel/xcpengine

############################
# Get the xcpengine algorithm from DockerHub
FROM pennbbl/xcpengine:1.1.0

MAINTAINER Ted Satterthwaite <sattertt@upenn.edu>
ENV DEBIAN_FRONTEND noninteractive
ENV XCPENGINE_VERSION 1.1.0 
RUN apt-get update && apt-get -y install \
  jq \
  tar \
  zip \
  build-essential

############################
# Install the Flywheel SDK
RUN apt-get -y install \
 autoconf \
  automake \
  libtool \
  python-dev 
RUN pip install flywheel-sdk numpy pandas scipy

RUN apt-get -y install jq && apt-get update 
############################
# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
ENV USER whoami
RUN mkdir -p ${FLYWHEEL}
COPY run ${FLYWHEEL}/run
COPY manifest.json ${FLYWHEEL}/manifest.json
COPY generate_taskfsfmodel.py ${FLYWHEEL}/generate_taskfsfmodel.py 
COPY taskfslmodel.py ${FLYWHEEL}/taskfslmodel.py 
COPY template.fsf ${FLYWHEEL}/template.fsf
COPY create_archive_fw_heudiconv.py ${FLYWHEEL}/create_archive_fw_heudiconv.py 
ENTRYPOINT ["/flywheel/v0/run"]
ADD https://raw.githubusercontent.com/PennBBL/xcpEngine/master/Dockerfile  ${FLYWHEEL}/xcpengine_${XCPENGINE_VERSION}_Dockerfile
RUN chmod +x ${FLYWHEEL}/*
ENV JQPATH  /usr/bin/
############################
# ENV preservation for Flywheel Engine
RUN env -u HOSTNAME -u PWD | \
  awk -F = '{ print "export " $1 "=\"" $2 "\"" }' > ${FLYWHEEL}/docker-env.sh

WORKDIR /flywheel/v0
