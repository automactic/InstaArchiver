from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api.requests import PostCreationFromShortcode

app = FastAPI()
app.mount('/web', StaticFiles(directory='/web', html=True), name='web')


@app.post('/api/posts/from_url/')
def create_post_from_url(request: PostCreationFromShortcode):
    return {'Hello': request.shortcode}
