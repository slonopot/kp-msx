import config


class MSX:

    def __init__(self):
        pass

    @staticmethod
    def start():
        return {
            'name': 'kino.pub',
            'version': '6.6.6',
            'parameter': f'menu:{config.MSX_HOST}/msx/menu?id={{ID}}',
            'welcome': 'none'
        }

    @staticmethod
    def unregistered_menu():
        return {
            "reuse": False,
            "cache": False,
            "restore": False,
            "headline": "kino.pub",
            "menu": [
                {
                    "icon": "vpn-key",
                    "label": "Регистрация",
                    "data": f"{config.MSX_HOST}/msx/registration?id={{ID}}"
                }
            ],
        }

    @staticmethod
    def registered_menu(categories):
        entry = {
            "reuse": False,
            "cache": False,
            "restore": False,
            "refocus": 1,
            "headline": "kino.pub",
            "menu": [category.to_msx() for category in categories or []],
        }
        entry['menu'].append({
            "type": "default",
            "label": "Поиск",
            "icon": "search",
            'data': f'request:interaction:{config.MSX_HOST}/msx/search?id={{ID}}&q={{INPUT}}|search:3|ru@http://msx.benzac.de/interaction/input.html'
        })
        entry['menu'].append({
            "type": "default",
            "label": "Закладки",
            "icon": "bookmark",
            'data': f'{config.MSX_HOST}/msx/bookmarks?id={{ID}}'
        })
        return entry

    @staticmethod
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

    @staticmethod
    def registration(user_code):
        return {
            "type": "pages",
            "headline": "Регистрация",
            "pages": [{
                "items": [
                    {
                        "type": "space",
                        "layout": "0,0,6,1",
                        "title": user_code,
                        "titleFooter": "Используйте этот код для добавления устройства"
                    },
                    {
                        "type": "button",
                        "layout": "0,1,6,1",
                        "label": "Я ввёл код",
                        "action": f"execute:{config.MSX_HOST}/msx/check_registration?id={{ID}}"
                    }]
            }]
        }

    @staticmethod
    def code_not_entered():
        return {
            'response': {
                'status': 200,
                'data': {'action': 'warn:Код не введён'}
            }
        }

    @staticmethod
    def restart():
        return {
            'response': {
                'status': 200,
                'data': {'action': 'reload'}
            }
        }

    @staticmethod
    def content(entries, category, page, extra=None, decompress=None):
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

        if page == 1 and extra is None:
            resp['items'] = [
                {
                    'title': 'Свежие',
                    'icon': 'fiber-new',
                    'action': f'content:request:interaction:{config.MSX_HOST}/msx/category?id={{ID}}&category={category}&extra=fresh&offset={{OFFSET}}&limit={{LIMIT}}|20@http://msx.benzac.de/interaction/paging.html'
                },
                {
                    'title': 'Горячие',
                    'icon': 'whatshot',
                    'action': f'content:request:interaction:{config.MSX_HOST}/msx/category?id={{ID}}&category={category}&extra=hot&offset={{OFFSET}}&limit={{LIMIT}}|20@http://msx.benzac.de/interaction/paging.html'
                },
                {
                    'title': 'Популярные',
                    'icon': 'thumb-up',
                    'action': f'content:request:interaction:{config.MSX_HOST}/msx/category?id={{ID}}&category={category}&extra=popular&offset={{OFFSET}}&limit={{LIMIT}}|20@http://msx.benzac.de/interaction/paging.html'
                }
            ]
            entries = entries[:17]
        for entry in entries:
            resp['items'].append(entry.to_msx())

        return resp

    @staticmethod
    def bookmark_folders(result):
        return {
            "type": "list",
            "headline": "Template",
            "template": {
                "type": "separate",
                "layout": "0,0,4,1",
                "color": "msx-glass",
            },
            "items": [i.to_msx() for i in result]
        }
