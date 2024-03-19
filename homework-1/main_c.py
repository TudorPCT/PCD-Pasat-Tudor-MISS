import time
import client

i = 0
while i < 10:
    time.sleep(0.3)
    client.main()
    i += 1

client.print_final_statistics()
