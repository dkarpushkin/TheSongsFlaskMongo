import os

MONGO_URI = f"mongodb://{os.environ.get('MONGO_LOGIN', 'root')}:{os.environ.get('MONGO_PASSWORD', 'toor')}@songs_db:27017/songs_test?authSource=admin"
