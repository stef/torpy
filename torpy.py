#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys
from TorCtl.TorCtl import connect
from config import passphrase

class Torpy(object):
    def __init__(self,passphrase):
        self.conn = connect(passphrase=passphrase)
        print >>sys.stderr, 'connected to', self.conn.get_info("version")["version"]

    def status(self, service):
        for opt in self.conn.get_option("HiddenServiceOptions"):
            if opt[0]=='HiddenServiceDir' and filter(None,opt[1].split('/'))[-1]==service:
                return True
        return False

    def start(self, service, endpoint, port):
        if self.status(service):
            print >>sys.stderr, "already running"
            return
        tmp=[]
        tmp.extend((('HiddenServiceDir', "%s/%s/" %
                     (os.path.dirname(os.path.abspath(__file__)), service)),
                    ('HiddenServicePort', "%s %s" % (port, endpoint))))
        print >>sys.stderr, '\n'.join(str(x) for x in tmp)
        self.loadcfg(tmp)

    def stop(self, service):
        if not self.status(service):
            print >>sys.stderr, "not running"
            return
        opts=self.conn.get_option("HiddenServiceOptions")
        i=0
        cfg=[]
        while i<len(opts):
            if opts[i][0]=='HiddenServiceDir' and filter(None,opts[i][1].split('/'))[-1]==service:
                i=i+1
                while i<len(opts) and opts[i][0]=='HiddenServicePort':
                    i=i+1
            else:
                cfg.append(opts[i])
                i=i+1
        print '\n'.join(str(x) for x in cfg)
        self.loadcfg(cfg)

    def list(self):
        opts=self.conn.get_option("HiddenServiceOptions")
        i=0
        curr=None
        res={}
        while i<len(opts):
            if opts[i][0]=='HiddenServiceDir':
                curr=filter(None,opts[i][1].split('/'))[-1]
                res[curr]={'path': opts[i][1]}
            elif opts[i][0]=='HiddenServicePort':
                port, endpoint=opts[i][1].split(' ',1)
                res[curr]['port']=port
                res[curr]['endpoint']=endpoint
            i=i+1
        print '\n'.join("%-16s %s" % i for i in sorted(res.iteritems()))

    def loadcfg(self, cfg):
        self.conn.set_options(cfg)

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    if len(sys.argv)<2:
        print "%s list" % os.path.filename(__file__)
        print "%s status <service>" % os.path.filename(__file__)
        print "%s start <service> <host:port> <serviceport>" % os.path.filename(__file__)
        print "%s stop <service>" % os.path.filename(__file__)
        sys.exit(0)

    tp=Torpy(passphrase)
    if sys.argv[1].lower()=='list':
        tp.list()
    elif sys.argv[1].lower()=='start' and len(sys.argv)==5:
        tp.start(sys.argv[2],sys.argv[3],sys.argv[4])
    elif sys.argv[1].lower()=='status' and len(sys.argv)==3:
        print "running" if tp.status(sys.argv[2]) else "not running"
    elif sys.argv[1].lower()=='stop' and len(sys.argv)==3:
        tp.stop(sys.argv[2])
    tp.close()
