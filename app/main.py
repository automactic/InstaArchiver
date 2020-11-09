from typing import List

import sqlalchemy
from fastapi import BackgroundTasks, Depends, FastAPI, Response
from pydantic import BaseModel

from services import create_connection, PostService

app = FastAPI()


class PostCreationRequest(BaseModel):
    shortcodes: List[str]


@app.get('/')
def read_root():
    return {'Hello': 'World'}


@app.post('/api/posts/')
async def create_post(
        request: PostCreationRequest,
        background_tasks: BackgroundTasks,
        connection: sqlalchemy.engine.Connection = Depends(create_connection),
):
    background_tasks.add_task(PostService().create, request.shortcodes, connection)
    return Response(status_code=202)
