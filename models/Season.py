import config
from models.Episode import Episode
from models.MSX import MSX


class Season:

    def __init__(self, data, content_id):
        self.content_id = content_id

        self.n = data.get('number')
        self.id = data.get('id')
        self.episodes = [Episode(i, content_id, self.n) for i in data.get('episodes')]

    def to_episode_pages(self):
        items = []
        for i, episode in enumerate(self.episodes):
            entry = {
                "label": episode.menu_title(),
                'action': episode.msx_action(),
                'stamp': '{ico:check}' if episode.watched else None,
                #'properties': episode.subtitle_tracks
            }
            items.append(entry)
        return items

    def to_msx_player_update_actions(self, episode=0):
        episode = int(episode) - 1
        acts = []
        acts += MSX.player_update_button('content', 'list-alt',  f'panel:{config.MSX_HOST}/msx/episodes?id={{ID}}&content_id={self.content_id}&season={self.n}')

        if episode != 0:
            acts += MSX.player_update_button('prev', 'skip-previous', self.episodes[episode - 1].msx_action())
        if episode + 1 < len(self.episodes):
            acts += MSX.player_update_button('next', 'skip-next', self.episodes[episode + 1].msx_action())

        return acts
