FROM python:3

COPY telegram-download-daemon.py /

RUN pip install telethon cryptg

CMD [ "python", "./telegram-download-daemon.py" ]