import OSC

client = OSC.OSCClient()
client.connect(('127.0.0.1', 5000))
oscmsg = OSC.OSCMessage(address="/test")
#oscmsg.append([10,1,2])
oscmsg.append(4)
oscmsg.append(2)
client.send(oscmsg)
"""
oscmsg.clearData()
oscmsg.append(2.121)
client.send(oscmsg)
"""