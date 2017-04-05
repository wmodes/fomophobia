FOMOphobia
===
Concept
---
FOMOphobia is a network-connected installation that immerses the
viewer in a visualization of the artist's real-time social
networking anxiety, sounding alarms and keeping count of unhandled
content. 

Fear Of Missing Out (FOMO) is a form of social anxiety described as "a
compulsive concern that one might miss an opportunity for social
interaction, a novel experience, or other satisfying event." FOMO is
the result of our bombardment by modern networking, more insidious
because we take an active part in it, simultaneously stressed out
about and perpetuating our own addiction.

FOMOphobia brings this private guilt to the surface with glaring
numeric displays and alarm bells. It exposes the artist's social
networking burden and addiction, revealing both the accumulation and
content of his social media messages. FOMOphobia provokes viewers to
re-weigh the value of their relentless connectedness.

Like social media itself, FOMOphobia simultaneously attracts and
repels. The installation features individual monitors for each of the
artist's most insistent social media and chairs inviting the
visitor to become immersed in the piece.  Each monitor consists of a
prominent numeric LED counter of the number of unread or unhandled
items, paired with a clangorous electric bell that sounds whenever the
number increments. A single line LED display scrolls through messages
as they are received exposing the content of the artist's social
networking.

At the debut of FOMOphobia there were five individual pieces
representing Twitter, Facebook, email, sms/voicemail, and rss feeds
(blog reader). Each piece consisted of a two-by-two foot wooden
medallion of white mahogany inlaid into golden oak replicating in
large-scale the familiar iPhone icons, a large red LED numeric display
showing the number of unread messages inset into the upper right
corner (also calling to mind the badge notifications on an iPhone), a
red alphanumeric display along the bottom displaying incoming
messages, and a red alarm bell hung above the piece.

As each message arrived, the corresponding piece rang for
several seconds, the number of unread messages would be updated, and
the message, sms, email, or tweet would be displayed.

Software
---
**Organization**
* fomoclient runs on clients; retrieves data from server via https
* fomofetch runs on server; retrieves, processes data, and stores in mysql db
* fomoserver runs on server; serves data to clients via https
* A special gmail account is used as a Data Warehouse

**Content Data Storage**
* Database app serves data through CGI (or node.js) and https
* System has to track state to ensure multiple installations can draw from database without conflict
* FOMOclient is responsible for remembering state
* FOMOclient specifies last content ID retrieved (+1) and type of content needed

**Display and timing**
* FOMOclient retrieves unread count
    * If new count is greater than old count, change and flash numerical display and ring bell.
    * If new count is less than or equal old count, change numerical display
* FOMOclient retrieves content data
    * New content interrupts old queued content.
    * If there is new content, queue new content for display
    * If no new content, do nothing.
    * End of queued content is held briefly then blanks

**Pacing**
To provide interesting pacing as data is placed in the data store, clients get each message 
one by one:  1) check every X seconds for new content, 2) get one message, 3) increment 
the counter by one 4) ring the bell to announce new content, 5) display the content on the 
alpha LED, 6) wait a delay between 0 and Z second, and 7) immediately, check for new content, 
lapsing into (1) if no content is available.  

**Garbage Collection**
The FOMOserver immediately deletes content from the Data Warehouse as soon as it retreives it. The
fomoserver deletes content over a fixed age.

Networking
---
The clients connect to a local router for which they know the SSID and password. This router can be
connected to an ethernet drop or to another router which serves as a client bridge to the WAN wireless
router.

Clients
---
**Self-Test**
When clients power up, they display a visible self-test:
* wifi network status
* outside connection status
* connection to server status

**Access to clients**
With this configuration, the fomo clients are assigned DHCP by the WAP router, so there is no telling how
they will be IP'd. One way to find likely candidates is to

wmodes$ nmap -sP 192.168.0.1/24

where I found them assigned as a suspicious block of 5 ajoining IPs.

They are accessible via ssh.

**Logs**
The clients (and the server) write their logs to /var/log/fomo.log

Installation
===
For the fomo server, use a server that is continuously up and has access to python, pip, etc. (This ruled
out a Gandi Simple Hosting solution.) I used Debian, so adjust as necessary..

    git clone https://github.com/wmodes/fomophobia.git
    cd fomophobia

Make logs writable:

    chown `whoami` /var/log/

Install dependencies:

    sudo apt-get install python-mysqldb python-flask
    pip install -r requirements.txt

FOMOfetch Service Installation
---
Test fetch:

    cd ~/fomophobia/fomofetch
    python fomofetch.py &
    less /var/log/fomo.log

If everything seems to be working, create fomofetch as service:

    cd ~/fomophobia/init.d
    sudo cp fomofetch /etc/init.d/
    sudo chmod 755 /etc/init.d/fomofetch
    sudo update-rc.d fomofetch defaults
    sudo /etc/init.d/fomofetch start
    less /var/log/fomo.log

FOMOserver Instalation
---
Test server:

    cd ~/fomophobia/fomoserver
    python fomoserver.py
    less /var/log/fomo.log

TODO: Flask installation
