import logging
from http import HTTPStatus
from pathlib import Path

import aiohttp
import databases
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.websockets import WebSocket, WebSocketDisconnect

from api.requests import PostCreationFromShortcode
from services import schema
from services.entities import ProfileListResult, Profile
from services.exceptions import PostNotFound
from services.post import PostService
from services.profile import ProfileService

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI()
app.mount('/media', StaticFiles(directory='/media'), name='media')

logger.debug(f'Database: {schema.database_url}')
database = databases.Database(schema.database_url)
http_session = aiohttp.ClientSession()


@app.on_event('startup')
async def startup():
    try:
        await database.connect()
    except Exception as e:
        logger.error(e)
        raise e


@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()
    await http_session.close()


@app.get('/api/profiles/', response_model=ProfileListResult)
async def list_profiles():
    return await ProfileService(database, http_session).list()


@app.get('/api/profiles/{username:str}/', response_model=Profile)
async def list_profiles(username: str):
    return await ProfileService(database, http_session).get(username)


@app.post('/api/posts/from_shortcode/')
def create_post_from_url(request: PostCreationFromShortcode, background_tasks: BackgroundTasks):
    background_tasks.add_task(PostService(database, http_session).create_from_shortcode, request.shortcode)
    return Response(status_code=HTTPStatus.ACCEPTED)


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
