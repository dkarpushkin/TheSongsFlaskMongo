docker-compose exec songs_db \
    mongoimport \
        --db songs --collection songs \
        --authenticationDatabase admin --username root --password example \
        --drop --file /data_json/songs.json