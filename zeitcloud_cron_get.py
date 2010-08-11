#Zeitcloud cron:  inserts SC URL requests into the queue.  
from google.appengine.api.labs import taskqueue
import logging

# First, get soundcloud URLS into the DB, one at a time, to some given offset
logging.info("Beginning database update:  fetching SC urls")
for i in range(0, 25):
	taskqueue.add(url='/get', method='get', params={'offset': i})
