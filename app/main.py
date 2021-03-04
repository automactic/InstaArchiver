import logging
from datetime import datetime
from http import HTTPStatus
from pathlib import Path
from typing import Optional

import aiohttp
import databases
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocket, WebSocketDisconnect
from fastapi_utils.tasks import repeat_every

from entities.posts import PostListResult, PostCreationFromShortcode, PostCreationFromTimeRange
from services import schema, AutoArchiveService
from services.entities import ProfileListResult, ProfileDetail, ProfileUpdates
from services.exceptions import PostNotFound
from services.post import PostService
from services.profile import ProfileService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount('/media', StaticFiles(directory='/media'), name='media')

database = databases.Database(schema.database_url)
http_session = aiohttp.ClientSession()


@app.on_event('startup')
async def startup():
    await database.connect()


@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()
    await http_session.close()


@app.on_event('startup')
@repeat_every(seconds=60, wait_first=True)
async def auto_archive():
    await AutoArchiveService(database, http_session).update_profiles()


@app.get('/api/profiles/', response_model=ProfileListResult)
async def list_profiles():
    return await ProfileService(database, http_session).list()


@app.get('/api/profiles/{username:str}/', response_model=ProfileDetail)
async def get_profile(username: str):
    profile = await ProfileService(database, http_session).get(username)
    return profile if profile else Response(status_code=HTTPStatus.NOT_FOUND)


@app.patch('/api/profiles/{username:str}/', response_model=ProfileDetail)
async def update_profile(username: str, updates: ProfileUpdates):
    service = ProfileService(database, http_session)
    await service.update(username, updates)
    profile = await service.get(username)
    return profile if profile else Response(status_code=HTTPStatus.NOT_FOUND)


@app.get('/api/posts/', response_model=PostListResult)
async def list_posts(
        offset: Optional[int] = 0,
        limit: int = 10,
        username: Optional[str] = None,
        creation_time_start: Optional[datetime] = None,
        creation_time_end: Optional[datetime] = None,
):
    return await PostService(database, http_session).list(offset, limit, username, creation_time_start, creation_time_end)


@app.post('/api/posts/from_shortcode/')
def create_post_from_shortcode(request: PostCreationFromShortcode, background_tasks: BackgroundTasks):
    service = PostService(database, http_session)
    background_tasks.add_task(service.create_from_shortcode, request.shortcode)
    return Response(status_code=HTTPStatus.ACCEPTED)


@app.post('/api/posts/from_time_range/')
def create_post_from_time_range(request: PostCreationFromTimeRange, background_tasks: BackgroundTasks):
    service = PostService(database, http_session)
    background_tasks.add_task(service.create_from_time_range, request.username, request.start, request.end)
    return Response(status_code=HTTPStatus.ACCEPTED)


@app.delete('/api/posts/{shortcode:str}/')
async def delete_post(shortcode: str):
    await PostService(database, http_session).delete(shortcode)


@app.delete('/api/posts/{shortcode:str}/{index:int}/')
async def delete_post_item(shortcode: str, index: int):
    await PostService(database, http_session).delete(shortcode, index)


@app.websocket('/web_socket/posts/')
async def posts(web_socket: WebSocket):
    await web_socket.accept()
    try:
        while True:
            data = await web_socket.receive_json()
            if shortcode := data.get('shortcode'):
                try:
                    post = await PostService(database, http_session).create_from_shortcode(shortcode)
                    await web_socket.send_json({'event': 'post.saved', 'shortcode': shortcode, 'post': post.response})
                except PostNotFound as e:
                    await web_socket.send_json(e.response)
    except WebSocketDisconnect:
        logger.debug('Web socket disconnected.')


@app.get('/{path:path}')
async def web(path: str):
    path = Path(path)
    if len(path.parts) == 1 and path.suffix in ['.html', '.css', '.js']:
        return FileResponse(Path('/web/').joinpath(path.parts[-1]))
    else:
        return FileResponse(Path('/web/index.html'))
