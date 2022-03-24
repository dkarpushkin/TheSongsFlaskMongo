

1. Run containers
```
docker-compose up -d
```

2. Initialize mongo with data/songs.json
```
docker-compose run --rm manage init_mongo
```

3. Run tests
```
docker-compose run --rm manage test
```

### Connect to localhost:8081 for mongo-express
### Connect to localhost:8080 for API

***

### Request examples:
#### Paginated song list
```
GET localhost:8080/songs?per_page=5&page=1
```
####  Average difficulty of all songs
```
GET localhost:8080/songs/difficulty_avg
```
#### Search by title and artist
```
GET localhost:8080/songs/search?query=boss
```
#### The average, the lowest and the highest rating of a song by id
```
GET localhost:8080/songs/rating?song_id=623b97370a9a4ad5b85feca9
```
#### Add rating to a song with song_id
```
POST localhost:8080/songs/rating
json data:
{
    "song_id": "623b97370a9a4ad5b85feca9",
    "rating": 3
}
```