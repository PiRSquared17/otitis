#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Otitis - IRC bot for Wikimedia projects
# Copyright (C) 2008 Emilio José Rodríguez Posada
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

import wikipedia
import re
import datetime
import time
import random
import sys
import urllib

# Otitis modules
import otitisglobals

def encodeLine(line):
	""" Codifica una cadena en UTF-8 a poder ser """
	""" Encode string into UTF-8 """
	
	try:
		line2=unicode(line,'utf-8')
	except UnicodeError:
		try:
			line2=unicode(line,'iso8859-1')
		except UnicodeError:
			print u'Unknown codification'
			return ''
	return line2

def getParameters():
	""" Gestionar parámetros capturados de la consola """
	""" Manage console parameters """
	args=sys.argv
	
	obligatory=2
	for arg in args[1:]:
		if arg.startswith('-lang'):
			if len(arg) == 5:
				otitisglobals.preferences['language'] = wikipedia.input(u'Please enter the language (es, en, de, fr, ...):')
			else:
				otitisglobals.preferences['language'] = arg[6:]
		elif arg.startswith('-family'):
			if len(arg) == 7:
				otitisglobals.preferences['family'] = wikipedia.input(u'Please enter the family project (wikipedia, wiktionary, ...):')
			else:
				otitisglobals.preferences['family'] = arg[8:]
		elif arg.startswith('-newbie'):
			if len(arg) == 7:
				otitisglobals.preferences['newbie'] = int(wikipedia.input(u'Please enter the number of edits for newbie users:'))
			else:
				otitisglobals.preferences['newbie'] = int(arg[8:])
		elif arg.startswith('-botnick'):
			if len(arg) == 8:
				otitisglobals.preferences['botNick'] = wikipedia.input(u'Please enter bot username:')
			else:
				otitisglobals.preferences['botNick'] = arg[9:]
			obligatory-=1
		elif arg.startswith('-statsdelay'):
			if len(arg) == 11:
				otitisglobals.preferences['statsDelay'] = int(wikipedia.input(u'Please enter stats delay (in seconds):'))
			else:
				otitisglobals.preferences['statsDelay'] = int(arg[12:])
		elif arg.startswith('-network'):
			if len(arg) == 8:
				otitisglobals.preferences['network'] = wikipedia.input(u'Please enter IRC network:')
			else:
				otitisglobals.preferences['network'] = arg[9:]
		elif arg.startswith('-channel'):
			if len(arg) == 8:
				otitisglobals.preferences['channel'] = wikipedia.input(u'Please enter IRC channel (with #):')
			else:
				otitisglobals.preferences['channel'] = arg[9:]
		elif arg.startswith('-ownernick'):
			if len(arg) == 10:
				otitisglobals.preferences['ownerNick'] = wikipedia.input(u'Please enter owner username:')
			else:
				otitisglobals.preferences['ownerNick'] = arg[11:]
			obligatory-=1
	
	if obligatory:
		wikipedia.output(u"Not all obligatory parameters were found. Please, check (*) parameters.")
		sys.exit()

def loadUserEdits(author):
	""" Carga número de ediciones de un usuario en concreto """
	""" Load user edits number """
	author_=re.sub(' ', '_', author)
	try:
		rawdata=otitisglobals.preferences['site'].getUrl("/w/api.php?action=query&list=users&ususers=%s&usprop=editcount&format=xml" % urllib.quote(author_))
		if re.search(u"editcount", rawdata):
			m=re.compile(ur' editcount="(?P<editcount>\d+)"').finditer(rawdata)
			for i in m:
				return int(i.group('editcount'))
		else:
			return 0
	except:
		return 0
