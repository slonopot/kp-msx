import os


MSX_HOST = os.environ.get('RENDER_EXTERNAL_URL') or os.environ.get('MSX_HOST')
MONGODB_URL = os.environ.get('MONGODB_URL')
MONGODB_COLLECTION = os.environ.get('MONGODB_COLLECTION') or 'kp'
SQLITE_URL = os.environ.get('SQLITE_URL') or './kp-sqlite.db'
IS_SQLITE = (MONGODB_URL is None or len(MONGODB_URL) == 0) and len(SQLITE_URL) > 0
PORT = int(os.environ.get('PORT', 10000))
PLAYER = os.environ.get('PLAYER') or f'{MSX_HOST}/player/hlsx.html'
ALTERNATIVE_PLAYER = os.environ.get('ALTERNATIVE_PLAYER') or 'http://msx.benzac.de/plugins/html5x.html'
KP_CLIENT_ID = os.environ.get('KP_CLIENT_ID') or 'xbmc'
KP_CLIENT_SECRET = os.environ.get('KP_CLIENT_SECRET') or 'cgg3gtifu46urtfp2zp1nqtba0k2ezxh'
KP_API_DOMAIN = os.environ.get('KP_API_DOMAIN') or 'https://api.service-kp.com'
QUALITY = os.environ.get('QUALITY')
PROTOCOL = os.environ.get('PROTOCOL') or 'hls4'
TIZEN = os.environ.get('TIZEN') == 'yes'
TIMEOUT = int(os.environ.get('TIMEOUT', 5))
