import os
import sqlite3

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

try:
    os.makedirs(app.instance_path)
except OSError:
    pass

def init_db():
    conn = sqlite3.connect(current_app.config['DATABASE'])
    c = conn.cursor()

    with current_app.open_resource('schema.sql') as f:
        c.executescript(f.read().decode('utf-8'))

@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear existing data and create new map table"""
    init_db()
    click.echo('Initialized the database.')

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
