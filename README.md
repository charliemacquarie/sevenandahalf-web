# Seven And A Half

sevenandahalf is a web app that uses your location to show you the USGS topographic maps covering where you are. It is built using [Flask](https://flask.palletsprojects.com/en/2.1.x/)

The "original" sevenandahalf is designed to work on a local network that's not connected to the internet. But I decided to make one to just exist on the web too.

sevenandahalf also includes a script to read a .csv file of maps, specify which ones you want using a year cutoff, a US State list, or a bounding box, download the maps, and initialize the app database with that data to allow you to access the maps.

To run, this app requires an apache2 webserver configured to use the WSGI standard.

## Initial setup for sevenandahalf
Create a virtual environment in which to install the app.
> bash:
```
python3 -m venv venv
```

Activate the environment you just created.
> bash:
```
source venv/bin/activate
```

Install sevenandahalf into the virtual environment:
> bash:
```
pip install https://charliemacquarie.com/software/sevenandahalf/dist/sevenandahalf-1.2.0-py3-none-any.whl
```

## Create the proper files for whatever will be your WSGI service
This can vary a lot by service type, so you'll need to figure out what's the right process for you.

Generally, you're going to have some kind of python script that calls sevenandahalf and serves it as the wsgi application. Usually, this will look something like this:
> python:
```
import sevenandahalf

application = sevenandahalf.create_app()
```

## Setup sevenandahalf!
Tell the system what/where the flask app is to use the setup processes.
> bash:
```
export FLASK_APP=sevenandahalf
```

Go get a list of all the USGS topographic maps to use to initialize your sevenandahalf
> bash:
```
wget https://charliemacquarie.com/librarystorage/resources/topomaps_all.zip
unzip topomaps_all.zip
```

the resulting csv file `topomaps_all.csv` will be the file you should use with the get-maps command.

Download some map metadata with the get-metadata command.
> bash:
```
flask get-metadata ./topomaps_all.csv
```

Initialize the database for the maps you downloaded
> bash:
```
flask init-db
```

Your site should now be ready to visit! https://192.168.1.153 in a browser on my network, yours may vary.

### Setup the secret key in the config file

Follow directions at (https://flask.palletsprojects.com/en/2.1.x/tutorial/deploy/#configure-the-secret-key)
