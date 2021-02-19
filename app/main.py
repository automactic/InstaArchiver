import logging
from http import HTTPStatus

import sqlalchemy
from fastapi import FastAPI, BackgroundTasks
from fastapi.param_functions import Depends
from fastapi.responses import Response, RedirectResponse
from fastapi.staticfiles import StaticFiles

from api.requests import PostCreationFromShortcode
from services.post import PostService
from services.schema import create_connection

app = FastAPI()
app.mount('/web', StaticFiles(directory='/web', html=True), name='web')
logging.basicConfig(level=logging.DEBUG)


@app.get('/')
def root():
    return RedirectResponse(url='web/index.html')


@app.get('/index.html')
def index():
    return RedirectResponse(url='web/index.html')


@app.post('/api/posts/from_shortcode/')
def create_post_from_url(
        request: PostCreationFromShortcode,
        background_tasks: BackgroundTasks,
        connection: sqlalchemy.engine.Connection = Depends(create_connection)
):
    background_tasks.add_task(PostService(connection).create_from_shortcode, request.shortcode)
    return Response(status_code=HTTPStatus.ACCEPTED)
