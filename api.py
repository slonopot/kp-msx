import traceback

import uvicorn
from brotli_asgi import BrotliMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, FileResponse, Response

import config
from models.Category import Category
from models.Content import Content
from models.Device import Device
from models.KinoPub import KinoPub
from util import msx, proxy

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(BrotliMiddleware, minimum_size=1000)

ENDPOINT = '/msx'
UNAUTHORIZED = [
    '/',
    '/subtitleShifter',
    '/paging.html',
    '/paging.js',
    ENDPOINT + '/start.json',
    ENDPOINT + '/proxy'
]


def extract_real_ip(request):
    real_ip = request.headers.get("cf-connecting-ip")
    if real_ip is None:
        real_ip = request.headers.get("x-forwarded-for")
    if real_ip is None:
        real_ip = request.headers.get("x-real-ip")
    return real_ip


@app.middleware('http')
async def auth(request: Request, call_next):
    if request.method == 'OPTIONS':
        return await call_next(request)
    device_id = request.query_params.get('id')

    if device_id is None and str(request.url.path) not in UNAUTHORIZED:
        result = JSONResponse({
            'response': {
                'status': 200,
                'data': {'action': 'warn:ID не может быть пустым'}
            }
        })
        result.headers['Access-Control-Allow-Credentials'] = 'true'
        result.headers['Access-Control-Allow-Origin'] = '*'
        return result

    if device_id == '{ID}' and str(request.url.path) not in UNAUTHORIZED:
        result = JSONResponse(msx.unsupported_version())
        result.headers['Access-Control-Allow-Credentials'] = 'true'
        result.headers['Access-Control-Allow-Origin'] = '*'
        return result

    request.state.device = Device.by_id(device_id)
    if request.state.device is None and device_id is not None:
        request.state.device = Device.create(device_id)
    if request.state.device is not None and request.state.device.user_agent is None and (ua := request.headers.get('user-agent')) is not None:
        request.state.device.update_user_agent(ua)

    try:
        real_ip = extract_real_ip(request)
        if real_ip is not None and request.state.device is not None:
            request.state.device.set_real_ip(real_ip)
    except Exception as ex:
        pass

    try:
        result = await call_next(request)
    except Exception as e:
        result = JSONResponse(msx.handle_exception())
        result.headers['Access-Control-Allow-Credentials'] = 'true'
        result.headers['Access-Control-Allow-Origin'] = '*'
        traceback.print_exc()
    return result

# Static files

@app.get('/')
async def index(request: Request):
    return FileResponse('pages/index.html')

@app.get('/subtitleShifter')
async def subtitle_editor(request: Request):
    return FileResponse('pages/subtitle_shifter.html')

@app.get('/paging.html')
async def subtitle_editor(request: Request):
    return FileResponse('pages/paging.html')

@app.get('/paging.js')
async def subtitle_editor(request: Request):
    return FileResponse('pages/paging.js')

@app.get(ENDPOINT + '/start.json')
async def start(request: Request):
    return msx.start()

# General endpoints

@app.get(ENDPOINT + '/menu')
async def menu(request: Request):
    if not request.state.device.registered():
        return msx.unregistered_menu()

    categories = await request.state.device.kp.get_content_categories()
    if categories is None:
        request.state.device.delete()
        return msx.unregistered_menu()
    categories += Category.static_categories()
    for category in categories:
        if category.id in request.state.device.settings.menu_blacklist:
            category.blacklisted = True
    return msx.registered_menu(categories)


@app.get(ENDPOINT + '/registration')
async def registration(request: Request):
    if request.state.device.registered():
        return msx.already_registered()
    else:
        user_code, device_code = await KinoPub.get_codes()
        request.state.device.update_code(device_code)
        return msx.registration(user_code)


@app.post(ENDPOINT + '/check_registration')
async def check_registration(request: Request):
    result = await KinoPub.check_registration(request.state.device.code)
    if result is None:
        if request.query_params.get('silent') == 'true':
            return msx.delay_registration_check()
        else:
            return msx.code_not_entered()
    request.state.device.update_tokens(result['access_token'], result['refresh_token'])
    await request.state.device.notify()
    return msx.restart()


@app.get(ENDPOINT + '/category')
async def category(request: Request):
    page = int(request.query_params.get('page'))
    cat = request.query_params.get('category')
    extra = request.query_params.get('extra')
    genre = request.query_params.get('genre')
    sort = request.query_params.get('sort')
    result = await request.state.device.kp.get_content(category=cat, page=page, extra=extra, genre=genre, sort=sort)
    result = msx.content(result, cat, page, extra=(extra or genre), device_settings=request.state.device.settings)
    return result


