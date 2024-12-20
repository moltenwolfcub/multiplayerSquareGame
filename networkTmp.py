# Due to how python imports work, entrypoint has to be in this directory
# but as this is temporary for testing a new file is needed

from client.network import Network

import _thread

n = Network()

_thread.start_new_thread(n.packetLoop, ())
_thread.start_new_thread(n.readLoop, ())

while not n.quit:pass # to stop auto-closing program
