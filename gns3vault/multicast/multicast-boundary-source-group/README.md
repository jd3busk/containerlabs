# Multicast Boundary Filtering: Source and Group

## Scenario

The Tennessee Titans share live video and replays with a broadcast partner. The private coaching feed must stay inside the team network. The partner should receive the shared feeds only when production sends them from `1.1.1.1`.

## Goal

- IP addresses, OSPF, PIM sparse mode, and joins for all three groups are preconfigured.
- On production, advertise `Loopback0` (`1.1.1.1`) as the Auto-RP and mapping agent for all three groups.
- On border, enable the Auto-RP listener. Apply an extended ACL multicast boundary **out** on `Ethernet0/2` toward partner. Allow Auto-RP discovery, `(*,G)` state, and traffic from `1.1.1.1` to `239.1.1.1` and `239.2.2.2`. Block `239.3.3.3` toward partner.
- Verify coaches can still receive all three groups.

## Topology

<img src="./topology.svg" style="max-width: 700px; width: 100%; height: auto;">

| Group | Feed |
| --- | --- |
| `239.1.1.1` | Live video |
| `239.2.2.2` | Replays |
| `239.3.3.3` | Private coaching video |

## Verification

After configuring Auto-RP, check that both receivers learn the RP and all three groups work **before** applying the boundary.

**Partner and coaches**

```text
show ip pim rp mapping
```

**Production**

```text
ping 239.1.1.1 source Loopback0 repeat 5
```

```text
ping 239.2.2.2 source Loopback0 repeat 5
```

```text
ping 239.3.3.3 source Loopback0 repeat 5
```

Apply the boundary on border, then repeat the three pings. Partner (`192.168.23.3`) should answer for the first two groups; coaches (`192.168.24.4`) should answer for all three. Partner can still learn the blocked group's RP mapping.

**Border**

```text
show running-config interface Ethernet0/2
show ip mroute 239.1.1.1
show ip mroute 239.2.2.2
show ip mroute 239.3.3.3
```

To check the source restriction, compare these two pings. A few initial packets may follow the shared tree; inspect sustained replies and border's `(S,G)` state.

**Production**

```text
ping 239.1.1.1 source Loopback0 repeat 20
```

```text
ping 239.1.1.1 source Ethernet0/1 repeat 20
```
