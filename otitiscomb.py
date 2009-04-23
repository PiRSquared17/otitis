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
import os

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

def loadUserEdits(author, lang, family):
	""" Carga número de ediciones de un usuario en concreto """
	""" Load user edits number """
	author_=re.sub(' ', '_', author)
	
	langs=otitisglobals.preferences['wikilangs']
	families=['commons', 'wiktionary', 'wikisource', 'wikinews', 'wikibooks', 'wikiquote', 'wikispecies', 'meta', 'wikiversity']
	try:
		site=wikipedia.Site(lang, family)
		rawdata=site.getUrl("/w/api.php?action=query&list=users&ususers=%s&usprop=editcount&format=xml" % author_.encode('utf-8'))
		if re.search(u"editcount", rawdata):
			m=re.compile(ur' editcount="(?P<editcount>\d+)"').finditer(rawdata)
			for i in m:
				return int(i.group('editcount'))
		else:
			return 0
	except:
		return 0

def existsLanguage(lang):
	return lang.lower() in otitisglobals.preferences['wikilangs']

def existsFamily(family):
	families=['commons', 'wiktionary', 'wikisource', 'wikinews', 'wikibooks', 'wikiquote', 'wikispecies', 'meta', 'wikiversity']
	return family.lower() in families

def translateFamily(family):
	family=family.lower()
	
	if family in ['wikipedia', 'wiki', 'w']:
		return 'wikipedia'
	elif family in ['commons']:
		return 'commons'
	elif family in ['wiktionary', 'wikt', 'wykt', 'wikc', 'wikci', 'wikcionario', 'wiktionario']:
		return 'wiktionary'
	elif family in ['wikisource', 'source', 's']:
		return 'wikisource'
	elif family in ['wikinews', 'news', 'wikinoticias', 'noticias', 'n']:
		return 'wikinews'
	elif family in ['wikibooks', 'books', 'wikilibros', 'libros', 'b']:
		return 'wikibooks'
	elif family in ['wikiquote', 'quote', 'q', 'wikicitas', 'citas']:
		return 'wikiquote'
	elif family in ['wikispecies', 'wikiespecies', 'species', 'especies']:
		return 'wikispecies'
	elif family in ['meta', 'metawiki', 'meta-wiki', 'm']:
		return 'meta'
	elif family in ['wikiversity', 'wikiversidad', 'v']:
		return 'wikiversity'
	
	return 'unknown'

def loadLanguages():
	raw=otitisglobals.preferences['site'].getUrl('/w/index.php?title=Special:SiteMatrix')
	m=re.compile(ur'http://(?P<lang>[a-z\-]+)\.wikipedia\.org').finditer(raw)
	l=[]
	for i in m:
		l.append(i.group('lang'))
	l.sort()
	return l

def getFirstLastEditInfo(user, lang, family, dir):
	article=timestamp=''
	user_=re.sub(' ', '_', user)
	raw=otitisglobals.preferences['site'].getUrl('/w/index.php?title=Especial:Contribuciones%s&limit=1&target=%s' % (dir, user_.encode('utf-8')))
	m=re.compile(ur'(\d\d:\d\d \d+ (ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic) \d\d\d\d)').finditer(raw)
	for i in m:
		timestamp=i.group(1)
	
	m=re.compile(ur'<a href="/wiki/[^\"]+?" title="(?P<article>[^>]+?)">\1</a>').finditer(raw)
	for i in m:
		article=i.group('article')
	
	return article, timestamp
	
def getFirstEditInfo(user, lang, family):
	return getFirstLastEditInfo(user, lang, family, '&dir=prev')
	
def getLastEditInfo(user, lang, family):
	return getFirstLastEditInfo(user, lang, family, '')

def getDateTimeObject(date):
	#02:13 4 ene 2003
	months={'ene':1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6, 'jul': 7, 'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12}
	
	t=date.split(' ')
	year=int(t[3])
	month=int(months[t[2]])
	day=int(t[1])
	hour=int(t[0][0:2])
	minute=int(t[0][3:5])
	
	return datetime.datetime(year, month, day, hour, minute)

def getProjectStats(lang, family):
	stats={}
	try:
		site=wikipedia.Site(lang, family)
		rawdata=site.getUrl("/w/index.php?title=Special:Statistics&action=raw")
		t=rawdata.split(';')
		for i in t:
			tt=i.split('=')
			stats[tt[0]]=int(tt[1])
	except:
		return stats
	return stats

def rankingLastXHours(period):
	output=u"Editores prolíficos de las últimas %d horas: " % period
	filename='temp.txt'
	now=datetime.datetime.now().strftime('%Y%m%d%H%M%S')
	lastxhours=datetime.datetime.now()-datetime.timedelta(hours=period)
	lastxhours=lastxhours.strftime('%Y%m%d%H%M%S')
	sql='''mysql -h eswiki-p.db.toolserver.org -e "use eswiki_p;select concat(rc_user_text,';',count(*)) from recentchanges where rc_timestamp<=%s and rc_timestamp>=%s group by rc_user_text order by count(*) desc limit 10" > %s''' % (now, lastxhours, filename)
	wikipedia.output(sql)
	os.system(sql)
	f=open(filename, 'r')
	c=0
	for l in f:
		l=unicode(l, 'utf-8')
		l=l[:len(l)-1]
		if c==0:
			c+=1
			continue
		t=l.split(';')
		output+=u'%s (%s), ' % (t[0], t[1])
	f.close()
	output+=u'... (Sujeto al lag de Toolserver)'
	
	return output

def game1():
	pass

def launchGame(game):
	return game1()
