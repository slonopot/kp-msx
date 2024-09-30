import config
from models.MSX import MSX


class Category:

    BLACKLIST = '4k'

    def __init__(self, data):
        self.id = data.get('id')
        self.title = data.get('title')
        self.blacklisted = self.id in Category.BLACKLIST

    def to_msx(self):
        return {
            "type": "default",
            "label": self.title,
            "data": f"request:interaction:{config.MSX_HOST}/msx/category?id={{ID}}&category={self.id}&offset={{OFFSET}}&limit={{LIMIT}}|20@http://msx.benzac.de/interaction/paging.html"
        }