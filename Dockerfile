FROM python:3.10.5 AS compile-image

RUN pip install --no-cache-dir telethon cryptg==0.2 pysocks

FROM python:3.10.5-slim AS run-image

COPY --from=compile-image /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

WORKDIR /app
COPY *.py ./
RUN chmod 777 /app/*.py

CMD [ "python3", "./telegram-download-daemon.py" ]
