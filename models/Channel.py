from urllib.parse import urlencode

import config
from models.DeviceSettings import DeviceSettings
from util.proxy import make_proxy_url


class Channel:

    def __init__(self, data):
        self.id = data.get('id')
        self.title = data.get('title')
        self.name = data.get('name')
        logos = data.get('logos') or {}
        self.logo = logos.get('l') or logos.get('m') or logos.get('s')
        self.stream = data.get('stream')

    def to_msx(self, device_settings: 'DeviceSettings' = None):
        url = self.stream

        if device_settings is not None and device_settings.alternative_player:
            player = config.ALTERNATIVE_PLAYER
        else:
            player = config.PLAYER

        if config.TIZEN:
            action = f'video:{self.stream}'
        else:
            action = f"video:plugin:{player}?" + urlencode({'url': url})

        entry = {
            'title': self.title,
            'playerLabel': self.title,
            'image': self.logo,
            'imageFiller': 'width-center',
            "action": action
        }
        return entry
