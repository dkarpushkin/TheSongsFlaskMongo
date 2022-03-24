import os

MONGODB_CONFIG = {
    'name': 'songs',
    'host': 'songs_db',
    'port': 27017,
    'login': os.environ.get('MONGO_LOGIN', 'root'),
    'password': os.environ.get('MONGO_PASSWORD', 'toor')
}