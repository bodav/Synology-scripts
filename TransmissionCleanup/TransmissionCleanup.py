import transmissionrpc

TRANSMISSION_IP = "192.168.0.105"
TRANSMISSION_PORT = 9091

if __name__ == "__main__":
	print "Strating transmission cleanup..."

	print "Connecting to transmission server..."
	tc = transmissionrpc.Client(address=TRANSMISSION_IP, port=TRANSMISSION_PORT)

	print "Getting torrents..."
	torrents = tc.get_torrents()

	print "Processing..."

	for tor in torrents:
		print "{0}, progress: {1}".format(tor, tor.progress)
		progress = float(tor.progress)

		if progress == 100.0:
			print "Torrent is done deleting..."
			tc.remove_torrent(tor.id)

	print "All done"