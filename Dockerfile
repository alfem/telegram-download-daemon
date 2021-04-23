FROM python:3.8

RUN apt-get update && apt-get install -y --no-install-recommends \
		lsb-release \
	&& rm -rf /var/lib/apt/lists/*

COPY *.py /

RUN pip install telethon cryptg

CMD [ "python", "./telegram-download-daemon.py" ]