@app.get(ENDPOINT + '/genres')
async def category(request: Request):
    cat = request.query_params.get('category')
    result = await request.state.device.kp.get_genres(category=cat)
    result = msx.genre_folders(cat, result)
    return result


@app.get(ENDPOINT + '/bookmarks')
async def bookmarks(request: Request):
    result = await request.state.device.kp.get_bookmark_folders()

    if len(result) == 0:
        await request.state.device.kp.create_bookmark_folder()
        result = await request.state.device.kp.get_bookmark_folders()

    result = msx.bookmark_folders(result)
    return result


@app.get(ENDPOINT + '/tv')
async def tv(request: Request):
    result = await request.state.device.kp.get_tv()

    result = msx.tv_channels(
        result,
        device_settings=request.state.device.settings
    )
    return result


@app.get(ENDPOINT + '/folder')
async def folder(request: Request):
    page = int(request.query_params.get('page'))
    f = request.query_params.get('folder')
    result = await request.state.device.kp.get_bookmark_folder(f, page=page)
    result = msx.content(result, "folder", page, extra="wtf", device_settings=request.state.device.settings)
    return result


@app.get(ENDPOINT + '/content')
async def content(request: Request):
    result = await request.state.device.kp.get_single_content(request.query_params.get('content_id'))
    #return result.to_msx_panel(
    return result.to_msx_content(
        device_settings=request.state.device.settings
    )


@app.get(ENDPOINT + '/multivideo')
async def content_multivideo(request: Request):
    result = await request.state.device.kp.get_single_content(request.query_params.get('content_id'))
    return result.to_multivideo_msx_panel(
        device_settings=request.state.device.settings
    )


@app.get(ENDPOINT + '/content/bookmarks')
async def content_bookmarks(request: Request):
    result = await request.state.device.kp.get_single_content(request.query_params.get('content_id'))

    content_folders = await request.state.device.kp.get_content_folders(request.query_params.get('content_id'))
    result.update_bookmarks(content_folders)

    folders = await request.state.device.kp.get_bookmark_folders()

    if len(folders) == 0:
        await request.state.device.kp.create_bookmark_folder()
        folders = await request.state.device.kp.get_bookmark_folders()

    return result.to_bookmarks_msx_panel(folders)


@app.get(ENDPOINT + '/seasons')
async def seasons(request: Request):
    result = await request.state.device.kp.get_single_content(request.query_params.get('content_id'))
    panel = result.to_seasons_msx_panel()
    return panel


@app.get(ENDPOINT + '/episodes')
async def episodes(request: Request):
    result = await request.state.device.kp.get_single_content(request.query_params.get('content_id'))
    return result.to_episodes_msx_panel(
        int(request.query_params.get('season')),
        device_settings=request.state.device.settings
    )


@app.get(ENDPOINT + '/search')
async def search(request: Request):
    result = await request.state.device.kp.search(request.query_params.get('q'))
    result = msx.content(result, "search", 1, extra=request.query_params.get('q'), decompress=False,
                         device_settings=request.state.device.settings)
    return result


@app.get(ENDPOINT + '/search/content')
async def search_content(request: Request):
    page = int(request.query_params.get('page'))
    result = await request.state.device.kp.search(request.query_params.get('q'), page=page, field=request.query_params.get('field'))
    result = msx.content(result, "search", page, extra=False, device_settings=request.state.device.settings)
    return result


@app.get(ENDPOINT + '/history')
async def history(request: Request):
    page = int(request.query_params.get('page'))
    result = await request.state.device.kp.get_history(page=page)
    result = msx.content(result, "history", page, extra="wtf", device_settings=request.state.device.settings)
    return result


@app.get(ENDPOINT + '/watching')
async def watching(request: Request):
    result = await request.state.device.kp.get_watching(subscribed=1)
    result = msx.content(result, "watching", 0, extra='wtf', device_settings=request.state.device.settings)
    return result


@app.get(ENDPOINT + '/collections')
async def collections(request: Request):
    page = int(request.query_params.get('page'))
    sort = request.query_params.get('sort')
    result = await request.state.device.kp.get_collections(page=page, sort=sort)
    result = msx.collections(result, page=page, sort=sort, device_settings=request.state.device.settings)
    return result


@app.get(ENDPOINT + '/collection')
async def single_collection(request: Request):
    collection_id = request.query_params.get('collection_id')
    result = await request.state.device.kp.get_single_collection(collection_id)
    result = msx.content(result, "collection", 0, extra='wtf', device_settings=request.state.device.settings)
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

    return msx.empty_response()


