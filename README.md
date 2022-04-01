# Seven And A Half

sevenandahalf is a web app that uses your location to show you the USGS topographic maps covering where you are. It is built using [Flask](https://flask.palletsprojects.com/en/2.1.x/)

The "original" sevenandahalf is designed to work on a local network that's not connected to the internet. But I decided to make one to just exist on the internet too (that's this one). It works slightly differently, because it just links directly to the maps on USGS servers rather than copying them to its own server, which would be unnecessary.

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

One problem you are likely to encounter is that the wsgi script may not be using the correct version of python (you made a virtual environment, which contains the python you need to use -- this script won't be running in that environment). You can edit the script above to, using the sys and os libraries, check which python it's using, and change it to the virtual environment python if it's not using that one. Again, how you choose do do this may vary, but you are frequently wanting to check the sys.executable() or sys.prefix() and generate a new path for the system to use for python (which points to the virtual environment python)

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

Download some map metadata with the get-metadata command. (Note that this command, if run with the entire maps list (topomaps_all.csv) may take a long-time to run, on the order of several hours, depending on how many computing resources you have access to on your server.)
> bash:
```
flask get-metadata ./topomaps_all.csv
```

Initialize the database for the maps you downloaded
> bash:
```
flask init-db
```

Your site should now be ready to visit!

### Setup the secret key in the config file

Follow directions at (https://flask.palletsprojects.com/en/2.1.x/tutorial/deploy/#configure-the-secret-key)
