# This task gets the URLS from SC

import webbrowser
from google.appengine.ext import db
import logging
import os
import datetime
from datetime import date
import wsgiref.handlers    
from google.appengine.runtime import DeadlineExceededError
from google.appengine.ext import webapp
import scapi

class SoundCloudUrl(db.Model):
	date = db.DateProperty(required=True)
	stream_url = db.StringProperty(required=True)

	
class SCURLUpdate(webapp.RequestHandler):
  def get(self):	
	# Connect to SoundCloud, publically
	try:
		logging.info("Fetching SC url...")
		API_HOST = "api.soundcloud.com"
		CONSUMER = "74CAKi2MhN6FIIUgR5YnA"
		oauth_authenticator = scapi.authentication.OAuthAuthenticator(CONSUMER)
		root = scapi.Scope(scapi.ApiConnector(host=API_HOST, authenticator=oauth_authenticator))
		
		# Now, we can start talking to SoundCloud:
		offset = self.request.get('offset')
		daystr = (date.today() - datetime.timedelta(1)).strftime('%Y-%m-%d')
		querystr = '?order=hotness&created_at[from]=' + daystr + '+00:00:00' + '&duration[to]=612000&limit=1&offset=' + offset
		
		tracks = root.tracks(querystr)
		
		#Stores directly in databse
		for track in tracks:	
			if type(track.stream_url) == type(unicode()):
				current_url = SoundCloudUrl(date = date.today(), stream_url = track.stream_url)
				db.put(current_url)
				
	except DeadlineExceededError:
		logging.warning("SC url fetch has been canceled due to Deadline Exceeded")
		
def main():
 	wsgiref.handlers.CGIHandler().run(webapp.WSGIApplication([('/get', SCURLUpdate),]))            
      
if __name__ == '__main__':
  main()