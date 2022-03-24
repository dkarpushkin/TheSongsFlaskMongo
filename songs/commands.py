import json
import os
import click
import pymongo

from pymongo import MongoClient
from pymongo.collection import Collection

import songs.settings as settings


HERE = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.join(HERE, os.pardir)
TEST_PATH = os.path.join(PROJECT_ROOT, "tests")


@click.command('test')
def test():
    """Run the tests."""
    import pytest

    rv = pytest.main([TEST_PATH, "--verbose"])
    exit(rv)


@click.command('init_mongo')
def init_mongo():
    """
    Initializes MongoDB
    Creates collection
    Creates indices
    Imports data from songs.json
    """
    db_name = settings.MONGODB_CONFIG['name']
    uri = f"mongodb://{settings.MONGODB_CONFIG['login']}:{settings.MONGODB_CONFIG['password']}@{settings.MONGODB_CONFIG['host']}/{db_name}?authSource=admin"
    
    client = MongoClient(uri)

    db = client[db_name]

    try:
        db.create_collection('songs')
    except pymongo.errors.CollectionInvalid:
        # the collection already exists
        pass
    
    print("Collection songs created")

    songs: Collection = db.songs

    songs.create_index([('title', pymongo.TEXT), ('artist', pymongo.TEXT)])
    songs.create_index([('released', pymongo.ASCENDING)])

    print("Indices created")

    with open(os.path.join(PROJECT_ROOT, 'data', 'songs.json')) as f:
        songs_data = map(lambda x: json.loads(x), f.readlines())
    
    songs.insert_many(songs_data)

    print("Data imported")
