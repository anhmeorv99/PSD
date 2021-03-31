import json
import logging

logger = logging.getLogger(__name__)


def reset_log():
    with open('log/log.txt', 'w') as json_file:
        json.dump({}, json_file)


def add_log(prop, number):
    data = {}
    try:
        json_file = open("log/log.txt", "r")
        data = json.load(json_file)
        json_file.close()
    except Exception as e:
        pass

    if prop in data:
        data[prop] += number
    else:
        data[prop] = number

    with open('log/log.txt', 'w') as json_file:
        json.dump(data, json_file)


def get_log():
    data = {}
    try:
        json_file = open("log/log.txt", "r")
        data = json.load(json_file)
        json_file.close()
    except Exception as e:
        pass
    print(f'save success:: [{data["image"]}/{data["total"]}] file')

