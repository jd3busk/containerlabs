# Multicast Auto-RP

## Goal

* All IP addresses, OSPF routing and PIM-SM have been preconfigured for you.
* Configure AutoRP.
* rendezvous-point's Loopback0 is the Rendezvous Point (RP).
* mapping-agent's Loopback0 is the Mapping Agent (MP).
* Configure receiver's Ethernet0/1 to join the multicast group 224.4.4.4.
* Make sure you can ping the 224.4.4.4 group address from router mapping-agent.

## Topology

<img src="./topology.svg" style="max-width: 700px; width: 100%; height: auto;">

## Solutions

**Configure AutoRP.**
```
# All Routers
configure terminal

ip pim autorp listener

end
```

**rendezvous-point's Loopback0 is the Rendezvous Point (RP).**
```
# rendezvous-point
configure terminal

ip pim send-rp-announce Loopback0 scope 20

end
```

**mapping-agent's Loopback0 is the Mapping Agent (MP).**
```
# mapping-agent
configure terminal

ip pim send-rp-discovery Loopback0 scope 20

end
```

**Configure receiver's Ethernet0/1 to join the multicast group 224.4.4.4.**
```
# receiver
configure terminal

interface Ethernet0/1
 ip igmp join-group 224.1.1.1

end
```

**Make sure you can ping the 224.4.4.4 group address from router mapping-agent.**
```
# mapping-agent
ping 224.1.1.1 repeat 5
```

## Verification

```text
# All routers
show ip interface brief
show ip ospf neighbor
show ip pim neighbor
```

Verify: <mark>***AutoRP is enabled***</mark>
```text
#All routers
show ip pim autorp
```

Verify: <mark>***RP 2.2.2.2***</mark>

```text
# All routers
show ip pim rp mapping
```

Verify: <mark>***This system is an RP-mapping agent (Loopback0)***</mark>

```text
# mapping-agent
show ip pim rp mapping
```

Verify: <mark>***Info source: 1.1.1.1***</mark>

```text
# rendezvous-point, transit-1, transit-2 & receiver
show ip pim rp mapping
```

Verify: <mark>***224.1.1.1***</mark>'s Last Reporter is <mark>***192.168.45.5***</mark>

```text
# transit-2 & receiver
show ip igmp groups 224.1.1.1
```

Verify: <mark>***Reply to request # from 192.168.45.5***</mark>

```text
# mapping-agent
ping 224.1.1.1 repeat 5 source Ethernet0/1
```