@app.post(ENDPOINT + '/toggle_subscription')
async def toggle_subscription(request: Request):
    content_id = request.query_params.get('content_id')
    await request.state.device.kp.toggle_subscription(content_id)
    result = await request.state.device.kp.get_single_content(content_id)
    return msx.update_content(Content.SUBSCRIPTION_BUTTON_ID, result.to_subscription_button())


@app.post(ENDPOINT + '/toggle_bookmark')
async def toggle_bookmark(request: Request):
    content_id = request.query_params.get('content_id')
    folder_id = int(request.query_params.get('folder_id'))
    await request.state.device.kp.toggle_bookmark(content_id, folder_id)
    result = await request.state.device.kp.get_single_content(content_id)

    content_folders = await request.state.device.kp.get_content_folders(request.query_params.get('content_id'))
    result.update_bookmarks(content_folders)

    upd = result.to_bookmark_stamp(folder_id)
    return msx.update_panel(str(folder_id), upd)

# Settings


@app.get(ENDPOINT + '/settings/screen')
async def settings_screen(request: Request):
    return msx.settings_screen(screen=True)


@app.get(ENDPOINT + '/settings')
async def settings(request: Request):
    return msx.settings_menu(request.state.device.settings)


@app.get(ENDPOINT + '/settings/menu_entries')
async def menu_entries(request: Request):
    categories = await request.state.device.kp.get_content_categories()
    categories += Category.static_categories()
    for category in categories:
        if category.id in request.state.device.settings.menu_blacklist:
            category.blacklisted = True

    entry = msx.menu_entries_settings_panel(categories)
    return entry

@app.get(ENDPOINT + '/settings/posters')
async def settings_posters(request: Request):
    results = await request.state.device.kp.get_content()
    entry = msx.poster_settings_panel([result.poster for result in results])
    return entry

@app.post(ENDPOINT + '/settings/toggle/{setting}')
async def settings_toggle_proxy(request: Request, setting: str):
    match setting:
        case msx.FOURK_ID:
            await request.state.device.toggle_4k()
            return msx.update_panel(msx.FOURK_ID, msx.stamp(request.state.device.settings.fourk))
        case msx.HDR_ID:
            await request.state.device.toggle_hdr()
            return msx.update_panel(msx.HDR_ID, msx.stamp(request.state.device.settings.hdr))
        case msx.HEVC_ID:
            await request.state.device.toggle_hevc()
            return msx.update_panel(msx.HEVC_ID, msx.stamp(request.state.device.settings.hevc))
        case msx.MIXED_PLAYLIST_ID:
            await request.state.device.toggle_mixed_playlist()
            return msx.update_panel(msx.MIXED_PLAYLIST_ID, msx.stamp(request.state.device.settings.mixed_playlist))
        case msx.SERVER_ID:
            new_label = await request.state.device.toggle_server()
            return msx.update_panel(msx.SERVER_ID, msx.label(new_label))
        case msx.PROXY_ID:
            await request.state.device.toggle_proxy()
            return msx.update_panel(msx.PROXY_ID, msx.stamp(request.state.device.settings.proxy))
        case msx.ALTERNATIVE_PLAYER_ID:
            await request.state.device.toggle_alternative_player()
            return msx.update_panel(msx.ALTERNATIVE_PLAYER_ID, msx.stamp(request.state.device.settings.alternative_player))
        case _:
            return msx.empty_response()


@app.post(ENDPOINT + '/settings/toggle_menu_entry/{menu_entry}')
async def toggle_menu_entry(request: Request, menu_entry :str):
    current_state = request.state.device.toggle_menu_entry(menu_entry)
    update = msx.update_panel(menu_entry, msx.stamp(current_state))
    return update


@app.post(ENDPOINT + '/settings/poster/set/{poster_size}/{poster_proxy}')
async def set_poster_settings(request: Request, poster_size :str, poster_proxy: str):
    request.state.device.set_poster_settings(poster_size, poster_proxy)
    update = msx.restart()
    return update


@app.post(ENDPOINT + '/settings/reset_menu')
async def toggle_menu_entry(request: Request):
    request.state.device.reset_menu()
    return msx.restart()

# Errors

@app.get(ENDPOINT + '/error')
async def error_page(request: Request):
    return msx.handle_exception(error_page=True)

@app.get(ENDPOINT + '/too_old')
async def too_old(request: Request):
    return msx.unsupported_version()

# Proxy

@app.get(ENDPOINT + '/proxy')
async def proxy_req(request: Request):
    url = request.query_params.get('url')
    try:
        proxy.check_url(url)
        real_ip = extract_real_ip(request)
        code, content_type, contents = await proxy.get(url, real_ip=real_ip)
    except:
        return Response(status_code=403)
    return Response(contents, code, media_type=content_type)


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=int(config.PORT))
