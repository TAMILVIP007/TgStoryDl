FROM python:3.12.1-alpine3.18
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
WORKDIR /OtakuFeed
ENV PATH="$VIRTUAL_ENV/bin:$PATH" TZ=Asia/Kolkata PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
COPY . .
RUN apk update && apk upgrade --available && sync && apk add --no-cache --virtual .build-deps build-base && python3 -m pip install -U pip && pip3 install --no-cache-dir -U setuptools wheel && pip3 install --no-cache-dir -U -r requirements.txt && rm -rf requirements.txt && apk --purge del .build-deps
RUN python3 -m compileall -b -o 2 . && rm -rf main.py requirements.txt
CMD ["python3", "main.pyc"]
