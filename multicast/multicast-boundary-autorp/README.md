# Multicast Boundary Filtering: Auto-RP Mappings

## Goal

- IP addresses, OSPF, PIM sparse mode, and receiver joins for both groups are preconfigured.
- Make rp's `Loopback0` (`1.1.1.1`) the candidate RP and mapping agent for `239.1.1.1` and `239.2.2.2`.
- On boundary, enable the Auto-RP listener.
  - Apply a **standard ACL** multicast boundary with `filter-autorp` on `Ethernet0/2` toward receiver-outside.
  - Permit Auto-RP control groups and `239.1.1.1`; deny `239.2.2.2`.
- Verify receiver-outside learns only the `239.1.1.1` mapping. receiver-inside should retain both mappings.

## Topology

<img src="./topology.svg" style="max-height: 500px; height: 100%; width: auto;">

## Solutions

**Make rp's `Loopback0` (`1.1.1.1`) the candidate RP and mapping agent for `239.1.1.1` and `239.2.2.2`.**

```text
# rp
configure terminal

ip access-list standard GROUPS
 permit 239.1.1.1
 permit 239.2.2.2
exit

ip pim autorp listener
ip pim send-rp-announce Loopback0 scope 10 group-list GROUPS
ip pim send-rp-discovery Loopback0 scope 10

end
```

**On boundary, enable the Auto-RP listener.**

```text
# boundary
configure terminal

ip pim autorp listener

end
```

**Permit Auto-RP control groups and `239.1.1.1`; deny `239.2.2.2`.**

```text
# boundary
configure terminal

ip access-list standard BOUNDARY
 permit 224.0.1.39
 permit 224.0.1.40
 permit 239.1.1.1
 deny 239.2.2.2

end
```

**Apply a standard ACL multicast boundary with `filter-autorp` on `Ethernet0/2` toward receiver-outside.**

```text
# boundary
configure terminal

interface Ethernet0/2
 ip multicast boundary BOUNDARY filter-autorp

end
```

## Verification

Verify: <mark>***Permit 224.0.1.39, 224.0.1.40 and 239.1.1.1; deny 239.2.2.2.***</mark>

```text
# boundary
show access-lists BOUNDARY
```

Verify: <mark>***`239.1.1.1` receives replies from both receivers: 192.168.24.4 and 192.168.23.3.***</mark>

```text
# rp
ping 239.1.1.1 source Loopback0 repeat 5
```

Verify: <mark>***`239.2.2.2` receives replies only from receiver-inside: 192.168.24.4.***</mark>

```text
# rp
ping 239.2.2.2 source Loopback0 repeat 5
```

Verify: <mark>***receiver-outside maps only 239.1.1.1 to RP 1.1.1.1.***</mark>

```text
# receiver-outside
show ip pim rp mapping
```

Verify: <mark>***receiver-inside maps both groups to RP 1.1.1.1.***</mark>

```text
# receiver-inside
show ip pim rp mapping
```