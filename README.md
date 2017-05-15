# better-billboard
Simple Flask application which scrubs the Billboard 200 and affords a usable search function.  Basic functionality provides a user search, but an API† to update and 'heal' the database to stay up to date.

† - Note, the API requires a simple key (setup in the following section) to authenticate requests.

## Setup
Add a config.py file to the main program directory, with the following:

```python
#!/usr/local/env python

WUML_SECRET = 'YOUR KEY HERE'
MY_URL = '0.0.0.0'
MY_PORT = 54321
APP_PATH = 'PARENT-PATH-TO-APPLICATION-FOLDER-ON-SERVER'
```
* WUML_SECRET:  The key you plan to use to authenticate administrative functions to the API
* MY_URL: The IP or URL of the application when it runs.
  * This example is the default, localhost (0.0.0.0)
* MY_PORT: The port number the application will run on
  * This example is the default, 54321
* APP_PATH: The folder/parent path to the application on the server

#### Dependencies
* [Billboard](https://github.com/guoguo12/billboard-charts)
* [Flask](http://flask.pocoo.org/)

## API

#### Update
* Type: POST
* Funciton: Forces the application to perform an update for the last 7 days.  It will scrub the billboard website for the last 7 days of chart records and incorporate into its json flat-file database.
* Example:
```
curl -H "Content-Type: application/json" -sX POST -d '{"key":"YOUR KEY HERE"}' http://URL-TO-THE-APPLCIATION:MY_PORT/update/
```

#### Heal
* Type: POST
* Function: Forces the application to find the latest chart record, and attempt to update the json flat-file database from that date to present.
* Example:
```
curl -H "Content-Type: application/json" -sX POST -d '{"key":"YOUR KEY HERE"}' http://URL-TO-THE-APPLCIATION:MY_PORT/heal/
```
