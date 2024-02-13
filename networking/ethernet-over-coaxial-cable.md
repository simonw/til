# Running Ethernet over existing coaxial cable

I recently noticed that the router in our garage was providing around 900 Mbps if I plugged my laptop directly into it via an Ethernet cable, but that speed fell to around 80MBps (less than 1/10th that speed) elsewhere in our house.

Our house came pre-wired with Ethernet, and we run a Netgear Orbi mesh network where the main router lives in the garage and the other two satellite routers are connected to it via that in-the-wall Ethernet.

Those numbers would seem to indicate that the Ethernet that is built into the walls is Cat5, which maxes out at about 100Mbps. If we had Cat5e or Cat6 those cables would likely go up to 1000Mbps instead.

After some poking around I convinced myself that this was the problem - that the cables in the walls were Cat5.

I didn't particularly want to run new cables through our walls, so I poked around with ChatGPT to see if there were any alternatives.

It lead me to an option called **MoCA** - for Multimedia over Coax Alliance.

MoCA lets you run Ethernet over existing coaxial cables. And our house has coaxial cables running from the garage to several different rooms.

Crucially, MoCA 2.5 can run at up to 2.5Gbps, easily enough to handle the 900Mbps we're getting in the garage.

I ordered a [ScreenBeam MoCA 2.5 Network Adapter](https://www.amazon.com/dp/B088KV2YYL) kit from Amazon ($129.99 at time of purchase) to see if I could hook one of our Orbi satellites up to the garage router via the coaxial cables.

... and it seems to work!

Today I installed the MoCA adapters. There are two of them - one for each end of the in-wall coaxial cable. They each included a power adapter, a Cat5e Ethernet cable and a coaxial cable, plus a "splitter" in case I wanted to also run a TV off the same cable (I didn't use the splitters).

I wired one in the garage directly into our main router, and the other in a room the other end of the house into the Orbi satellite.

After "forget network" and then reconnecting (to try and trick my device into connecting to the new satellite) I managed to get 800Mbps on https://fast.com/ on WiFi in the room with the satellite. Previously I'd been lucky to get 80Mbps.

Here's everything that came in the MoCA box. I'm pretty happy about this - I may even buy another one to further extend the network to another room.

![2 ECB6250 Adapters, 2 Coax Cables, 2 Power Adapters, 2 Ethernet Cables, 2 Coax Splitters, 1 Quick Start Guide](https://static.simonwillison.net/static/2024/moca-startup.jpg)
