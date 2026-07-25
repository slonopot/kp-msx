from models.DeviceSettings import DeviceSettings
from models.Folder import Folder
from models.Poster import Poster
from models.Season import Season
from models.Video import Video
from util import msx


class Content:

    def __init__(self, data, media=None):
        self.media = media

        self.id = data.get('id')
        self.title = data.get('title')
        self.type = data.get('type')
        self.plot = data.get('plot')
        self.voice = data.get('voice')
        self.cast = data.get('cast')
        self.director = data.get('director')
        self.year = data.get('year')
        self.subscribed = data.get('subscribed')
        self.imdb = data.get('imdb')

        #if self.voice:
        #    self.plot += f'\n\nОзвучки: {self.voice}'
        #if self.cast:
        #    self.plot += f'\n\nВ ролях: {self.cast}'

        self.poster = Poster((data.get('posters') or {}))

        self.rating = data.get('imdb_rating') or data.get('kinopoisk_rating')
        self.is_4k = data.get('quality') == 2160

        self.bookmarks = data.get('bookmarks')
        if self.bookmarks is not None and isinstance(self.bookmarks, list):
            self.bookmarks = [Folder(i).id for i in self.bookmarks]

        self.watched = data.get('watched') == 1

        self.videos = None

        if (videos := data.get('videos')) is not None:
           self.videos = [Video(i, self.id, self.title) for i in videos]

        self.seasons = None

        if (seasons := data.get('seasons')) is not None:
            self.seasons = [Season(i, self.id) for i in seasons]

        self.new_episodes = data.get('new')

        self.trailer = (data.get('trailer') or {}).get('url')

    def update_bookmarks(self, folders):
        self.bookmarks = [i.id for i in folders]

    def to_msx(self, device_settings: 'DeviceSettings' = None):
        entry = {
            'title': self.title,
            'image': self.poster.get(device_settings=device_settings),
            #"action": msx.format_action('/msx/content', params={'content_id': self.id}, module='panel')
            "action": msx.format_action('/msx/content', params={'content_id': self.id}, module='content')
        }
        if self.media is not None and self.media.season > 0:
            entry['titleFooter'] = self.media.to_subtitle()
        else:
            entry['titleFooter'] = ''
            if self.rating:
                entry['titleFooter'] += f' {{ico:stars}} {self.rating}'
            if self.year:
                entry['titleFooter'] += f' {{ico:calendar-month}} {self.year}'
            if self.new_episodes is not None:
                entry['titleFooter'] += f' {{ico:new-releases}} {self.new_episodes}'
            if self.is_4k:
                entry['titleFooter'] += f' {{ico:4k}}'

            entry['titleFooter'] = entry['titleFooter'].strip()
        return entry

    def msx_action(self, device_settings: 'DeviceSettings' = None):
        if self.videos is not None:
            if len(self.videos) == 1:
                return self.videos[0].msx_action(device_settings=device_settings)
            else:
                return msx.format_action('/msx/multivideo', params={'content_id': self.id}, module='panel')
        if self.seasons is not None:
            return msx.format_action('/msx/seasons', params={'content_id': self.id}, module='panel')

    SUBSCRIPTION_BUTTON_ID = "subscription_button"
    BOOKMARK_BUTTON_ID = "bookmark_button"
    WATCH_BUTTON_ID = "watch_button"
    TRAILER_BUTTON_ID = "trailer_button"

    def to_subscription_button(self, in_content=False):
        if self.subscribed:
            label = "{ico:msx-yellow:new-releases}"
        else:
            label = "{ico:msx-white:new-releases}"
        button = {
            "id": self.SUBSCRIPTION_BUTTON_ID,
            "type": "button",
            "layout": f"6,5,1,1" if not in_content else f"10,5,1,1",
            "label": label,
            'action': msx.format_action('/msx/toggle_subscription', params={'content_id': self.id}, module='execute'),
        }

        return button

    def to_bookmark_button(self, in_content=False):
        if self.in_bookmarks():
            label = "{ico:msx-yellow:bookmark}"
        else:
            label = "{ico:msx-white:bookmark}"

        button = {
            "id": self.BOOKMARK_BUTTON_ID,
            "type": "button",
            "layout": f"7,5,1,1" if not in_content else f"11,5,1,1",
            "label": label,
            'action': msx.format_action('/msx/content/bookmarks', params={'content_id': self.id}, module='panel')
        }

        return button


    def to_trailer_button(self, qty=0, device_settings: 'DeviceSettings' = None, in_content=False):
        props = {
            'trigger:background': 'player:button:eject:execute'
        }

        props.update(msx.DEFAULT_PLAY_BUTTON_PROPS)

        button = {
            "id": self.TRAILER_BUTTON_ID,
            "type": "button",
            "layout": f"{7-qty},5,1,1" if not in_content else f"6,5,1,1",
            "label": '{ico:msx-white:movie}',
            "playerLabel": f'Трейлер {self.title}',
            'properties': props,
            'action': msx.play_action(self.trailer, device_settings=device_settings, disable_proxy=True),
        }

        return button

    def to_msx_panel(self, device_settings: 'DeviceSettings' = None):

        buttons = [self.to_bookmark_button()]

        if self.seasons:
            buttons.append(self.to_subscription_button())

        if self.trailer:
            buttons.append(self.to_trailer_button(len(buttons), device_settings=device_settings))

        watch_button = {
            "id": self.WATCH_BUTTON_ID,
            "type": "button",
            "layout": f"4,5,{4-len(buttons)},1",
            "label": "Смотреть" if len(buttons) <= 2 else "{ico:msx-white:play-circle-outline}",
            "playerLabel": self.title,
            'focus': True,
            'action': self.msx_action(device_settings=device_settings),
        }

        if self.videos is not None and len(self.videos) == 1:
            watch_button['properties'] = self.videos[0].msx_properties(device_settings=device_settings)

        buttons = [watch_button] + buttons

        stamp = ''
        if self.rating:
            stamp += f' {{ico:stars}} {self.rating}'
        if self.year:
            stamp += f' {{ico:calendar-month}} {self.year}'
        if self.is_4k:
            stamp += f' {{ico:4k}}'

        stamp = stamp.strip()
        if len(stamp) == 0:
            stamp = None

        return {
            "type": "pages",
            "headline": self.title,
            "pages": [
                {
                    "items": [
                        {
                            'id': 'teaser',
                            "type": "teaser",
                            "layout": "0,0,4,6",
                            "image": self.poster.get(device_settings=device_settings),
                            "imageFiller": "height-left",
                            'action': 'focus:plot',
                            'stamp': stamp
                        },
                        {
                            "type": "default",
                            "layout": "4,0,4,5",
                            "text": self.plot,
                            'action': 'focus:plot'
                        }
                    ] + buttons
                }, {
                    'items': [
                        {
                            'id': 'plot',
                            "type": "default",
                            "layout": "0,0,8,6",
                            "text": self.plot,
                            'action': 'focus:teaser'
                        }
                    ]
                }
            ]

        }

    def to_msx_content(self, device_settings: 'DeviceSettings' = None,):

        buttons = [self.to_bookmark_button(in_content=True)]

        if self.seasons:
            buttons.append(self.to_subscription_button(in_content=True))

        if self.trailer:
            buttons.append(self.to_trailer_button(in_content=True, device_settings=device_settings))

        watch_button = {
            "id": self.WATCH_BUTTON_ID,
            "type": "button",
            "layout": f"4,5,2,1",
            "label": "Смотреть",
            "playerLabel": self.title,
            'focus': True,
            'action': self.msx_action(device_settings=device_settings),
        }

        if self.videos is not None and len(self.videos) == 1:
            watch_button['properties'] = self.videos[0].msx_properties(device_settings=device_settings)

        buttons = [watch_button] + buttons

        stamp = ''
        if self.rating:
            stamp += f' {{ico:stars}} {self.rating}'
        if self.year:
            stamp += f' {{ico:calendar-month}} {self.year}'
        if self.is_4k:
            stamp += f' {{ico:4k}}'

        stamp = stamp.strip()
        if len(stamp) == 0:
            stamp = None

        pages = [
            {
                "items": [
                    {
                        "type": "space",
                        "layout": "0,0,4,6",
                        "image": self.poster.get(device_settings=device_settings),
                        "imageFiller": "height-left",
                        'stamp': stamp
                    },
                    {
                        "type": "space",
                        "layout": "4,0,8,5",
                        "text": self.plot,
                    }
                ] + buttons
            }
        ]

        def section_title(title):
            return {
                'layout': '0,0,3,1',
                'enumerate': False,
                'type': "space",
                'title': title,
                'alignment': 'right',
                'centration': 'title',
                'color': 'transparent'
            }

        def action_button(i, title, field):
            x = (i + 1) % 4
            y = (i + 1) // 4
            return {
                'type': 'button',
                'layout': f'{x*3},{y},3,1',
                'enumerate': False,
                'label': title,
                'action': msx.format_action('/msx/search/content', params={'q': title, 'field': field, 'page': '{PAGE}'}, interaction='/paging.html', module='content'),
             }


        if self.director is not None and self.director != '':
            items = [section_title('Режиссер')]
            items += [action_button(i, val.strip(), 'director') for i, val in enumerate(self.director.split(',')[:23])]
            pages.append({'items': items})

        if self.cast is not None and self.cast != '':
            items = [section_title('В ролях')]
            items += [action_button(i, val.strip(), 'cast') for i, val in enumerate(self.cast.split(',')[:23])]
            pages.append({'items': items})

        return {
            "type": "list",
            "headline": self.title,
            "pages": pages
        }


    def to_seasons_msx_panel(self):
        entry = {
            "type": "list",
            "headline": self.title,
            "template": {
                'enumerate': False,
                "type": "button",
                'layout': "0,0,2,1",
                'stampColor': 'msx-glass',
            },
            "items": []
        }

        for season in self.seasons:
            entry['items'].append({
                "label": f"Cезон {season.n}",
                'stamp': '{ico:check}' if season.watched else None,
                'focus': not season.watched,
                "action": msx.format_action('/msx/episodes', params={'content_id': self.id, 'season': season.n}, module='panel')
            })
        return entry

    def to_multivideo_msx_panel(self, device_settings: 'DeviceSettings' = None):
        entry = {
            "type": "list",
            "headline": self.title,
            'template': {
                'enumerate': False,
                "type": "button",
                "layout": f"0,0,8,1",
                'stampColor': 'msx-glass',
                'playerLabel': self.title,
            },
            "items": [i.to_multivideo_entry(device_settings=device_settings) for i in self.videos]
        }
        return entry

    def to_episodes_msx_panel(self, season_number, device_settings: 'DeviceSettings' = None) -> dict:
        for season in self.seasons:
            if season.n == season_number:
                break
        entry = {
            "type": "list",
            "headline": f'{self.title} [S{season.n}]',
            'template': {
                "type": "button",
                "layout": f"0,0,8,1",
                'stampColor': 'msx-glass',
            },
            "items": season.to_episode_pages(device_settings=device_settings)
        }
        return entry

    def in_bookmarks(self):
        return self.bookmarks is not None and len(self.bookmarks) > 0

    def to_bookmark_stamp(self, folder_id):
        return {
            'stampColor': 'msx-glass' if folder_id in self.bookmarks else 'transparent',
            'stamp': '{ico:check}' if folder_id in self.bookmarks else '{ico:blank}'
        }

    def to_bookmarks_msx_panel(self, folders: 'list[Folder]'):
        entry = {
            "type": "list",
            "headline": 'Закладки',
            "template": {
                'enumerate': False,
                "type": "button",
                'layout': "0,0,4,1",
            },
            "items": []
        }
        for folder in folders:
            subentry = {
                "id": str(folder.id),
                "label": folder.title,
                "action": msx.format_action('/msx/toggle_bookmark', params={'content_id': self.id, 'folder_id': folder.id}, module='execute')
            }
            subentry.update(self.to_bookmark_stamp(folder.id))
            entry['items'].append(subentry)
        return entry

