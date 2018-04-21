from pymongo import MongoClient

import config


def get_connection():
    connect = MongoClient(config.MONGODB_IP, config.MONGODB_POST)
    return connect[config.MONGODB_DN_NAME]

