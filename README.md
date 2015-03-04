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