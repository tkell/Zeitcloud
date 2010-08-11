#Zeitcloud cron:  inster SC URL requests into the queue for processing by echo nest
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db
import logging
from datetime import date

class SoundCloudUrl(db.Model):
	date = db.DateProperty(required=True)
	stream_url = db.StringProperty(required=True)

# First, get soundcloud URLS into the DB, one at a time, to some given offset
logging.info("Beginnng backend update:  fetching SC urls for processing")

# get a URL out of the database.
query = SoundCloudUrl.all()
query.order('-date')
results = query.fetch(25)



for result in results:
	taskqueue.add(url='/process', method='get', params={'stream_url': result.stream_url})
