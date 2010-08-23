#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Otitis - IRC bot for Wikimedia projects
# Copyright (C) 2010 emijrp, bryan
# MIT License

import os
import random
import socket
import sys
import time

conn = ''
botnick = 'otitis%d' % (random.randint(1000,9999))
server = 'irc.freenode.net'
channel = '#wikipedia-es-testing'

preferences = {}
preferences['log'] = False

os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))

def p(target=channel, msg=""):
    conn.send('PRIVMSG %s :%s\r\n' % (target, msg))

def do(cmd, params):
    cmd = cmd.lower()
    if cmd in ['date', 'time', 'datetime']:
        p(msg=time.strftime('%Y-%m-%d %H:%M:%S'))

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
                        if len(message)>1 and message[0] == '!':
                            params = message[1:].split(' ')
                            do(params[0], params[1:])
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
    while True:
        try:
            run()
        except socket.error, e:
            print >>sys.stderr, 'Socket error!', e

if __name__ == '__main__':
    main()



