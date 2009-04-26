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

#TODO
# ultimas creaciones
# velocidad
# ediciones dia globales
# paginas antiguas
# contenido por wikiproyecto?
# lag toolserver
# poner retardo a comandos pesados
# diff aleatorio
# curiosidad aleatoria
# parsear special pages (longpages...)
# !info mostrar usuarios anterior y posterior al usuario en el ranking
# !estimación actividad hoy
# !cafe hilos + concurridos/nuevos
# última versión del código en !author
# !fap !fapfap
# !fetch que se salte las infoboxes
# !old paginas viejas
# !long
# !new
# !dpd
# ediciones borradas en !info manuelt15

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

def on_pubmsg_thread(self, c, e):
	""" Captura cada línea del canal de IRC """
	""" Fetch and parse each line in the IRC channel """
	
	line = (e.arguments()[0])
	line = otitiscomb.encodeLine(line)
	nick = nm_to_n(e.source())
	
	wikipedia.output('%s > %s' % (nick, line))
	
	#trivial
	if otitisglobals.trivial and line.lower() in otitisglobals.trivialAnswers:
		if not otitisglobals.trivialAnswerWinner:
			otitisglobals.trivialAnswerWinner=nick
	
	if re.search(ur'(?i)(Orej[oi]tas|Orej[oó]n|Otitis|Torrente)', nick):
		return
	
	line=line.strip()
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
		'ainfo': {
			'aliases': ['ainfo', 'pageinfo'],
			'description': u'Muestra información sobre una página',
			},
		'angela': {
			'aliases': ['angela', 'angelabeesley', 'beesley'],
			'descripcion': u'Muestra información actual sobre Angela Beesley, co-fundadora de Wikia.com',
			},
		'botopedia': {
			'aliases': ['botopedia', 'botoxpedia', 'boto'],
			'description': u'Analiza conductas de botopedia en el idioma y proyectos seleccionados',
			},
		'brion': {
			'aliases': ['brion', 'brionvibber', 'vibber'],
			'descripcion': u'Muestra información actual sobre Brion Vibber, desarrollador de MediaWiki',
			},
		'cab': {
			'aliases': ['cab', 'cabs', 'rfa'],
			'description': u'Muestra información sobre las Candidaturas a bibliocario en curso',
			},
		'compare': {
			'aliases': ['compare', 'comp', 'compara'],
			'description': u'Compara un artículo con sus homólogos en otras Wikipedias',
			},
		'demoda': {
			'aliases': ['demoda', 'de_moda', 'moda', 'hot'],
			'description': u'Muestra las páginas más editadas de las últimas horas',
			},
		'dest': {
			'aliases': ['dest', 'destruir', 'destroy', 'delete', 'borrar'],
			'description': u'Muestra el número de páginas a la espera de ser destruidas',
			},
		'die': {
			'aliases': ['die', 'muerete', 'bye', 'quit'],
			'description': u'Finge una muerte atroz'
			},
		'dpd': {
			'aliases': ['dpd'],
			'description': u'Busca una palabra en el Diccionario Panhispánico de Dudas'
			},
		'drae': {
			'aliases': ['drae', 'rae'],
			'description': u'Busca una palabra en el DRAE'
			},
		'dump': {
			'aliases': ['dump', 'dumps'],
			'description': u'Muestra información sobre el último dump',
			},
		'efem': {
			'aliases': ['efem', 'efe', 'efeme', 'efemerides', 'galletita'],
			'description': u'Muestra una efeméride para el día actual',
			},
		'encarta': {
			'aliases': ['encarta', 'enc', 'progresoencarta', 'pencarta', 'penc'],
			'description': u'Muestra cuántos artículos de la Encarta tenemos',
			},
		'flames': {
			'aliases': ['flames', 'flame', 'disc', 'discu', 'polvorin', u'polvorín'],
			'description': u'Muestra las discusiones más activas en las últimas horas',
			},
		'global': {
			'aliases': ['global', 'globalstats', 'globales'],
			'description': u'Muestra estadísticas globales',
			},
		'info': {
			'aliases': ['info', 'uinfo', 'userinfo', 'user', 'usuario'],
			'description': u'Muestra información sobre un usuario. Por ejemplo: !info Jimbo Wales',
			},
		'jimbo': {
			'aliases': ['jimbo', 'jimmy', 'jwales', 'wales', 'jimbowales', 'jimmywales'],
			'description': u'Muestra información actual sobre Jimbo Wales',
			},
		'juego': {
			'aliases': ['juego', 'juegos', 'game', 'games'],
			'description': u'Algunos juegos de frikis',
			},
		'lemario': {
			'aliases': ['lemario', 'lem', 'progresolemario'],
			'description': u'Muestra cuántas palabras del idioma español tenemos',
			},
		'maldoror': {
			'aliases': ['maldoror', 'maldo', 'mald', 'tanques', 'tanque'],
			'description': u'Muestra un artículo creado por Maldoror, elegido aleatoriamente',
			},
		'mant': {
			'aliases': ['mant', 'mantenimiento'],
			'description': u'Muestra el mantenimiento actual o de una fecha concreta',
			},
		'preg': {
			'aliases': ['preg', 'pregunta', 'nuevapregunta'],
			'description': u'Añade una nueva pregunta al wikitrivial. El formato es: pregunta;;respuesta1;respuesta2;respuesta3... Las respuestas no son sensibles a mayúsculas o minúsculas',
			},
		'rank': {
			'aliases': ['rank', 'ranking', 'stat', 'stats', 'statistics'],
			'description': u'Muestra los editores más prolíficos de las últimas X horas. Por ejemplo: !rank 24',
			},
		'raro': {
			'aliases': ['raro', 'odd', 'peculiar'],
			'description': u'Muestra un artículo curioso al azar.',
			},
		#'stats': {
		#	'aliases': ['stats', 'statistics'],
		#	'description': u'Muestra algunas estadísticas de Wikipedia',
		#	},
		'tim': {
			'aliases': ['tim', 'timstarling', 'starling'],
			'descripcion': u'Muestra información actual sobre Tim Starling, desarrollador de MediaWiki, creador de las parserFunctions',
			},
		'time': {
			'aliases': ['time', 'timestamp', 'hora'],
			'description': u'Muestra la hora del sistema en UTC',
			},
		'trivial': {
			'aliases': ['trivial', 'triv', 'hora'],
			'description': u'Comienza una partida de wikitrivial',
			},
		'vec': {
			'aliases': ['vec', 'wp:vec'],
			'description': u'Muestra información acerca de Wikipedia:Vandalismo en curso',
			},
		'visitas': {
			'aliases': ['visitas', 'visit', 'visits', 'vis', 'v'],
			'description': u'Muestra el número de visitas de cierta página. Está sujeto a la disponibilidad de http://stats.grok.se',
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
			'aliases': ['author', 'autor', 'creador', 'creator'],
			'description': u'Muestra información sobre el creador de un artículo',
			},
		'readme': {
			'aliases': ['readme', 'leeme', 'acerca', 'acercade', 'about'],
			'description': u'Muestra información sobre el creador de Otitis',
			},
	}
	
	#parseo de la línea
	args=line[1:].split(' ')
	cmd=args[0].lower()
	
	#qué comando ha introducido?
	if cmd in cmds['info']['aliases']:
		[lang, family, user]=otitiscomb.splitParameter(nick, args)
		user=re.sub(ur"(User|Usuario)\:", ur"", user) #por si acaso alguien mete !info User:Emijrp
		msg=error=u""
		ediciones=otitiscomb.loadUserEdits(user, lang, family)
		if ediciones>=0:
			msg+=u"\"%s:%s:User:%s\" tiene *%d* ediciones." % (lang, family, user, ediciones)
			[primeraArticulo, primeraFecha, diff]=otitiscomb.getFirstEditInfo(user, lang, family)
			[ultimaArticulo, ultimaFecha, diff]=otitiscomb.getLastEditInfo(user, lang, family)
			media=0.0
			edad_text=u''
			if primeraFecha and ultimaFecha:
				primeraFechaObject=otitiscomb.getDateTimeObject(primeraFecha)
				ultimaFechaObject=otitiscomb.getDateTimeObject(ultimaFecha)
				edad=datetime.datetime.now()-primeraFechaObject
				edad_text=u'%s días' % edad.days
				media=ediciones*1.0/int(edad.days)
				msg+=u" Primera: \"%s\" (Fecha: %s). Última: \"%s\" (Fecha: %s). Edad: %s (%.1f ediciones/día)." % (primeraArticulo, primeraFecha, ultimaArticulo, ultimaFecha, edad_text, media)
			grupos=""
			#hacer función busca grupos
			if grupos:
				msg+=u" Grupos: %s." % grupos
			ranking=""
			if lang=='es':
				rankingpage=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), u'Wikipedia:Ranking de ediciones')
				m=re.compile(ur"(?im)^\| (?P<position>\d+) \|\| \[\[User:%s\|%s\]\]" % (user, user)).finditer(rankingpage.get())
				for i in m:
					ranking=i.group('position')
				if not ranking:
					ranking=u">500"
			if ranking:
				msg+=u" Puesto en el ranking de ediciones: *%s*." % ranking
			msg+=u" Detalles: http://%s.%s.org/wiki/Special:Contributions/%s" % (lang, family, re.sub(ur' ', ur'_', user))
		else:
			error+=u"Ese usuario no existe."
		if error:
			c.privmsg(self.channel, error.encode('utf-8'))
		elif msg:
			c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['ainfo']['aliases']:
		[lang, family, pagina]=otitiscomb.splitParameter('Main Page', args)
		page=wikipedia.Page(wikipedia.Site(lang, family), pagina)
		msg=''
		if page.exists():
			pagina=':'.join([family, lang, pagina])
			if page.isRedirectPage():
				msg=u"\"%s\": #REDIRECT \"%s\"" % (pagina, page.getRedirectTarget().title())
			elif page.isDisambig():
				msg=u"\"%s\": Desambiguación" % (pagina)
			else:
				msg=u"\"%s\": %d bytes, %d enlaces, %d imágenes, %d categorías, %d interwikis. Extraido de http://%s.wikipedia.org/wiki/%s" % (pagina, len(page.get()), len(page.linkedPages()), len(page.imagelinks()), len(page.categories()), len(page.interwiki()), lang, re.sub(' ', '_', page.title()))
		c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['all']['aliases']:
		temp=[]
		for k, v in cmds.items():
			temp.append(k)
		temp.sort()
		msg=u"Comandos disponibles: !%s. Para saber más sobre ellos utiliza !help comando. Por ejemplo: !help info" % (', !'.join(temp))
		c.notice(nick, msg.encode('utf-8'))
	elif cmd in cmds['angela']['aliases']:
		otitiscomb.famousEditor('Angela', c, self.channel)
	elif cmd in cmds['art']['aliases']:
		msg=error=""
		[lang, family, pagina]=otitiscomb.splitParameter('', args+[':'])
		good=otitiscomb.getProjectStats(lang, family)['good']
		hours=24
		good_last=otitiscomb.getNewPagesLastXHours(lang, family, hours)
		if lang=='es':
			if family=='wikipedia':
				msg=u"http://%s.%s.org tiene %d artículos. Se han creado %d en las últimas %d horas. Puedes crear un artículo solicitado (http://es.wikipedia.org/wiki/Wikipedia:Artículos_solicitados)" % (lang, family, good, good_last, hours)
			else:
				msg=u"http://%s.%s.org tiene %d artículos. Se han creado %d en las últimas %d horas." % (lang, family, good, good_last, hours)
		else:
			good_es=otitiscomb.getProjectStats('es', family)['good']
			good_diff=good-good_es
			good_diff_text=''
			if good_diff<0:
				good_diff_text=u'%d menos' % abs(good_diff)
			else:
				good_diff_text=u'%d más' % abs(good_diff)
			msg=u"http://%s.%s.org tiene %d artículos (%s que %s en español). Se han creado %d en las últimas %d horas. Puedes ver sus últimas creaciones en: http://%s.%s.org/wiki/Special:Newpages" % (lang, family, good, good_diff_text, family, good_last, hours, lang, family)
		if error:
			c.privmsg(self.channel, error.encode('utf-8'))
		elif msg:
			c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['author']['aliases']:
		[lang, family, pagina]=otitiscomb.splitParameter('Main Page', args)
		otitiscomb.whoIsItsAuthor(lang, family, pagina, c, self.channel)
	elif cmd in cmds['botopedia']['aliases']:
		msg=u""
		hours=24
		[lang, family, pagina]=otitiscomb.splitParameter('', args+[':'])
		authors=otitiscomb.getNewPagesAuthorsLastXHours(lang, family, hours)
		authors_list=[]
		total=0.0
		for k, v in authors.items():
			authors_list.append([v, k])
			total+=v
		authors_list.sort()
		authors_list.reverse()
		msg=u"Analizando máximos creadores en http://%s.%s.org en las últimas %d horas: " % (lang, family, hours)
		cont=0
		while cont<5:
			msg+=u"%s (%d), " % (authors_list[cont][1], authors_list[cont][0])
			cont+=1
		if msg:
			msg+=u"... (Total: %d creaciones)" % total
			max_porcentaje=authors_list[0][0]*1.0/(total/100)
			if max_porcentaje>=10:
				msg+=u" *%s ha creado el %.2f%%*, ¿es un bot?" % (authors_list[0][1], max_porcentaje)
			msg+=u" http://%s.%s.org/wiki/Special:Contributions/%s" % (lang, family, re.sub(' ', '_', authors_list[0][1]))
			c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['brion']['aliases']:
		otitiscomb.famousEditor('Brion VIBBER', c, self.channel)
	elif cmd in cmds['cab']['aliases']:
		cabtemplate=wikipedia.Page(otitisglobals.preferences['site'], u'Plantilla:ResumenCandidaturasBibliotecario')
		#| 1 || [[Usuario:Nicop|Nicop]] || [[Wikipedia:Candidaturas a bibliotecario/Nicop|Ver]] || 72 || 2 || style='background-color:#D0F0C0;' | 97% 
		m=re.compile(ur"(?im)^\| *\d+ \|\| *\[\[Usuario\:(?P<user>[^\|]*?)\|[^\]]+?\]\] *\|\| *\[\[(?P<cab>.+?)\|Ver\]\] *\|\| *(?P<afavor>\d+) *\|\| *(?P<encontra>\d+) *\|\|[^\|]+?\| *(?P<porcentaje>[\d\.]+)").finditer(cabtemplate.get())
		for i in m:
			msg=u"\"User:%s\": A favor (%s), En contra (%s), Porcentaje favorables (%s%%). Detalles: http://es.wikipedia.org/wiki/%s" % (i.group('user'), i.group('afavor'), i.group('encontra'), i.group('porcentaje'), re.sub(' ', '_', i.group('cab')))
			c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['compare']['aliases']:
		[lang, family, pagina]=otitiscomb.splitParameter(u'Jimmy Wales', args)
		page=wikipedia.Page(wikipedia.Site(lang, family), pagina)
		msg=u''
		if page.exists():
			if page.isRedirectPage():
				page=page.getRedirectTarget()
			iws=page.interwiki()
			iws.append(page)
			iws.sort()
			for iw in iws:
				if iw.site().lang in ['en', 'fr', 'de', 'es', 'pt', 'it', 'ca', 'eu', 'pl', 'ru']:
					if iw.site().lang==page.site().lang:
						msg+=u"\"%s:%s\" (*%d* bytes), " % (iw.site().lang, iw.title(), len(iw.get()))
					else:
						msg+=u"\"%s:%s\" (%d bytes), " % (iw.site().lang, iw.title(), len(iw.get()))
		if msg:
			msg+=u"..."
			c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['demoda']['aliases']:
		parametro=24
		if len(args)>=2:
			parametro=int(args[1])
		otitiscomb.mostEditedLastXHours(c, self.channel, parametro)
	elif cmd in cmds['dest']['aliases']:
		msg=u""
		destcat=catlib.Category(wikipedia.Site('es', 'wikipedia'), u"Categoría:Wikipedia:Borrar (definitivo)")
		destnum=len(destcat.articlesList())
		print destcat.articlesList()
		if destnum>0:
			msg=u"*Hay que borrar* %d páginas. Por favor, comprueba http://es.wikipedia.org/wiki/%s_" % (destnum, re.sub(' ', '_', destcat.title()))
		else:
			msg=u"*No hay que borrar* ninguna página. Todo en orden en http://es.wikipedia.org/wiki/%s_" % (re.sub(' ', '_', destcat.title()))
		if msg:
			c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['dpd']['aliases']:
		msg=u""
		[null, null, pagina]=otitiscomb.splitParameter('', args)
		url=u"http://buscon.rae.es/dpdI/SrvltGUIBusDPD?lema=%s" % pagina
		f=urllib.urlopen(url.encode('utf-8'), 'r')
		raw=f.read()
		f.close()
		if re.search(ur'(?i)no est\&\#x00E1\; registrada en el', raw):
			msg=u"La palabra \"%s\" no está en el DPD" % pagina
		else:
			msg=u"La palabra \"%s\" está recogida en el DPD. Ver: %s" % (pagina, url)
		if msg:
			c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['drae']['aliases']:
		msg=u""
		[null, null, pagina]=otitiscomb.splitParameter('', args)
		url=u"http://buscon.rae.es/draeI/SrvltGUIBusUsual?TIPO_HTML=2&LEMA=%s" % pagina
		f=urllib.urlopen(url.encode('utf-8'), 'r')
		raw=f.read()
		f.close()
		if re.search(ur'(?i)no está en el Diccionario', raw):
			msg=u"La palabra \"%s\" no está en el Diccionario de la RAE" % pagina
		else:
			msg=u"La palabra \"%s\" está recogida en el Diccionario de la RAE. Ver: %s" % (pagina, url)
		if msg:
			c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['dump']['aliases']:
		[lang, family, pagina]=otitiscomb.splitParameter('', args)
		url=urllib.urlopen('http://download.wikimedia.org/backup-index.html', 'r')
		raw=url.read()
		url.close()
		if family=='wikipedia':
			family='wiki'
		m=re.compile(ur'<li>(?P<date>[^<]+?)<a href="%s%s/\d+">%s%s</a>: <span class=\'[^\']+\'>(?P<comment>[^<]+?)</span></li>' % (lang, family, lang, family)).finditer(raw)
		msg=u""
		for i in m:
			msg+="%s%s dump: %s, %s. Extraido de: http://download.wikimedia.org/%s%s/latest/" % (lang, family, i.group('date'), i.group('comment'), lang, family)
		if msg:
			c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['efem']['aliases']:
		fecha=datetime.datetime.today()
		diademes=u'%s de %s' % (fecha.day, otitiscomb.number2month(fecha.month))
		[lang, family, pagina]=otitiscomb.splitParameter(diademes, args)
		msg=error=u""
		efempage=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), pagina) #pillamos el es: y leugo saltamos al otro idioma si es necesario
		if lang!='es':
			iws=efempage.interwiki()
			for iw in iws:
				if iw.site().lang==lang:
					efempage=iw
					break
		m=re.compile(ur'(?im)^[\*\#] *(?P<line>\[\[\d\d\d\d?\]\].+?) *$').finditer(efempage.get().split('==')[2])
		temp=[]
		for i in m:
			temp.append(i.group('line'))
		if temp:
			selected=temp[random.randint(0,len(temp))]
			selected=otitiscomb.cleanLinks(selected)
			selected=otitiscomb.cleanHTML(selected)
			msg=u"Un día como hoy (%s): %s Extraido de http://%s.wikipedia.org/wiki/%s" % (efempage.title(), selected, lang, re.sub(' ', '_', efempage.title()))
		else:
			error=u"No ha sido posible extraer efemérides de %s:" % lang
		if error:
			c.privmsg(self.channel, error.encode('utf-8'))
		elif msg:
			c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['encarta']['aliases']:
		msg=""
		encarta=wikipedia.Page(otitisglobals.preferences['site'], u"Plantilla:ProgresoEncarta")
		m=re.compile(ur"Total\: *(?P<total>[\d\.]+?)\%").finditer(encarta.get())
		for i in m:
			msg=u"Progreso Encarta: Tenemos el *%s%%* de los artículos de /Enciclopedia Encarta/. Detalles: http://es.wikipedia.org/wiki/Plantilla:ProgresoEncarta" % (i.group('total'))
		if msg:
			c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['flames']['aliases']:
		msg="Discusiones muy activas: "
		flames=wikipedia.Page(otitisglobals.preferences['site'], u"Plantilla:DiscusionesActivas")
		#| [[Discusión:Día de la Tierra|Día de la Tierra]] || [http://es.wikipedia.org/w/index.php?title=Discusión:Día_de_la_Tierra&action=history 20] 
		m=re.compile(ur"(?im)^\| *\[\[(?P<discu>[^\|]+?)\|[^\]]+?\]\] *\|\| *.*?\=history *(?P<edits>\d+)\]").finditer(flames.get())
		for i in m:
			msg+=u"http://es.wikipedia.org/wiki/%s (%s), " % (re.sub(' ', '_', i.group('discu')), i.group('edits'))
		if msg:
			msg+=u'...'
			c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['global']['aliases']:
		otitiscomb.getGlobalStats(c, self.channel)
	elif cmd in cmds['jimbo']['aliases']:
		otitiscomb.famousEditor(u'Jimbo Wales', c, self.channel)
	elif cmd in cmds['lemario']['aliases']:
		msg=""
		encarta=wikipedia.Page(otitisglobals.preferences['site'], u"Plantilla:ProgresoLemario")
		m=re.compile(ur"Total\: *(?P<total>[\d\.]+?)\%").finditer(encarta.get())
		for i in m:
			msg=u"Progreso Lemario: Tenemos el *%s%%* de las palabras del idioma español. Detalles: http://es.wikipedia.org/wiki/Plantilla:ProgresoLemario" % (i.group('total'))
		if msg:
			c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['maldoror']['aliases']:
		msg=u""
		maldopage=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), u'Wikipedia:Ranking de creaciones (sin redirecciones)/Maldoror/1')
		links=maldopage.linkedPages()
		linkselected=links[random.randint(0, len(links))]
		otitiscomb.whoIsItsAuthor('es', 'wikipedia', linkselected.title(), c, self.channel)
	elif cmd in cmds['mant']['aliases']:
		parametro=0
		if len(args)>=2:
			parametro=int(args[1])
		msg=u""
		if parametro>365 or parametro<-365:
			msg=u"El parámetro debe estar entre -365 y 365, ambos inclusive. Por ejemplo: !mant -2 para el mantenimiento de anteayer"
		else:
			fecha=datetime.datetime.today()+datetime.timedelta(days=parametro)
			diames=u'%s de %s' % (fecha.day, otitiscomb.number2month(fecha.month))
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
		error=u""
		if len(args)>=2:
			parametro=int(args[1])
		if parametro>=1 and parametro<=72:
			otitiscomb.rankingLastXHours(c, self.channel, parametro)
		else:
			error=u"El periodo debe estar entre 1 y 72 horas, ambos inclusive"
		if error:
			c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['raro']['aliases']:
		msg=u""
		page=wikipedia.Page(wikipedia.Site('es', 'wikipedia'), u'Wikipedia:Artículos peculiares')
		m=re.compile(ur"(?im)^[\*\#] *\[\[(?P<article>.+?)\]\](?P<line>.+?)$").finditer(page.get())
		raros=[]
		for i in m:
			raros.append([i.group('article'), i.group('line')])
		[article, line]=raros[random.randint(0,len(raros))]
		line=otitiscomb.cleanWikiSyntax(line)
		msg=u"Artículo curioso/raro al azar: \"%s\"%s Ver en http://es.wikipedia.org/wiki/%s" % (article, line, re.sub(' ', '_', article))
		if msg:
			c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['juego']['aliases']:
		parametro=1
		otitiscomb.launchGame(parametro, c, self.channel)
		msg=u"El único juego que tengo es el !trivial"
		c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['preg']['aliases']:
		msg=cmds['preg']['description']
		if len(args)>=2:
			parametro=' '.join(args[1:])
			t=parametro.split(';;')
			if len(t)==2:
				tt=t[1].split(';')
				if len(tt)>0:
					pregunta=t[0]
					respuestas=tt
					if len(pregunta)>10 and len(respuestas[0])>=2:
						otitiscomb.saveQuestion(pregunta, respuestas)
						time.sleep(3)
						msg=u"Pregunta guardada con éxito. Ahora hay %d preguntas en el wikitrivial. Inícialo con !trivial" % (len(otitiscomb.loadQuestions()))
		c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['tim']['aliases']:
		otitiscomb.famousEditor('Tim Starling', c, self.channel)
	elif cmd in cmds['trivial']['aliases']:
		parametro=10
		if len(args)>1:
			try:
				parametro=int(args[1])
			except:
				pass
		if False and not otitisglobals.trivial:
			otitiscomb.trivial(parametro, c, self.channel)
		msg=u"Trivial desactivado para evitar flooding"
		c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['vec']['aliases']:
		otitiscomb.checkVEC(c, self.channel)
	elif cmd in cmds['visitas']['aliases']:
		#<li class="sent bar" style="height: 280px; left: 400px;"><p style="margin-left: -3px;">3</p></li>
		parametro=u""
		pagina=u""
		lang=u""
		msg=u""
		error=u""
		url=u""
		day=datetime.datetime.today().day
		month=datetime.datetime.today().month
		if len(args)>=2:
			parametro=' '.join(args[1:])
		else:
			parametro=u'Usuario:%s' % nick
		if parametro:
			t=parametro.split(':')
			if len(t)>1 and otitiscomb.existsLanguage(t[0]):
				pagina=':'.join(t[1:])
				lang=t[0]
			else:
				lang='es'
				pagina=parametro
			try:
				url=u"http://stats.grok.se/%s/%s/%s" % (lang, datetime.datetime.now().strftime('%Y%m'), re.sub(' ', '_', pagina))
				f=urllib.urlopen(url.encode('utf-8'), 'r')
				m=re.compile(ur"(?i)<li class=\"sent bar\" style=\"height: \d+px; left: \d+px;\"><p style=\"margin-left: \-?\d+px;\">(?P<visits>[\d\.km]+)</p></li>").finditer(f.read())
				cont=0
				for i in m:
					cont+=1
					if cont in [day-3, day-2, day-1]:
						visitas=i.group('visits')
						if re.search(ur"(?i)k", visitas):
							visitas=re.sub(ur'(?i)k', ur'', visitas)
							visitas=float(visitas)*1000
						elif re.search(ur"(?i)m", visitas):
							visitas=re.sub(ur'(?i)m', ur'', visitas)
							visitas=float(visitas)*1000000
						msg+=u"%d de %s (%s), " % (cont, otitiscomb.number2month(month), int(visitas))
				f.close()
			except:
				error=u"Hubo un error al leer la página de estadísticas"
		else:
			error=u"Introduzca un nombre de página. Puedes ver estadísticas de visitas en http:/stats.grok.se"
		if msg:
			msg=u"Hoy es %s de %s. Visitas a \"%s\" en los últimos días: %s... Extraido de: %s. Página en Wikipedia: http://%s.wikipedia.org/wiki/%s" % (day, otitiscomb.number2month(month), parametro, msg, url, lang, re.sub(' ', '_', pagina))
			c.privmsg(self.channel, msg.encode('utf-8'))
		elif error:
			c.privmsg(self.channel, error.encode('utf-8'))
	elif cmd in cmds['readme']['aliases']:
		msg=u"(C) 2009 - emijrp (Harriet & Vostok Corporation). Licencia GPL. Código: http://code.google.com/p/otitis/. Han aportado algo (ideas, bugs, sugerencias): Taichi, Paintman, Chabacano, sabbut, Dferg, Drini, ejmeza, Nixón"
		c.privmsg(self.channel, msg.encode('utf-8'))
	elif cmd in cmds['help']['aliases']:
		parametro="help"
		msg=u""
		error=u""
		if len(args)>=2:
			parametro=' '.join(args[1:])
			parametro=re.sub(ur'(?im)^\!+', ur'', parametro)
			if not cmds.has_key(parametro):
				for k, v in cmds.items():
					if parametro in v['aliases']:
						parametro=k
			if cmds.has_key(parametro):
				msg=u"Comando '!%s': %s. Redirecciones de este comando son: !%s" % (parametro, cmds[parametro]['description'], ', !'.join(cmds[parametro]['aliases']))
			else:
				error=u"Comando desconocido. Puedes ver una lista de comandos con !all"
		else:
			if cmds.has_key(parametro):
				msg=u"%s" % (cmds[parametro]['description'])
			else:
				error=u"Comando desconocido. Puedes ver una lista de comandos con !all"
		if msg:
			c.notice(nick, msg.encode('utf-8'))
		elif error:
			c.notice(nick, error.encode('utf-8'))
	else:
		msg=u"Comando desconocido. Puedes ver una lista de comandos con !all"
		c.notice(nick, msg.encode('utf-8'))

class BOT(SingleServerIRCBot):
	""" Clase BOT """
	""" BOT class """
	
	def __init__(self):
		self.channel       = otitisglobals.preferences['channel']
		self.nickname      = otitisglobals.preferences['nickname']
		SingleServerIRCBot.__init__(self, [(otitisglobals.preferences['network'], otitisglobals.preferences['port'])], self.nickname, self.nickname)
	
	def on_welcome(self, c, e):
		""" Se une al canal de IRC de Cambios recientes """
		""" Joins to IRC channel with Recent changes """
		
		thread.start_new_thread(otitiscomb.periodicFunctions,(c, self.channel,))
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
		thread.start_new_thread(on_pubmsg_thread,(self, c, e,))

def main():
	""" Crea un objeto BOT y lo lanza """
	""" Creates and launches a bot object """
	
	#Starting bot...
	bot = BOT()
	bot.start()

if __name__ == '__main__':
	main()
