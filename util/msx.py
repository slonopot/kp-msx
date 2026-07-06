from urllib.parse import urlencode
import config
from config import ALTERNATIVE_PLAYER
from models.DeviceSettings import DeviceSettings
from util.proxy import make_proxy_url

LENNY =  "¯\\_(ツ)_/¯"
SAD_LENNY = "(◡︵◡)"


def format_action(path: str, params: dict = None, interaction: str = None, options: str = None, module: str = None):
    if params is None:
        params = {}
    params.update({'id': '{ID}'})

    if path.startswith('/'):
        data = f'{config.MSX_HOST}{path}'
    else:
        data = path

    data = data + '?' + urlencode(params, safe='{}')

    if interaction:

        if interaction.startswith('/'):
            interaction = f'{config.MSX_HOST}{interaction}'

        data = 'request:interaction:' + data
        if options:
            data = data + '|' + options
        data = data + '@' + interaction

    if module:
        data = module + ':' + data

    return data


def start():
    return {
        'name': 'kino.watch',
        'version': '6.6.6',
        'parameter': format_action('/msx/menu', module='menu'),
        'welcome': 'none',
        'launcher': {
            "parameter": format_action('/msx/menu', module='menu'),
            "icon": "movie-filter",
            "image": "none",
            "color": "none"
        }
    }


def unregistered_menu():
    return {
        "reuse": False,
        "cache": False,
        "restore": False,
        "headline": "kino.watch",
        "menu": [
            {
                "icon": "vpn-key",
                "label": "Регистрация",
                "data": format_action('/msx/registration')
            }
        ],
    }


def registered_menu(categories: 'List[Category]'):
    menu = [category.to_msx() for category in categories or [] if not category.blacklisted]
    if len(menu) == 0:
        menu = [sad_screen()]
    entry = {
        "reuse": False,
        "cache": False,
        "restore": False,
        "refocus": 1,
        "headline": "kino.watch",
        "options": settings_screen(),
        "menu": menu,
    }
    return entry

def sad_screen():
    return {
        "type": "default",
        "label": SAD_LENNY,
        "data": {
            "type": "pages",
            "headline": SAD_LENNY,
            "pages": [
                {
                    "items": [
                        {
                            "type": "space",
                            "layout": "0,0,6,2",
                            "title": 'Вот так вот',
                            "titleFooter": 'Вы выключили все разделы меню, поэтому теперь здесь ничего нет.'
                        },
                        {
                            "type": "button",
                            "layout": "0,2,6,1",
                            "label": "Вернуть назад",
                            "action": format_action('/msx/settings/reset_menu', module='execute')
                        }
                    ],
                }
            ]
        }
    }

def already_registered():
    return {
        "type": "list",
        "headline": "Template",
        "template": {
            "type": "separate",
            "layout": "0,0,2,4",
            "color": "msx-glass",
            "title": "Title",
        },
        "items": [{
            "title": "Уже зарегистрирован"
        }]
    }


def registration(user_code):
    return {
        "type": "pages",
        "headline": "Регистрация",
        "pages": [
            {
                "items": [
                    {
                        "type": "space",
                        "layout": "0,0,7,2",
                        "title": 'Что это',
                        "titleFooter": 'Это неофициальный киновотч для Media Station X. Не обращайтесь в поддержку по вопросам, связанным с этим приложением. При возникновении проблем с запуском видео или постерами откройте настройки и ознакомьтесь с пунктами.'
                    },
                    {
                        "type": "space",
                        "layout": "0,2,7,2",
                        "title": user_code,
                        "titleFooter": 'Используйте этот код для добавления устройства на kino.watch или зеркале, после ввода кода нажмите кнопку "Я ввел код".'
                    }, {
                        "type": "button",
                        "layout": "0,4,7,1",
                        "label": "Я ввёл код",
                        "action": format_action('/msx/check_registration', module='execute')
                    }
                ]
            }
        ]
    }


def code_not_entered():
    return {
        'response': {
            'status': 200,
            'data': {'action': 'warn:Код не введён. Если прошло больше 5 минут, перезапустите приложение для получения нового кода.'}
        }
    }


def restart():
    return {
        'response': {
            'status': 200,
            'data': {'action': 'reload'}
        }
    }


def content(entries, category, page, extra=None, decompress=None, device_settings: 'DeviceSettings' = None):
    resp = {
        "type": "list",
        "template": {
            "type": "separate",
            "layout": "0,0,2,4",
            "color": "msx-glass",
            "title": "Title"
        },
        "items": []
    }

    if decompress is not None:
        resp['template']['decompress'] = decompress

    if page == 1 and category is not None and extra is None:
        from models.CategoryExtra import CategoryExtra
        resp['header'] = {
            "items": [i.to_msx(category) for i in CategoryExtra.static_extras()]
        }
    for entry in entries:
        resp['items'].append(entry.to_msx(device_settings=device_settings))

    return resp


