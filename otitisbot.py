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
import thread
import urllib

#TODO:
#returns when kicked
#local times using -utc:+10 or -utc:-2
#!stats in local lang
#newpages patrol
#wikitext flag (bn: only when !link)

conn = '' #conection
langs = []
newpageslog = []
editslog = []
preferences = {
    'lang': 'en',
    'family': 'wikipedia',
    'server': 'irc.freenode.net',
    'channel': '#wikipedia-en',
    'botnick': 'Otitis%d' % (random.randint(1000,9999)),
    'ownernick': 'Emijrp',
    'log': False,
    'test': False,
    'newpages': False,
    'edits': False,
    'wikitext': False,
}

commands = {
    'en': {
        'date': {
            'aliases': ['date', 'd', 'time', 't', 'datetime', 'dt'],
            'description': u"Show the current time and date",
            },
        'help': {
            'aliases': ['help', 'h'],
            'description': u"Show available commands",
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
        'help': {
            'aliases': ['ayuda', u'ayúdame', 'ayudame'],
            'description': u"Muestra los comandos disponibles",
        },
        'stats': {
            'aliases': [u'estadísticas', 'estadisticas', u'páginas', 'paginas'],
            'description': u"Muestra las estadísticas básicas del proyecto",
            },
        },
    'bn': {
        'date': {
            'aliases': [],
            'description': u"বর্তমান সময় ও তারিখ প্রদর্শন করবে",
            },
        'help': {
            'aliases': [],
            'description': u"প্রযোজ্য কমান্ডগুলো প্রদর্শন করবে",
        },
        'stats': {
            'aliases': [],
            'description': u"বর্তমান পরিসংখ্যান প্রদর্শন করবে",
            },
        },
}

os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

def newpages():
    recentchanges(rctype="new")

def edits():
    recentchanges(rctype="edit")

def recentchanges(rctype=""):
    global newpageslog
    global editslog
    
    rclimit = 10
    t1 = time.time()
    while True:
        while time.time()-t1 < 10:
            time.sleep(1)
        t1 = time.time()
        domain = "%s.%s.org" % (preferences['lang'], preferences['family'])
        path = "/w/api.php?action=query&list=recentchanges&rctype=%s&rcnamespace=&rcprop=title|user|ids&rclimit=%d" % (rctype, rclimit)
        raw = urllib.urlopen(u"http://%s%s" % (domain, path)).read()
        regexp = """(?im)<span style="color:blue;">&lt;rc type=&quot;(?P<type>%s)&quot; ns=&quot;\d+&quot; title=&quot;(?P<title>[^\n]+?)&quot; rcid=&quot;(?P<rcid>\d+?)&quot; pageid=&quot;(?P<pageid>\d+?)&quot; revid=&quot;(?P<revid>\d+?)&quot; old_revid=&quot;(?P<old_revid>\d+?)&quot; user=&quot;(?P<user>[^\n]+?)&quot;( anon=&quote;&quote;)? /&gt;</span>""" % (rctype)
        #http://bn.wikipedia.org/w/api.php?action=query&list=recentchanges&rctype=new&rcnamespace=&rcprop=title|user|ids&rclimit=10
        #<span style="color:blue;">&lt;rc type=&quot;new&quot; ns=&quot;0&quot; title=&quot;রামপ্রসাদ সেন&quot; rcid=&quot;701636&quot; pageid=&quot;114556&quot; revid=&quot;701795&quot; old_revid=&quot;0&quot; user=&quot;Jonoikobangali&quot; /&gt;</span>

        m = re.compile(regexp).finditer(raw)
        for i in m:
            type = i.group('type')
            title = i.group('title')
            rcid = i.group('rcid')
            pageid = i.group('pageid')
            revid = i.group('revid')
            old_revid = i.group('old_revid')
            user = i.group('user')
            
            #print title, rcid, pageid, revid, old_revid, user
            
            msg = ""
            if type == "new":
                if len(newpageslog)>rclimit:
                    if revid not in newpageslog:
                        msg = " [[%s]] *created* by User:%s. Link: http://%s/wiki/%s_ Permalink: http://%s/w/index.php?oldid=%s User contributions: http://%s/wiki/Special:Contributions/%s_" % (title, user, domain, title, domain, revid, domain, user)
                if revid not in newpageslog:
                    newpageslog.append(revid)
            elif type == "edit":
                if len(editslog)>rclimit:
                    if revid not in editslog:
                        msg = "[[%s]] *edited* by User:%s. Diff: http://%s/w/index.php?oldid=%s&diff=prev User contributions: http://%s/wiki/Special:Contributions/%s_" % (title, user, domain, revid, domain, user)
                if revid not in editslog:
                    editslog.append(revid)
            if msg:
                p(msg=msg)
    

def getParameters():
    """ Gestionar parámetros capturados de la consola """
    """ Manage console parameters """
    args=sys.argv
    
    obligatory=5
    for arg in args[1:]:
        if arg.startswith('-lang'):
            if len(arg) == 5:
                pass
                #preferences['lang'] = wikipedia.input(u'Please enter the language (es, en, de, fr, bn, ...):')
            else:
                preferences['lang'] = arg[6:]
            obligatory-=1
        elif arg.startswith('-family'):
            if len(arg) == 7:
                pass
                #preferences['family'] = wikipedia.input(u'Please enter the family project (wikipedia, wiktionary, ...):')
            else:
                preferences['family'] = arg[8:]
            obligatory-=1
        elif arg.startswith('-botnick'):
            if len(arg) == 8:
                pass
                #preferences['botnick'] = wikipedia.input(u'Please enter bot username:')
            else:
                preferences['botnick'] = arg[9:]
            obligatory-=1
        elif arg.startswith('-statsdelay'):
            if len(arg) == 11:
                pass
                #preferences['statsdelay'] = int(wikipedia.input(u'Please enter stats delay (in seconds):'))
            else:
                preferences['statsdelay'] = int(arg[12:])
        elif arg.startswith('-network'):
            if len(arg) == 8:
                pass
                #preferences['network'] = wikipedia.input(u'Please enter IRC network:')
            else:
                preferences['network'] = arg[9:]
        elif arg.startswith('-channel'):
            if len(arg) == 8:
                pass
                #preferences['channel'] = wikipedia.input(u'Please enter IRC channel (with #):')
            else:
                preferences['channel'] = arg[9:]
            obligatory-=1
        elif arg.startswith('-ownernick'):
            if len(arg) == 10:
                pass
                #preferences['ownernick'] = wikipedia.input(u'Please enter owner username:')
            else:
                preferences['ownernick'] = arg[11:]
            obligatory-=1
        elif arg.startswith('-test'):
            if len(arg) == 5:
                pass
                #preferences['test'] = wikipedia.input(u'Please enter test mode (True or False):')
            else:
                preferences['test'] = arg[6:]
        elif arg.startswith('-log'):
            if len(arg) == 4:
                preferences['log'] = True
        elif arg.startswith('-newpages'):
            if len(arg) == 9:
                preferences['newpages'] = True
        elif arg.startswith('-edits'):
            if len(arg) == 6:
                preferences['edits'] = True
        elif arg.startswith('-wikitext'):
            if len(arg) == 9:
                preferences['wikitext'] = True
    
    if obligatory:
        print u"Not all obligatory parameters were found. Please, check (*) parameters."
        sys.exit()

def loadLanguages():
    l = []
    raw = ""
    try:
        f = urllib.urlopen('http://noc.wikimedia.org/conf/all.dblist')
        raw = f.read()
        f.close()
    except:
        pass
    
    m = re.compile(ur'(?im)^(?P<lang>[^\s]+?)wiki\n').finditer(raw)
    for i in m:
        lang=i.group('lang')
        if lang not in l:
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

def p(target="", nick="", msg=""):
    if not target: #not possible argument target=preferences['channel'], loaded before getParameters()
        target = preferences['channel']
    if msg:
        #msg = msg.encode("utf-8")
        if nick:
            conn.send('PRIVMSG %s :%s> %s\r\n' % (target, nick, msg))
        else:
            conn.send('PRIVMSG %s :%s\r\n' % (target, msg))
    #time.sleep(1) #delay to avoid flooding

def do(nick, cmd, params):
    cmd = cmd.lower()
    if cmd in commands['en']['help']['aliases']+commands[preferences['lang']]['help']['aliases']:
        if len(params)>=0 and len(params)<=1:
            if len(params) == 0:
                #show available commands
                msg = u'Available commands: !'
                if commands.has_key(preferences['lang']):
                    msg += u', !'.join(commands[preferences['lang']].keys())
                else:
                    msg = u'No commands found'
            elif len(params) == 1:
                params[0] = re.sub(ur'!', ur'', params[0]).lower()
                if commands.has_key(preferences['lang']):
                    for command, props in commands[preferences['lang']].items():
                        if params[0] in [command]+props['aliases']:
                            msg = u'!%s: %s (English: %s)' % (params[0], props['description'], commands['en'][command]['description'])
                            break
                        else:
                            msg = u'Command !%s not found' % (params[0])
                else:
                    msg = u'No available commands for %s language' % (preferences['lang'])
        else:
            msg = u'Write !help'
        p(nick=nick, msg=msg)
    elif cmd in commands['en']['date']['aliases']+commands[preferences['lang']]['date']['aliases']:
        p(nick=nick, msg=time.strftime('%Y-%m-%d %H:%M:%S'))
    elif cmd in commands['en']['stats']['aliases']+commands[preferences['lang']]['stats']['aliases']:
        if len(params)>=0 and len(params)<=2:
            domain = ""
            if len(params) == 0:
                domain = "%s.%s.org" % (preferences['lang'], preferences['family'])
            elif len(params) == 1:
                params = params[0].split('.')
                if len(params) == 1:
                    params = params[0].split('-')
            
            if len(params) == 1:
                if params[0] in langs:
                    domain = "%s.%s.org" % (params[0], preferences['family'])
                else:
                    params[0] = convertFamily(params[0])
                    domain = "%s.%s.org" % (preferences['lang'], params[0])
            elif len(params) == 2:
                if params[0] in langs:
                    params[1] = convertFamily(params[1])
                elif params[1] in langs:
                    temp = params[1]
                    params[1] = convertFamily(params[0])
                    params[0] = temp
                domain = "%s.%s.org" % (params[0], params[1])
            try:
                url = "http://%s/wiki/Special:Statistics?action=raw" % (domain)
                f = urllib.urlopen(url);raw = f.read();f.close()
                if re.search(ur'(?i)DOCTYPE', raw):
                    msg = u'Project not found'
                else:
                    msg = u'http://%s ' % domain
                    msg += u', '.join(raw.split(';'))
                    msg += u' (from http://%s/wiki/Special:Statistics?action=raw)' % domain
            except:
                msg = 'Error while retrieving statistics'
        else:
            msg = 'Unknown project. Options: !stats or !stats lang or !stats lang project'
        p(nick=nick, msg=msg)

def run():
    global conn
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((preferences['server'], 6667))

    conn.sendall('USER %s * * %s\r\n' % (preferences['botnick'], preferences['botnick']))
    conn.sendall('NICK %s\r\n' % (preferences['botnick']))
    conn.sendall('JOIN %s\r\n' % preferences['channel'])
    
    open_log()
    buffer = ''
    while True:
        if '\n' in buffer:
            line = buffer[:buffer.index('\n')]
            #line = unicode(line, "utf-8")
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
                if target == preferences['channel']:
                    if message.startswith('\x01ACTION'):
                        if preferences['log']:
                            log('* %s %s' % (nick, message[8:]))
                    else:
                        message = message.strip()
                        message = re.sub(ur"  +", ur" ", message)
                        if len(message)>1 and message[0] == '!':
                            params = message[1:].split(' ')
                            do(nick=nick, cmd=params[0], params=params[1:])
                        if preferences['wikitext']:
                            links = re.findall(ur"\[\[([^\|\[\]]+?)[\]\|]", message)
                            links2 = []
                            for link in links:
                                link = re.sub(r" ", r"_", link)
                                links2.append("http://%s.%s.org/wiki/%s_" % (preferences['lang'], preferences['family'], link))
                            msg = " ".join(links2[:5])
                            p(nick=nick, msg=msg)
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
    file = open('%s_%s.txt' % (preferences['channel'][1:], date), 'a')
    log_file = (date, file)

def main():
    global langs
    
    langs = loadLanguages()
    getParameters()
    
    print preferences
    
    if preferences['newpages']:
        thread.start_new_thread(newpages, ())
    if preferences['edits']:
        thread.start_new_thread(edits, ())
    
    
    #sys.exit()
    while True:
        try:
            run()
        except socket.error, e:
            print >>sys.stderr, 'Socket error!', e

if __name__ == '__main__':
    main()
