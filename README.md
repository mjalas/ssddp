2015-group1

Decision diary

Implementation history:

12.2.2015
Implemented message and service classes with container classes for both.
No changes were made to design.

23.2.2015
Implemented manager classes for descriptions and discovery message handling.
Still no changes in protocol nor prototype design.

2.3.2015
Added node main loop, which also is the application main loop. Main loop
creates all the managers and starts the select loop for handling incoming
 input from standard input and sockets.

3.3.2015
Many name and description improvements were made to make the code easier to
read and maintain. Changed description and discovery manager classes to
handler classes, which only creates and parses messages. Added broadcast
discovery loop class to handle discovery message broadcasting, which uses
discovery handler for message creation and modification. Added discovery
listener for listening to incoming discovery messages and handle them accordingly.

We noticed that our design was missing multiple TCP sockets for sending and
receiving descriptions messages, and by adding a TCP socket for each case
might be tedious to implement in the select loop.

Decided to keep the select loop and implement the message handling parts in
the background. First version of the implementation utilizes threads for
the background work, and queues for messaging between threads.

5.3.2015
We realized that our Discovery Broadcast Loop has no way of knowing whether or not 
the Hub exists. Discovery Listener will have to determine whether or not the Hub is 
available and then communicate that info to the Broadcast Loop.

10.3.2015
Instead of having the Discovery Listener determining hub availability, it now 
only tells Discovery Broadcast Loop whenever there has been a new message received 
from the hub. The broadcast loop itself will then update a timestamp, which is used 
to determine whether the discovery message should be sent to the hub only or also to 
all available ports.
The discovery message is sent to the hub even when the hub has timed out.
This allows the program to recover from a scenario where the hub is temporarily 
unavailable.
We also have plans for implementing separate smaller messages to be used for the p2p 
messaging in case our regular discovery packets were to cause congestion or other 
problems due to their size.  

31.3.2015
It turned out that we had been using an unbound socket for sending udp messages.
After making the discovery broadcast loop use our listening udp socket also for 
sending messages, we were able to get the udp hub working.

11.4.2015
We implemented active discovery which allows the network to discover nodes faster.
This means that a node will immediately respond when it receives a discovery message
from a previously unknown node. 

26.4.2015
We optimized the port scanning function. Now, when the hub is not available, the node will only do a port scan every tenth time the broadcast loop runs. Other times, the node will only message its known peers. This improvement considerably reduces network flooding in the absence of a hub, while still maintaining connections between nodes.

28.5.2015
The program works now and we have managed to get some measurement data as well.
However, there were several planned improvements which we did not have time to implement.
The following improvements were dropped due to time constraints:

Creating unit tests for all classes and methods
We did create tests for some of the more important parts of the program but didn’t have time to do it for everything. This improvement would have made further development and debugging easier.
Implementing message types
We planned having message types included in the message payloads. The program works just fine without this feature as there’s only three message types which can be identified by the used transport protocol and contents. However, this feature would have been useful for further development and optimization.
Improving message contents
We had planned on leaving service information out of description request messages. This feature was done and almost implemented, but it had to be dropped as it would not work without the message types. As the program is currently, it does not distinguish between description and discovery messages. Therefore, leaving service list out of the message would have caused the program to misinterpret that the sender had lost all their services.
Implementing security measures
We had discussed implementing some kind of methods for verifying message integrity. This feature was dropped because it was not essential for the performance of the program.
Adding/removing services to local node at runtime
The program fully supports peer nodes adding, removing or updating their services. However, it does not currently have any mechanism for manipulating the node’s own services at runtime. This means that any changes to service list require the node to be shut down and restarted.
Implementing a method for toggling output between stdout and logfile
This feature would have allowed for cleaner testing of multiple nodes simultaneously. However, our testing framework mostly obsoleted this feature.
Support description requests for single service
Currently our program fully supports a description request, which is answered with descriptions of all services. We thought it might be good to also support requests that would ask for the description of only one service.This improvement would have slightly lowered network load in the case where nodes have huge amounts of services but are only interested in the descriptions of one or two services.
