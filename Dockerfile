FROM python:3.12

RUN python -m pip install hatch

COPY . .

RUN hatch run cov
