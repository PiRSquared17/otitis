#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Otitis - IRC bot for Wikimedia projects
# Copyright (C) 2009 Emilio José Rodríguez Posada
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" External modules """
""" Python modules """
import re
import random
import sys
import wikipedia
import time

""" Otitis modules """
import otitiscomb

""" Default bot preferences """
global preferences
preferences = {
	'botNick':       'Bot',             #Bot name
	'ownerNick':     'Owner',             #Owner nick
	'language':      'es',                #Default language is Spanish
	'family':        'wikipedia',         #Default project family is Wikipedia
	'site':          0,                    #Empty var
	'network':       'irc.freenode.net', #IRC network where is the IRC channel with recent changes
	'channel':       0,                    #RSS channel for recent changes in Wikipedia
	'nickname':      0,                    #Bot nick in channel, with random numbers to avoid nick collisions
	'port':          6667,                 #Port number
	'logsDirectory': 'botlogs/',           #Directory reverts logs
	'newbie':        25,                   #Who is a newbie user? How many edits?
	'statsDelay':    60*15,                   #How man seconds between showing stats in screen
	'colors':        {
		'sysop': 'lightblue',
		'bot':   'lightpurple',
		'reg':   'lightgreen',
		'anon':  'lightyellow',
	},
	'context':       ur'[ \@\º\ª\·\#\~\$\<\>\/\(\)\'\-\_\:\;\,\.\r\n\?\!\¡\¿\"\=\[\]\|\{\}\+\&]',
	'msg':           {},
}

""" Header message """
header  = u"\nOtitis Copyright (C) 2008 Emilio José Rodríguez Posada\n"
header += u"This program comes with ABSOLUTELY NO WARRANTY.\n"
header += u"This is free software, and you are welcome to redistribute it\n"
header += u"under certain conditions. See license.\n\n"
header += u"############################################################################\n"
header += u"# Name:    Otitis                                                          #\n"
header += u"# Version: 0.1                                                             #\n"
header += u"# Tasks:   Nothing                                                         #\n"
header += u"############################################################################\n\n"
header += u"Parameters available (* obligatory): -lang, -family, -newbie, -botnick*, -statsdelay, -network, -channel, -ownernick*\n"
header += u"Example: python otitis.py -botnick:MyBot -ownernick:MyUser\n"
wikipedia.output(header)

otitiscomb.getParameters()

#if otitiscomb.checkForUpdates():
#	wikipedia.output(u"***New code available*** Please, update your copy of AVBOT from https://forja.rediris.es/svn/cusl3-avbot/")
#	#sys.exit()

preferences['site']     = wikipedia.Site(preferences['language'], preferences['family'])
#testEdit                = wikipedia.Page(preferences['site'], 'User:%s/Sandbox' % preferences['botNick'])
#testEdit.put(u'Test edit', u'BOT - Arrancando robot') #same text always, avoid avbotcron edit panic
if not preferences['channel']:
	preferences['channel']  = '#%s-%s' % (preferences['family'], preferences['language'])
if not preferences['nickname']:
	preferences['nickname'] = '%s%s' % (preferences['botNick'], str(random.randint(1000, 9999)))

preferences['wikilangs']=otitiscomb.loadLanguages()

global trivial
trivial=False
global trivialAnswers
trivialAnswers=[]
global trivialAnswerWinner
trivialAnswerWinner=u""
global trivialTimer
trivialTimer=u""
global globalStats
globalStats={'0':{},'+1':{}}
global cloaks
cloaks={
	u'wikimedia/Melos': u'Chabacano',
	u'unaffiliated/david0811': u'David0811',
	u'Wikimedia/Dferg': u'Dferg',
	u'wikimedia/Drini': u'Drini',
	u'wikipedia/ejmeza': u'Ejmeza',
	u'wikimedia/Melos': u'Melos',
	u'wikipedia/Netito777': u'Netito777',
	u'wikipedia/Nicop': u'Nicop',
	u'wikipedia/Paintman': u'Paintman',
	u'wikipedia/Platonides': u'Platonides',
	u'wikipedia/saloca': u'Saloca',
	u'wikimedia/Taichi': u'Taichi',
	u'wikipedia/txo': u'Txo',
}
global nicks
nicks={
	u'Nixon-': u'Nixón',
}
