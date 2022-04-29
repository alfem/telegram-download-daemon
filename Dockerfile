FROM python:3.9-bullseye AS compile-image

RUN echo $TARGETPLATFORM
RUN if [ "$TARGETPLATFORM" = "linux/arm/v7" ]; then \
    which lsb_release \
    lsb_release -a \
    mv /usr/bin/lsb_release /usr/bin/lsb_release.bak \
    pip install --no-cache-dir --user telethon; \
  else \
    pip install --no-cache-dir --user telethon cryptg; \
  fi

FROM python:3.9-slim-bullseye AS run-image

COPY --from=compile-image /root/.local /root/.local

WORKDIR /app
COPY *.py ./

CMD [ "python3", "./telegram-download-daemon.py" ]
