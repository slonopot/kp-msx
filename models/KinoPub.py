import aiohttp

import config
from models.Category import Category
from models.Content import Content
from models.Folder import Folder
from util import db


class KinoPub:

    def __init__(self, token, refresh):
        self.token = token
        self.refresh = refresh

    async def api(self, path, params=None):
        headers = {'Authorization': 'Bearer ' + self.token}
        async with aiohttp.ClientSession(headers=headers) as s:
            response = await s.get(f'https://api.service-kp.com/v1{path}', params=params)
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
            return []
        return [Category(i) for i in result['items']]

    async def get_content(self, category, page=1, extra=None):
        path = '/items'
        if extra is not None:
            path += f'/{extra}'
        result = await self.api(path, params={'type': category, 'page': page})
        if result is None:
            return []
        results = [Content(i) for i in result['items']]
        return results

    async def search(self, query):
        result = await self.api('/items/search', params={'q': query})
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

    async def get_bookmark_folder(self, id, page=1):
        result = await self.api(f'/bookmarks/{id}', {'page': page})
        if result is None:
            return None
        return [Content(i) for i in result['items']]

    async def notify(self):
        pass

    @staticmethod
    async def get_codes():
        params = {
            'grant_type': 'device_code',
            'client_id': config.KP_CLIENT_ID,
            'client_secret': config.KP_CLIENT_SECRET
        }
        async with aiohttp.ClientSession() as s:
            response = await s.post('https://api.service-kp.com/oauth2/device', params=params)
            result = await response.json()
            return result['user_code'], result['code']

    @staticmethod
    async def check_registration(code):
        params = {
            'grant_type': 'device_token',
            'client_id': 'xbmc',
            'client_secret': 'cgg3gtifu46urtfp2zp1nqtba0k2ezxh',
            'code': code
        }
        async with aiohttp.ClientSession() as s:
            response = await s.post('https://api.service-kp.com/oauth2/device', params=params)
            result = await response.json()
            if result.get('error') is not None:
                return None
            return result

    async def refresh_tokens(self):
        params = {
            'grant_type': 'refresh_token',
            'client_id': 'xbmc',
            'client_secret': 'cgg3gtifu46urtfp2zp1nqtba0k2ezxh',
            'refresh_token': self.refresh
        }
        async with aiohttp.ClientSession() as s:
            response = await s.post('https://api.service-kp.com/oauth2/device', params=params)
            result = await response.json()
            if result.get('error') is not None:
                return False

            db.update_tokens(self.token, result['access_token'], result['refresh_token'])
            self.token = result['access_token']
            self.refresh = result['refresh_token']

            return True



