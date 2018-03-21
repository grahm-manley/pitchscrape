# Pitchscrape 

Pitchscrape is a webservice to keep an updated database of 
[Pitchfork.com](www.pitchfork.com) album reviews, developed to be used
by pitchify (A chrome extension to add 
pitchfork reviews to the spotify web player).

## Getting Started


### Prerequisites

I would recommend using [pyenv](https://github.com/pyenv/pyenv) to keep
your python dependencies and versions separate. Install a 3.6.0 version of 
python and then install the dependencies which are listed in the 
requirements.txt file with the following command. 

```
pip3 install -r requirements.txt
```

You will also need a running instance of a MySQL database that the system
can save the reviews to. 

### Installing

In [config.py](./pitchscrape/core/config.py) you can change the database 
configurations to point to your MySQL instance and change logging 
configurations if necessary. 

That should be it!

Now to run the scraper just make sure you in the correct python environment
and that your MySQL instance is running. Then run the following command.

```
python3 scraper.py
```

Once you have data in your database you can start the webservice 
using the command 

```
python3 app.py
```

#### To Do list for future development:
* Better exception handling and system to keep track of which review saves fail
* A better command line interface possibly using [click](click.pocoo.org/5/)
* Test cases for components that do not currently have them
* Better documentation for interfacing with the system


