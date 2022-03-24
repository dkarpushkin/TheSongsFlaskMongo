import math
from flask import Blueprint, make_response

from songs.decorators import pydantic_params
from songs.models import Song
from songs.query_models import SongIdQueryModel, RatingQueryModel, SearchQueryModel, PaginationQueryModel


blueprint = Blueprint('songs', __name__, url_prefix='/songs')


@blueprint.route('/', methods=['GET'])
@pydantic_params(PaginationQueryModel)
def songs_list(params: PaginationQueryModel):
    """
        Returns paginated list of songs.
        Query params:
            page: int - page number
            per_page: int - number of items per page
    """
    songs_objects, count = Song.get_all_paginated(params.page, params.per_page)
    has_next = (params.per_page * params.page) <= count

    links = {}
    if params.page > 1:
        links['prev'] = f'/songs/?page={params.page - 1}&per_page={params.per_page}'
    if has_next:
        links['next'] = f'/songs/?page={params.page + 1}&per_page={params.per_page}'

    return {
        'songs': [song.dict() for song in songs_objects],
        '_links': links,
        '_max_page': math.ceil(count / params.per_page)
    }


@blueprint.route('/difficulty_avg', methods=['GET'])
def difficulty():
    """
        Returns average difficulty of all songs.
    """
    average_difficulty = Song.get_average_difficulty()

    return {
        'average_difficulty': average_difficulty
    }


@blueprint.route('/search', methods=['GET'])
@pydantic_params(SearchQueryModel)
def search(params: SearchQueryModel):
    """
        Returns songs that contain query in its title or artist name.
        Query params:
            query: str - the search query
    """
    result = Song.search_by_title_and_artist(params.query)
    return {
        'result': [song.dict() for song in result]
    }


@blueprint.route('/rating', methods=['GET'])
@pydantic_params(SongIdQueryModel)
def song(params: SongIdQueryModel):
    """
        Returns the average, the lowest and the highest rating of the given song.
        Query params:
            song_id: str - song id
    """
    song = Song.get_raiting_aggregation(params.song_id)

    if song is None:
        return make_response({
            'errors': {'params': {'song_id': 'Song not found'}}
        }, 404)
    else:
        return song


@blueprint.route('/rating', methods=['POST', 'PATCH'])
@pydantic_params(RatingQueryModel, 'json')
def rate(params: RatingQueryModel):
    """
        Adds a rating for the given song with id = song_id.
        Rating should be between 1 and 5 inclusive.
        Json params:
            song_id: str - song id
            rating: int - raiting
    """

    result = Song.add_rating(params.song_id, params.rating)
    if result:
        return {'status': 'Ok'}
    else:
        return make_response({
            'errors': {'params': {'song_id': 'Song not found'}}
        }, 404)
