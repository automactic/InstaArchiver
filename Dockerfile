FROM node:14.15

RUN npm install -g @angular/cli
COPY web /web
WORKDIR /web
RUN npm install
RUN ng build --prod


FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

COPY --from=0 /web/dist/InstaSaver /web

COPY ./requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ENV USER_ID=""
ENV GROUP_ID=""
ENV DATABASE_HOSTNAME="localhost"

COPY ./app /app

EXPOSE 80
