FROM python:3.12-slim

WORKDIR /usr/src/app

COPY . .

RUN pip install .

ENTRYPOINT ["bash"]
