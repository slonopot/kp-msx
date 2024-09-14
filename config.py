import os


MSX_HOST = os.environ.get('RENDER_EXTERNAL_URL') or os.environ.get('MSX_HOST')
MONGODB_URL = os.environ.get('MONGODB_URL')
PORT = int(os.environ.get('PORT'))
PLAYER = os.environ.get('PLAYER')
KP_CLIENT_ID = os.environ.get('KP_CLIENT_ID')
KP_CLIENT_SECRET = os.environ.get('KP_CLIENT_SECRET')
