FROM python:3

COPY *.py /

RUN pip install telethon cryptg

CMD [ "python", "./telegram-download-daemon.py" ]