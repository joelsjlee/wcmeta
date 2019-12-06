import requests
import argparse
import json
import os
import sys
import csv

import sys, os, traceback

from pprint import pprint
from time import sleep

template = 'http://experiment.worldcat.org/oclc/{}.jsonld'

def parse_args():
    parser = argparse.ArgumentParser(
        description="Downlad JSON-LD metadata from worldcat based on OCLC #."
    )

    parser.add_argument('-d', '--destination', type=str, default='.',
                        help="Save json files to this dir. Defaults to "
                             "current directory.")
    parser.add_argument('-j', '--jsons', type=str, default='.',
                        help="Save json files to this dir. Defaults to "
                             "current directory.")
    parser.add_argument('-f', '--field', type=str, default='.',
                        help="choose which field to pull: genre, workexamples")
    args = parser.parse_args()
    # if not args.oclc_nums:
    #     args.oclc_nums = (n for l in sys.stdin for n in l.split())
    return args

def genre(meta):
    genres = []
    for item in meta['@graph']:
        #print(item)
        #print("genre" in item)
        if "genre" in item:
            item = item['genre']
            if isinstance(item, str):
                genres.append(item)
            elif isinstance(item, list):
                for i in item:
                    if isinstance(i, str):
                        genres.append(i)
                    elif isinstance(i, dict):
                        genres.append(i['@value'])
            elif isinstance(item, dict):
                genres.append(item['@value'])
    return [g.strip() for g in genres]

def workExampleGenre(meta):
    genres = []
    for item in meta['@graph']:
        #print(item)
        #print("genre" in item)
        if "genre" in item:
                return genre(meta)
        else:
            if "workExample" in item:
                for x in workexamples(meta):
                    try:
                        metas = genre(get_meta(x))
                        if metas != []:
                            return metas
                    except Exception as e:
                        if hasattr(e, 'response'):
                            response = e.response
                            if response.status_code == 404:
                                print(f'404 {response.url}')
                            else:
                                print(getattr(response, 'content'))
                        else:
                            print(e)

def get_meta(oclc):
    r = requests.get(template.format(oclc))
    #sleep(1)
    if r.status_code == 200:
        return r.json()
    else:
        r.raise_for_status()

def workexamples(meta):
    workexamples = []
    for item in meta['@graph']:

        if "workExample" in item:
            item = item['workExample']
            if isinstance(item, str):
                workexamples.append(item.split('/')[4])
            elif isinstance(item, list):
                for x in item:
                    workexamples.append(x.split('/')[4])
    return workexamples



def save_oclc_meta(dest, oclc, data):
    with open(dest, 'a', encoding='utf-8') as op:
        tsv = csv.writer(op, delimiter='\t')
        tsv.writerow([oclc, ', '.join(data)])


def main(args):
    with open(args.destination, 'w', encoding='utf-8') as writer:
        writer.write('')
    lst = []
    for filename in os.listdir(args.jsons):
        with open("../json/" + filename, 'r') as jsonfile:
            try:

                data = json.load(jsonfile)
                #print('ERROR' in data)
                if 'ERROR' in data:
                    continue
                if (args.field == 'genre'):
                    data = genre(data)
                if (args.field == 'workexamples'):
                    data = workexamples(data)
                if (args.field == 'workexamplesgenre'):
                    data = workExampleGenre(data)
                if (data == []):
                    continue
                save_oclc_meta(args.destination, filename.split('.')[0], data)
                #print('hi')
            except:
                continue

if __name__ == '__main__':
    main(parse_args())
