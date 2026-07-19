import aiohttp

import config
from models.Category import Category
from models.Channel import Channel
from models.Collection import Collection
from models.Content import Content
from models.Folder import Folder
from models.Genre import Genre
from models.Media import Media
from models.Reference import Reference
from util import db
from util.msx import LENNY


class KinoPub:

    def __init__(self, token, refresh, user_agent=None):
        self.token = token
        self.refresh = refresh
        self.real_ip = None
        self.user_agent = user_agent

    async def api(self, path, params=None, method='GET'):
        headers = {'Authorization': 'Bearer ' + self.token, 'Accept-Encoding': 'br'}

        if self.real_ip is not None:
            headers['X-Real-Ip'] = self.real_ip
        if self.user_agent is not None:
            headers['User-Agent'] = 'kp-msx/' + self.user_agent

        async with aiohttp.ClientSession(headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as s:
            if method == 'GET':
                response = await s.get(f'{config.KP_API_DOMAIN}/v1{path}', params=params)
            else:
                response = await s.request(method, f'{config.KP_API_DOMAIN}/v1{path}', json=params)

            if response.status == 401:
                reauth_result = await self.refresh_tokens()
                if reauth_result:
                    return await self.api(path, params=params)
                else:
                    return None
            result = await response.json()
            return result

    async def get_content_categories(self):
        result = await self.api('/types')
        if result is None:
            return None
        return [Category(i) for i in result['items']]

    async def get_genres(self, category=None):
        result = await self.api('/genres', params={'type': category})
        if result is None:
            return None
        return [Genre(i) for i in result['items']]

    async def get_content(self, category=None, page=1, extra=None, genre=None, sort=None):
        path = '/items'
        if extra is not None:
            path += f'/{extra}'
        params = {'page': page}
        if category is not None:
            params['type'] = category
        if genre is not None:
            params['genre'] = genre
        if sort is not None:
            params['sort'] = sort
        result = await self.api(path, params=params)
        if result is None:
            return []
        results = [Content(i) for i in result['items']]
        return results

    async def search(self, query, page=1, field=None):
        params = {'q': query, 'page': page}
        if field is not None:
            params['field'] = field

        result = await self.api('/items/search', params=params)
        if result is None:
            return []
        results = [Content(i) for i in result['items']]
        return results

    async def get_single_content(self, id):
        result = await self.api(f'/items/{id}')
        if result is None:
            return None
        return Content(result['item'])

    async def get_bookmark_folders(self):
        result = await self.api(f'/bookmarks')
        if result is None:
            return None
        return [Folder(i) for i in result['items']]

    async def create_bookmark_folder(self, name: str = 'Мои закладки'):
        req = {'title': name}
        result = await self.api(f'/bookmarks/create', req, method='POST')

    async def get_content_folders(self, content_id):
        req = {'item': content_id}
        result = await self.api(f'/bookmarks/get-item-folders', req)
        if result is None:
            return None
        return [Folder(i) for i in result['folders']]

    async def get_bookmark_folder(self, folder_id, page=1):
        result = await self.api(f'/bookmarks/{folder_id}', {'page': page})
        if result is None:
            return None
        try:
            current_page = result['pagination']['current']
            if page > current_page:
                return []
        except:
            pass
        return [Content(i) for i in result['items']]

    async def get_history(self, page=1):
        result = await self.api(f'/history', {'page': page})
        if result is None:
            return None
        return [Content(i['item'], Media(i['media'])) for i in result['history']]

    async def get_watching(self, subscribed=0):
        result = await self.api(f'/watching/serials', {'subscribed': subscribed})
        if result is None:
            return None
        return [Content(i) for i in result['items']]

    async def get_tv(self):
        result = await self.api(f'/tv')
        if result is None:
            return None
        return [Channel(i) for i in result['channels']]

    async def get_collections(self, page, sort=None):
        params = {'page': page}
        if sort is not None:
            params['sort'] = sort
        result = await self.api('/collections', params=params)
        if result is None:
            return None
        return [Collection(i) for i in result['items']]

    async def get_single_collection(self, collection_id):
        result = await self.api('/collections/view', params={'id': collection_id})
        if result is None:
            return None
        return [Content(i) for i in result['items']]

    async def notify(self, device_id):
        await self.api(f'/device/notify', {'title': "KP-MSX", 'hardware': LENNY, 'software': device_id}, method='POST')

    async def toggle_watched(self, content_id, season=None, episode=None):
        params = {'id': content_id}
        if season is not None:
            params['season'] = season
        if episode is not None:
            params['video'] = episode
        await self.api(f'/watching/toggle', params)

    async def toggle_subscription(self, content_id):
        await self.api('/watching/togglewatchlist', {'id': content_id})

    async def toggle_bookmark(self, content_id, folder_id):
        await self.api('/bookmarks/toggle-item', {'item': content_id, 'folder': folder_id}, method='POST')

    async def get_current_device_info(self):
        data = await self.api('/device/info')
        from models.Device import Device
        return Device(data.get('device', {}))

    FOURK_SETTING = 'support4k'
    HEVC_SETTING = 'supportHevc'
    HDR_SETTING = 'supportHdr'
    MIXED_PLAYLIST_SETTING = 'mixedPlaylist'
    SERVER_LOCATION_SETTING = 'serverLocation'

    async def update_device_setting(self, device_id: int, name: str, value: 'bool | int'):
        await self.api(f'/device/{device_id}/settings', {name: value}, 'POST')

    @staticmethod
    async def get_codes():
        params = {
            'grant_type': 'device_code',
            'client_id': config.KP_CLIENT_ID,
            'client_secret': config.KP_CLIENT_SECRET
        }
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as s:
            response = await s.post(f'{config.KP_API_DOMAIN}/oauth2/device', params=params)
            result = await response.json()
            return result['user_code'], result['code']

    @staticmethod
    async def check_registration(code):
        params = {
            'grant_type': 'device_token',
            'client_id': config.KP_CLIENT_ID,
            'client_secret': config.KP_CLIENT_SECRET,
            'code': code
        }
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as s:
            response = await s.post(f'{config.KP_API_DOMAIN}/oauth2/device', params=params)
            result = await response.json()
            if result.get('error') is not None:
                return None
            return result

    async def refresh_tokens(self):
        params = {
            'grant_type': 'refresh_token',
            'client_id': config.KP_CLIENT_ID,
            'client_secret': config.KP_CLIENT_SECRET,
            'refresh_token': self.refresh
        }
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as s:
            response = await s.post(f'{config.KP_API_DOMAIN}/oauth2/device', params=params)
            result = await response.json()
            if result.get('error') is not None:
                return False

            db.update_tokens(self.token, result['access_token'], result['refresh_token'])
            self.token = result['access_token']
            self.refresh = result['refresh_token']

            return True

    async def get_available_servers(self):
        result = await self.api('/references/server-location')
        return [Reference(i) for i in result.get('items', [])]

