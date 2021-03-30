import sqlite3
import csv

import click
from flask import current_app
from flask.cli import with_appcontext

def init_db():
    conn = sqlite3.connect(
        current_app.config['DATABASE'],
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    c = conn.cursor()

    # read in file to clear any existing data and make empty table
    with current_app.open_resource('schema.sql') as f:
        c.executescript(f.read().decode('utf-8'))

    # read in csv file with map data
    maps = []
    with current_app.open_resource('initialize.csv', 'r') as csvf:
        reader = csv.reader(csvf)
        for row in reader:
            maps.append(row)

    # insert map data to db and close the connection
    c.executemany('''INSERT INTO map VALUES (?,?,?,?,?,?,?,?,?,?,?,?,
    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,
    ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', maps)
    conn.commit()
    conn.close()

# create the init-db command
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new map table"""
    init_db()
    click.echo('Initialized the map database.')

def init_app(app):
    # register the db init command with the app
    app.cli.add_command(init_db_command)
