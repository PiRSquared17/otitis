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

#TODO
# ultimas creaciones
# velocidad
# ediciones dia

""" External modules """
""" Python modules """
import os,sys,re
import threading,thread
import httplib,urllib,urllib2
import time,datetime
import string,math,random
import random

""" irclib modules """
from ircbot import SingleServerIRCBot
from irclib import nm_to_n, nm_to_h, irc_lower, ip_numstr_to_quad, ip_quad_to_numstr

""" pywikipediabot modules """
import wikipedia, difflib, catlib

""" Otitis modules """
import otitisglobals  #Shared info
import otitiscomb  #Shared info

wikipedia.output(u'Joining to IRC channel...\n')

class BOT(SingleServerIRCBot):
	""" Clase BOT """
	""" BOT class """
	
	def __init__(self):
		"""  """
		"""  """
		self.channel       = otitisglobals.preferences['channel']
		self.nickname      = otitisglobals.preferences['nickname']
		SingleServerIRCBot.__init__(self, [(otitisglobals.preferences['network'], otitisglobals.preferences['port'])], self.nickname, self.nickname)
	
	def on_welcome(self, c, e):
		""" Se une al canal de IRC de Cambios recientes """
		""" Joins to IRC channel with Recent changes """
		
		c.join(self.channel)
	
	def on_privmsg(self, c, e):
		line = (e.arguments()[0])
		line = otitiscomb.encodeLine(line)
		nick = nm_to_n(e.source())
		
		f=open('privados.txt', 'a')
		timestamp=time.strftime('%X %x')
		line=timestamp+' '+nick+' > '+line+'\n'
		f.write(line.encode('utf-8'))
		f.close()
	
	def on_pubmsg(self, c, e):
		""" Captura cada línea del canal de IRC """
		""" Fetch and parse each line in the IRC channel """
		
		line = (e.arguments()[0])
		line = otitiscomb.encodeLine(line)
		nick = nm_to_n(e.source())
		
		wikipedia.output('%s > %s' % (nick, line))
		
		#descartamos lineas muy cortas o que no empiezan por !
		if len(line)<2 or line[0]!='!':
			return
		
		#definición de comandos
		#die*, info, tam, art, en-es*, es-en*, orto*, drae*, [[]]*, {{}}*, busca-es*, busca-en*, busca-ca*, busca-de*, busca-fr*, busca-it*, busca-co*, busca-go*, mantenimiento*, tonteria*, mes*, galletita, =*, hora*, pi*, e*, wikipedia*, google*, help*, all*
		cmds={
			'art': {
				'aliases': ['art', 'arts', 'pene'],
				'description': u'Muestra el número de artículos de cierta Wikipedia',
				},
			'info': {
				'aliases': ['info', 'uinfo', 'userinfo', 'user', 'usuario'],
				'description': u'Muestra información sobre un usuario. Por ejemplo: !info Jimbo Wales',
				},
			'ainfo': {
				'aliases': ['ainfo', 'pageinfo'],
				'description': u'Muestra información sobre una página',
				},
			'compare': {
				'aliases': ['compare', 'comp', 'compara'],
				'description': u'Compara un artículo con sus homólogos en otras Wikipedias',
				},
			'die': {
				'aliases': ['die', 'muerete', 'bye', 'quit'],
				'description': u'Finge una muerte atroz'
				},
			'dump': {
				'aliases': ['dump', 'dumps'],
				'description': u'Muestra información sobre el último dump',
				},
			'efem': {
				'aliases': ['efem', 'efe', 'efeme', 'efemerides', 'galletita'],
				'description': u'Muestra una efeméride para el día actual',
				},
			'juego': {
				'aliases': ['juego', 'juegos', 'game', 'games'],
				'description': u'Algunos juegos de frikis',
				},
			'mant': {
				'aliases': ['mant', 'mantenimiento'],
				'description': u'Muestra el mantenimiento actual',
				},
			'rank': {
				'aliases': ['rank', 'ranking'],
				'description': u'Muestra algunos rankings',
				},
			'stats': {
				'aliases': ['stats', 'statistics'],
				'description': u'Muestra algunas estadísticas de Wikipedia',
				},
			'time': {
				'aliases': ['time', 'timestamp', 'hora'],
				'description': u'Muestra la hora del sistema en UTC',
				},
			'vec': {
				'aliases': ['vec', 'wp:vec'],
				'description': u'Muestra información acerca de Wikipedia:Vandalismo en curso',
				},
			'all': {
				'aliases': ['all', 'cmd', 'cmds', 'comando', 'comandos'],
				'description': u'Muestra todos los comandos existentes',
				},
			'help': {
				'aliases': ['help', 'ayuda'],
				'description': u'Esta es la ayuda de Otitis. Para ver los comandos existentes escribe !all. Para saber más sobre un comando usa !help comando',
				},
			'author': {
				'aliases': ['author', 'autor', 'creador'],
				'description': u'Muestra información sobre mi(s) creador(es)',
				},
		}
		
		#parseo de la línea
		args=line[1:].split(' ')
		cmd=args[0].lower()
		
		#qué comando ha introducido?
		if cmd in cmds['info']['aliases']:
			parametro=nick
			if len(args)>=2:
				parametro=' '.join(args[1:])
			parametro=re.sub(ur'[\[\]]', ur'', parametro)
			parametro=re.sub(ur'([^\|]*?)\|.*', ur'\1', parametro)
			t=parametro.split(':')
			lang=''
			family=''
			user=nick
			if len(t)>=3:
				user=':'.join(t[2:])
				for i in range(0,2):
					if otitiscomb.existsLanguage(t[i]):
						lang=t[i]
					if otitiscomb.existsFamily(otitiscomb.translateFamily(t[i])):
						family=otitiscomb.translateFamily(t[i])
			elif len(t)==2:
				user=':'.join(t[1:])
				if otitiscomb.existsLanguage(t[0]):
					lang=t[0]
				if otitiscomb.existsFamily(otitiscomb.translateFamily(t[0])):
					family=otitiscomb.translateFamily(t[0])
			else:
				user=t[0]
				lang='es'
				family='wikipedia'
			
			msg=u""
			error=u"Has cometido un error. El formato adecuado es: !info usuario, !info idioma:usuario, !info proyecto:usuario o !info idioma:proyecto:usuario"
			
			if lang:
				if family:
					if not user:
						user=nick
					ediciones=otitiscomb.loadUserEdits(user, lang, family)
					if ediciones!=0:
						[primeraArticulo, primeraFecha]=otitiscomb.getFirstEditInfo(user, lang, family)
						[ultimaArticulo, ultimaFecha]=otitiscomb.getLastEditInfo(user, lang, family)
						primeraFechaObject=otitiscomb.getDateTimeObject(primeraFecha)
						ultimaFechaObject=otitiscomb.getDateTimeObject(ultimaFecha)
						edad=datetime.datetime.now()-primeraFechaObject
						grupos=""
						ranking=""
						rankingpage=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), u'Wikipedia:Ranking de ediciones')
						m=re.compile(ur"(?im)^\| (?P<position>\d+) \|\| \[\[User:%s\|%s\]\]" % (user, user)).finditer(rankingpage.get())
						for i in m:
							ranking=i.group('position')
						if not ranking:
							ranking=u">500"
						msg=u"\"%s:%s:User:%s\" tiene %d ediciones. Primera: \"%s\" (%s). Última: \"%s\" (%s). Edad: %s días. Ediciones/día: %.1f. Grupos: %s. Puesto en el ranking de ediciones: *%s*. Detalles: http://%s.%s.org/wiki/Special:Contributions/%s" % (lang, family, user, ediciones, primeraArticulo, primeraFecha, ultimaArticulo, ultimaFecha, edad.days, ediciones*1.0/int(edad.days), grupos, ranking, lang, family, re.sub(ur' ', ur'_', user))
				else:
					msg=error
			else:
				msg=error
			c.privmsg(self.channel, msg.encode('utf-8'))
		elif cmd in cmds['ainfo']['aliases']:
			parametro='Wikipedia:Portada'
			if len(args)>=2:
				parametro=' '.join(args[1:])
			page=wikipedia.Page(otitisglobals.preferences['site'], parametro)
			msg=''
			if page.exists():
				if page.isRedirectPage():
					msg=u"\"%s\": #REDIRECCIÓN [[%s]]" % (parametro, page.getRedirectTarget().title())
				elif page.isDisambig():
					msg=u"\"%s\": Desambiguación" % (parametro)
				else:
					msg=u"\"%s\": %d bytes, %d enlaces, %d imágenes, %d categorías, %d interwikis" % (parametro, len(page.get()), len(page.linkedPages()), len(page.imagelinks()), len(page.categories()), len(page.interwiki()))
			c.privmsg(self.channel, msg.encode('utf-8'))
		elif cmd in cmds['all']['aliases']:
			temp=[]
			for k, v in cmds.items():
				temp.append(k)
			temp.sort()
			msg=u"Comandos disponibles: !%s. Para saber más sobre ellos utiliza !help comando. Por ejemplo: !help info" % (', !'.join(temp))
			c.privmsg(self.channel, msg.encode('utf-8'))
		elif cmd in cmds['art']['aliases']:
			parametro='es'
			if len(args)>=2:
				parametro=' '.join(args[1:])
			
			msg=""
			if otitiscomb.existsLanguage(parametro):
				good=otitiscomb.getProjectStats(parametro, 'wikipedia')['good']
				hours=24
				good_last=otitiscomb.getNewPagesLastXHours(parametro, 'wikipedia', hours)
				if parametro=='es':
					msg=u"http://%s.wikipedia.org tiene %d artículos. Puedes crear un artículo solicitado (http://es.wikipedia.org/wiki/Wikipedia:Artículos_solicitados)" % (parametro, good)
				else:
					good_es=otitiscomb.getProjectStats('es', 'wikipedia')['good']
					good_diff=good-good_es
					good_diff_text=''
					if good_diff<0:
						good_diff_text=u'%d menos' % abs(good_diff)
					else:
						good_diff_text=u'%d más' % abs(good_diff)
					msg=u"http://%s.wikipedia.org tiene %d artículos (%s que Wikipedia en español). Se han creado %d en las últimas %d horas. Puedes ver sus últimas creaciones en: http://%s.wikipedia.org/wiki/Special:Newpages" % (parametro, good, good_diff_text, good_last, hours, parametro)
			else:
				msg=u"Error: ese idioma no existe"
			c.privmsg(self.channel, msg.encode('utf-8'))
		elif cmd in cmds['author']['aliases']:
			msg=u"(C) 2009 - emijrp (Harriet & Vostok Corporation)"
			c.privmsg(self.channel, msg.encode('utf-8'))
		elif cmd in cmds['compare']['aliases']:
			parametro='Wikipedia:Portada'
			if len(args)>=2:
				parametro=' '.join(args[1:])
			page=wikipedia.Page(otitisglobals.preferences['site'], parametro)
			msg=u''
			if page.exists():
				iws=page.interwiki()
				iws.sort()
				for iw in iws:
					if iw.site().lang in ['en', 'fr', 'de', 'pt', 'it', 'ca', 'eu', 'pl', 'ru']:
						msg+=u"\"%s:%s\" (%d bytes), " % (iw.site().lang, iw.title(), len(iw.get()))
			if msg:
				msg+=u"..."
				c.privmsg(self.channel, msg.encode('utf-8'))
		elif cmd in cmds['dump']['aliases']:
			parametro='es'
			if len(args)>=2:
				parametro=' '.join(args[1:])
			
			url=urllib.urlopen('http://download.wikimedia.org/backup-index.html', 'r')
			raw=url.read()
			url.close()
			m=re.compile(ur'<li>(?P<date>[^<]+?)<a href="%swiki/\d+">%swiki</a>: <span class=\'[^\']+\'>(?P<comment>[^<]+?)</span></li>' % (parametro, parametro)).finditer(raw)
			msg=u""
			for i in m:
				msg+="%swiki dump: %s, %s" % (parametro, i.group('date'), i.group('comment'))
			if msg:
				c.privmsg(self.channel, msg.encode('utf-8'))
		elif cmd in cmds['efem']['aliases']:
			mes={1:'enero', 2:'febrero', 3:'marzo', 4:'abril', 5:'mayo', 6:'junio', 7:'julio'}
			fecha=datetime.datetime.today()
			diames=u'%s de %s' % (fecha.day, mes[fecha.month])
			msg=u""
			efempage=wikipedia.Page(otitisglobals.preferences['site'], diames)
			m=re.compile(ur'(?im)^\* *(?P<line>\[\[\d+\]\].*?)$').finditer(efempage.get().split('==')[2])
			temp=[]
			for i in m:
				temp.append(i.group('line'))
			if temp:
				selected=temp[random.randint(0,len(temp))]
				selected=re.sub(ur'\[\[([^\|]*?)\|([^\]]*?)\]\]', ur'\2', selected)
				selected=re.sub(ur'\[\[([^\|\]]*?)\]\]', ur'\1', selected)
				msg=u"Un día como hoy: %s (Extraido de http://es.wikipedia.org/wiki/%s)" % (selected, re.sub(' ', '_',efempage.title()))
			if msg:
				c.privmsg(self.channel, msg.encode('utf-8'))
		elif cmd in cmds['mant']['aliases']:
			parametro=0
			if len(args)>=2:
				parametro=int(args[1])
			msg=u""
			if parametro>365 or parametro<-365:
				msg=u"El parámetro debe estar entre -365 y 365, ambos inclusive. Por ejemplo: !mant -2 para el mantenimiento de anteayer"
			else:
				mes={1:'enero', 2:'febrero', 3:'marzo', 4:'abril', 5:'mayo', 6:'junio', 7:'julio'}
				fecha=datetime.datetime.today()+datetime.timedelta(days=parametro)
				diames=u'%s de %s' % (fecha.day, mes[fecha.month])
				mantcat=catlib.Category(otitisglobals.preferences['site'], u'Categoría:Wikipedia:Mantenimiento:%s' % diames)
				
				mantnum=len(mantcat.articlesList())
				if mantnum>0:
					msg=u"*Hay que hacer mantenimiento* en %d páginas. Por favor, comprueba http://es.wikipedia.org/wiki/%s" % (mantnum, re.sub(' ', '_', mantcat.title()))
				else:
					msg=u"*No hay mantenimiento* que hacer. Todo en orden en http://es.wikipedia.org/wiki/%s" % (re.sub(' ', '_', mantcat.title()))
			if msg:
				c.privmsg(self.channel, msg.encode('utf-8'))
		elif cmd in cmds['rank']['aliases']:
			parametro=24
			msg=u""
			if len(args)>=2:
				parametro=int(args[1])
			if parametro>=1 and parametro<=72:
				msg=otitiscomb.rankingLastXHours(parametro)
			else:
				msg=u"El periodo debe estar entre 1 y 72 horas, ambos inclusive"
			if msg:
				c.privmsg(self.channel, msg.encode('utf-8'))
		elif cmd in cmds['juego']['aliases']:
			parametro=1
			otitiscomb.launchGame(parametro, c, self.channel)
			#c.privmsg(self.channel, msg.encode('utf-8'))
		elif cmd in cmds['vec']['aliases']:
			vecpage=wikipedia.Page(otitisglobals.preferences['site'], u'Wikipedia:Vandalismo en curso')
			m=re.compile(ur'(?i)a rellenar por un bibliotecario').finditer(vecpage.get())
			cont=0
			for i in m:
				cont+=1
			if cont>0:
				msg=u"*Hay %d informes* de vandalismo en curso sin analizar. Por favor, vigila http://es.wikipedia.org/wiki/Wikipedia:Vandalismo_en_curso" % cont
			else:
				msg=u"*No hay informes* de vandalismo en curso sin analizar. Todo en orden en http://es.wikipedia.org/wiki/Wikipedia:Vandalismo_en_curso"
			c.privmsg(self.channel, msg.encode('utf-8'))
		elif cmd in cmds['help']['aliases']:
			parametro="help"
			msg=u""
			error=u""
			if len(args)>=2:
				parametro=' '.join(args[1:])
				if cmds.has_key(parametro):
					msg=u"Comando '!%s': %s. Redirecciones de este comando son: !%s" % (parametro, cmds[parametro]['description'], ', !'.join(cmds[parametro]['aliases']))
				else:
					error=u"Comando desconocido"
				c.privmsg(self.channel, msg.encode('utf-8'))
			else:
				if cmds.has_key(parametro):
					msg=u"%s" % (cmds[parametro]['description'])
				else:
					error=u"Comando desconocido"
			if msg:
				c.privmsg(self.channel, msg.encode('utf-8'))
			elif error:
				c.notice(nick, error.encode('utf-8'))
		else:
			msg=u"Comando desconocido."
			c.notice(nick, msg.encode('utf-8'))

def main():
	""" Crea un objeto BOT y lo lanza """
	""" Creates and launches a bot object """
	
	#Starting bot...
	bot = BOT()
	bot.start()

if __name__ == '__main__':
	main()
