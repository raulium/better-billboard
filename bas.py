#!/usr/local/env python

# REQ:
#	Billboard
#	flask

import billboard
import datetime
import json

from config import WUML_SECRET, MY_URL, MY_PORT, APP_PATH

from flask import Flask
from flask import request
from flask import render_template
from os import listdir
from os.path import isfile, join

app = Flask(__name__)

# def spotify_get(uri):
# 	my_user = uri.split(':')[2]
# 	my_playlist_id = uri.split(':')[4]
# 	sp_oauth = oauth2.SpotifyOAuth( WUML_ID, WUML_SECRET,scope=SCOPE,cache_path=CACHE )
# 	sp = spotipy.Spotify()
# 	data = sp.user_playlist(my_user, playlist_id=my_playlist_id)
# 	return data

# def build_database(my_dict):
# 	timeString = dto_to_string(datetime.datetime.now())
# 	print "loop starting:" + "\t" + timeString
# 	while int(timeString.split('-')[0]) >= 1952:
# 		chart = billboard.ChartData('billboard-200', date=timeString, quantize=True)
# 		update_dict(my_dict, chart, timeString)
# 		if chart.previousDate is None:
# 			print "no previous date found"
# 			timeString = dto_to_string(string_to_dto(timeString) - datetime.timedelta(days=7))
# 			print "Grabbing:" + "\t" + timeString
# 		else:
# 			timeString = chart.previousDate
# 			print "Grabbing:" + "\t" + chart.previousDate

def heal():
	current_time = datetime.date(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day)
	master_time = datetime.date(1963,8,17)
	my_dict = jload()

	print("Finding latest date in database...")

	for k in my_dict:
		if datetime.datetime.strptime(my_dict[k][1].split('/')[5], "%Y-%m-%d").date() > master_time:
			master_time = datetime.datetime.strptime(my_dict[k][1].split('/')[5], "%Y-%m-%d").date()
	print("Fetching data...")
	print("Latest Date:\t" + str(master_time))
	while master_time < current_time:
		chart = billboard.ChartData('billboard-200', date=dto_to_string(current_time), quantize=True)
		update_dict(my_dict, chart, dto_to_string(current_time))
		if chart.previousDate is None:
			print("No data found for " + str(chart.previousDate))
			current_time -= datetime.timedelta(days=7)
		else:
			print("Grabbing " + str(chart.previousDate))
			current_time = datetime.datetime.strptime(chart.previousDate, "%Y-%m-%d").date()
	print("Saving database...")
	jsave(my_dict)
	print("Database Saved!")


def weekly_update():
	timeString = dto_to_string(datetime.datetime.now())
	my_dict = jload()
	chart = billboard.ChartData('billboard-200', date=timeString, quantize=True)
	update_dict(my_dict, chart, timeString)
	jsave(my_dict)

def update_dict(my_dict, my_chart, timeString):
	for i in range(0, len(my_chart), 1):
		if str(my_chart[i].artist) in my_dict:
			if my_dict[my_chart[i].artist][0] > (i+1):
				my_dict[my_chart[i].artist] = [ i+1, 'http://www.billboard.com/charts/billboard-200/' + timeString ]
		else:
			my_dict[my_chart[i].artist] = [ i+1, 'http://www.billboard.com/charts/billboard-200/' + timeString ]
	return my_dict

def last_update():
	master_time = datetime.date(1963,8,17)
	my_dict = jload()
	for k in my_dict:
		if datetime.datetime.strptime(my_dict[k][1].split('/')[5], "%Y-%m-%d").date() > master_time:
			master_time = datetime.datetime.strptime(my_dict[k][1].split('/')[5], "%Y-%m-%d").date()
	return master_time.strftime("%B %d, %Y")

def dto_to_string(dto):
	year = dto.year
	month = zero_padding(dto.month)
	day = zero_padding(dto.day)
	my_string = str(year) + "-" + str(month) + "-" + str(day)
	return my_string


def zero_padding(num):
	if num < 10:
		return "0" + str(num)
	else:
		return str(num)


def jsave(my_dict):
	d = datetime.datetime.now()
	filename = dto_to_string(d) + '.json'
	with open(APP_PATH + "/" + filename, 'w') as fp:
		json.dump(my_dict, fp)


def jload():
	times = list()
	files = [f for f in listdir(APP_PATH) if isfile(join(APP_PATH, f))]
	for f in files:
		if '.json' in f:
			times.append(f)
	times = sorted(times)
	filename = times[len(times)-1]
	with open(APP_PATH + "/" + filename) as data_file:
		data = json.load(data_file)
	return data


def find_it(my_string):
	my_dict = jload()
	eList = list()
	cList = list()
	for i in my_dict:
		if my_string.lower() == i.lower():
			eList.append([i, my_dict[i]])
		elif my_string.lower() in i.lower():
			cList.append([i, my_dict[i]])
	return sorted(eList), sorted(cList)


@app.route('/')
def my_form():
    return render_template("search.html", first='true', time=last_update())


@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['searchBar']
    elist, clist = find_it(text)

    if len(elist) == 0 and len(clist) == 0: # No Match Found
    	return render_template('search.html', first= 'false', result='false', tested=text, time=last_update())
    if len(elist) >= 1 and len(clist) == 0: # Exact Match Found
    	return render_template('search.html', first='false', result='true', e_list=elist, tested=text, time=last_update())
    if len(elist) == 0 and len(clist) >= 1: # Partial Match Found
    	return render_template('search.html', first='false', result='true', c_list=clist, tested=text, time=last_update())
    if len(elist) >= 1 and len(clist) >= 1: # Lots of Matches Found
    	return render_template('search.html', first='false', result='true', e_list=elist, c_list=clist, tested=text, time=last_update())

@app.route('/update/', methods=['POST'])
def auto_update():
	data = request.get_json(force=True)
	if data is not None:
		app.logger.debug("JSON Recieved -- " + str(data))

		if WUML_SECRET in data["key"]:
			weekly_update()
			return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
		else:
			abort(404)
	else:
		app.logger.debug("No JSON received")
		abort(404)

@app.route('/heal/', methods=['POST'])
def auto_heal():
	data = request.get_json(force=True)
	if data is not None:
		app.logger.debug("JSON Recieved -- " + str(data))

		if WUML_SECRET in data["key"]:
			heal()
			return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
		else:
			abort(404)
	else:
		app.logger.debug("No JSON received")
		abort(404)


if __name__ == '__main__':
    app.run(debug=True, port=MY_PORT, host=MY_URL, threaded=True)
