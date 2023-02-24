FROM xiaoqianxiao/restingfmri_denoise:0.1.0

LABEL maintainer="xiaoqian@stanford.edu"

# Make directory for flywheel spec (v0)
ENV FLYWHEEL /flywheel/v0
WORKDIR ${FLYWHEEL}

# Remove expired LetsEncrypt cert
RUN rm /usr/share/ca-certificates/mozilla/DST_Root_CA_X3.crt && \
    update-ca-certificates
ENV REQUESTS_CA_BUNDLE "/etc/ssl/certs/ca-certificates.crt"

# Save docker environ here to keep it separate from the Flywheel gear environment
RUN python -c 'import os, json; f = open("/flywheel/v0/gear_environ.json", "w"); json.dump(dict(os.environ), f)'

# Python 3.7.1 (default, Dec 14 2018, 19:28:38)
# [GCC 7.3.0] :: Anaconda, Inc. on linux
RUN pip install poetry && \
    rm -rf /root/.cache/pip


COPY poetry.lock pyproject.toml $FLYWHEEL/
RUN poetry install --only main

ENV PYTHONUNBUFFERED 1

############## DEV ONLY ##########
#COPY user.json /root/.config/flywheel/user.json
# Copy executable/manifest to Gear
COPY manifest.json ${FLYWHEEL}/manifest.json
COPY utils ${FLYWHEEL}/utils
COPY run.py ${FLYWHEEL}/run.py

# Configure entrypoint
RUN chmod a+x ${FLYWHEEL}/run.py
#ENTRYPOINT ["/flywheel/v0/run.py"]
ENTRYPOINT ["poetry","run","python","/flywheel/v0/run.py"]
