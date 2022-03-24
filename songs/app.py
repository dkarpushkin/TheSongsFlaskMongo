import os
import pymongo
from flask import Flask
from urllib import parse

from songs import commands, views
from songs.extensions import mongo

MONGODB_URI_TEMPLATE = 'mongodb://{login}:{password}@{host}:{port}/{name}?authSource=admin'

def create_app(config_object='songs.settings'):
    app = Flask(__name__)
    app.config.from_object(config_object)

    if 'MONGO_URI' not in app.config:
        mongo_config = app.config.get('MONGODB_CONFIG')
        if mongo_config is not None:
            app.config['MONGO_URI'] = MONGODB_URI_TEMPLATE.format(
                login=mongo_config["login"],
                password=mongo_config["password"],
                host=mongo_config["host"],
                port=mongo_config["port"],
                name=mongo_config["name"]
            )
        else:
            print("Either MONGODB_CONFIG or MONGO_URI must be defined in settings")
            exit(1)
    
    mongo.init_app(app)

    app.cli.add_command(commands.test)
    app.cli.add_command(commands.init_mongo)
    
    app.register_blueprint(views.blueprint)

    # try:
    #     os.makedirs(app.instance_path)
    # except OSError:
    #     pass

    return app
