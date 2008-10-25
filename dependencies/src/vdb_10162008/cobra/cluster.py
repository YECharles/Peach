
"""
Cobra's built in clustering framework
"""

import gc
import sys
import time
import cobra
import dcode
import Queue
import struct
import socket
import urllib2
import traceback
import threading
import subprocess

cluster_port = 32123
cluster_ip = "224.69.69.69"

sub_cmd = """
import cobra.cluster
cobra.cluster.getAndDoWork("%s", docode=%s)
"""

wid_lock = threading.Lock()

class ClusterWork(object):
    """
    Extend this object to create your own work units.  Do it in
    a proper module (and not __main__ to be able to use this
    in conjunction with cobra.dcode).
    """
    def __init__(self, timeout=None):
        object.__init__(self)
        self.id = None # Set by adding to the server
        self.server = None # Set by ClusterClient
        self.tottime = None # Set on return to server (maybe used by done() callback)
        self.timeout = timeout

    def work(self):
        """
        Actually do the work associated with this work object.
        """
        print "OVERRIDE ME"
        for i in range(10):
            self.setCompletion(i*10)
            self.setStatus("Sleeping: %d" % i)
            time.sleep(1)

    def done(self):
        """
        This is called back on the server once a work unit
        is complete and returned.
        """
        print "OVERRIDE DONE"

    def setCompletion(self, percent):
        """
        Work units may call this whenever they like to
        tell the server how far along their work they are.
        """
        self.server.setWorkCompletion(self.id, percent)

    def setStatus(self, status):
        """
        Work units may call this to inform the server of
        their status.
        """
        self.server.setWorkStatus(self.id, status)

class ClusterCallback:
    """
    Place one of these in the ClusterServer to get synchronous
    event information about what's going on in the cluster server.
    (mostly for the GUI).
    """

    def workAdded(self, server, work):
        pass
    def workGotten(self, server, work):
        pass
    def workStatus(self, server, workid, status):
        pass
    def workCompletion(self, server, workid, completion):
        pass
    def workDone(self, server, work):
        pass
    def workTimeout(self, server, work):
        pass

class ClusterServer:
    def __init__(self, name, maxsize=0, docode=False):
        self.go = True
        self.added = False
        self.name = name
        self.nextwid = 0
        self.inprog = {}
        self.timer = {}
        self.maxsize = maxsize
        self.queue = Queue.Queue(maxsize)
        self.cobrad = cobra.CobraDaemon(host="", port=0)
        self.cobraname = self.cobrad.shareObject(self)

        # Set this to a ClusterCallback extension if
        # you want notifications.
        self.callback = None

        if docode:
            self.cobrad.shareObject(dcode.DcodeFinder(), "DcodeServer")

    def _checkTimeouts(self):
        # Internal function to monitor work unit time
        now = time.time()
        for id,work in self.inprog.items():
            if work.timeout == None:
                continue

            start = self.timer.get(id)

            if now - start > work.timeout:
                self.timer.pop(id)
                self.inprog.pop(id)
                self.timeoutWork(work)

    def shutdownServer(self):
        self.go = False

    def runServer(self, firethread=False):
        if firethread:
            thr = threading.Thread(target=self.runServer)
            thr.setDaemon(True)
            thr.start()
        else:
            self.cobrad.fireThread()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            while self.go:
                if not self.queue.empty():
                    buf = "cobra:%s:%s:%d" % (self.name, self.cobraname, self.cobrad.port)
                    sock.sendto(buf, (cluster_ip, cluster_port))
                self._checkTimeouts()
                time.sleep(2)

    def addWork(self, work):
        """
        Add a work object to the ClusterServer.  This 
        """
        self.added = True # One time add detection
        if not isinstance(work, ClusterWork):
            raise Exception("%s is not a ClusterWork extension!")
        # Get the next work unit id
        wid_lock.acquire()
        id = self.nextwid
        self.nextwid += 1
        wid_lock.release()
        work.id = id
        self.queue.put(work)
        if self.callback:
            self.callback.workAdded(self, work)

    def getWork(self):
        try:
            ret = self.queue.get_nowait()
            self.inprog[ret.id] = ret
            self.timer[ret.id] = time.time()
            if self.callback:
                self.callback.workGotten(self, ret)
            return ret
        except Queue.Empty, e:
            return None

    def doneWork(self, work):
        """
        Used by the clients to report work as done.
        """
        self.inprog.pop(work.id)
        start = self.timer.pop(work.id)
        work.tottime = time.time()-start
        work.done()
        if self.callback:
            self.callback.workDone(self, work)

    def timeoutWork(self, work):
        """
        This method may be over-ridden to handle
        work units that time our for whatever reason.
        """
        if self.callback:
            self.callback.workTimeout(self, work)

    def setWorkStatus(self, workid, status):
        if self.callback:
            self.callback.workStatus(self, workid, status)

    def setWorkCompletion(self, workid, percent):
        if self.callback:
            self.callback.workCompletion(self, workid, percent)

