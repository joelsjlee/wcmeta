import requests
import argparse
import json
import os
import sys

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
    parser.add_argument('oclc_nums', type=str, nargs='*',
                        help="A list of OCLC numbers. If no numbers are "
                             "supplied, a space-delimited list will be read "
                             "from standard input.")
    args = parser.parse_args()
    if not args.oclc_nums:
        args.oclc_nums = (n for l in sys.stdin for n in l.split())
    return args

def get_meta(oclc):
    r = requests.get(template.format(oclc))
    if r.status_code == 200:
        return r.json()
    else:
        r.raise_for_status()

def save_oclc_meta(dest, oclc, data):
    dest = os.path.join(dest, '{}.json'.format(oclc))
    with open(dest, 'w', encoding='utf-8') as op:
        json.dump(data, op, indent=2)

def main(args):
    for oclc in args.oclc_nums:
        sleep(1)
        try:
            meta = get_meta(oclc)
        except requests.exceptions.HTTPError as exc:
            meta = {'ERROR': str(exc)}

        save_oclc_meta(args.destination, oclc, meta)

if __name__ == '__main__':
    main(parse_args())
