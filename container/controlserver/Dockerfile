FROM python:3

WORKDIR /usr/src/app

COPY ../../server/ ./
RUN pip install --no-cache-dir -r pyproject.toml

CMD [ "python", "./src/main.py" ]