def collections(entries, device_settings: 'DeviceSettings' = None) -> dict:
    resp = {
        "type": "list",
        "template": {
            "type": "separate",
            "layout": "0,0,3,6",
            "color": "msx-glass",
            "title": "Title"
        },
        "items": []
    }

    for entry in entries:
        resp['items'].append(entry.to_msx(device_settings=device_settings))

    return resp


def bookmark_folders(result):
    return {
        "type": "list",
        "headline": "Закладки",
        "template": {
            "type": "separate",
            "layout": "0,0,4,1",
            "color": "msx-glass",
        },
        "items": [i.to_msx() for i in result]
    }


def genre_folders(category, result):
    return {
        "type": "list",
        "headline": "Жанры",
        "template": {
            "type": "separate",
            "layout": "0,0,4,1",
            "color": "msx-glass",
        },
        "items": [i.to_msx(category) for i in result]
    }


def update_panel(content_id, value):
    return {
        'response': {
            'status': 200,
            'data': {
                'action': f'update:panel:{content_id}',
                'data': value
            }
        }
    }


def empty_response():
    return {
        'response': {
            'status': 200,
            'data': {'action': '[]'}
        }
    }


def tv_channels(channels, device_settings: 'DeviceSettings' = None):
    resp = {
        "type": "list",
        'header': {
            'items': [
                {
                    'type': 'default',
                    'layout': '0,0,12,1',
                    "color": "msx-glass",
                    'headline': 'Спортивные каналы предоставляются в качестве бонуса и работают «как есть»',
                    'titleFooter': 'Для просмотра полноценного онлайн-ТВ с архивом рекомендуется использовать другие сервисы',
                    'action': '[]'
                }
            ]
        },
        "template": {
            "type": "separate",
            "layout": "0,0,2,3",
            "color": "msx-glass",
            "title": "Title",
            "properties": {
                'control:type': 'extended',
                "button:content:enable": "false",
                'button:restart:icon': 'settings',
                'button:restart:action': player_action_btn(),
                'progress:display': 'false'
            }
        },
        "items": [channel.to_msx(device_settings=device_settings) for channel in channels]
    }

    return resp


def handle_exception(error_page=False):
    msg = {
        "type": "space",
        "layout": "0,0,6,2",
        "title": 'Произошла ошибка загрузки',
        "titleFooter": 'Скорее всего, киновотч сейчас недоступен. Проверьте статус на kinopub.online и ожидайте ремонта.'
    }
    restart_app_btn = {
        "type": "button",
        "layout": "0,2,6,1",
        "label": "Перезапустить приложение",
        "action": f"reload"
    }
    reload_content_btn = {
        "type": "button",
        "layout": "0,3,6,1",
        "label": "Перезагрузить раздел",
        "action": f"reload:content"
    }
    reload_panel_btn = {
        "type": "button",
        "layout": "0,4,6,1",
        "label": "Перезагрузить окно",
        "action": f"reload:panel"
    }

    if error_page:
        items = [msg, restart_app_btn]
    else:
        items = [msg, restart_app_btn, reload_content_btn, reload_panel_btn]

    return {
        "menu": [{
            "label": LENNY,
            "data": format_action('/msx/error')
        }],
        "type": "pages",
        "headline": "Ошибка",
        "pages": [
            {
                "items": items
            }
        ]
    }


def unsupported_version():
    return {
        "menu": [{
            "label": LENNY,
            "data": format_action('/msx/too_old')
        }],
        "type": "pages",
        "headline": "Ошибка",
        "pages": [
            {
                "items": [
                    {
                        "type": "space",
                        "layout": "0,0,6,2",
                        "title": 'Старая версия MSX',
                        "titleFooter": 'Используемая версия MSX слишком старая. Выберите один из параметров ниже для обновления. При выборе версии web.msx.benzac.de используйте вариант HTTPS. После обновления настройте киновотч снова.'
                    }, {
                        "type": "button",
                        "layout": "0,2,6,1",
                        "label": "Параметр id:web",
                        "action": f"start",
                        "data": {
                            "name": "id:web",
                            "version": "2.0.3",
                            "parameter": "content:https://msx.benzac.de/services/web.php"
                        }
                    }, {
                        "type": "button",
                        "layout": "0,3,6,1",
                        "label": "Параметр web.msx.benzac.de",
                        "action": f"start",
                        "data": {
                            'name': 'web.msx.benzac.de',
                            'version': '1.0.2',
                            'parameter': "content:http://web.msx.benzac.de/msx/start.json",
                        }
                    }
                ]
            }
        ]
    }


def player_action_btn():
    if config.TIZEN:
        return 'content:request:interaction:init@https://msx.benzac.de/interaction/tizen.html'
    else:
        return 'panel:request:player:options'


