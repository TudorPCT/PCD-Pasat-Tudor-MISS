import threading
import time

import server
import client


protocol, mechanism, message_size = "2", "2", "500MB"

i = 0
while i < 100:
    # call server.main on different thread
    server_thread = threading.Thread(target=server.main, args=(protocol, mechanism))
    server_thread.start()

    time.sleep(0.0001)
    # call client.main on different thread
    client_thread = threading.Thread(target=client.main, args=(protocol, mechanism, message_size))
    client_thread.start()

    server_thread.join()
    client_thread.join()

    i += 1

server.print_final_statistics(protocol, mechanism)
client.print_final_statistics(protocol, mechanism)
