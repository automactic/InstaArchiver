from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount('/web', StaticFiles(directory='/web', html=True), name='web')

@app.post('/api/posts/from_url/')
def create_post_from_url():
    return {'Hello': 'World'}