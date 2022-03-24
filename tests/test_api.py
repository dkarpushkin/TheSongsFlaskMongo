from typing import Optional, Type
from flask.testing import FlaskClient


def test_songs_list(client: Optional[Type[FlaskClient]]):
    response = client.get("/songs", query_string={
        'per_page': '5',
        'page': '1'
    }, follow_redirects=True)
    assert response.status_code == 200, 'First page: wrong status code'

    response_data = response.get_json()
    assert len(response_data['songs']) == 5, 'Incorrect songs list'
    assert response_data['_links']['next'] == '/songs/?page=2&per_page=5', 'Incorrect next link'

    response = client.get("/songs/", query_string={
        'per_page': '5',
        'page': '3'
    }, follow_redirects=True)
    assert response.status_code == 200, 'Last page: wrong status code'

    response_data = response.get_json()
    assert len(response_data['songs']) == 1, 'Incorrect songs list'
    assert response_data['_links']['prev'] == '/songs/?page=2&per_page=5', 'Incorrect prev link'


def test_difficulty_avg(client: Optional[Type[FlaskClient]]):
    response = client.get("/songs/difficulty_avg", follow_redirects=True)
    assert response.status_code == 200, 'Wrong status code'

    response_data = response.get_json()
    assert response_data['average_difficulty'] == 10.323636363636364, 'Incorrect average_difficulty'


def test_search(client: Optional[Type[FlaskClient]]):
    test_cases = [
        {
            'query_string': {'query': 'Fastfinger'},
            'result_len': 1,
            'has_artist': 'Mr Fastfinger',
        },
        {
            'query_string': {'query': 'Yousicians'},
            'result_len': 10,
            'has_artist': 'The Yousicians',
        },
        {
            'query_string': {'query': 'new'},
            'result_len': 1,
            'has_title': 'A New Kennel',
        },
    ]

    for test_case in test_cases:
        response = client.get("/songs/search", follow_redirects=True, query_string=test_case['query_string'])
        assert response.status_code == 200, 'Wrong status code'

        response_data = response.get_json()
        assert len(response_data['result']) == test_case['result_len']

        has_title = test_case.get('has_title')
        if has_title:
            assert any(song['title'] == has_title for song in response_data['result']), f'Result does not have {has_title} title for {test_case["query_string"]}'
        
        has_artist = test_case.get('has_artist')
        if has_artist:
            assert any(song['artist'] == has_artist for song in response_data['result']), f'Result does not have {has_artist} artist for {test_case["query_string"]}'
