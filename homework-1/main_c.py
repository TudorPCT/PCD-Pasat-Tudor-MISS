import time

import client


i = 0
while i < 10:

    time.sleep(0.3)
    # call client.main on different thread
    client.main()

    i += 1

client.print_final_statistics()

# ( 10655 + 17571 + 18537 ) / 3 = 15521
# (104856000 + 104856000 + 104856000) / 3 = 104856000
