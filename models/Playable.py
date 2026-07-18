from urllib.parse import urlencode

import config
from models.SubtitleTrack import SubtitleTrack
from util import msx
from util.proxy import make_proxy_url


class Playable:

    def __init__(self, data):
        self.title = data.get('title')
        self.video_url = Playable._extract_video_url(data)
        self.subtitles = [SubtitleTrack(s) for s in data.get('subtitles', [])]

    @staticmethod
    def _extract_video_url(data):
        video_files = None
        if config.QUALITY is not None:
            video_files = [i for i in data.get('files', []) if i['quality'] == config.QUALITY]
            video_files = video_files[0] if video_files else None

        if video_files is None:
            files = data.get('files', [])
            if files:
                video_files = sorted(files, key=lambda x: x.get('quality_id'))[-1]

        if video_files:
            return video_files['url'][config.PROTOCOL]
        return None

    def msx_action(self, device_settings: 'DeviceSettings' = None):
        if not self.video_url:
            return "warn:Почему-то нет видео"

        return msx.play_action(self.video_url, device_settings=device_settings)

    def msx_properties(self, device_settings: 'DeviceSettings' = None):
        props = {
            'resume:key': self.resume_key(),
            'trigger:ready': self.trigger_ready()
        }

        props.update(msx.DEFAULT_PLAY_BUTTON_PROPS)

        if device_settings is not None and device_settings.alternative_player:
            for track in self.subtitles:
                props.update({f'html5x:subtitle:{track.lang}:{track.lang.upper()}': track.url})

        return props
