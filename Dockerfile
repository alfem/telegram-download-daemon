FROM python:3.6

COPY *.py /

RUN pip install telethon cryptg

CMD [ "python", "./telegram-download-daemon.py" ]