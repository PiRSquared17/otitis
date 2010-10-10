#!/usr/bin/python
# MIT License: bryan, emijrp

import sys, socket, time, os, thread, re

conn = None
server = 'irc.freenode.net'
channel = '#wikimedia-fundraising'
feedhistory = []

os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

#todo: avoid flooding, avoid publish items with date < last one

def feed():
	global feedhistory
	
	while True:
		time.sleep(60)
		url = 'http://wikimediafoundation.org/w/index.php?title=Special:ContributionHistory'
		os.system('wget "%s" -O donorsfeed.html > /dev/null 2> /dev/null' % (url))
		f = open('donorsfeed.html', 'r')
		raw = f.read()
		f.close()
		
		#<tr><td class="left  alt"><a name="529885"></a><a href="http://wikimediafoundation.org/wiki/Special:ContributionHistory?offset=1286707692#529885"><strong>John Sneevang</strong><br />Please join me in donating fonds for the much valued and used Wikipedia</a></td><td class="left  alt" style="width: 100px;">10:48, 10 October 2010</td><td class="right  alt" style="width: 75px;"><span title="USD 35.00">USD 35.00</span></td></tr>
		regexp = ur'(?i)<tr><td class="left[^>]*?"><a name="\d+"></a><a href="(?P<permalink>[^>]*?)"><strong>(?P<donor>[^<]*?)</strong>(<br />(?P<message>[^<]*?))?</a></td><td class="left[^>]*?>(?P<date>[^<]*?)</td><td class[^>]*?><span[^>]*?>(?P<donation>[^<]*?)</span></td></tr>'
		c = re.findall(regexp, raw)
		m = re.compile(regexp).finditer(raw)
		feed = []
		for i in m:
			feed.append([i.group('donor'), i.group('message'), i.group('date'), i.group('donation'), i.group('permalink')])
		feed.reverse()
		for feeditem in feed:
			if feeditem not in feedhistory:
				feedhistory.append(feeditem)
				if len(feedhistory) >= len(c):
					#print feeditem
					if feeditem[1]:
						msg = '[%s] "%s" by %s (%s) %s' % (feeditem[3], feeditem[1], feeditem[0], feeditem[2], feeditem[4])
					else:
						msg = '[%s] by %s (%s) %s' % (feeditem[3], feeditem[0], feeditem[2], feeditem[4])
					conn.send('PRIVMSG %s :%s\r\n' % (channel, msg))

def run():
	global server, channel, conn
	
	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	conn.connect((server, 6667))

	nick = 'donorsfeed'
	conn.sendall('USER %s * * %s\r\n' % (nick, nick))
	conn.sendall('NICK %s\r\n' % nick)
	conn.sendall('JOIN %s\r\n' % channel)
	
	#feed
	thread.start_new_thread(feed, ())
	
	buffer = ''
	while True:
		if '\n' in buffer:
			line = buffer[:buffer.index('\n')]
			buffer = buffer[len(line) + 1:]
			line = line.strip()
			print >>sys.stderr, line

			data = line.split(' ', 3)
			if data[0] == 'PING':
				conn.sendall('PONG %s\r\n' % data[1])
			elif data[1] == 'PRIVMSG':
				nick = data[0][1:data[0].index('!')]
				target = data[2]
				message = data[3][1:]
				"""if target == channel:
					if message.startswith('\x01ACTION'):
						log('* %s %s' % (nick, message[8:]))
					else:
						log('<%s>\t%s' % (nick, message))"""
		else:
			data = conn.recv(1024)
			if not data: raise socket.error
			buffer += data

def main():
	while True:
		try:
			run()
		except socket.error, e:
			print >>sys.stderr, 'Socket error!', e

if __name__ == '__main__':
	main()
