import webbrowser
import httplib
import re
import urllib
import time
import logging
from datetime import date

from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.runtime import DeadlineExceededError

from pyechonest import config
from pyechonest import track as echo_track

# This task does the averaging math from the raw echo nest data that gets placed in the datastore

# Returns the mode of a list of integers or floats
# This loses data:  if two items are tied, it will print the larger
def find_mode(list):
    counts = {}
    for item in list:
    	temp = counts.get(item)
    	if temp == None:
    		temp = 0
        counts[item] = temp + 1
    swapcounts = dict (zip(counts.values(),counts.keys()))
    return swapcounts[max(swapcounts)]

# Finds the median, as an int.  
def find_median(theValues):
  if len(theValues) % 2 == 1:
    return theValues[(len(theValues)+1)/2-1]
  else:
    lower = theValues[len(theValues)/2-1]
    upper = theValues[len(theValues)/2]
    return int ((lower + upper) / 2)     
    
    
# per track
class TrackData(db.Model):
	date = db.DateProperty(required=True)
	tempo = db.IntegerProperty(required=True)
	loudness = db.FloatProperty(required=True)
	duration = db.IntegerProperty(required=True)
	musical_key = db.IntegerProperty(required=True)
	mode = db.IntegerProperty(required=True)
	time_sig = db.IntegerProperty(required=True)
    
    
# Per overall set of tracks
class MusicData(db.Model):
	date = db.DateProperty(required=True)
	tempo_mean = db.IntegerProperty(required=True)
	tempo_mode = db.IntegerProperty(required=True)
	tempo_median = db.IntegerProperty(required=True)
	tempo_array = db.ListProperty(int, required=True)
	loudness_mean = db.FloatProperty(required=True)
	loudness_mode = db.FloatProperty(required=True)
	loudness_median = db.FloatProperty(required=True)
	loudness_array = db.ListProperty(float, required=True)
	duration_mean = db.IntegerProperty(required=True)
	duration_mode = db.IntegerProperty(required=True)
	duration_median = db.IntegerProperty(required=True)
	duration_array = db.ListProperty(int, required=True)
	musical_key_array = db.ListProperty(int, required=True)
	musical_key_mode = db.StringProperty(required=True)
		
# Average and format properly here
echo_key_dict = {0 : 'C', 1 : 'C#', 2 : 'D', 3 : 'Eb', 4 : 'E', 5 : 'F', 6 : 'F#', 7 : 'G', 8 : 'Ab', 9 : 'A', 10 : 'Bb', 11 : 'B'}
	

try:
	logging.info("Averaging data...")		
	query = TrackData.all()
	query.order('-date')
	results = query.fetch(25)
	
	tempo_array = []
	loudness_array = []
	duration_array = []
	key_array = []
	
	for result in results:
		tempo_array.append(int(result.tempo))
		loudness_array.append(result.loudness)
		duration_array.append(result.duration)
		key_array.append(result.musical_key)

	
	tempo_array.sort()	
	tempo_mean = int(sum(tempo_array) / len(tempo_array))
	tempo_mode = find_mode(tempo_array)
	tempo_median = find_median(tempo_array)
	
	loudness_array.sort()
	loudness_mean = round(sum(loudness_array) / len(loudness_array), 3)
	loudness_mode = find_mode(loudness_array)
	loudness_median = find_median(loudness_array)
	
	duration_array.sort()
	duration_mean = int(sum(duration_array) / len(duration_array))
	duration_mode = find_mode(duration_array)
	duration_median = find_median(duration_array)
	
	key_hist = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
	musical_key_mode = echo_key_dict[find_mode(key_array)]
	for k in key_array:
		key_hist[k] = key_hist[k] + 1

	
	# now we dump these into the final object in the database
	current_data = MusicData(
							date = date.today(), 
							tempo_mean = tempo_mean, 
							tempo_mode = tempo_mode, 
							tempo_median = tempo_median, 
							tempo_array = tempo_array, 
							loudness_mean = loudness_mean, 
							loudness_mode = loudness_mode, 
							loudness_median = loudness_median, 
							loudness_array = loudness_array, 
							duration_mean = duration_mean, 
							duration_mode = duration_mode, 
							duration_median = duration_median, 
							duration_array = duration_array, 
							musical_key_array = key_hist,
							musical_key_mode = musical_key_mode
							)
	db.put(current_data)
except DeadlineExceededError:
	logging.warning("Url processing has been canceled due to Deadline Exceeded")
	for name in os.environ.keys():
		logging.info("%s = %s" % (name, os.environ[name]))	