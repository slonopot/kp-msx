import config


class Folder:

    def __init__(self, data):
        self.id = data.get('id')
        self.title = data.get('title')

    def to_msx(self):
        return {
            "type": "default",
            "label": self.title,
            "action": f"content:request:interaction:{config.MSX_HOST}/msx/folder?id={{ID}}&folder={self.id}&offset={{OFFSET}}&limit={{LIMIT}}|20@http://msx.benzac.de/interaction/paging.html"
        }
