# Multicast BSR

## Goal

* All IP addresses, endpoint default routes, OSPF routing and PIM-SM have been preconfigured for you. Only rp-1, bsr and rp-2 participate in OSPF and PIM.
* Configure BSR.
  * bsr's Loopback0 is the Bootstrap Router, with priority 100 and a hash mask length of 31.
  * rp-1's and rp-2's Loopback0 interfaces are candidate Rendezvous Points for 239.1.1.0 through 239.1.1.3, both with priority 0.
* Configure receiver's Ethernet0/1 to join all four multicast groups.
* Keep rp-2 on the shared tree by disabling its automatic shortest-path-tree switch.
* Verify 239.1.1.0 and 239.1.1.1 select rp-1, while 239.1.1.2 and 239.1.1.3 select rp-2.
* Make sure you can ping all four group addresses from source.

## Topology

<img src="./topology.svg" style="max-height: 500px; height: 100%; width: auto;">

## Solutions

**bsr's Loopback0 is the Bootstrap Router, with priority 100 and hash mask length 31.**
```text
# bsr
configure terminal

ip pim bsr-candidate Loopback0 31 100

end
```

**rp-1's and rp-2's Loopback0 interfaces are candidate Rendezvous Points for all four groups, both with priority 0.**
```text
# rp-1 & rp-2
configure terminal

ip access-list standard GROUPS
 permit 239.1.1.0 0.0.0.3

ip pim rp-candidate Loopback0 group-list GROUPS priority 0

end
```

**Configure receiver's Ethernet0/1 to join all four multicast groups.**
```text
# receiver
configure terminal

interface Ethernet0/1
 ip igmp join-group 239.1.1.0
 ip igmp join-group 239.1.1.1
 ip igmp join-group 239.1.1.2
 ip igmp join-group 239.1.1.3

end
```

**Keep rp-2 on the shared tree by disabling its automatic shortest-path-tree switch.**
```text
# rp-2
configure terminal

ip pim spt-threshold infinity

end
```

**Verify 239.1.1.0 and 239.1.1.1 select rp-1, while 239.1.1.2 and 239.1.1.3 select rp-2.**
```text
# bsr
show ip pim rp-hash 239.1.1.0
show ip pim rp-hash 239.1.1.1
show ip pim rp-hash 239.1.1.2
show ip pim rp-hash 239.1.1.3
```

**Make sure you can ping all four group addresses from source.**
```text
# source
ping 239.1.1.0 source Ethernet0/1 repeat 5
ping 239.1.1.1 source Ethernet0/1 repeat 5
ping 239.1.1.2 source Ethernet0/1 repeat 5
ping 239.1.1.3 source Ethernet0/1 repeat 5
```

## Verification

```text
# All routers
show ip interface brief
```

```text
# rp-1, bsr & rp-2
show ip ospf neighbor
show ip pim neighbor
```

Verify: <mark>***Replies from 192.168.45.5.***</mark>
```text
# source
ping 192.168.45.5 source Ethernet0/1 repeat 5
```

Verify: <mark>***BSR address 2.2.2.2, priority 100, hash mask length 31.***</mark>
```text
# rp-1, bsr & rp-2
show ip pim bsr-router
```

Verify: <mark>***This system is the Bootstrap Router (BSR).***</mark>
```text
# bsr
show ip pim bsr-router
```

Verify: <mark>***RP 1.1.1.1 and RP 4.4.4.4, via bootstrap, both priority 0.***</mark>
```text
# rp-1, bsr & rp-2
show ip pim rp mapping
```

Verify: <mark>***239.1.1.0 through 239.1.1.3 have Last Reporter 192.168.45.5 on Ethernet0/2.***</mark>
```text
# rp-2
show ip igmp groups
```

Verify: <mark>***239.1.1.0 and 239.1.1.1 select RP 1.1.1.1.***</mark>
```text
# bsr
show ip pim rp-hash 239.1.1.0
show ip pim rp-hash 239.1.1.1
```

Verify: <mark>***239.1.1.2 and 239.1.1.3 select RP 4.4.4.4.***</mark>
```text
# bsr
show ip pim rp-hash 239.1.1.2
show ip pim rp-hash 239.1.1.3
```

Verify: <mark>***Reply to request # from 192.168.45.5 for each group.***</mark>
```text
# source
ping 239.1.1.0 source Ethernet0/1 repeat 5
ping 239.1.1.1 source Ethernet0/1 repeat 5
ping 239.1.1.2 source Ethernet0/1 repeat 5
ping 239.1.1.3 source Ethernet0/1 repeat 5
```

Verify: <mark>***(*,G) RP 1.1.1.1, incoming Ethernet0/1, outgoing Ethernet0/2.***</mark>
```text
# rp-2
show ip mroute 239.1.1.0
show ip mroute 239.1.1.1
```

Verify: <mark>***(*,G) RP 4.4.4.4; traffic forwards out Ethernet0/2 toward receiver.***</mark>
```text
# rp-2
show ip mroute 239.1.1.2
show ip mroute 239.1.1.3
```

Verify: <mark>***Forwarded packet counters increase while source sends multicast pings.***</mark>
```text
# rp-2
show ip mroute count
```
