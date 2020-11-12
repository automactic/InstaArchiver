import logging
from datetime import datetime
from http import HTTPStatus
from typing import List

import sqlalchemy
from fastapi import BackgroundTasks, Depends, FastAPI, Response
from pydantic import BaseModel

from services import create_connection, PostService

app = FastAPI()

logging.basicConfig(level=logging.INFO)


class PostCreationFromShortcodesRequest(BaseModel):
    shortcodes: List[str]


class PostCreationFromTimeRangeRequest(BaseModel):
    username: str
    start_time: datetime
    end_time: datetime


@app.get('/')
def read_root():
    return {'Hello': 'World'}


@app.post('/api/posts/from_shortcodes/')
async def create_post_from_shortcodes(
        request: PostCreationFromShortcodesRequest,
        background_tasks: BackgroundTasks,
        connection: sqlalchemy.engine.Connection = Depends(create_connection),
):
    background_tasks.add_task(PostService().create_from_shortcodes, request.shortcodes, connection)
    return Response(status_code=HTTPStatus.ACCEPTED)


@app.post('/api/posts/from_time_range/')
async def create_post_from_time_range(
        request: PostCreationFromTimeRangeRequest,
        background_tasks: BackgroundTasks,
        connection: sqlalchemy.engine.Connection = Depends(create_connection),
):
    background_tasks.add_task(
        PostService().create_from_time_range,
        request.username,
        request.start_time,
        request.end_time,
        connection
    )
    return Response(status_code=HTTPStatus.ACCEPTED)
