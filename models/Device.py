from models.DeviceSettings import DeviceSettings
from models.KinoPub import KinoPub
from util import db


class Device:

    def __init__(self, data):
        self.id = data.get('id')
        self.code = data.get('code')
        self.token = data.get('token')
        self.refresh = data.get('refresh')
        self.settings = DeviceSettings(data.get('settings'))
        self.user_agent = data.get('user_agent')
        self.kp = KinoPub(self.token, self.refresh, self.user_agent)

    def registered(self):
        if self.token is not None:
            return True
        return False

    @classmethod
    def by_id(cls, device_id):
        entry = db.get_device_by_id(device_id)
        if entry is None:
            return None
        return cls(entry)

    @classmethod
    def create(cls, device_id):
        entry = {
            'id': device_id
        }
        db.create_device(entry)
        return cls(entry)

    def update_code(self, code):
        db.update_device_code(self.id, code)

    def update_tokens(self, token, refresh):
        db.update_device_tokens(self.id, token, refresh)
        self.token = token
        self.refresh = refresh
        self.kp = KinoPub(token, refresh)

    def update_settings(self):
        db.update_device_settings(self.id, self.settings.to_dict())

    async def notify(self):
        await self.kp.notify(self.id)

    def delete(self):
        db.delete_device(self.id)

    async def toggle_4k(self):
        self.settings.fourk = not self.settings.fourk
        device_info = await self.kp.get_current_device_info()
        await self.kp.update_device_setting(device_info.id, KinoPub.FOURK_SETTING, self.settings.fourk)
        self.update_settings()

    async def toggle_hdr(self):
        self.settings.hdr = not self.settings.hdr
        device_info = await self.kp.get_current_device_info()
        await self.kp.update_device_setting(device_info.id, KinoPub.HDR_SETTING, self.settings.hdr)
        self.update_settings()

    async def toggle_hevc(self):
        self.settings.hevc = not self.settings.hevc
        device_info = await self.kp.get_current_device_info()
        await self.kp.update_device_setting(device_info.id, KinoPub.HEVC_SETTING, self.settings.hevc)
        self.update_settings()

    async def toggle_mixed_playlist(self):
        self.settings.mixed_playlist = not self.settings.mixed_playlist
        device_info = await self.kp.get_current_device_info()
        await self.kp.update_device_setting(device_info.id, KinoPub.MIXED_PLAYLIST_SETTING, self.settings.mixed_playlist)
        self.update_settings()

    async def toggle_proxy(self):
        self.settings.proxy = not self.settings.proxy
        self.update_settings()

    async def toggle_alternative_player(self):
        self.settings.alternative_player = not self.settings.alternative_player
        self.update_settings()

    async def toggle_server(self) -> str:
        device_info = await self.kp.get_current_device_info()
        available_servers = await self.kp.get_available_servers()

        new_server = available_servers[0]
        for i, server in enumerate(available_servers):
            if server.name == self.settings.server and i+1 != len(available_servers):
                new_server = available_servers[i+1]
                break

        await self.kp.update_device_setting(device_info.id, KinoPub.SERVER_LOCATION_SETTING, new_server.id)
        self.settings.server = new_server.name
        self.update_settings()

        return f'Сервер: {new_server.name}'

    def toggle_menu_entry(self, menu_entry):
        if menu_entry in self.settings.menu_blacklist:
            self.settings.menu_blacklist.remove(menu_entry)
        else:
            self.settings.menu_blacklist.append(menu_entry)
        self.update_settings()
        return not menu_entry in self.settings.menu_blacklist

    def set_poster_settings(self, poster_size, poster_proxy):
        self.settings.poster_size = poster_size
        self.settings.poster_proxy = poster_proxy
        self.update_settings()

    def reset_menu(self):
        self.settings.menu_blacklist = []
        self.update_settings()

    def update_user_agent(self, user_agent):
        db.update_device_user_agent(self.id, user_agent)

    def set_real_ip(self, real_ip):
        self.kp.real_ip = real_ip