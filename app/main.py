from typing import List

from fastapi import BackgroundTasks, FastAPI, Response
from pydantic import BaseModel

from services import PostService

app = FastAPI()


class PostCreationRequest(BaseModel):
    shortcodes: List[str]


@app.get('/')
def read_root():
    return {'Hello': 'World'}


@app.post('/api/posts/')
async def create_post(request: PostCreationRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(PostService().create, request.shortcodes)
    return Response(status_code=202)
