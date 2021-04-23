FROM python:3

COPY *.py /

RUN mv /usr/bin/lsb_release /usr/bin/lsb_release_back
RUN pip install telethon cryptg

CMD [ "python", "./telegram-download-daemon.py" ]