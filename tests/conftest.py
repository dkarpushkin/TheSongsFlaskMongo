import json
import os
import pymongo
import pytest
from pymongo.collection import Collection
from songs.app import create_app
from songs.extensions import mongo

HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, "tests")


@pytest.fixture()
def app():
    """
    Use test database.
    Create songs collection, import the data from songs.json and remove it afterwards.
    """
    app = create_app('tests.settings')
    app.config.update({
        "TESTING": True,
    })
    
    mongo.db.drop_collection('songs')
    mongo.db.create_collection('songs')
    songs: Collection = mongo.db.songs
    
    with open(os.path.join(PROJECT_ROOT, 'tests', 'songs.json')) as f:
        songs_data = map(lambda x: json.loads(x), f.readlines())
    
    songs.insert_many(songs_data)

    songs.create_index([('title', pymongo.TEXT), ('artist', pymongo.TEXT)])
    songs.create_index([('released', pymongo.ASCENDING)])

    yield app

    mongo.db.drop_collection('songs')


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
