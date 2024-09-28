import config
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

        self.watched = data.get('watched') == 1

        self.subtitle_tracks = dict()

        if (videos := data.get('videos')) is not None:
            self.poster = (data.get('posters') or {}).get('big')

            video_entry = None

            for _video in videos:
                if len(_video['files']) > 0:
                    video_entry = _video
                    break

            video_files = None
            if config.QUALITY is not None:
                video_files = [i for i in video_entry['files'] if i['quality'] == config.QUALITY]
                if len(video_files) == 0:
                    video_files = None
                else:
                    video_files = video_files[0]

            if video_files is None:
                video_files = sorted(video_entry['files'], key=lambda x: x.get('quality_id'))[-1]

            self.video = video_files['url'][config.PROTOCOL]

            if config.PROTOCOL == 'http':
                for subtitle_track in video_entry['subtitles']:
                    language = subtitle_track.get('lang')
                    self.subtitle_tracks[f'html5x:subtitle:{language}:{language}'] = subtitle_track['url']

        self.seasons = None

        if (seasons := data.get('seasons')) is not None:
            self.poster = (data.get('posters') or {}).get('big')
            self.seasons = [Season(i, self.id) for i in seasons]

    def msx_path(self):
        return f'/content?id={{ID}}&content_id={self.id}'

    def to_msx(self):
        return {
            'title': self.title,
            'image': self.poster,
            "action": f"panel:{config.MSX_HOST}/msx/content?id={{ID}}&content_id={self.id}"
        }

    def msx_action(self):
        if self.video is not None:
            return f"[video:plugin:{config.PLAYER}?url={self.video}|execute:{config.MSX_HOST}/msx/play?content_id={self.id}&id={{ID}}]"
        if self.seasons is not None:
            return f"panel:{config.MSX_HOST}/msx/seasons?id={{ID}}&content_id={self.id}"

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
                        #"headline": self.title,
                        "text": self.plot
                    },
                    {
                        "type": "button",
                        "layout": "4,5,4,1",
                        "label": "Смотреть",
                        'focus': True,
                        'action': self.msx_action(),
                        #'properties': self.subtitle_tracks
                    }
                ]
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
                "action": f'panel:{config.MSX_HOST}/msx/episodes?id={{ID}}&content_id={self.id}&season={season.n}',
                'focus': focus,
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
            "pages": season.to_episode_pages()
        }
        return entry

    def to_player_opts(self, season=None, episode=None):
        acts = []
        if self.seasons is None:
            acts += MSX.player_update_title(self.title)
            #acts += MSX.player_commit(self.subtitle_tracks)
        else:
            for _season in self.seasons:
                if _season.n != int(season):
                    continue
                for _episode in _season.episodes:
                    if _episode.n == int(episode):
                        break
                break
            acts += _season.to_msx_player_update_actions(episode)
            acts += MSX.player_update_title(_episode.player_title())
            #acts += MSX.player_commit(_episode.subtitle_tracks)
        return acts
