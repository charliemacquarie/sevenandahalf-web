import os
import sqlite3
import csv

import click
from flask import (
    Flask, render_template, request, current_app
)
from flask.cli import with_appcontext

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'maps.sqlite')
)

# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass

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

# register the db init command with the app
app.cli.add_command(init_db_command)

@app.route('/', methods=('GET', 'POST'))
def main():
    if request.method == 'POST':
        latitude = request.form['latitude']
        longitude = request.form['longitude']
        coords = (latitude, longitude)

        return render_template('index.html', coords=coords)

    return render_template('index.html')

app.add_url_rule('/', endpoint='index')

@app.route('/config')
def show_configs():
    configs = []

    configs.append('Instance path: {}'.format(app.instance_path))
    configs.append('app.config: {}'.format(app.config))
    configs.append('__name__: {}'.format(__name__))
    configs.append('current_app.config: {}'.format(current_app.config))

    return render_template('config.html', configs=configs)

if __name__ == '__main__':
    app.run()
