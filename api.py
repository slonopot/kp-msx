import traceback
import uuid

from fastapi import encoders
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, HTMLResponse
from functools import wraps

import config
from models.Category import Category
from models.Device import Device
from models.KinoPub import KinoPub
from models.MSX import MSX
from util import pages

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ENDPOINT = '/msx'
UNAUTHORIZED = ['/', ENDPOINT + '/start.json']


@app.middleware('http')
async def auth(request: Request, call_next):
    if request.method == 'OPTIONS':
        return await call_next(request)
    device_id = request.query_params.get('id')
    if device_id is None and str(request.url.path) not in UNAUTHORIZED:
        return JSONResponse({
            'response': {
                'status': 200,
                'data': {'action': 'warn:ID не может быть пустым'}
            }
        })
    request.state.device = Device.by_id(device_id)
    if request.state.device is None and device_id is not None:
        request.state.device = Device.create(device_id)
    try:
        result = await call_next(request)
    except Exception as e:
        result = JSONResponse({'success': False, 'error': f'{type(e)}: {e}'})
        result.headers['Access-Control-Allow-Credentials'] = 'true'
        result.headers['Access-Control-Allow-Origin'] = '*'
        traceback.print_exc()
    return result


@app.get('/')
async def root(request: Request):
    return HTMLResponse(pages.ROOT)


@app.get(ENDPOINT + '/start.json')
async def start(request: Request):
    return MSX.start()


@app.get(ENDPOINT + '/menu')
async def menu(request: Request):
    if not request.state.device.registered():
        return MSX.unregistered_menu()

    categories = await request.state.device.kp.get_content_categories()
    if categories is None:
        request.state.device.delete()
        return MSX.unregistered_menu()
    return MSX.registered_menu(categories)


@app.get(ENDPOINT + '/registration')
async def registration(request: Request):
    if request.state.device.registered():
        return MSX.already_registered()
    else:
        user_code, device_code = await KinoPub.get_codes()
        request.state.device.update_code(device_code)
        return MSX.registration(user_code)


@app.post(ENDPOINT + '/check_registration')
async def check_registration(request: Request):
    result = await KinoPub.check_registration(request.state.device.code)
    if result is None:
        return MSX.code_not_entered()
    request.state.device.update_tokens(result['access_token'], result['refresh_token'])
    await request.state.device.notify()
    return MSX.restart()


@app.get(ENDPOINT + '/category')
async def category(request: Request):
    offset = request.query_params.get('offset') or 0
    page = int(offset) // 20 + 1
    cat = request.query_params.get('category')
    extra = request.query_params.get('extra')
    result = await request.state.device.kp.get_content(cat, page=page, extra=extra)
    result = MSX.content(result, cat, page, extra=extra)
    return result


@app.get(ENDPOINT + '/bookmarks')
async def bookmarks(request: Request):
    result = await request.state.device.kp.get_bookmark_folders()

    result = MSX.bookmark_folders(result)
    return result


@app.get(ENDPOINT + '/folder')
async def folder(request: Request):
    offset = request.query_params.get('offset') or 0
    page = int(offset) // 20 + 1
    f = request.query_params.get('folder')
    result = await request.state.device.kp.get_bookmark_folder(f, page=page)
    result = MSX.content(result, "folder", page, extra="wtf")
    return result


@app.get(ENDPOINT + '/content')
async def content(request: Request):
    result = await request.state.device.kp.get_single_content(request.query_params.get('content_id'))
    return result.to_msx_panel()


@app.get(ENDPOINT + '/seasons')
async def seasons(request: Request):
    result = await request.state.device.kp.get_single_content(request.query_params.get('content_id'))
    panel = result.to_seasons_msx_panel()
    return panel


@app.get(ENDPOINT + '/episodes')
async def episodes(request: Request):
    result = await request.state.device.kp.get_single_content(request.query_params.get('content_id'))
    return result.to_episodes_msx_panel(int(request.query_params.get('season')))


@app.get(ENDPOINT + '/search')
async def search(request: Request):
    result = await request.state.device.kp.search(request.query_params.get('q'))
    result = MSX.content(result, "search", 1, extra=request.query_params.get('q'), decompress=False)
    return result


@app.get(ENDPOINT + '/history')
async def history(request: Request):
    offset = request.query_params.get('offset') or 0
    page = int(offset) // 20 + 1
    result = await request.state.device.kp.get_history(page=page)
    result = MSX.content(result, "history", page, extra="wtf")
    return result


@app.get(ENDPOINT + '/watching')
async def watching(request: Request):
    result = await request.state.device.kp.get_watching(subscribed=1)
    result = MSX.content(result, "watching", 0, extra='wtf')
    return result


@app.post(ENDPOINT + '/play')
async def play(request: Request):
    content_id = request.query_params.get('content_id')
    season = request.query_params.get('season')
    episode = request.query_params.get('episode')
    result = await request.state.device.kp.get_single_content(request.query_params.get('content_id'))

    if season is not None and episode is not None:
        for _season in result.seasons:
            if _season.n != int(season):
                continue
            for _episode in _season.episodes:
                if _episode.n == int(episode):
                    if not _episode.watched:
                        await request.state.device.kp.toggle_watched(content_id, season, episode)
                    break
            break
    else:
        if not result.watched:
            await request.state.device.kp.toggle_watched(content_id)
    acts = result.to_player_opts(season, episode)
    return MSX.play(acts)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(config.PORT))

