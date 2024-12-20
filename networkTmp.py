# Due to how python imports work, entrypoint has to be in this directory
# but as this is temporary for testing a new file is needed

from client.network import Network

n = Network()
input() # to stop auto-closing program
