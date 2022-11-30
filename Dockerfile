FROM node:18 AS web

RUN npm install -g @angular/cli
COPY web /web
WORKDIR /web
RUN npm install
RUN ng build


FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

COPY --from=web /web/dist /web

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ENV USER_ID=""
ENV GROUP_ID=""

ENV DATABASE_USERNAME="postgres"
ENV DATABASE_PASSWORD="postgres"
ENV DATABASE_HOSTNAME="localhost"
ENV DATABASE_PORT="5432"

ENV INSTAGRAM_USERNAME=""
ENV INSTAGRAM_PASSWORD=""

COPY ./app /app

EXPOSE 80
