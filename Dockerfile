FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ENV USER_ID=""
ENV GROUP_ID=""
ENV DATABASE_HOSTNAME="localhost"

COPY ./app /app

EXPOSE 80
