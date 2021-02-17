from fastapi import FastAPI

app = FastAPI()


@app.post('/api/posts/from_url/')
def create_post_from_url():
    return {'Hello': 'World'}