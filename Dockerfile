FROM python:3 AS compile-image

RUN pip install --no-cache-dir --user telethon cryptg==0.2

FROM python:3 AS run-image

COPY --from=compile-image /root/.local /root/.local

WORKDIR /app
COPY *.py ./

CMD [ "python3", "./telegram-download-daemon.py" ]
