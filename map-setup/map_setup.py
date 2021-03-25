#!/usr/bin/env python
# coding: utf-8

import re
import csv
import sys
import os
import os.path
from shutil import rmtree
from time import sleep

try:
    import requests
except ModuleNotFoundError:
    print('Requests module not installed on this system or in this environment')
    print('install it with: $ pip install requests')
    sys.exit()

def main():
    print('Reading maps list...')

    csv_loc = 'data'
    csv_files = []
    for file in os.listdir(csv_loc):
        if file[-4:] == '.csv':
            path = os.path.join(csv_loc, file)
            csv_files.append(path)
        else:
            continue

    maps = []
    map_ids = [] # store ids to check for duplicates

    for csv_file in csv_files:
        with open(csv_file, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                if row[0] == 'Series': # exclude the headers
                    continue
                else:
                    if row[54] in map_ids: # check if map is duplicate
                        continue
                    else:
                        maps.append(row)
                        map_ids.append(row[54])

    sleep(1)

    print('Creating maps storage directory')
    sleep(1)

    map_dirname = '../storage/maps'
    map_pathname = '/storage/maps'

    map_dir = os.path.join(os.getcwd(), map_dirname)
    if os.path.exists(map_dir):
        print('The maps storage directory exists already')
        c = input('Enter Y to delete and remake, enter N to stop here and exit: ')
        if c == 'Y' or c == 'y':
            print('the directory will be remade')
            rmtree(map_dir) # delete directory if it exists already
            os.makedirs(map_dir)
        else:
            sys.exit()
    else:
        os.makedirs(map_dir)

    print('Downloading {} maps into {}'.format(len(maps), map_dir))
    print('This will take some time...')

    sleep(1)

    retries = []

    with open('../initialize.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        for m in maps:
            url = m[50]
            map_filename = url.split('/')[-1].replace('%20', '_')
            save_loc = os.path.join(map_dir, map_filename)
            local_download_loc = os.path.join(map_pathname, map_filename)
            print('====> {}'.format(m[50]))
            print('Downloading...')
            try:
                map_request = requests.get(url)
                print('{}\n'.format(map_request))
                with open(save_loc, 'wb') as f:
                    f.write(map_request.content)
                m.append(local_download_loc)
                writer.writerow(m)
            except TimeoutError:
                retries.append(m)
                continue

    print('{} files failed:'.format(len(retries)))
    for r in retries:
        print(r)

if __name__ == '__main__':
    main()
