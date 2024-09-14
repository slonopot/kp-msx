from models.MSX import MSX
from models.Season import Season


class Content:

    def __init__(self, data):
        self.id = data.get('id')
        self.title = data.get('title')
        self.type = data.get('type')
        self.plot = data.get('plot')
        self.poster = (data.get('posters') or {}).get('medium')
        self.video = None
        if (videos := data.get('videos')) is not None:
            self.poster = (data.get('posters') or {}).get('big')
            self.video = videos[-1]['files'][0]['url']['hls4']
        if (seasons := data.get('seasons')) is not None:
            self.poster = (data.get('posters') or {}).get('big')
            self.seasons = [Season(i) for i in seasons]

    def msx_path(self):
        #return f'/{self.type}?id={{ID}}&content_id={self.id}'
        return f'/content?id={{ID}}&content_id={self.id}'

    def to_msx(self):
        return {
            'title': self.title,
            'image': self.poster,
            #"action": f"panel:{MSX.HOST}/msx{self.msx_path()}"
            "action": f"panel:{MSX.HOST}/msx/content?id={{ID}}&content_id={self.id}"
        }

    def msx_action(self):
        if self.video is not None:
            return f"video:plugin:https://slonopot.github.io/msx-hlsx/hlsx.html?url={self.video}"
            #return f'video:resolve:request:interaction:{self.video}@http://msx.benzac.de/interaction/play.html'
        if self.seasons is not None:
            return f"panel:{MSX.HOST}/msx/seasons?id={{ID}}&content_id={self.id}"

    def to_msx_panel(self):
        return {
            "type": "pages",
            "headline": self.title,
            "pages": [{
                "items": [
                    {
                        "type": "teaser",
                        "layout": "0,0,4,6",
                        "image": self.poster,
                        "imageFiller": "height-left"
                    },
                    {
                        "type": "default",
                        "layout": "4,0,4,5",
                        "headline": self.title,
                        "text": self.plot
                    },
                    {
                        "type": "button",
                        "layout": "4,5,4,1",
                        "label": "Смотреть",
                        'focus': True,
                        "action": self.msx_action(),
                        "playerLabel": self.title,
                        "properties": {
                            "button:restart:icon": "settings",
                            "button:restart:action": "panel:request:player:options"
                        }
                    }]
            }]
        }

    def to_seasons_msx_panel(self):
        entry = {
            "type": "pages",
            "headline": self.title,
            "pages": []
        }
        items = []
        focus = True
        for season in self.seasons:
            items.append({
                    "type": "button",
                    "layout": f"{(season.n - 1) % 24 // 6 * 2},{(season.n - 1) % 6},2,1",
                    "label": f"Cезон {season.n}",
                    "action": f'panel:{MSX.HOST}/msx/episodes?id={{ID}}&content_id={self.id}&season={season.n}',
                    'focus': focus
                })
            focus = False
            if len(items) == 24:
                entry['pages'].append({'items': items})
                items = []
                focus = True
        if len(items) > 0:
            entry['pages'].append({'items': items})
        return entry

    def to_episodes_msx_panel(self, season_number):
        for season in self.seasons:
            if season.n == season_number:
                break
        entry = {
            "type": "pages",
            "headline": self.title,
            "pages": []
        }
        items = []
        focus = True
        for episode in season.episodes:
            items.append({
                "type": "button",
                "layout": f"0,{(episode.n - 1) % 6},8,1",
                "label": f"{episode.n}. {episode.title}",
                "action": f'video:plugin:http://msx.benzac.de/plugins/html5x.html?url={episode.video}',
                'focus': focus,
                "playerLabel": f'[S{season.n}/E{episode.n}] {self.title}',
                "properties": {
                    "button:restart:icon": "settings",
                    "button:restart:action": "panel:request:player:options"
                }
            })
            focus = False
            if len(items) == 6:
                entry['pages'].append({'items': items})
                items = []
        if len(items) > 0:
            entry['pages'].append({'items': items})
        return entry
