from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from api.requests import PostCreationFromShortcode

app = FastAPI()
app.mount('/web', StaticFiles(directory='/web', html=True), name='web')


@app.get('/')
def root():
    return RedirectResponse(url='web/index.html')


@app.get('/index.html')
def index():
    return RedirectResponse(url='web/index.html')


@app.post('/api/posts/from_url/')
def create_post_from_url(request: PostCreationFromShortcode):
    return {'Hello': request.shortcode}
