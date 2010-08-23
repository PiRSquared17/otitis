#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Otitis - IRC bot for Wikimedia projects
# Copyright (C) 2010 emijrp, bryan
# MIT License

import os
import random
import re
import socket
import sys
import time
import urllib

conn = ''
botnick = 'otitis%d' % (random.randint(1000,9999))
lang = 'es'
family = 'wikipedia'
server = 'irc.freenode.net'
channel = '#%s-%s-testing' % (family, lang)

preferences = {}
preferences['log'] = False

commands = {
    'en': {
        'date': {
            'aliases': ['date', 'd', 'time', 't', 'datetime', 'dt'],
            'description': u"Show the current time and date",
            },
        'stats': {
            'aliases': ['stats', 's', 'pages', 'pags', 'p', 'art', 'arts'],
            'description': u"Show the current stats",
            },
        },
    'es': {
        'date': {
            'aliases': ['fecha', 'hora'],
            'description': u"Muestra la hora y la fecha actuales",
            },
        'stats': {
            'aliases': [u'estadísticas', 'estadisticas', u'páginas', 'paginas', 'art', 'arts'],
            'description': u"Show the current stats",
            },
        },
}

os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

def loadLanguages():
    l = []
    raw = ""
    try:
        f = urllib.urlopen('http://en.wikipedia.org/w/index.php?title=Special:SiteMatrix')
        raw = f.read()
        f.close()
    except:
        pass
    
    m = re.compile(ur'http://(?P<lang>[a-z\-]+)\.wikipedia\.org').finditer(raw)
    for i in m:
        lang=i.group('lang')
        if lang not in ['www',] and not lang in l:
            l.append(lang)
    l.sort()
    
    return l

def convertFamily(family):
    family = family.lower()
    
    if family in ['wikipedia', 'wiki', 'w']:
        return 'wikipedia'
    elif family in ['commons', 'commmons', 'commos']:
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
    
    return family

def p(target=channel, nick="", msg=""):
    if msg:
        if nick:
            conn.send('PRIVMSG %s :%s> %s\r\n' % (target, nick, msg))
        else:
            conn.send('PRIVMSG %s :%s\r\n' % (target, msg))

def do(nick, cmd, params):
    cmd = cmd.lower()
    if cmd in commands['en']['date']['aliases']+commands[lang]['date']['aliases']:
        p(nick=nick, msg=time.strftime('%Y-%m-%d %H:%M:%S'))
    elif cmd in commands['en']['stats']['aliases']+commands[lang]['stats']['aliases']:
        if len(params)>=0 and len(params)<=2:
            if len(params) == 0:
                domain = "%s.%s.org" % (lang, family)
            elif len(params) == 1:
                domain = "%s.%s.org" % (params[0], family)
            elif len(params) == 2:
                params[1] = convertFamily(params[1])
                domain = "%s.%s.org" % (params[0], params[1])
            try:
                url = "http://%s/wiki/Special:Statistics?action=raw" % (domain)
                f = urllib.urlopen(url);raw = f.read();f.close()
                msg = domain
                msg += ' ' + ', '.join(raw.split(';'))
            except:
                msg = 'Error while retrieving statistics'
        else:
            msg = 'Unknown project. Options: !stats or !stats lang or !stats lang project'
        p(nick=nick, msg=msg)

def run():
    global conn
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((server, 6667))

    conn.sendall('USER %s * * %s\r\n' % (botnick, botnick))
    conn.sendall('NICK %s\r\n' % (botnick))
    conn.sendall('JOIN %s\r\n' % channel)
    
    open_log()
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
                if target == channel:
                    if message.startswith('\x01ACTION'):
                        if preferences['log']:
                            log('* %s %s' % (nick, message[8:]))
                    else:
                        message = message.strip()
                        message = re.sub(ur"  +", ur" ", message)
                        if len(message)>1 and message[0] == '!':
                            params = message[1:].split(' ')
                            do(nick=nick, cmd=params[0], params=params[1:])
                        if preferences['log']:
                            log('<%s>\t%s' % (nick, message))
        else:
            data = conn.recv(1024)
            if not data: raise socket.error
            buffer += data
    
log_file = None
def log(msg):
    date = time.strftime('%Y-%m-%d')
    now = time.strftime('%Y-%m-%d %H:%M:%S')
    
    if date != log_file[0]:
        log_file[1].close()
        open_log()
    log_file[1].write('[%s]\t%s\n' % (now, msg))
    log_file[1].flush()
    
def open_log():
    global log_file, channel
    date = time.strftime('%Y-%m-%d')
    file = open('%s_%s.txt' % (channel[1:], date), 'a')
    log_file = (date, file)

def main():
    global langs
    
    langs = loadLanguages()
    
    while True:
        try:
            run()
        except socket.error, e:
            print >>sys.stderr, 'Socket error!', e

if __name__ == '__main__':
    main()



