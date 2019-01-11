FROM pennbbl/baseimages:common

RUN sed -i '$iexport XCPEDIR=/xcpEngine-master' $ND_ENTRYPOINT

RUN sed -i '$iexport PATH=$PATH:$XCPEDIR' $ND_ENTRYPOINT

RUN bash -c 'cd / \
    && wget -nv https://github.com/PennBBL/xcpEngine/archive/master.zip \
    && unzip master.zip \
    && rm master.zip \
    && cd  /xcpEngine-master \
    && wget -nv https://www.dropbox.com/s/92i491mrtslb56i/space.tar.xz \
    && tar xvfJm space.tar.xz \
    && rm space.tar.xz' \
    && echo 123456

RUN bash -c 'BRAINATLAS=/xcpEngine-master/atlas BRAINSPACE=/xcpEngine-master/space XCPEDIR=/xcpEngine-master FSLDIR=/opt/fsl-5.0.10 AFNI_PATH=/opt/afni-latest C3D_PATH=/opt/convert3d-nightly/bin ANTSPATH=/opt/ants-2.2.0 /xcpEngine-master/xcpReset \
    && BRAINATLAS=/xcpEngine-master/atlas BRAINSPACE=/xcpEngine-master/space XCPEDIR=/xcpEngine-master /xcpEngine-master/utils/repairMetadata'

# Compile genlouvain with octave
RUN apt-get update -qq \
    && apt-get install -y -q --no-install-recommends \
           octave liboctave-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && cd /xcpEngine-master/thirdparty/genlouvain/MEX_SRC \
    && octave compile_mex.m 


RUN bash -c 'source /neurodocker/startup.sh'


    ###########################
# Install basic dependencies
RUN apt-get update && apt-get -y install \
    jq \
    tar \
    zip \
    build-essential


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
