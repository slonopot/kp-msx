import config
from urllib.parse import urlencode


class Episode:

    # TODO: Merge with Content?

    def __init__(self, data):
        self.n = data.get('number')
        self.title = data.get('title')

        self.watched = data.get('watched') == 1

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

    def menu_title(self):
        result = f'{self.n}. {self.title}'
        if self.watched:
            result += ' 📺'
        return result

    def player_title(self, season):
        return f'[S{season}/E{self.n}] {self.title}'


class Season:

    def __init__(self, data):
        self.n = data.get('number')
        self.id = data.get('id')
        self.episodes = [Episode(i) for i in data.get('episodes')]

    def to_episode_pages(self, content_id=0):
        pages = []
        items = []
        focus = True
        for episode in self.episodes:
            entry = {
                "type": "button",
                "layout": f"0,{(episode.n - 1) % 6},8,1",
                "label": episode.menu_title(),
                'focus': focus,
            }

            opts = {
                "playerLabel": episode.player_title(self.n),
                "properties": {
                    "button:content:icon": "list-alt",
                    "button:content:action": f'panel:{config.MSX_HOST}/msx/episodes?id={{ID}}&content_id={content_id}&season={self.n}',
                    "button:restart:icon": "settings",
                    "button:restart:action": "panel:request:player:options"
                } | episode.subtitle_tracks
            }

            if episode.watched:
                entry.update({"action": f'video:plugin:{config.PLAYER}?url={episode.video}'} | opts)
            else:
                params = {
                    'content_id': content_id,
                    'season': self.n,
                    'episode': episode.n
                }
                entry.update({
                    "action": f'[video:plugin:{config.PLAYER}?url={episode.video}|execute:{config.MSX_HOST}/msx/toggle_watched?{urlencode(params)}&id={{ID}}]',
                    'data': opts
                })
            items.append(entry)
            focus = False
            if len(items) == 6:
                pages.append({'items': items})
                items = []
        if len(items) > 0:
            pages.append({'items': items})
        return pages
