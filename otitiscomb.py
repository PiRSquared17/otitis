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
import thread

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

def number2month(month):
	months={1:'enero', 2:'febrero', 3:'marzo', 4:'abril', 5:'mayo', 6:'junio', 7:'julio', 8:'agosto', 9:'septiembre', 10:'octubre', 11:'noviembre', 12:'diciembre'}
	
	return months[month]

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
			return -1
	except:
		return -1

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
		lang=i.group('lang')
		if lang not in ['www',] and not lang in l:
			l.append(lang)
	l.sort()
	return l

def getFirstLastEditInfo(user, lang, family, dir):
	article=timestamp=''
	user_=re.sub(' ', '_', user)
	site=wikipedia.Site(lang, family)
	raw=site.getUrl('/w/index.php?title=Special:Contributions%s&limit=1&target=%s' % (dir, user_.encode('utf-8')))
	m=re.compile(ur'(?P<timestamp>\d\d:\d\d \d+ (ene|feb|mar|abr|may|jun|jul|ago|sep|oct|nov|dic) \d\d\d\d)').finditer(raw)
	for i in m:
		if not timestamp:
			timestamp=i.group('timestamp')
	
	m=re.compile(ur'\;action\=history\" title="(?P<article>[^>]+?)">').finditer(raw)
	for i in m:
		if not article:
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
	if len(t)==4:
		year=int(t[3])
		month=int(months[t[2]])
		day=int(t[1])
		hour=int(t[0][0:2])
		minute=int(t[0][3:5])
		return datetime.datetime(year, month, day, hour, minute)
	else:
		return datetime.datetime.now()

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

def rankingLastXHours(c, channel, period=1):
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
		c+=1
		t=l.split(';')
		if c<=4:
			output+=u'*%s* (%s), ' % (t[0], t[1])
		else:
			output+=u'%s (%s), ' % (t[0], t[1])
	f.close()
	output+=u'... (Sujeto al lag de Toolserver: http://es.wikipedia.org/wiki/Plantilla:Toolserver)'
	
	c.privmsg(channel, output.encode('utf-8'))

def game1():
	pass

def launchGame(parametro, c, channel):
	return game1()

def getNewPagesLastXHours(lang, family, period):
	site=wikipedia.Site(lang, family)
	cont=0
	try:
		offset=datetime.datetime.now()-datetime.timedelta(hours=period)
		offset=offset.strftime('%Y%m%d%H%M%S')
		raw=site.getUrl('/w/index.php?title=Special:Newpages&offset=%s&dir=prev&limit=5000' % (offset))
		m=re.compile(ur'(?i)\<li[^\>]*?\>\d\d:\d\d').finditer(raw)
		for i in m:
			cont+=1
	except:
		pass
	
	return cont-1

def loadQuestions():
	f=open('trivial.txt', 'r')
	qa=[]
	cont=0
	for l in f:
		if cont==0:
			cont+=1
			continue
		l=unicode(l, 'utf-8')
		l=l[:len(l)-1] #quitamos \n
		t=l.split(';;')
		if len(t)==2:
			tt=t[1].split(';')
			if len(tt)>0:
				pregunta=t[0]
				respuestas=[]
				for i in tt:
					respuestas.append(i.lower())
				if len(pregunta)>10 and len(respuestas[0])>2:
					qa.append([pregunta, respuestas])
	f.close()
	return qa

def saveQuestion(question, answers):
	f=open('trivial.txt', 'a')
	line=u"%s;;%s\n" % (question, ';'.join(answers))
	f.write(line.encode('utf-8'))
	f.close()
	
	#backup
	f=open('trivial.txt', 'r')
	g=open('trivial_backup.txt', 'w')
	g.write(f.read())
	f.close()
	g.close()

def trivial(parametro, c, channel):
	sleep=15 #segundos para responder
	otitisglobals.trivial=True
	inicio=u"@@ Comenzando una partida de wikitrivial (%d preguntas) @@" % parametro
	c.privmsg(channel, inicio.encode('utf-8'))
	time.sleep(2)
	inicio2=u"@@ Recuerda que las respuestas no son sensibles a mAyúScuLaS pero sí a acentos @@"
	c.privmsg(channel, inicio2.encode('utf-8'))
	
	preguntas=loadQuestions()
	preguntas_hechas=[]
	puntuaciones={}
	
	for i in range(0, parametro):
		time.sleep(4)
		timer=time.time() #temporizador
		rand=random.randint(0, len(preguntas)-1) #id para pregunta aleatoria
		while rand in preguntas_hechas:
			rand=random.randint(0, len(preguntas)-1) #id para pregunta aleatoria
		preguntas_hechas.append(rand)
		pregunta=u"@@ *Pregunta:* %s @@" % (preguntas[rand][0])
		otitisglobals.trivialTimer=time.time()
		otitisglobals.trivialAnswers=preguntas[rand][1]
		c.privmsg(channel, pregunta.encode('utf-8'))
		tiempo_respuesta=0
		while time.time()-timer<sleep:
			if otitisglobals.trivialAnswerWinner:
				tiempo_respuesta=time.time()-timer
				respuesta=u"@@ ¡%s ha acertado en %.2f segundos! Las respuestas posibles eran: %s @@" % (otitisglobals.trivialAnswerWinner, tiempo_respuesta, ', '.join(preguntas[rand][1]))
				c.privmsg(channel, respuesta.encode('utf-8'))
				break
			time.sleep(0.1) #cada cuanto hacer una iteración del bucle
		
		puntos=sleep*1.0-tiempo_respuesta #calculo de puntos, por ahora va que chuta con esto, cuanto menos tarde más puntos da
		if otitisglobals.trivialAnswerWinner:
			if puntuaciones.has_key(otitisglobals.trivialAnswerWinner):
				puntuaciones[otitisglobals.trivialAnswerWinner]+=puntos #puntos según tiempo de respuesta
			else:
				puntuaciones[otitisglobals.trivialAnswerWinner]=puntos
			otitisglobals.trivialAnswerWinner=u""
		else:
			respuesta=u"@@ Las respuestas posibles eran: %s @@" % (', '.join(preguntas[rand][1]))
			c.privmsg(channel, respuesta.encode('utf-8'))
		
	
	otitisglobals.trivial=False
	resumen=u"@@ Podium: "
	temp=[]
	for k, v in puntuaciones.items():
		temp.append([v, k])
	temp.sort()
	temp.reverse()
	max=len(temp)
	if max>10:
		max=10
	for i in range(0,max):
		if i==0:
			resumen+=u" *%s* (%.2f), " % (temp[i][1], temp[i][0])
		else:
			resumen+=u" %s (%.2f), " % (temp[i][1], temp[i][0])
	resumen+=u"... @@"
	time.sleep(2)
	c.privmsg(channel, resumen.encode('utf-8'))
	time.sleep(2)
	fin=u"@@ La partida de wikitrivial ha finalizado @@"
	c.privmsg(channel, fin.encode('utf-8'))

