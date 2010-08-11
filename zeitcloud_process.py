import webbrowser
import httplib
import re
import urllib
import time
import logging
import os
from datetime import date
import wsgiref.handlers  

from google.appengine.api import urlfetch
from google.appengine.ext import db
from google.appengine.runtime import DeadlineExceededError  
from google.appengine.ext import webapp

from pyechonest import config
from pyechonest import track as echo_track

# Helper Functions:  
# Search for echonest_param in the given xml_string.  Only valid for analysis parsing, not URL extraction
def get_echo_data(xml_string, echonest_param):
	pattern = '(<' + echonest_param + '.*?>)(.*)(</' + echonest_param + '>)'
	m = re.search(pattern, xml_string)
	if m != None:
		return m.group(2)
	else:
		return 0

class SoundCloudUrl(db.Model):
	stream_url = db.StringProperty(required=True)				

# this is for each TRACK
class TrackData(db.Model):
	date = db.DateProperty(required=True)
	tempo = db.IntegerProperty(required=True)
	loudness = db.FloatProperty(required=True)
	duration = db.IntegerProperty(required=True)
	musical_key = db.IntegerProperty(required=True)
	mode = db.IntegerProperty(required=True)
	time_sig = db.IntegerProperty(required=True)

# Adds a version header to our requests, should make Echo Nest happy.
class AppURLopener(urllib.FancyURLopener):
    version = "ZeitCloud 0.0"
urllib._urlopener = AppURLopener()	
	
class EchoNestProcess(webapp.RequestHandler):
  def get(self):	
	try:
		logging.info("Processing url with Echonest")
		# Create a connection to EchoNest
		echo_key = 'WOUHTN44BMS5SMPF2'
		echo_version = '3'
		config.ECHO_NEST_API_KEY="WOUHTN44BMS5SMPF2" 
		echo_id = []
		
		# Do the processing
		stream_url = self.request.get('stream_url')
		params = urllib.urlencode({'api_key': echo_key, 'url': stream_url, 'version': echo_version})
		url_string = "http://developer.echonest.com/api/upload?%s" % params
		r = urlfetch.fetch(url = url_string, deadline = 10)
		m = re.search('(<track id=")(.*)(" md5)(.*)(">)', r.content)
		
		t = echo_track.Track(m.group(2))
		
		tempo = (int(t.tempo['value']))
		loudness = (float(t.loudness))
		duration = (int(t.duration))
		time_sig = (int(t.time_signature['value']))
		mode =(int(t.mode['value']))
		key = (int(t.key['value']))
		
		# Write to DB
		current_data = TrackData(date = date.today(), tempo = tempo, loudness = loudness, duration = duration, musical_key = key, mode = mode, time_sig = time_sig)
		db.put(current_data)
		
	except DeadlineExceededError:
		logging.warning("Url processing has been canceled due to Deadline Exceeded")
		for name in os.environ.keys():
			logging.info("%s = %s" % (name, os.environ[name]))
	
def main():
  wsgiref.handlers.CGIHandler().run(webapp.WSGIApplication([('/process', EchoNestProcess),]))            
      
if __name__ == '__main__':
  main()		