DEFAULT_PLAY_BUTTON_PROPS = {
    'control:type': 'extended',
    'button:content:icon': 'list-alt',
    'button:content:action': f'player:content',
    'button:restart:icon': 'settings',
    'button:restart:action': player_action_btn(),
    'button:speed:icon': 'replay',
    'button:speed:action': 'player:restart',
}


def settings_screen(screen: bool = False):
    entry = {
        "headline": "Настройки",
        "caption": "/{ico:msx-blue:stop}Настройки",
        "template": {
            "enumerate": False,
            "type": "control",
            "layout": "0,0,6,1" if screen else "0,0,8,1"
        },
        "items": [
            {
                "label": 'Настройки kino.watch',
                'action': format_action('/msx/settings', module='panel'),
                'icon': 'movie-filter',
                'restore': False
            }, {
                "label": 'Настройки Media Station X',
                'action': 'settings',
                'icon': 'settings'
            }, {
                "label": 'Перезапустить приложение',
                'action': 'reload',
                'icon': 'restart-alt'
            }
        ]
    }

    if screen:
        entry['items'].append({
            "position": "context:context1",
            'type': 'space',
            'id': 'info',
            'offset': '-6,1,6,1',
            #'offset': '0,0,4,1',
            'headline': 'Настройки можно также открыть из главного меню (слева) нажатием синей цветной [{ico:msx-blue:stop}] кнопки или кнопки "меню" [{ico:menu}] на пульте. Подсказка находится справа снизу экрана.\nЭтот (и любой другой) пункт меню можно скрыть в разделе "Настройки kino.watch".',
            'action': '[]',
        })

    return entry


FOURK_ID = 'fourk'
HDR_ID = 'hdr'
HEVC_ID = 'hevc'
MIXED_PLAYLIST_ID = 'mixed_playlist'
SERVER_ID = 'server'
PROXY_ID = 'proxy'
ALTERNATIVE_PLAYER_ID = 'alternative_player'
POSTERS_ID = 'posters'
MENU_ID = 'menu'
HELP_ID = 'help'

def settings_menu(device_settings: 'DeviceSettings'):
    return {
        "headline": "Настройки kino.watch",
        #"caption": "/{ico:msx-blue:stop}Настройки",
        "template": {
            "enumerate": False,
            "type": "control",
            "layout": "0,0,4,1"
        },
        "items": [
            device_settings.to_fourk_msx_button(),
            device_settings.to_hdr_msx_button(),
            device_settings.to_hevc_msx_button(),
            device_settings.to_mixed_playlist_msx_button(),
            device_settings.to_server_msx_button(),
            device_settings.to_proxy_msx_button(),
            device_settings.to_alternative_player_msx_button(),
            device_settings.to_posters_msx_button(),
            device_settings.to_menu_msx_button(),
            device_settings.to_help_msx_button(),
            {
                "position": "context:context1",
                'type': 'space',
                'id': 'info',
                #'offset': '-4,1,4,1',
                'offset': '0,0,4,1',
                'headline': '',
                'action': '[]',
            }
        ]
    }

def stamp(cond):
    return {
        'stampColor': 'msx-glass' if cond else 'transparent',
        'stamp': '{ico:check}' if cond else '{ico:blank}'
    }

def label(text):
    return {'label': text}

def settings_button(id, label, action, hint):
    return {
        'id': id,
        "label": label,
        'action': action,
        "selection": {
            "action": "update:panel:info",
            "data": {
                "headline": hint
            }
        }
    }


def menu_entries_settings_panel(categories: 'List[Category]'):
    return {
            "type": "list",
            "headline": 'Пункты меню',
            'template': {
                'enumerate': False,
                "type": "button",
                "layout": f"0,0,4,1",
                'stampColor': 'msx-glass',
            },
            "items": [i.to_msx_settings_button() for i in categories if not i.ignored]
        }

def poster_settings_panel(posters: list['Poster']):
    from models.Poster import Poster
    items = []
    i = 0

    for size in Poster.SIZES:
        for proxy in Poster.PROXIES:
            items.append({
                    'title': f"{size} / {proxy['title']}",
                    'image': posters[i].format(size, proxy['id']),
                    "action": format_action(f"/msx/settings/poster/set/{size}/{proxy['id']}", module='execute')
                })
            i += 1

    return {
            "type": "list",
            "headline": 'Выберите первый рабочий постер',
            'template': {
                'enumerate': False,
                "type": "separate",
                "layout": f"0,0,2,4",
                'stampColor': 'msx-glass',
            },
            "items": items
        }

def play_action(video_url, device_settings: 'DeviceSettings' = None):
    url = make_proxy_url(video_url) if device_settings is not None and device_settings.proxy else video_url
    player = config.ALTERNATIVE_PLAYER if device_settings is not None and device_settings.alternative_player else config.PLAYER

    if config.TIZEN:
        return f'video:{url}'
    else:
        return f"video:plugin:{player}?" + urlencode({'url': url})
