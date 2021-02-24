import os
from flask import Flask, render_template, request

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATABASE=os.path.join(app.instance_path, 'maps.sqlite')
)

try:
    os.makedirs(app.instance_path)
except OSError:
    pass

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

    return render_template('config.html', configs=configs)

if __name__ == '__main__':
    app.run()
