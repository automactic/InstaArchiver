from fastapi import BackgroundTasks, FastAPI, Response

from services import PostService

app = FastAPI()


@app.get('/')
def read_root():
    return {'Hello': 'World'}


@app.post('/api/posts/{post_shortcode}')
async def create_post(post_shortcode: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(PostService().create, post_shortcode)
    return Response(status_code=202)
