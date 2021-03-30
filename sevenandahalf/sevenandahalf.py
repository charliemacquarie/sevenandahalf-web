import sqlite3

from flask import (
    Blueprint, render_template, request, current_app, url_for
)

bp = Blueprint('sevenandahalf', __name__)

@bp.route('/', methods=('GET', 'POST'))
def main():
    if request.method == 'POST':
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        conn = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        maps = c.execute('''SELECT map_name, primary_state_name,
            scale, date_on_map, local_download FROM map WHERE
            n_lat >= ? AND
            s_lat <= ? AND
            w_long <= ? AND
            e_long >= ?''', (latitude, latitude, longitude, longitude
            )).fetchall()

        conn.close()

        return render_template('index.html', maps=maps)

    return render_template('index.html')

@bp.route('/configs')
def show_configs():
    configs = []

    configs.append('Instance path: {}'.format(current_app.instance_path))
    configs.append('app.config: {}'.format(current_app.config))
    configs.append('__name__: {}'.format(__name__))
    configs.append('current_app.config: {}'.format(current_app.config))
    configs.append('static url: {}'.format(url_for('static', filename='style.css')))

    return render_template('configs.html', configs=configs)
