In order to automate the fallback process from SDDP to SDDP-P2P, you might have to discover if the broadcast service (udp-hub) is available. In the first version of udp-hub, the hub did not provide any mechanism through which a node could figure out the presence of udp-hub. This has now been updated and by sending an "echo" string to the udp-hub, you will get an echo response, thus confirming if udp-hub is available.
Send a simple "echo" string to the udp-hub and you will receive "echo" string as a response on the sending address (port and IP). An "echo" string will not be broadcasted to other nodes. It will however update the "last-seen" time for the sending node.
Rest of the functionality of udp-hub remains the same.

If you are not automating the fallback process and the user assumes that the broadcasting services are not present for assignment 2, you can skip this step. Automating this process, however, will earn you 5% bonus points in assignment 2.
