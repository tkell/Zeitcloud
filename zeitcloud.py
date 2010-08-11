# TODO:  Tempo bargraph
# TODO:  Clean out middle-step entries every week or so
# TODO:  Figure out bars beats tatums sections
# TODO:  Make pretty:  links to the hot tracks, clever jokes for each tempo range
# TODO:  Add remix API.  http://code.google.com/p/echo-nest-remix/
# TODO:  Add caching
# TODO:  Add archives

import webbrowser
import time
import os
from datetime import date
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db


def ms(seconds):
    minutes = seconds / 60
    seconds -= 60*minutes
    return "%02d:%02d" % (minutes, seconds)

# Setting up a very simple info model, with our six things in it and a date field for when the job was run
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


class MainPage(webapp.RequestHandler):
    def get(self):
# Extract our data and display it
		query = MusicData.all()
		query.order('-date')
		result = query.fetch(1)[0]
		
		# this hack is required because app engine stores ints as longs, and raphael wants ints
		tempo_list = []
		for i in result.tempo_array:
			tempo_list.append(int(i))

		duration_list = []	
		for i in result.duration_array:
			duration_list.append(int(i))

		key_hist_list = []	
		for i in result.musical_key_array:
			key_hist_list.append(int(i))
		
		template_values = {
						'tempo_array' : tempo_list, 
						'tempo_min' : min(result.tempo_array),
						'tempo_mean': result.tempo_mean, 
						'tempo_mode': result.tempo_mode, 
						'tempo_median': result.tempo_median, 
						'tempo_max' : max(result.tempo_array),
						'loudness_array' : result.loudness_array, 
						'loudness_min' : min(result.loudness_array),
						'loudness_mean': result.loudness_mean, 
						'loudness_mode': result.loudness_mode, 
						'loudness_median': result.loudness_median, 
						'loudness_max' : max(result.loudness_array),
						'duration_array' : duration_list, 
						'duration_min' : ms(min(result.duration_array)),
						'duration_mean': ms(result.duration_mean), 
						'duration_mode': ms(result.duration_mode), 
						'duration_median': ms(result.duration_median), 
						'duration_max' : ms(max(result.duration_array)),						
						'musical_key_array' : key_hist_list,
						'musical_key_mode' : result.musical_key_mode,
						'musical_key_c' : key_hist_list[0],
						'musical_key_cs' : key_hist_list[1],
						'musical_key_d' : key_hist_list[2],
						'musical_key_eb' : key_hist_list[3],
						'musical_key_e' : key_hist_list[4],
						'musical_key_f' : key_hist_list[5],
						'musical_key_fs' : key_hist_list[6],
						'musical_key_g' : key_hist_list[7],
						'musical_key_ab' : key_hist_list[8],
						'musical_key_a' : key_hist_list[9],
						'musical_key_bb' : key_hist_list[10],
						'musical_key_b' : key_hist_list[11]
						}

		path = os.path.join(os.path.dirname(__file__), 'index.html')
		self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication(
                                     [('/', MainPage), 
                                     ('/index.html', MainPage)],
                                     debug=True)
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
