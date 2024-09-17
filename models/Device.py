from models.KinoPub import KinoPub
from util import db


class Device:

    def __init__(self, data):
        self.id = data.get('id')
        self.code = data.get('code')
        self.token = data.get('token')
        self.refresh = data.get('refresh')
        self.kp = KinoPub(self.token, self.refresh)

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

    async def notify(self):
        await self.kp.notify(self.id)

    def delete(self):
        db.delete_device(self.id)
