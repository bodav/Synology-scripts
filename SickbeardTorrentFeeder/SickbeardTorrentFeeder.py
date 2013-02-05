import transmissionrpc, urllib, urllib2, json, argparse, gzip
import xml.etree.ElementTree as ET
from StringIO import StringIO

#Config
SICKBEARD_API_URL = "http://192.168.0.105:8081/api/"
SICKBEARD_API_KEY = "7ed841267291e081f6981b5918e8c8a3"
EZTV_FEED_URL = "http://feeds.feedburner.com/eztv-rss-atom-feeds?format=xml"
KATPH_BASE_URL = "http://kat.ph/usearch/"
TRANSMISSION_IP = "192.168.0.105"
TRANSMISSION_PORT = 9091


def get_missed_episodes():
	print "Getting missed episodes from Sickbeard"
	api = SickbeardApi(SICKBEARD_API_URL, SICKBEARD_API_KEY)
	missed = []
	for episode in api.get_future_missed()["data"]["missed"]:
		missed.append(WantedEpisode(episode["show_name"], episode["season"], 
			episode["episode"], episode["quality"]))

	print "Found {0} missed episodes".format(len(missed))
	return missed


def get_backlogged_episodes():
	print "Getting backlogged episodes from Sickbeard"
	api = SickbeardApi(SICKBEARD_API_URL, SICKBEARD_API_KEY)
	backlogged = []
	shows = api.get_all_shows()["data"]

	for showKey in shows:
		print "Getting seasons for show: " + shows[showKey]["show_name"]
		seasons = api.get_show_seasons(showKey)["data"]

		for seasonKey in seasons:
			for episodeKey in seasons[seasonKey]:
				if seasons[seasonKey][episodeKey]["status"] == "Wanted":
					print "Found wanted episode: S{0}E{1}".format(seasonKey, episodeKey)
					backlogged.append(WantedEpisode(shows[showKey]["show_name"], seasonKey, episodeKey, 
						seasons[seasonKey][episodeKey]["quality"]))

	return backlogged


class SickbeardApi(object):
	def __init__(self, url, key):
		self.url = url
		self.key = key

	def get_future_missed(self):
		return self._get("future", **{"type": "missed", "paused": "0"})

	def get_all_shows(self):
		return self._get("shows", **{"paused": "0"})

	def get_show_seasons(self, show_tvdbid):
		return self._get("show.seasons", **{"tvdbid": show_tvdbid})

	def _get(self, cmd, **kwargs):
		url =  "{0}{1}/?cmd={2}&{3}".format(self.url, self.key, cmd, urllib.urlencode(kwargs))
		print "SBAPI: Requesting " + url
		data = urllib2.urlopen(url).read()
		return json.loads(data)


class WantedEpisode(object):
	def __init__(self, showName, seasonNo, episodeNo, quality):
		self.showName = showName
		self.seasonNo = str(seasonNo)
		self.episodeNo = str(episodeNo)
		self.quality = quality

	def get_episode_title(self):
		return "{0} S{1} E{2}".format(self.showName, self.seasonNo, self.episodeNo)

	def get_search_strings(self):
		#show name SxxExx
		#show name xxXxx
		str1 = "{0} S{1}E{2}".format(self.showName, self.seasonNo.zfill(2), self.episodeNo.zfill(2))
		str2 = "{0} {1}x{2}".format(self.showName, self.seasonNo, self.episodeNo.zfill(2))
		return (str1, str2)

	def get_quality(self):
		if self.quality == "HD":
			return "720p"
		else:
			return "HDTV"


class FeedItem(object):
	def __init__(self, title, uri):
		self.title = title
		self.uri = uri


def find_missed_episodes():
	print "Finding missed episodes"
	missed = get_missed_episodes()
	eztvfeed = get_eztv_feed()

	for episode in missed:
		print "trying to find torrent for: " + episode.get_episode_title()

		searchStr1, searchStr2 = episode.get_search_strings()
		for item in eztvfeed:
			quality = episode.get_quality()
			
			if searchStr1 in item.title or searchStr2 in item.title:
				if quality == "HDTV" and quality in item.title and "720p" not in item.title:
					print "Found match: " + item.title
					send_to_transmission(item.uri)
					break
				elif quality == "720p" and quality in item.title:
					print "Found match: " + item.title
					send_to_transmission(item.uri)
					break



def find_backlogged_episodes():
	print "Finding backlogged episodes"
	backlog = get_backlogged_episodes()

	for episode in backlog:
		print "trying to find torrent for: " + episode.get_episode_title()
		feed = get_katph_feed(episode.showName, episode.seasonNo, episode.episodeNo)
		searchStr1, searchStr2 = episode.get_search_strings()

		for item in feed:
			quality = episode.get_quality()
			
			if searchStr1 in item.title or searchStr2 in item.title:
				if quality == "HDTV" and quality in item.title and "720p" not in item.title:
					print "Found match: " + item.title
					send_to_transmission(item.uri)
					break
				elif quality == "720p" and quality in item.title:
					print "Found match: " + item.title
					send_to_transmission(item.uri)
					break


def get_eztv_feed():
	data = urllib2.urlopen(EZTV_FEED_URL).read()
	root = ET.fromstring(data)
	items = []
	for item in root.iter("item"):
		if item.find("link").text.startswith("magnet"):
			items.append(FeedItem(item.find("title").text, item.find("link").text))

	return items


def get_katph_feed(show_name, season, episode):
	#build kat.ph uri
	#ex. http://kat.ph/usearch/%22Futurama%22%20category%3Atv%20season%3A7/?rss=1
	url = KATPH_BASE_URL + urllib.quote('{0} ettv OR vtv OR eztv OR FQM category:tv season:{1} episode:{2}/?rss=1'.format(show_name, season, episode))
	print "feed url: " + url

	items = []
	#magnet:?xt=urn:btih:L2MAGQD6ZXN36CSZYLDDTGZMYNOROILG
	try:
		#data is gzip'ed unzip to read xml
		zipData = urllib2.urlopen(url).read()
		buf = StringIO(zipData)
		data = gzip.GzipFile(fileobj=buf).read()

		root = ET.fromstring(data)
		for item in root.iter("item"):
			items.append(FeedItem(item.find("title").text, "magnet:?xt=urn:btih:" + item.find("hash").text))
	except:
		print "No items in feed!"

	return items


def send_to_transmission(url):
	print "Sending to transmission: " + url
	tc = transmissionrpc.Client(address=TRANSMISSION_IP, port=TRANSMISSION_PORT)

	try:
		tc.add_torrent(url)
	except:
		print "Torrent already added to transmission"




if __name__ == "__main__":
	# Set up and gather command line arguments
    parser = argparse.ArgumentParser(description="Search for missed/backlogged Sickbeard episodes and feed them to transmission")
    parser.add_argument('-m', '--missed', action='store_true', help='Search for missed episodes')
    parser.add_argument('-b', '--backlog', action='store_true', help='Search for backlogged episodes')
    
    args = parser.parse_args()

    if args.missed:
    	print "Starting search for missed episodes"
    	find_missed_episodes()


    if args.backlog:
    	print "Starting search for backlogged episodes"
    	find_backlogged_episodes()

