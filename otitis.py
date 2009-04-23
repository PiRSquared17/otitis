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
import wikipedia, difflib

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
		#c.notice(nick, line.encode('utf-8'))
		
		if len(line)<2 or line[0]!='!':
			return
		
		args=line[1:].split(' ')
		cmd=args[0].lower()
		
		cmds={u'info':{}, u'ainfo':{}, u'all':{}}
		
		if cmd=='info':
			parametro=nick
			if len(args)>=2:
				parametro=' '.join(args[1:])
			parametro_=re.sub(" ", "_", parametro)
			ediciones=otitiscomb.loadUserEdits(parametro)
			primeraArticulo=""
			primeraFecha=""
			ultimaArticulo=""
			ultimaFecha=""
			edad=""
			grupos=""
			msg=u"[[Usuario:%s]] tiene %d ediciones. Primera: [[%s]] (%s). Última: [[%s]] (%s). Edad: %s. Ediciones/día: %.1f. Grupos: %s. Detalles: http://%s.%s.org/wiki/Special:Contributions/%s" % (parametro, ediciones, primeraArticulo, primeraFecha, ultimaArticulo, ultimaFecha, edad, 1.0, grupos, otitisglobals.preferences['language'], otitisglobals.preferences['family'], parametro_)
			c.privmsg(self.channel, msg.encode('utf-8'))
		elif cmd=='ainfo':
			parametro=nick
			if len(args)>=2:
				parametro=' '.join(args[1:])
			page=wikipedia.Page(otitisglobals.preferences['site'], parametro)
			msg=''
			if page.exists():
				if page.isRedirectPage():
					msg=u"[[%s]]: #REDIRECCIÓN [[%s]]" % (parametro, page.getRedirectTarget().title())
				elif page.isDisambig():
					msg=u"[[%s]]: Desambiguación" % (parametro)
				else:
					msg=u"[[%s]]: %d bytes, %d enlaces, %d imágenes, %d categorías, %d interwikis" % (parametro, len(page.get()), len(page.linkedPages()), len(page.imagelinks()), len(page.categories()), len(page.interwiki()))
			c.privmsg(self.channel, msg.encode('utf-8'))
		elif cmd=='all':
			msg=u""
			for k, v in cmds.items():
				msg+=k+u", "
			msg+=u"..."
			c.privmsg(self.channel, msg.encode('utf-8'))

def main():
	""" Crea un objeto BOT y lo lanza """
	""" Creates and launches a bot object """
	
	#Starting bot...
	bot = BOT()
	bot.start()

if __name__ == '__main__':
	main()
