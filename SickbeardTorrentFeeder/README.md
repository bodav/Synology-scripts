## About ##

finds missing or backlogged episodes and adds them to transmission

## REQUIREMENTS ##

* transmissionrpc `easy_install transmissionrpc`

## CRON ##

Run every 3rd hour  
0 */3 * * * root sh /volume1/scripts/SickbeardTorrentFeeder/feeder_start_missing.sh