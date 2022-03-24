import random
import string
import pytest
from flask.testing import FlaskClient
from pymongo.collection import Collection
from songs.extensions import mongo
from typing import Optional, Type


def avg(args):
    return sum(args) / len(args)


def rand_name():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))


@pytest.fixture
def make_entries_for_rating_test():
    name = rand_name()
    entries = [
        {
            "artist": "qwer",
            "difficulty": 2.0,
            "level": 3,
            "ratings": [1, 2, 3, 4, 5],
            "released": "Tue, 01 Mar 2016 00:00:00 GMT",
            "title": f"{name} 1"
        },
        {
            "artist": "qwer",
            "difficulty": 2.0,
            "level": 3,
            "ratings": [1, 4, 5],
            "released": "Tue, 01 Mar 2016 00:00:00 GMT",
            "title": f"{name} 2"
        },
    ]

    from pymongo.collection import Collection
    from songs.extensions import mongo

    songs: Collection = mongo.db.songs
    songs.insert_many(entries)

    entries = songs.find({
        '$text': {'$search': name}
    })

    yield [
        (
            entry['_id'],
            {
                "average_raiting": avg(entry['ratings']),
                "highest_raiting": max(entry['ratings']),
                "lowest_raiting": min(entry['ratings'])
            }
        ) for entry in entries
    ]

    songs.delete_many({
        '$text': {'$search': name}
    })


def test_rating(client: Optional[Type[FlaskClient]], make_entries_for_rating_test):
    for entry in make_entries_for_rating_test:
        response = client.get("/songs/rating", follow_redirects=True, query_string={'song_id': entry[0]})
        assert response.status_code == 200, 'Wrong status code'
        
        response_data = response.get_json()
        assert response_data == entry[1]
    
    response = client.get("/songs/rating", follow_redirects=True, query_string={'song_id': 'boo'})
    assert response.status_code == 404, 'Wrong status code'
    
    response_data = response.get_json()
    assert response_data == {
        'errors': {'params': {'song_id': 'Song not found'}}
    }, f'Incorrect response data for 404 test: {response_data}'


@pytest.fixture
def test_add_rating_fixture():
    name = rand_name()
    entries = [
        {
            "artist": "qwer",
            "difficulty": 2.0,
            "level": 3,
            "released": "2022-01-01",
            "title": f"{name} 1"
        },
    ]

    songs: Collection = mongo.db.songs
    print(songs.insert_many(entries).inserted_ids)

    entries = songs.find({
        '$text': {'$search': 'entry 1'}
    })

    yield [(entry['_id'], entry['title']) for entry in entries]

    songs.delete_many({
        '$text': {'$search': 'entry 1'}
    })


def test_add_rating(client: Optional[Type[FlaskClient]], test_add_rating_fixture):
    song_id_title = test_add_rating_fixture[0]

    response = client.post("/songs/rating", json={'song_id': str(song_id_title[0]), 'rating': 3})
    assert response.status_code == 200, 'Wrong status code'

    response = client.get("/songs/search", follow_redirects=True, query_string={'query': song_id_title[1]})
    assert response.status_code == 200, 'Wrong status code'

    response_data = response.get_json()
    assert response_data['result'][0]['ratings'] == [3]
