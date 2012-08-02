
# Simple client to test the Cred_DeviceServer 

import agdevicecontrol
from twisted.spread import pb
from twisted.internet import reactor
from twisted.cred.portal import Portal
from twisted.cred import credentials, error


class Client(pb.Referenceable):


    # expose a remotely callable function
    def remote_print(self, message):
        print "remote_print() called:"
        print message
        #reactor.stop()


    def printer(self, *args):
        print args

    def connect(self):
        factory = pb.PBClientFactory()
        reactor.connectTCP("hobo", 9986, factory)
        #add the client=self to the login call
        def1 = factory.login(credentials.UsernamePassword("pwarren","CoMplexPassWoRd!"), client=self)
        def1.addCallback(self.connected)
        reactor.run()

    def connected(self, perspective):
        d = perspective.callRemote("getDeviceList")
        d.addCallback(self.printer)

        
   
Client().connect()
