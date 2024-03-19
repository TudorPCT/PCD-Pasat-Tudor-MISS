import time
import server

i = 0
while i < 10:
    time.sleep(0.1)
    server.main()
    i += 1

server.print_final_statistics()
