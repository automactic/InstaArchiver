import logging
from http import HTTPStatus

from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import Response, RedirectResponse
from fastapi.staticfiles import StaticFiles

from api.requests import PostCreationFromShortcode
from services.post import PostService

app = FastAPI()
app.mount('/web', StaticFiles(directory='/web', html=True), name='web')
logging.basicConfig(level=logging.DEBUG)


@app.get('/')
def root():
    return RedirectResponse(url='web/index.html')


@app.get('/index.html')
def index():
    return RedirectResponse(url='web/index.html')


@app.post('/api/posts/from_url/')
def create_post_from_url(request: PostCreationFromShortcode, background_tasks: BackgroundTasks):
    background_tasks.add_task(PostService().create_from_shortcode, request.shortcode)
    return Response(status_code=HTTPStatus.ACCEPTED)
