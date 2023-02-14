FROM xiaoqianxiao/test:latest

LABEL maintainer="xiaoqian@stanford.edu"

ENV FLYWHEEL /flywheel/v0
WORKDIR ${FLYWHEEL}

# Remove expired LetsEncrypt cert
RUN rm /usr/share/ca-certificates/mozilla/DST_Root_CA_X3.crt && \
    update-ca-certificates
ENV REQUESTS_CA_BUNDLE "/etc/ssl/certs/ca-certificates.crt"

# Save docker environ here to keep it separate from the Flywheel gear environment
RUN python -c 'import os, json; f = open("/flywheel/v0/gear_environ.json", "w"); json.dump(dict(os.environ), f)'

RUN pip install poetry && \
    rm -rf /root/.cache/pip


COPY poetry.lock pyproject.toml $FLYWHEEL/
RUN poetry install --no-dev

ENV PYTHONUNBUFFERED 1

# Copy executable/manifest to Gear
COPY manifest.json ${FLYWHEEL}/manifest.json
COPY run.py ${FLYWHEEL}/run.py

# Configure entrypoint
RUN chmod a+x ${FLYWHEEL}/run.py
ENTRYPOINT ["/flywheel/v0/run.py"
