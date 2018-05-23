from pymongo import MongoClient

import config


def get_connection():
    connect = MongoClient(config.MONGODB_IP, config.MONGODB_POST)
    return connect[config.MONGODB_DN_NAME]


class Collection(object):
    def __init__(self, collection, buffer_size=1000):
        self.collection = collection

        self.buffer_size = buffer_size
        self.insert_buffer = []

    def insert(self, doc):
        self.insert_buffer.append(doc)
        if len(self.insert_buffer) >= self.buffer_size:
            self.collection.insert(self.insert_buffer)
            self.insert_buffer.clear()

    def insert_done(self):
        if self.insert_buffer:
            self.collection.insert(self.insert_buffer)
            self.insert_buffer.clear()

    def update(self, doc_id, new_field):
        self.collection.update(
            {'_id': doc_id},
            {'$set': new_field}
        )
