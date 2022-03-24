
from bson.objectid import ObjectId as BsonObjectId
from bson.errors import InvalidId
from datetime import date
from pydantic import BaseModel, Field
from typing import List, Optional, Tuple
import pymongo
from pymongo.collection import Collection

from songs.extensions import mongo


class ObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if not isinstance(value, BsonObjectId):
            raise TypeError('ObjectId required')
        return str(value)


class Song(BaseModel):
    id: ObjectId = Field(alias='_id')
    artist: str
    title: str
    difficulty: float
    level: int
    released: date
    ratings: Optional[List[int]]
    
    @classmethod
    def add_rating(cls, song_id, rating) -> bool:
        songs: Collection = mongo.db.songs

        try:
            song_id_object = BsonObjectId(song_id)
        except InvalidId:
            return None
        
        result = songs.update_one({
            '_id': song_id_object
        }, {
            '$push': {
                'ratings': rating
            }
        })

        return result.modified_count > 0

    @classmethod
    def get_by_id(cls, song_id: str) -> Optional['Song']:
        try:
            song_id_object = BsonObjectId(song_id)
        except InvalidId:
            return None
        
        cursor = mongo.db.songs.find({
            '_id': song_id_object
        })

        songs = [Song(**song) for song in cursor]
        
        return songs[0] if len(songs) > 0 else None
    
    @classmethod
    def get_raiting_aggregation(cls, song_id: str) -> Optional[dict]:
        songs: Collection = mongo.db.songs

        try:
            song_id_object = BsonObjectId(song_id)
        except InvalidId:
            return None

        cursor = songs.aggregate([
            {'$match': { '_id': song_id_object }},
            {'$set': {
                'lowest_raiting': { '$min': '$ratings' },
                'highest_raiting': { '$max': '$ratings' },
                'average_raiting': { '$avg': '$ratings' },
            }}
        ])

        songs = [{
            'lowest_raiting': song['lowest_raiting'],
            'highest_raiting': song['highest_raiting'],
            'average_raiting': song['average_raiting']
        } for song in cursor]

        return songs[0] if len(songs) > 0 else None

    @classmethod
    def get_all_paginated(cls, page, per_page) -> Tuple[List['Song'], bool]:
        songs: Collection = mongo.db.songs

        cursor = songs.find().sort('released', pymongo.ASCENDING).skip(per_page * (page - 1)).limit(per_page)

        return [Song(**doc) for doc in cursor], songs.estimated_document_count()
    
    @classmethod
    def get_average_difficulty(self) -> Optional[float]:
        songs: Collection = mongo.db.songs

        cursor = songs.aggregate([
            {'$group': {'_id': None, 'average_difficulty': {'$avg': '$difficulty'}}}
        ])

        avgs = [avg['average_difficulty'] for avg in cursor]

        return avgs[0] if len(avgs) > 0 else None
    
    @classmethod
    def search_by_title_and_artist(cls, query) -> List['Song']:
        songs: Collection = mongo.db.songs

        cursor = songs.find({
            '$text': {'$search': query}
        })

        return [Song(**doc) for doc in cursor]
