## About ##

Removes finished torrent from transmission
Finished as in where progress = 100%


## REQUIREMENTS ##

* transmissionrpc `easy_install transmissionrpc`


## CRON setup ##

Run every 5 minutes
*/5 * * * * root sh /volume1/scripts/TransmissionCleanup/Start_TransmissionCleanup.sh