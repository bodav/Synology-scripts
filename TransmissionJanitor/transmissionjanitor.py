import transmissionrpc, time

HOST = "nas.local"
PORT = 9091
SLEEP_SEC = 60

while True:
    print("Connecting to transmission...")
    tc = transmissionrpc.Client(address=HOST, port=PORT)

    print("Getting torrents...")
    torrents = tc.get_torrents()

    print("Processing torrents...")

    for tor in torrents:
        print("{0}, progress: {1}".format(tor.name, tor.progress))
        progress = float(tor.progress)

        if progress == 100.0:
            print("Torrent is done removing...")
            tc.remove_torrent(tor.id)

    print("All done")

    time.sleep(SLEEP_SEC)
