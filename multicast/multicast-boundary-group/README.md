# Multicast Boundary Filtering: Group Boundary

## Scenario

The Tennessee Titans provide live video and replays to a broadcast partner. A third multicast feed carries private coaching video. Configure the border so the partner receives the first two feeds while the coaches retain all three.

## Goal

- All IP addresses and OSPF are preconfigured for you.
- Confirm OSPF connectivity and that partner and coaches learn production's Auto-RP mappings.
- Confirm both receivers initially answer pings to all three multicast groups from production.
- On border's `Ethernet0/2`, configure a **group-based** multicast boundary. Permit Auto-RP traffic and `239.1.1.1` (live video) and `239.2.2.2` (replays); block `239.3.3.3` (coaching video) toward partner.
- Verify coaches still receive the coaching feed through `Ethernet0/3`.

## Topology

<img src="./topology.svg" style="max-width: 700px; width: 100%; height: auto;">

| Group | Feed |
| --- | --- |
| `239.1.1.1` | Live video |
| `239.2.2.2` | Replays |
| `239.3.3.3` | Private coaching video |

## Verification

After you add the boundary, partner (`192.168.23.3`) should reply for the first two groups. Only coaches (`192.168.24.4`) should reply for the third. Partner may still show the third group’s RP mapping because the boundary blocks its traffic, not the mapping announcement.

**Border**
```text
show ip ospf neighbor
show ip pim neighbor
```

**Partner**
```text
show ip pim rp mapping
show ip igmp groups
```

**Coaches**
```text
show ip pim rp mapping
show ip igmp groups
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
