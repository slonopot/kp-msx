class Episode:

    def __init__(self, data):
        self.n = data.get('number')
        self.title = data.get('title')
        self.video = data['files'][0]['url']['hls4']


class Season:

    def __init__(self, data):
        self.n = data.get('number')
        self.id = data.get('id')
        self.episodes = [Episode(i) for i in data.get('episodes')]