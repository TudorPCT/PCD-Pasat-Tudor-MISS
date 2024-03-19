import time

import server


i = 0
while i < 10:
    time.sleep(0.1)
    # call server.main on different thread
    server.main()

    i += 1

server.print_final_statistics()
