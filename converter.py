import json
from io import BytesIO
from tokenize import tokenize
from zipfile import ZipFile
from clausewitz.parse import parse
from clausewitz.util.tokenize import prepare


def jsonify(f):
    return parse(tokenize(prepare(f.readline)))

def unzip_save(f: BytesIO):
    with ZipFile(f) as zip:
            with zip.open('meta') as meta:
                print("Parsing meta")
                yield 'meta', meta
            with zip.open('gamestate') as gamestate:
                print("Parsing gamestate")
                yield 'gamestate', gamestate

def savToJson(filelocation):
    with open(filelocation, "rb") as save:
        f = BytesIO(save.read())

        result = {
            name: jsonify(unzipped)
            for name, unzipped in unzip_save(f)
        }
        print("done")
        with open('data2.json', 'w') as json_f:
            json.dump(result, json_f)
        return result