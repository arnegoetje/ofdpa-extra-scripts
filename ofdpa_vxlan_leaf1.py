#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 11:33:48 2018

@author: Arne Goetje <arne_goetje@edge-core.com>
"""

"""
Set up OF-DPA groups and flows configuring a Data Center Overlay Tunnel scenario. The
script sets up Access and Network logical ports.

This script invokes OF-DPA API services via RPC. The RPC calls are served by the ofdpa
process running on the switch.

"""
from OFDPA_python import *
from socket import *

def main():
    rc = ofdpaClientInitialize("OFDPA_example")
    if rc == OFDPA_E_NONE:

        # local and remote end station MAC addresses
        localStationMac  = "00:00:00:00:00:11"
        remoteStationMac = "00:00:00:00:00:99"

        # tenant parameters
        tunnelIdIndex = 1
        vnid = 1

        # Tunnel Access Port parameters
        accessPortIndex = 1
        accessPhysicalPort = 33
        accessVlanId = 80
        accessPacketsUntagged = 0

        # Tunnel Next Hop parameters
        nextHop1Id = 1
        nextHop1SourceMac  = "c4:39:3a:f4:5b:da" # leaf 1
        nextHop1DestMac    = "cc:39:ab:d0:d2:20" # spine 1
        nextHop1PhysicalPort = 49
        nextHop1VlanId = 100

        nextHop2Id = 2
        nextHop2SourceMac  = "c4:39:3a:f4:5b:da" # leaf 1
        nextHop2DestMac    = "cc:39:ab:d0:d4:28" # spine 2
        nextHop2PhysicalPort = 50
        nextHop2VlanId = 200

        # Tunnel Endpoint Port parameters
        endpointPortIndex = 2
        remoteEndpointIp =  0x02020202  # 2.2.2.2
        localEndpointIp = 0x01010101    # 1.1.1.1
        ttl = 45
        terminatorUdpDestPort = 132
        initiatorUdpDestPort = 133
        udpSrcPortIfNoEntropy = 0
        useEntropy = 1

        # configure tenant
        tunnelId_p = new_uint32_tp()
        ofdpaTunnelIdTypeSet(tunnelId_p, OFDPA_TUNNELID_TYPE_DATA_CENTER_OVERLAY)
        ofdpaTunnelIdIndexSet(tunnelId_p, tunnelIdIndex)
        tunnelId = uint32_tp_value(tunnelId_p)

        tenantEntry = ofdpaTunnelTenantConfig_t()
        tenantEntry.protocol = OFDPA_TUNNEL_PROTO_VXLAN
        tenantEntry.virtualNetworkId = vnid
        ofdpaTunnelTenantCreate(tunnelId, tenantEntry)

        # create Tunnel Access Port
        accessPortId_p = new_uint32_tp()
        ofdpaPortTypeSet(accessPortId_p, OFDPA_PORT_TYPE_LOGICAL_TUNNEL)
        ofdpaPortIndexSet(accessPortId_p, accessPortIndex)
        accessPortId = uint32_tp_value(accessPortId_p)

        accessPortCfg = ofdpaTunnelPortConfig_t()
        accessPortCfg.type = OFDPA_TUNNEL_PORT_TYPE_ACCESS
        accessPortCfg.tunnelProtocol = OFDPA_TUNNEL_PROTO_VXLAN
        accessPortCfg.configData.access.physicalPortNum = accessPhysicalPort
        accessPortCfg.configData.access.vlanId = accessVlanId
        accessPortCfg.configData.access.untagged = accessPacketsUntagged

        accessPortName = "AccessPort"
        portNameBuffDesc = ofdpa_buffdesc()
        portNameBuffDesc.size = len(accessPortName) + 1
        BuffDesc_pstart_setbytes(portNameBuffDesc, accessPortName)

        ofdpaTunnelPortCreate(accessPortId, portNameBuffDesc, accessPortCfg)

        # create Tunnel Next Hop 1
        tunnelNextHopCfg = ofdpaTunnelNextHopConfig_t()
        tunnelNextHopCfg.protocol = OFDPA_TUNNEL_PROTO_VXLAN
        MACAddress_set(tunnelNextHopCfg.srcAddr, nextHop1SourceMac)
        MACAddress_set(tunnelNextHopCfg.dstAddr, nextHop1DestMac)
        tunnelNextHopCfg.physicalPortNum = nextHop1PhysicalPort
        tunnelNextHopCfg.vlanId = nextHop1VlanId

        ofdpaTunnelNextHopCreate(nextHop1Id, tunnelNextHopCfg)

        # create Tunnel Next Hop 2
        tunnelNextHopCfg = ofdpaTunnelNextHopConfig_t()
        tunnelNextHopCfg.protocol = OFDPA_TUNNEL_PROTO_VXLAN
        MACAddress_set(tunnelNextHopCfg.srcAddr, nextHop2SourceMac)
        MACAddress_set(tunnelNextHopCfg.dstAddr, nextHop2DestMac)
        tunnelNextHopCfg.physicalPortNum = nextHop2PhysicalPort
        tunnelNextHopCfg.vlanId = nextHop2VlanId

        ofdpaTunnelNextHopCreate(nextHop2Id, tunnelNextHopCfg)

        # create Tunnel ECMP Next Hop Group
        ecmpNextHopGroupId_p = new_uint32_tp()
        ecmpNextHopGroupId = uint32_tp_value(ecmpNextHopGroupId_p)

        ecmpNextHopGroupCfg = ofdpaTunnelEcmpNextHopGroupConfig_t()
        ecmpNextHopGroupCfg.protocol = OFDPA_TUNNEL_PROTO_VXLAN

        ofdpaTunnelEcmpNextHopGroupCreate(ecmpNextHopGroupId, ecmpNextHopGroupCfg)

        ofdpaTunnelEcmpNextHopGroupMemberAdd(ecmpNextHopGroupId, nextHop1Id)
        ofdpaTunnelEcmpNextHopGroupMemberAdd(ecmpNextHopGroupId, nextHop2Id)

        # create Tunnel Endpoint Port
        endpointPortId_p = new_uint32_tp()
        ofdpaPortTypeSet(endpointPortId_p, OFDPA_PORT_TYPE_LOGICAL_TUNNEL)
        ofdpaPortIndexSet(endpointPortId_p, endpointPortIndex)
        endpointPortId = uint32_tp_value(endpointPortId_p)

        endpointPortCfg = ofdpaTunnelPortConfig_t()
        endpointPortCfg.type = OFDPA_TUNNEL_PORT_TYPE_ENDPOINT
        endpointPortCfg.tunnelProtocol = OFDPA_TUNNEL_PROTO_VXLAN
        endpointPortCfg.configData.endpoint.remoteEndpoint = remoteEndpointIp
        endpointPortCfg.configData.endpoint.localEndpoint  = localEndpointIp
        endpointPortCfg.configData.endpoint.ttl = ttl
        endpointPortCfg.configData.endpoint.ecmp = 1
        endpointPortCfg.configData.endpoint.nextHopId = ecmpNextHopGroupId

        endpointPortCfg.configData.endpoint.protocolInfo.vxlan.terminatorUdpDstPort = terminatorUdpDestPort
        endpointPortCfg.configData.endpoint.protocolInfo.vxlan.initiatorUdpDstPort = initiatorUdpDestPort
        endpointPortCfg.configData.endpoint.protocolInfo.vxlan.udpSrcPortIfNoEntropy = udpSrcPortIfNoEntropy
        endpointPortCfg.configData.endpoint.protocolInfo.vxlan.useEntropy = useEntropy

        endpointPortName = "EndpointPort"
        portNameBuffDesc.size = len(endpointPortName) + 1
        BuffDesc_pstart_setbytes(portNameBuffDesc, endpointPortName)

        ofdpaTunnelPortCreate(endpointPortId, portNameBuffDesc, endpointPortCfg)

        # add Access and Endpoint ports to tenant
        ofdpaTunnelPortTenantAdd(accessPortId, tunnelId)
        ofdpaTunnelPortTenantAdd(endpointPort1Id, tunnelId)

        # set up Ingress Port flow
        ingressPortFlowEntry = ofdpaFlowEntry_t()
        ofdpaFlowEntryInit(OFDPA_FLOW_TABLE_ID_INGRESS_PORT, ingressPortFlowEntry)
        ingressPortFlowEntry.flowData.ingressPortFlowEntry.gotoTableId = OFDPA_FLOW_TABLE_ID_BRIDGING

        ingressPortFlowEntry.flowData.ingressPortFlowEntry.match_criteria.tunnelId = tunnelId
        ingressPortFlowEntry.flowData.ingressPortFlowEntry.match_criteria.tunnelIdMask = OFDPA_TUNNEL_ID_EXACT_MASK

        ofdpaFlowAdd(ingressPortFlowEntry)

        # set up VLAN flow admitting tagged traffic on next hop port 1
        vlanFlowEntry = ofdpaFlowEntry_t()
        ofdpaFlowEntryInit(OFDPA_FLOW_TABLE_ID_VLAN, vlanFlowEntry)
        vlanFlowEntry.flowData.vlanFlowEntry.gotoTableId = OFDPA_FLOW_TABLE_ID_TERMINATION_MAC
        vlanFlowEntry.flowData.vlanFlowEntry.match_criteria.inPort = nextHop1PhysicalPort
        vlanFlowEntry.flowData.vlanFlowEntry.match_criteria.vlanId = (OFDPA_VID_PRESENT | nextHop1VlanId)
        vlanFlowEntry.flowData.vlanFlowEntry.match_criteria.vlanIdMask = (OFDPA_VID_PRESENT | OFDPA_VID_EXACT_MASK)

        ofdpaFlowAdd(vlanFlowEntry)

        # set up VLAN flow admitting tagged traffic on next hop port 2
        vlanFlowEntry = ofdpaFlowEntry_t()
        ofdpaFlowEntryInit(OFDPA_FLOW_TABLE_ID_VLAN, vlanFlowEntry)
        vlanFlowEntry.flowData.vlanFlowEntry.gotoTableId = OFDPA_FLOW_TABLE_ID_TERMINATION_MAC
        vlanFlowEntry.flowData.vlanFlowEntry.match_criteria.inPort = nextHop2PhysicalPort
        vlanFlowEntry.flowData.vlanFlowEntry.match_criteria.vlanId = (OFDPA_VID_PRESENT | nextHop2VlanId)
        vlanFlowEntry.flowData.vlanFlowEntry.match_criteria.vlanIdMask = (OFDPA_VID_PRESENT | OFDPA_VID_EXACT_MASK)

        ofdpaFlowAdd(vlanFlowEntry)

        # set up Bridging flows for both directions
        bridgingFlowEntry = ofdpaFlowEntry_t()
        ofdpaFlowEntryInit(OFDPA_FLOW_TABLE_ID_BRIDGING, bridgingFlowEntry)
        bridgingFlowEntry.flowData.bridgingFlowEntry.gotoTableId = OFDPA_FLOW_TABLE_ID_ACL_POLICY
        bridgingFlowEntry.flowData.bridgingFlowEntry.match_criteria.tunnelId = tunnelId
        bridgingFlowEntry.flowData.bridgingFlowEntry.match_criteria.tunnelIdMask = OFDPA_TUNNEL_ID_EXACT_MASK
        MACAddress_set(bridgingFlowEntry.flowData.bridgingFlowEntry.match_criteria.destMacMask, "ffff.ffff.ffff")

        MACAddress_set(bridgingFlowEntry.flowData.bridgingFlowEntry.match_criteria.destMac, localStationMac)
        bridgingFlowEntry.flowData.bridgingFlowEntry.tunnelLogicalPort = accessPortId

        ofdpaFlowAdd(bridgingFlowEntry)

        MACAddress_set(bridgingFlowEntry.flowData.bridgingFlowEntry.match_criteria.destMac, remoteStationMac)
        bridgingFlowEntry.flowData.bridgingFlowEntry.tunnelLogicalPort = endpointPortId

        ofdpaFlowAdd(bridgingFlowEntry)

    else:
        print "Unable to initialize."


if __name__ == '__main__': main()
