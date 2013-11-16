import transmissionrpc, config, feeds, sickbeard, time



def find_missed_episodes():
    print("Finding missed episodes...")
    missed = sickbeard.get_missed_episodes()

    if len(missed) == 0:
        print("No missed episodes")
        return

    feed = feeds.get_combined_feeds()

    for episode in missed:
        print("Trying to find torrent for: {0}".
            format(episode.get_title()))

        for item in feed:
            if episode.matches_title_and_quality(item.title):
                print("Found matching episode in feed {0}, with title: {1}".
                    format(item.source, item.title))
                download(item.uri)
                break



def find_backlogged_episodes():
    print("Finding backlogged episodes")
    backlog = sickbeard.get_backlogged_episodes()

    for episode in backlog:
        print("Trying to find torrent for: " + episode.get_title())
        feed = feeds.search_katph_feed(episode.showname, 
            episode.season, episode.episode)

        for item in feed:
            if episode.matches_title_and_quality(item.title):
                print("Found matching episode in feed {0}, with title: {1}".
                    format(item.source, item.title))
                download(item.uri)
                break




def download(uri):
    print("Adding episode to transmission, uri: " + uri)
    client = transmissionrpc.Client(
        address=config.TRANSMISSION_HOST, 
        port=config.TRANSMISSION_PORT)

    try:
        client.add_torrent(uri)
    except Exception as ex:
        print("Error adding torrent to transmission, Error: {0}".format(ex))




if __name__ == "__main__":
    try:
        while True:
            find_missed_episodes()
            find_backlogged_episodes()

            print("Going to sleep for {0}secs".format(config.SLEEP_TIME_SECS))
            time.sleep(config.SLEEP_TIME_SECS)
    except KeyboardInterrupt:
        print("Interrupted, exiting...")
