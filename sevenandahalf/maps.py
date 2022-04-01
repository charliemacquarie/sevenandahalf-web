import re
import csv
import sys
import os
import os.path
from shutil import rmtree
from time import sleep

import click
from flask import current_app
from flask.cli import with_appcontext
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

@click.command('get-maps')
@click.option('--web-root', prompt='Document root for your webserver (full path)', help='full path of your webserver\'s document root')
@click.argument('mapfiles', nargs=-1, type=click.Path(exists=True))
@with_appcontext
def get_maps_command(mapfiles, web_root):
    """Download maps and write metadata to an intialize.csv file"""
    click.echo('Reading maps list from:')
    for f in mapfiles: # print out filenames which were input
        click.echo('{}'.format(f))

    map_config = {}

    click.echo('\nYou can either add maps to an existing site/map storage, or you can start from zero\n')
    map_append = input('Do you want to add to an existing map storage? (y/n): ')
    if map_append == 'y' or map_append == 'Y' or map_append == 'yes' or map_append == 'Yes':
        map_config['map_append'] = True
        map_config['map_append_value'] = 'a'
        click.echo('Will add to the existing map storage\n')
    else:
        map_config['map_append'] = False
        map_config['map_append_value'] = 'w'
        click.echo('Will create new map storage and start there\n')

    year_lim = input('Do you want to limit by year? (y/n): ')
    if year_lim == 'y' or year_lim == 'Y' or year_lim == 'yes' or year_lim == 'Yes':
        year = input('Enter the most recent year of maps you want to include: ')
        sleep(0.25)
        click.echo('Limiting to maps from {} and older\n'.format(year))
        map_config['year_lim'] = True
        map_config['year'] = year
    else:
        map_config['year_lim'] = False
        map_config['year'] = 'none'
        click.echo('Not limiting by year\n')
    sleep(0.5)

    state_lim = input('Do you want to limit by state? (y/n): ')
    if state_lim == 'y' or state_lim == 'Y' or state_lim == 'yes' or state_lim == 'Yes':
        state = (input('Enter the 2-letter abbreviations of the states you wish to limit to, separated by commas (ex.: CA,NV,UT): ')).split(',')
        sleep(0.25)
        click.echo('Limiting to maps from {}\n'.format(state))
        map_config['state_lim'] = True
        map_config['state'] = state
    else:
        map_config['state_lim'] = False
        map_config['state'] = 'none'
        click.echo('Not limiting by state\n')
    sleep(0.5)

    if not map_config['state_lim']:
        bounding_lim = input('Do you want to limit by bounding box? (answering no will likely fill your computer storage) (y/n): ')
        if bounding_lim == 'y' or bounding_lim == 'Y' or bounding_lim == 'yes' or bounding_lim == 'Yes':
            adding = bounding_lim
            bounding = []
            map_config['bounding_lim'] = True
            while adding == 'y' or adding == 'Y' or adding == 'yes' or adding == 'Yes':
                click.echo('Enter your bounding box as 4 coordinates separated by commas, in the following order: S Lat, W Long, N Lat, E Long')
                click.echo('i.e.: 37.509726,-121.794434,39.436193,-111.577148')
                bound_add = tuple(input('Bounding box: ').split(','))
                click.echo('Added bounding box {}\n'.format(bound_add))
                bounding.append(bound_add)
                adding = input('Do you want to add another bounding box? (y/n): ')
            map_config['bounding'] = bounding
        else:
            map_config['bounding_lim'] = False
            map_config['bounding'] = 'none'
            click.echo('Not limiting by bounding box\n')
    else:
        map_config['bounding_lim'] = False
        map_config['bounding'] = 'none'

    sleep(1)

    click.echo('\nChecking map storage directory\n')

    sleep(1)

    if os.path.exists(web_root): # check if entered document root exists
        map_pathname = 'storage/maps'
        map_dir = os.path.join(web_root, map_pathname)

        if os.path.exists(map_dir): # check if map storage directory exists
            if map_config['map_append']:
                click.echo('Using existing map storage directory at: {}\n'.format(map_dir))
            else:
                click.echo('The maps storage directory exists already')
                c = input('Are you sure you want to delete the storage and start over? (y/n): ')
                if c == 'Y' or c == 'y':
                    click.echo('the directory will be remade\n')
                    rmtree(map_dir) # delete directory if it exists already
                    os.makedirs(map_dir)
                    click.echo('Using map storage directory at: {}\n'.format(map_dir))
                else:
                    click.echo('Exiting now.')
                    sys.exit()
        else:
            os.makedirs(map_dir) # make directory if it doesn't exist already
            click.echo('Using map storage directory at: {}\n'.format(map_dir))

    else:
        click.echo('The document root you entered does not exist. Please double check and try again.')


    click.echo('**Downloading Maps!**')
    click.echo('Depending on how many maps fit your criteria, this may take a while\n')

    sleep(1)

    # store ids to check for duplicates
    map_ids = []

    init_file_path = os.path.join(current_app.root_path, 'initialize.csv')

    # retry strategy for requests
    retry_strategy = Retry(
        total=10,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=['HEAD', 'GET', 'PUT', 'DELETE', 'OPTIONS', 'TRACE', 'POST'],
        backoff_factor=1
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount('https://', adapter)
    http.mount('http://', adapter)

    with open(init_file_path, map_config['map_append_value']) as init_file: # open initialize.csv file
        writer = csv.writer(init_file, quoting=csv.QUOTE_ALL)
        for csv_file in mapfiles:
            with open(csv_file, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for row in reader:
                    if row[0] == 'Series': # exclude the headers
                        continue
                    elif row[54] in map_ids: # check if map is duplicate
                        continue
                    elif map_config['year_lim'] and row[6] >= map_config['year']: # check if map is newer than cutoff year
                        continue
                    elif map_config['state_lim'] and row[4] not in map_config['state']: # check if map is outside state selected
                        continue
                    elif map_config['bounding_lim']:
                        for b in map_config['bounding']:
                            if (float(row[45]) >= float(b[0])
                                and float(row[46]) <= float(b[3])
                                and float(row[47]) <= float(b[2])
                                and float(row[48]) >= float(b[1])
                                and row[54] not in map_ids):
                                # map is inside bounding box, download it
                                map_ids.append(row[54])
                                url = row[58]
                                map_filename = url.split('/')[-1].replace('%20', '_')
                                save_loc = os.path.join(map_dir, map_filename)
                                local_download_loc = os.path.join('/', map_pathname, map_filename)
                                click.echo('====> {}'.format(row[58]))
                                click.echo('Downloading...')
                                map_request = http.get(url)
                                click.echo('{}\n'.format(map_request))
                                with open(save_loc, 'wb') as f:
                                    f.write(map_request.content)
                                row.append(local_download_loc)
                                writer.writerow(row)
                            else:
                                continue
                    else: # download map to storage, add to initialize.csv
                        map_ids.append(row[54])
                        url = row[58]
                        map_filename = url.split('/')[-1].replace('%20', '_')
                        save_loc = os.path.join(map_dir, map_filename)
                        local_download_loc = os.path.join('/', map_pathname, map_filename)
                        click.echo('====> {}'.format(row[58]))
                        click.echo('Downloading...')
                        map_request = http.get(url)
                        click.echo('{}\n'.format(map_request))
                        with open(save_loc, 'wb') as f:
                            f.write(map_request.content)
                        row.append(local_download_loc)
                        writer.writerow(row)

    click.echo('Downloaded {} maps'.format(len(map_ids)))
    click.echo('------- FINALLY COMPLETE -------')

@click.command('get-metadata')
@click.argument('mapfiles', nargs=-1, type=click.Path(exists=True))
@with_appcontext
def get_metadata_command(mapfiles):
    """Write map metadata to an intialize.csv file"""
    click.echo('Reading maps list from:')
    for f in mapfiles: # print out filenames which were input
        click.echo('{}'.format(f))

    map_pathname = 'storage/maps'

    map_ids = [] # store ids to check for duplicates

    init_file_path = os.path.join(current_app.root_path, 'initialize.csv')

    with open(init_file_path, 'w') as init_file: # open initialize.csv file
        writer = csv.writer(init_file, quoting=csv.QUOTE_ALL)
        for csv_file in mapfiles:
            with open(csv_file, newline='') as csvfile:
                reader = csv.reader(csvfile, delimiter=',', quotechar='"')
                for row in reader:
                    if row[0] == 'Series': # exclude the headers
                        continue
                    else:
                        if row[54] in map_ids: # check if map is duplicate
                            continue
                        else: # add map to initialize.csv
                            map_ids.append(row[54])
                            url = row[58]
                            map_filename = url.split('/')[-1].replace('%20', '_')
                            local_download_loc = os.path.join(map_pathname, map_filename)
                            row.append(local_download_loc)
                            writer.writerow(row)

    click.echo('------- FINALLY COMPLETE -------')

def init_app(app):
    # register the get-maps command with the app
    app.cli.add_command(get_maps_command)
    # register the get-metadata command with the app
    app.cli.add_command(get_metadata_command)
