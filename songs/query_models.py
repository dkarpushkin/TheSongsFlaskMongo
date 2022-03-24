
from typing import Optional

from pydantic import BaseModel, validator


class PaginationQueryModel(BaseModel):
    page: Optional[int] = 1
    per_page: Optional[int] = 10

    @validator('page')
    def validate_page(cls, value):
        if value < 1:
            raise ValueError('page must be greater or equal than 1')
        return value
    
    @validator('per_page')
    def validate_per_page(cls, value):
        if value < 1:
            raise ValueError('per_page must be greater or equal than 1')
        return value


class SearchQueryModel(BaseModel):
    query: str


class SongIdQueryModel(BaseModel):
    song_id: str


class RatingQueryModel(SongIdQueryModel):
    rating: int

    @validator('rating')
    def validate_rating(cls, value):
        if value < 1 or value > 5:
            raise ValueError("'rating' must be between 1 and 5")
        return value
