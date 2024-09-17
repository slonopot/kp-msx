from pymongo import MongoClient

import config

client = MongoClient(config.MONGODB_URL)

db = client['kp']['devices']


def get_device_by_id(device_id):
    return db.find_one({'id': device_id})


def create_device(entry):
    return db.insert_one(entry)


def update_device_code(id, code):
    return db.update_one({'id': id}, {'$set': {'code': code}})


def update_device_tokens(id, token, refresh):
    return db.update_one({'id': id}, {'$set': {'token': token, 'refresh': refresh}})


def update_tokens(token, param, param1):
    return db.update_one({'token': token}, {'$set': {'token': param, 'refresh': param1}})


def delete_device(id):
    return db.delete_one({'id': id})
