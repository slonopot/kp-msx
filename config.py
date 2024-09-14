import os


MSX_HOST = os.environ.get('RENDER_EXTERNAL_URL') or os.environ.get('MSX_HOST')
MONGODB_URL = os.environ.get('MONGODB_URL')
PORT = os.environ.get('PORT') or 10000
PLAYER = os.environ.get('PLAYER') or 'https://slonopot.github.io/msx-hlsx/hlsx.html'
KP_CLIENT_ID = os.environ.get('KP_CLIENT_ID') or 'xbmc'
KP_CLIENT_SECRET = os.environ.get('KP_CLIENT_SECRET') or 'cgg3gtifu46urtfp2zp1nqtba0k2ezxh'
QUALITY = os.environ.get('QUALITY')
PROTOCOL = os.environ.get('PROTOCOL') or 'hls4'