def checkVEC(c, channel, limit=0):
	vecpage=wikipedia.Page(otitisglobals.preferences['site'], u'Wikipedia:Vandalismo en curso')
	m=re.compile(ur'(?i)a rellenar por un bibliotecario').finditer(vecpage.get())
	cont=0
	for i in m:
		cont+=1
	if cont>=limit:
		if cont>0:
			msg=u"*Hay %d informes* de vandalismo en curso sin analizar. Por favor, vigila http://es.wikipedia.org/wiki/Wikipedia:Vandalismo_en_curso" % cont
		else:
			msg=u"*No hay informes* de vandalismo en curso sin analizar. Todo en orden en http://es.wikipedia.org/wiki/Wikipedia:Vandalismo_en_curso"
		c.privmsg(channel, msg.encode('utf-8'))

def periodicFunctions(c, channel):
	timer1=timer2=time.time()
	
	while True:
		if time.time()-timer1>60*5:
			checkVEC(c, channel, 3)
			timer1=time.time()
		if time.time()-timer2>60*60:
			rankingLastXHours(c, channel, 1)
			timer2=time.time()
		
		time.sleep(1)

def getWikipediaStats(lang):
	dic={}
	
	try:
		url=urllib.urlopen('http://%s.wikipedia.org/wiki/Special:Statistics?action=raw' % lang)
		raw=url.read()
		trozos=raw.split(';')
		for trozo in trozos:
			trozos2=trozo.split('=')
			dic[trozos2[0]]=int(trozos2[1])
		url.close()
		otitisglobals.globalStats['+1'][lang]=dic
		
		for k, v in otitisglobals.globalStats['+1'][lang].items():
			if otitisglobals.globalStats['+1']['global'].has_key(k):
				otitisglobals.globalStats['+1']['global'][k]+=v
			else:
				otitisglobals.globalStats['+1']['global'][k]=v
	except:
		print 'error en %s' % lang
	
	otitisglobals.globalStats['+1']['cont']-=1


def getGlobalStats(c, channel):
	#total=16546867;good=2853216;views=63208805;edits=301818989;users=9503123;activeusers=158084;admins=1647;images=845544;jobs=6967 
	msg=u""
	otitisglobals.globalStats['+1']={'global':{},'cont':len(otitisglobals.preferences['wikilangs'])}
	for lang in otitisglobals.preferences['wikilangs']:
		#print lang
		thread.start_new_thread(getWikipediaStats,(lang,))
		time.sleep(0.01)
	otitisglobals.globalStats['+1']['time']=time.time()
	
	temp=time.time()
	while time.time()-temp<30 and otitisglobals.globalStats['+1']['cont']!=0:
		print 'quedan %d valores por devolver' % otitisglobals.globalStats['+1']['cont']
		time.sleep(1)
	
	#if otitisglobals.globalStats['0']:
	#	msg=u"Estadísticas globales (crecimiento en %.1f segundos): " % (time.time()-otitisglobals.globalStats['0']['time'])
	#	for k, v in otitisglobals.globalStats['+1']['global'].items():
	#		msg+=u"%s (%d, +%d), " % (k, otitisglobals.globalStats['0']['global'][k], v-otitisglobals.globalStats['0']['global'][k])
	#else:
		msg=u"Estadísticas globales (%d proyectos): " % len(otitisglobals.preferences['wikilangs'])
		for k, v in otitisglobals.globalStats['+1']['global'].items():
			msg+=u"%s (%d), " % (k, otitisglobals.globalStats['+1']['global'][k])
	
	msg+=u"..."
	c.privmsg(channel, msg.encode('utf-8'))
	
	otitisglobals.globalStats['0']=otitisglobals.globalStats['+1']
	otitisglobals.globalStats['+1']={}
