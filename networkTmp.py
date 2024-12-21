# Due to how python imports work, entrypoint has to be in this directory
# but as this is temporary for testing a new file is needed

import _thread

from client.network import Network

n = Network(5555)
n.connect()

_thread.start_new_thread(n.packetLoop, ())
_thread.start_new_thread(n.readLoop, ())

while not n.quit:pass # to stop auto-closing program
