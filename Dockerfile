FROM python:3.6

COPY *.py /

RUN echo $TARGETPLATFORM

RUN if [ "$TARGETPLATFORM" = "linux/arm/v7" ]; then \
    which lsb_release \
    lsb_release -a \
    mv /usr/bin/lsb_release /usr/bin/lsb_release.bak \
    pip install telethon; \
  else \
    pip install telethon cryptg; \
  fi

CMD [ "python", "./telegram-download-daemon.py" ]