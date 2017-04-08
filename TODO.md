TODO
===

fomoclient
---
* Replace RaspPis with Pi3s
* Extend HDMI ports to create external plug
* Extend USBs ports to create external plug
* Make clear instructions on setting up new wifi network
* When clients report, have them report their count

shared
---
* Take shared configs and combine
* Take shared constants and functions and combine (debug setup, database init, etc)
* Document server setup

fomoserver
---`
* Make ability to reset client count when they check-in
* Add to status: fomofetch run status
* Add to status: client count and server count for each category
* Add to status: last several lines of fomofetch.log and fomoserver.log
* Make sure we only report on approved msgtypes
* Figure out what conditions clients should automatically reset (maybe when any clients report count higher than server's count)
* Write count out as JSON rather than uh, whatever weird format it is in

fomofetch
---
* Copy init.d script into repo
* Make sure fomofetch respawns if it dies
* Make sure we ignore anything that isn't an approved msgtypes
* Confirm that prune is working


