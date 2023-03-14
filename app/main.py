import logging
import os
from datetime import datetime
from http import HTTPStatus
from pathlib import Path
from typing import List, Optional

import aiofiles
import aiohttp
import databases
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.responses import Response, FileResponse
from fastapi.websockets import WebSocket, WebSocketDisconnect

from entities.enums import TaskStatus
from entities.posts import Post, PostListResult, PostCreationFromShortcode, PostArchiveRequest, PostUpdateRequest
from entities.profiles import ProfileWithDetail, ProfileListResult, ProfileUpdates, ProfileStats
from entities.tasks import TaskCreateRequest, TaskListResponse
from services import schema
from services.exceptions import PostNotFound
from services.post import PostService
from services.profile import ProfileService
from services.task import TaskExecutor
from services.crud import TaskCRUDService

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO'))
logger = logging.getLogger(__name__)

app = FastAPI()
database = databases.Database(schema.database_url)
http_session = aiohttp.ClientSession()


@app.on_event('startup')
async def startup():
    await database.connect()


@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()
    await http_session.close()


@app.get('/api/profiles/', response_model=ProfileListResult)
async def list_profiles(search: Optional[str] = None, offset: Optional[int] = 0, limit: Optional[int] = 100):
    return await ProfileService(database, http_session).list(search, offset, limit)


@app.get('/api/profiles/{username:str}/', response_model=ProfileStats)
async def get_profile(username: str):
    profile = await ProfileService(database, http_session).get(username)
    return profile if profile else Response(status_code=HTTPStatus.NOT_FOUND)


@app.patch('/api/profiles/{username:str}/', response_model=ProfileWithDetail)
async def update_profile(username: str, updates: ProfileUpdates):
    service = ProfileService(database, http_session)
    await service.update(username, updates)
    profile = await service.get(username)
    return profile if profile else Response(status_code=HTTPStatus.NOT_FOUND)


@app.delete('/api/profiles/{username:str}/')
async def delete_profile(username: str):
    await ProfileService(database, http_session).delete(username)
    return Response(status_code=HTTPStatus.NO_CONTENT)


@app.get('/api/stats/', response_model=List[ProfileStats])
async def get_profile_statistics(username: Optional[str] = None):
    stats = await ProfileService(database, http_session).get_stats(username=username)
    return list(stats.values())


@app.get('/api/posts/', response_model=PostListResult)
async def list_posts(
    offset: int = 0,
    limit: int = 10,
    username: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
):
    return await PostService(database, http_session).list(offset, limit, username, start_time, end_time)


@app.get('/api/posts/{shortcode:str}/', response_model=Post)
async def get_post(shortcode: str):
    return await PostService(database, http_session).get(shortcode)


@app.post('/api/posts/from_shortcode/')
def create_post_from_shortcode(request: PostCreationFromShortcode, background_tasks: BackgroundTasks):
    service = PostService(database, http_session)
    background_tasks.add_task(service.create_from_shortcode, request.shortcode)
    return Response(status_code=HTTPStatus.ACCEPTED)


@app.post('/api/posts/from_time_range/')
def create_post_from_time_range(request: PostArchiveRequest.FromTimeRange, background_tasks: BackgroundTasks):
    service = PostService(database, http_session)
    background_tasks.add_task(service.create_from_time_range, request)
    return Response(status_code=HTTPStatus.ACCEPTED)


@app.post('/api/posts/from_saved/')
def create_post_from_saved(request: PostArchiveRequest.FromSaved, background_tasks: BackgroundTasks):
    service = PostService(database, http_session)
    background_tasks.add_task(service.archive_saved, request.count)
    return Response(status_code=HTTPStatus.ACCEPTED)


@app.patch('/api/posts/{shortcode:str}/')
async def update_post(shortcode: str, request: PostUpdateRequest):
    try:
        await PostService(database, http_session).update_username(shortcode, request.username)
    except PostNotFound:
        return Response(status_code=HTTPStatus.NOT_FOUND)


@app.delete('/api/posts/{shortcode:str}/')
async def delete_post(shortcode: str):
    await PostService(database, http_session).delete(shortcode)


@app.delete('/api/posts/{shortcode:str}/{index:int}/')
async def delete_post_item(shortcode: str, index: int):
    await PostService(database, http_session).delete(shortcode, index)


@app.post('/api/tasks/')
async def create_tasks(request: TaskCreateRequest, background_tasks: BackgroundTasks):
    # get non-terminal tasks
    service = TaskCRUDService(database, http_session)
    non_terminal_tasks = await service.list(limit=1, status=[TaskStatus.PENDING, TaskStatus.IN_PROGRESS])

    # create new tasks
    await service.create(request)

    # start task executor, but only if there was no non-terminal tasks before task creation
    if non_terminal_tasks.count == 0:
        background_tasks.add_task(TaskExecutor(database, http_session).run_tasks)
    return Response(status_code=HTTPStatus.CREATED)


@app.get('/api/tasks/', response_model=TaskListResponse)
async def list_tasks(offset: Optional[int] = 0, limit: Optional[int] = 100, username: Optional[str] = None):
    return await TaskCRUDService(database, http_session).list(
        offset, limit, username=username, is_ascending=False
    )


@app.get('/media/{path:path}')
async def get_media(path: str, request: Request):
    path = Path('/media').joinpath(path)
    if not path.exists():
        return Response(status_code=HTTPStatus.NOT_FOUND)
    if range_header := request.headers.get('Range'):
        size = path.stat().st_size

        try:
            start, end = range_header.strip('bytes=').split('-')
            start = int(start)
            end = size - 1 if end == '' else int(end)
            chunk_size = end - start + 1
            if chunk_size <= 0:
                raise ValueError
        except ValueError:
            return Response(status_code=HTTPStatus.REQUESTED_RANGE_NOT_SATISFIABLE)

        async with aiofiles.open(path, mode='rb') as file:
            await file.seek(start)
            chunk = await file.read(chunk_size)
            return Response(chunk, status_code=HTTPStatus.PARTIAL_CONTENT, headers={
                'Accept-Ranges': 'bytes',
                'Content-Range': f'bytes {start}-{end}/{size}',
                'Content-Length': str(chunk_size),
            })
    else:
        return FileResponse(path)


@app.websocket('/web_socket/posts/')
async def posts(web_socket: WebSocket):
    await web_socket.accept()
    try:
        while True:
            data = await web_socket.receive_json()
            if shortcode := data.get('shortcode'):
                try:
                    post = await PostService(database, http_session).create_from_shortcode(shortcode)
                    response = {
                        'shortcode': post.shortcode, 'username': post.username, 'timestamp': post.timestamp.isoformat()
                    }
                    await web_socket.send_json({'event': 'post.saved', 'shortcode': shortcode, 'post': response})
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
