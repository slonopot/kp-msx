from models.MSX import MSX


class Category:

    def __init__(self, data):
        self.id = data.get('id')
        self.title = data.get('title')

    def to_msx(self):
        return {
            "type": "default",
            "label": self.title,
            #"data": f"{MSX.HOST}/msx/category?id={{ID}}&category={self.id}"
            "data": f"request:interaction:{MSX.HOST}/msx/category?id={{ID}}&category={self.id}&offset={{OFFSET}}&limit={{LIMIT}}|20@http://msx.benzac.de/interaction/paging.html"
        }