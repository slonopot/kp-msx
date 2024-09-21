import config


class Episode:

    def __init__(self, data):
        self.n = data.get('number')
        self.title = data.get('title')
        self.subtitle_tracks = {}

        video_files = None
        if config.QUALITY is not None:
            video_files = [i for i in data['files'] if i['quality'] == config.QUALITY]
            if len(video_files) == 0:
                video_files = None
            else:
                video_files = video_files[0]

        if video_files is None:
            video_files = sorted(data['files'], key=lambda x: x.get('quality_id'))[-1]

        self.video = video_files['url'][config.PROTOCOL]

        if config.PROTOCOL == 'http':
            for subtitle_track in data['subtitles']:
                language = subtitle_track.get('lang')
                self.subtitle_tracks[f'html5x:subtitle:{language}:{language}'] = subtitle_track['url']


class Season:

    def __init__(self, data):
        self.n = data.get('number')
        self.id = data.get('id')
        self.episodes = [Episode(i) for i in data.get('episodes')]