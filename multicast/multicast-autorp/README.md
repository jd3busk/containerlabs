# Multicast Auto-RP

## Goal

* All IP addresses, OSPF routing and PIM-SM have been preconfigured for you.
* Configure AutoRP.
  * ma's Loopback0 is the Mapping Agent.
  * rp's Loopback0 is the Rendezvous Point.
* Configure receiver's Ethernet0/1 to join the multicast group 224.1.1.1.
* Make sure you can ping the 224.1.1.1 group address from source.

## Topology

<img src="./topology.svg" style="max-height: 500px; height: 100%; width: auto;">

## Solutions

**Configure AutoRP.**
```
# All Routers
configure terminal

ip pim autorp listener

end
```

**ma's Loopback0 is the Mapping Agent.**
```
# source
configure terminal

ip pim send-rp-discovery Loopback0 scope 20

end
```

**rp's Loopback0 is the Rendezvous Point.**
```
# rp
configure terminal

ip pim send-rp-announce Loopback0 scope 20

end
```

**Configure receiver's Ethernet0/1 to join the multicast group 224.1.1.1.**
```
# receiver
configure terminal

interface Ethernet0/1
 ip igmp join-group 224.1.1.1

end
```

**Make sure you can ping the 224.1.1.1 group address from router source.**
```
# source
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

Verify: <mark>***RP 3.3.3.3***</mark>

```text
# All routers
show ip pim rp mapping
```

Verify: <mark>***This system is an RP-mapping agent (Loopback0)***</mark>

```text
# ma
show ip pim rp mapping
```

Verify: <mark>***224.1.1.1***</mark>'s Last Reporter is <mark>***192.168.45.5***</mark>

```text
# transit & receiver
show ip igmp groups 224.1.1.1
```

Verify: <mark>***Reply to request # from 192.168.45.5***</mark>

```text
# source
ping 224.1.1.1 repeat 5 source Ethernet0/1
```