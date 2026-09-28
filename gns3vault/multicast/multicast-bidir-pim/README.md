# Multicast Bidirectional PIM

## Scenario

The Tennessee Titans have added two video crews at Nissan Stadium, one near R4 and one near R5. Both crews need to send and receive live replays during games. The network team has assigned one replay channel to a bidirectional PIM shared tree and the other to ordinary PIM sparse mode so they can compare how the groups behave. Before kickoff, make sure both crews can see both channels.

## Goal

* The IP addresses on the physical interfaces have been preconfigured for you.
* Configure R1 Loopback0 as `1.1.1.1/32` and Loopback1 as `11.11.11.11/32`.
* Configure OSPF area 0 on all five routers, advertise all connected networks, and achieve full unicast connectivity.
* Enable multicast routing and configure PIM sparse mode on the interfaces that carry multicast traffic.
* Enable bidirectional PIM on R1, R2, and R3. Make R1 Loopback0 the bidirectional RP for **only** `239.1.1.1`.
* Make R1 Loopback1 the ordinary sparse-mode RP for **only** `239.2.2.2`. This group must be able to build source trees.
* Configure both R4 and R5 to join `239.1.1.1` and `239.2.2.2` on `Ethernet0/1`.
* Ping both multicast groups from R4 and R5. Verify that the other edge router responds to each test.
* Check the RP mapping and multicast routing tables to confirm that `239.1.1.1` uses bidirectional PIM and `239.2.2.2` uses ordinary sparse mode.

## Topology

<img src="./topology.svg" style="max-width: 700px; width: 100%; height: auto;">

The `Ethernet0/0` interface on each Cisco IOL router is reserved for containerlab management. The diagram labels only data interfaces.

## Verification

On both R4 and R5, test each group:

```text
ping 239.1.1.1 source Ethernet0/1 repeat 5
```
```text
ping 239.2.2.2 source Ethernet0/1 repeat 5
```

On R2 or R3, confirm the group-specific RP mapping and forwarding state:

```text
terminal length 0
show ip pim rp mapping
show ip mroute 239.1.1.1
show ip mroute 239.2.2.2
```
