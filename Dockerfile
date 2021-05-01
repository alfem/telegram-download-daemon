FROM python:3.6

COPY *.py /

RUN echo $TARGETPLATFORM

RUN test  "$TARGETPLATFORM" = "linux/arm64" && pip install telethon || else pip install telethon cryptg

CMD [ "python", "./telegram-download-daemon.py" ]