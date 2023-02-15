FROM xiaoqianxiao/test:latest

LABEL maintainer="xiaoqian@stanford.edu"

ENV FLYWHEEL /flywheel/v0
WORKDIR ${FLYWHEEL}

RUN pip install poetry && \
    rm -rf /root/.cache/pip

COPY pyproject.toml $FLYWHEEL/
RUN poetry install --no-root

ENV PYTHONUNBUFFERED 1

# Copy executable/manifest to Gear
COPY manifest.json ${FLYWHEEL}/manifest.json
COPY utils ${FLYWHEEL}/utils
COPY run.py ${FLYWHEEL}/run.py

# Configure entrypoint
RUN chmod a+x ${FLYWHEEL}/run.py
ENTRYPOINT ["/flywheel/v0/run.py"]
