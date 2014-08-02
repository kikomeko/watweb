import pygtk
pygtk.require('2.0')
import gtk

from Yowsup.Common.utilities import Utilities
from Yowsup.connectionmanager import YowsupConnectionManager
from Yowsup.Common.debugger import Debugger
from Yowsup.Common.constants import Constants
import time, datetime, sys, os, base64

def getCredentials(config):
    if os.path.isfile(config):
        f = open(config)
        phone = ""
        idx = ""
        pw = ""
        cc = ""
        try:
            for l in f:
                line = l.strip()
                if len(line) and line[0] not in ('#',';'):
                    prep = line.split('#', 1)[0].split(';', 1)[0].split('=', 1)
                    varname = prep[0].strip()
                    val = prep[1].strip()
                    if varname == "phone":
                        phone = val
                    elif varname == "id":
                        idx = val
                    elif varname =="password":
                        pw =val
                    elif varname == "cc":
                        cc = val
            return (cc, phone, idx, pw);
        except:
            pass
    return 0

class cchatgui:
    def login(self):
        username=self.username
        password=self.password
        self.methodsInterface.call("auth_login", (username, password))
        self.methodsInterface.call("presence_sendAvailable",)
        print "online\n"
        '''
        while self.stayon:
            command=raw_input()
            if command=="/quit":
                self.stayon=False
            else:
                self.onCommand(command)
                continue
        '''

    def onAuthSuccess(self, username):
        print "Authed %s" % username
        self.methodsInterface.call("ready")

    def onAuthFailed(self, username, err):
        print "Auth Failed!"

    def onDisconnected(self, reason):
        print "Disconnected because %s" %reason
        if reason=="dns": time.sleep(30)
        time.sleep(1)
        self.login()

    def onPresenceUpdated(self, jid, lastSeen):
        formattedDate = datetime.datetime.fromtimestamp(long(time.time()) - lastSeen).strftime('%d-%m-%Y %H:%M')
        self.onMessageReceived(0, jid, "LAST SEEN RESULT: %s"%formattedDate, long(time.time()), False, None, False)

    def onMessageSent(self, jid, messageId):
        formattedDate = datetime.datetime.fromtimestamp(self.sentCache[messageId][0]).strftime('%d-%m-%Y %H:%M')
        print("%s [%s]:%s"%(self.username, formattedDate, self.sentCache[messageId][1]))

    def onMessageReceived(self, messageId, jid, messageContent, timestamp, wantsReceipt, pushName, isBroadcast):
        formattedDate = datetime.datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y %H:%M')
        print("%s [%s]:%s"%(jid, formattedDate, messageContent))

        if wantsReceipt and self.sendReceipts:
            self.methodsInterface.call("message_ack", (jid, messageId))

        self.edit_buffer(self.text_buffer, messageContent)

    def sendMessage(self, jid, message):
        msgId = self.methodsInterface.call("message_send", (jid, message))
        self.sentCache[msgId] = [int(time.time()), message]

    def close_window(self, widget, event, data=None):
        gtk.main_quit()
        return False

    def new_text(self, widget, event, data=None):
        pass

    def send(self, widget, data=None):
        self.sendMessage(self.jid, self.textbox.get_text())
        self.edit_buffer(self.text_buffer, self.textbox.get_text())
        self.textbox.set_text("")

    def clear(self, widget, data=None):
        pass

    def edit_buffer(self, text_buffer, data):
        iter = text_buffer.get_iter_at_offset(-1)
        text_buffer.insert(iter, "\n Username: " + data)

    def __init__(self, username, password, phoneNumber, keepAlive = False, sendReceipts = False):
        self.sendReceipts = sendReceipts
        self.phoneNumber = phoneNumber
        self.keepAlive = keepAlive
        self.jid = "%s@s.whatsapp.net" % phoneNumber

        self.sentCache = {}

        connectionManager = YowsupConnectionManager()
        connectionManager.setAutoPong(self.keepAlive)
        self.signalsInterface = connectionManager.getSignalsInterface()
        self.methodsInterface = connectionManager.getMethodsInterface()

        self.signalsInterface.registerListener("auth_success", self.onAuthSuccess)
        self.signalsInterface.registerListener("auth_fail", self.onAuthFailed)
        self.signalsInterface.registerListener("message_received", self.onMessageReceived)
        self.signalsInterface.registerListener("receipt_messageSent", self.onMessageSent)
        self.signalsInterface.registerListener("presence_updated", self.onPresenceUpdated)
        self.signalsInterface.registerListener("disconnected", self.onDisconnected)

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request(500, 350)
        self.window.set_border_width(10)
        self.window.set_title('cchat')
        self.window.connect('delete_event',self.close_window)
        self.vcontainer = gtk.VBox(False, 0)
        self.hcontainer = gtk.HBox(False, 0)
        self.chatview = gtk.ScrolledWindow()
        self.chatview.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.textview = gtk.TextView()
        self.textview.set_editable(False)
        self.textview.set_cursor_visible(False)
        self.textview.set_wrap_mode(gtk.WRAP_WORD)
        self.text_buffer = self.textview.get_buffer()
        self.chatview.add(self.textview)
        self.chatview.show()
        self.vcontainer.pack_start(self.chatview)
        self.textbox = gtk.Entry()
        self.send_button = gtk.Button('Send')
        self.send_button.connect('clicked', self.send)
        self.hcontainer.pack_start(self.textbox)
        self.hcontainer.pack_end(self.send_button)
        self.vcontainer.pack_end(self.hcontainer)
        self.window.show_all()

if __name__ == "__main__":
    cc, phone, idx, pw = getCredentials('./config')
    chat = cchatgui(idx, pw, phone)
    gtk.main()
