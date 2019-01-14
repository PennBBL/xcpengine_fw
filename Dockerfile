#flywheel/xcpengine

############################
# Get the xcpengine algorithm from DockerHub
FROM pennbbl/xcpengine

MAINTAINER pennbbl <pennbbl@pennmedicine.upenn.edu>


############################
# Install basic dependencies
RUN apt-get update && apt-get -y install \
    jq \
    tar \
    zip \
    build-essential
    
 ENV XCPEDIR="/xcpEngine-master" \
    FSLDIR="/opt/fsl-5.0.11" \
    AFNI_PATH="/opt/afni-latest" \
    C3D_PATH="/opt/convert3d-nightly/bin"

RUN sed -i '$iexport XCPEDIR=/xcpEngine-master' $ND_ENTRYPOINT

RUN sed -i '$iexport FSLDIR=/opt/fsl-5.0.11' $ND_ENTRYPOINT

RUN sed -i '$iexport AFNI_PATH=/opt/afni-latest' $ND_ENTRYPOINT

RUN sed -i '$iexport C3D_PATH=/opt/convert3d-nightly/bin' $ND_ENTRYPOINT

RUN sed -i '$iexport ANTSPATH=/opt/ants-2.2.0' $ND_ENTRYPOINT

RUN sed -i '$iexport PATH=$PATH:$XCPEDIR' $ND_ENTRYPOINT   
RUN bash -c 'XCPEDIR=/xcpEngine-master FSLDIR=/opt/fsl-5.0.11 AFNI_PATH=/opt/afni-latest C3D_PATH=/opt/convert3d-nightly/bin ANTSPATH=/opt/ants-2.2.0 /xcpEngine-master/xcpReset'

# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
RUN mkdir -p ${FLYWHEEL}
COPY run ${FLYWHEEL}/run
COPY manifest.json ${FLYWHEEL}/manifest.json

# ENV preservation for Flywheel Engine
RUN env -u HOSTNAME -u PWD | \
  awk -F = '{ print "export " $1 "=\"" $2 "\"" }' > ${FLYWHEEL}/docker-env.sh

RUN echo "export XVFB_WRAPPER_SOFT_FILE_LOCK=1" >> ${FLYWHEEL}/docker-env.sh

# Set the entrypoint
ENTRYPOINT ["/flywheel/v0/run"]