class ClusterClient:

    """
    Listen for our name (or any name if name=="*") on the cobra cluster
    multicast address and if we find a server in need, go help.

    maxwidth is the number of work units to do in parallel
    docode will enable code sharing with the server
    threaded == True will use threads, otherwise subprocess of the python interpreter (OMG CLUSTER)
    """

    def __init__(self, name, maxwidth=4, threaded=True, docode=False):
        self.go = True
        self.name = name
        self.width = 0
        self.maxwidth = maxwidth
        self.threaded = threaded
        self.verbose = False
        self.docode = docode

        if docode: dcode.enableDcodeClient()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("",cluster_port))
        mreq = struct.pack("4sL", socket.inet_aton(cluster_ip), socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    def processWork(self):
        """
        Runs handing out work up to maxwidth until self.go == False.
        """
        while self.go:
            
            buf, sockaddr = self.sock.recvfrom(4096)
            if self.width >= self.maxwidth:
                continue

            if not buf.startswith("cobra"):
                continue

            info = buf.split(":")
            if len(info) != 4:
                continue

            server, svrport = sockaddr
            cc,name,cobject,portstr = info
            if (self.name != name) and (self.name != "*"):
                continue

            port = int(portstr)

            uri = "%s://%s:%d/%s" % (cc,server,port,cobject)
            self.fireRunner(uri)

    def fireRunner(self, uri):
        thr = threading.Thread(target=self.threadForker, args=(uri,))
        thr.setDaemon(True)
        thr.start()

    def threadForker(self, uri):
        self.width += 1
        cmd = sub_cmd % (uri, self.docode)
        try:
            sub = subprocess.Popen([sys.executable, '-c', cmd], stdin=subprocess.PIPE)
            sub.wait()
        finally:
            self.width -= 1

def getHostPortFromUri(uri):
    """
    Take the server URI and pull out the
    host and port for use in building the
    dcode uri.
    """
    x = urllib2.Request(uri)
    port = None
    hparts = x.get_host().split(":")
    host = hparts[0]
    if len(hparts):
        port = int(hparts[1])
    return host,port

def workThread(work):
    try:
        work.work()
        work.server.doneWork(work)
    except Exception, e:
        traceback.print_exc()

def getAndDoWork(uri, docode=False):

    # If we wanna use dcode, set it up
    try:
        if docode:
            dcode.enableDcodeClient()
            host,port = getHostPortFromUri(uri)
            cobra.dcode.addDcodeServer(host, port=port)

        # Use a cobra proxy with timeout/maxretry so we
        # don't hang forever if the server goes away
        proxy = cobra.CobraProxy(uri, timeout=60, retrymax=3)

        work = proxy.getWork()
        # If we got work, do it.
        if work != None:
            work.server = proxy

            thr = threading.Thread(target=workThread, args=(work,))
            thr.setDaemon(True)
            thr.start()

            # Wait around for done or timeout
            start = time.time()
            while True:
                if work.timeout != None:
                    if (time.time() - start) >= work.timeout:
                        break

                # If the thread is done, lets get out.
                if not thr.isAlive():
                    break

                # If our parent, or some thread closes stdin,
                # time to pack up and go.
                if sys.stdin.closed:
                    break

                time.sleep(2)

    except Exception, e:
        traceback.print_exc()

    # Any way it goes we wanna exit now.  Work units may have
    # spun up non-daemon threads, so lets GTFO.
    gc.collect() # Try to call destructors
    sys.exit(0)  # GTFO

