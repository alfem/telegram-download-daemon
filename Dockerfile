FROM python:3.6

COPY *.py /

RUN echo $TARGETPLATFORM

RUN if [ "$TARGETPLATFORM" = "linux/arm64" ] ; then pip install telethon; else pip install telethon cryptg

CMD [ "python", "./telegram-download-daemon.py" ]