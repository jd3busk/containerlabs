# Multicast PIM-SSM

## Scenario

The Tennessee Titans send a live practice feed from their video server to a remote coaching room. The coaches should receive group `232.1.1.1` only from the approved source, `1.1.1.1`. Use Source Specific Multicast to build a direct source tree without relying on an RP to discover the feed.

## Goal

- IP addresses and OSPF area 0 are preconfigured on all three routers.
- Enable multicast routing and PIM sparse mode on all lab Ethernet interfaces and Loopback0 interfaces.
- Configure transit's Loopback0 (`3.3.3.3`) as the static RP on all routers, as specified in the guide.
- Enable SSM for the default `232.0.0.0/8` range on all routers.
- Configure video-client's Ethernet0/1 for IGMPv3 and join `232.1.1.1` with source `1.1.1.1`.
- Test from video-server's Loopback0.

The static RP is retained from the guide for ordinary PIM sparse-mode groups. SSM groups use source-specific trees and do not use the RP.

## Topology

<img src="./topology.svg" style="max-width: 700px; width: 100%; height: auto;">

## Verification

**video-server**

The approved source should receive replies from video-client (`192.168.23.3`). Initial packets may time out while multicast state forms.

```text
ping 232.1.1.1 source Loopback0 repeat 5
```

This unapproved source should receive no replies:

```text
ping 232.1.1.1 source Ethernet0/1 repeat 5
```

**video-client**

Confirm the source-specific membership and `(1.1.1.1, 232.1.1.1)` multicast entry.

```text
show ip igmp groups 232.1.1.1 detail
show ip mroute 232.1.1.1
```
