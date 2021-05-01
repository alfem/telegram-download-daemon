FROM python:3.6

COPY *.py /

RUN echo $TARGETPLATFORM

RUN if [ "$TARGETPLATFORM" = "linux/arm/v7" ]; then \
    pip install telethon; \
  else \
    pip install telethon cryptg; \
  fi

CMD [ "python", "./telegram-download-daemon.py" ]