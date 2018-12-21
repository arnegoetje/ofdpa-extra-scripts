#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 13:07:17 2018

@author: Arne Goetje <arne_goetje@edge-core.com>
"""

from OFDPA_python import *

# add group and bucket
def addGroupBucket(groupEntry, groupBucket):
    rc = ofdpaGroupAdd(groupEntry)
    if rc != OFDPA_E_NONE:
        print "Failed to add group entry. rc = %d" %(rc)
        return rc

    rc = ofdpaGroupBucketEntryAdd(groupBucket)
    if rc != OFDPA_E_NONE:
        print "Failed to add bucket to the group. rc = %d" %(rc)
        return rc

    return OFDPA_E_NONE


# add l2 interface group
def installL2InterfaceGroup(vlan, port, groupId1_p):

    uint32_tp_assign(groupId1_p, 0)
    groupEntry = ofdpaGroupEntry_t()
    groupBucket = ofdpaGroupBucketEntry_t()

    ofdpaGroupTypeSet(groupId1_p, OFDPA_GROUP_ENTRY_TYPE_L2_INTERFACE)
    ofdpaGroupVlanSet(groupId1_p, vlan)
    ofdpaGroupPortIdSet(groupId1_p, port)
    groupEntry.groupId = uint32_tp_value(groupId1_p)

    groupBucket.groupId = groupEntry.groupId
    groupBucket.bucketIndex = 0
    groupBucket.bucketData.l2Interface.outputPort = port
    return addGroupBucket(groupEntry, groupBucket)


# add mpls interface group
def installMplsInterfaceGroup(index, refGroupId, vlan, srcMac, dstMac, groupId1_p):
    uint32_tp_assign(groupId1_p, 0)
    groupEntry = ofdpaGroupEntry_t()
    groupBucket = ofdpaGroupBucketEntry_t()

    ofdpaGroupTypeSet(groupId1_p, OFDPA_GROUP_ENTRY_TYPE_MPLS_LABEL)
    ofdpaGroupMplsSubTypeSet(groupId1_p, OFDPA_MPLS_INTERFACE)
    ofdpaGroupIndexSet(groupId1_p, index)
    groupEntry.groupId = uint32_tp_value(groupId1_p)

    groupBucket.groupId = groupEntry.groupId
    groupBucket.bucketIndex = 0
    groupBucket.referenceGroupId = refGroupId
    groupBucket.bucketData.mplsInterface.vlanId = (vlan | OFDPA_VID_PRESENT)
    MACAddress_set(groupBucket.bucketData.mplsInterface.srcMac, srcMac)
    MACAddress_set(groupBucket.bucketData.mplsInterface.dstMac, dstMac)
    return addGroupBucket(groupEntry, groupBucket)


# add mpls label group
def installMplsLabelGroup(index, refGroupId, bos, mplsLabel, groupId1_p, subtype):
    uint32_tp_assign(groupId1_p, 0)
    groupEntry = ofdpaGroupEntry_t()
    groupBucket = ofdpaGroupBucketEntry_t()

    ofdpaGroupTypeSet(groupId1_p, OFDPA_GROUP_ENTRY_TYPE_MPLS_LABEL)
    ofdpaGroupMplsSubTypeSet(groupId1_p, subtype)
    ofdpaGroupIndexSet(groupId1_p, index)
    groupEntry.groupId = uint32_tp_value(groupId1_p)

    groupBucket.groupId = groupEntry.groupId
    groupBucket.bucketIndex = 0
    groupBucket.referenceGroupId = refGroupId
    groupBucket.bucketData.mplsLabel.mplsLabel = mplsLabel
    groupBucket.bucketData.mplsLabel.mplsBOS = bos
    groupBucket.bucketData.mplsLabel.pushMplsHdr = 1
    return addGroupBucket(groupEntry, groupBucket)


# add l3 unicast group
def installL3UnicastGroup(index, refGroupId, vlan, srcMac, dstMac, groupId1_p):
    uint32_tp_assign(groupId1_p, 0)
    groupEntry = ofdpaGroupEntry_t()
    groupBucket = ofdpaGroupBucketEntry_t()

    ofdpaGroupTypeSet(groupId1_p, OFDPA_GROUP_ENTRY_TYPE_L3_UNICAST)
    ofdpaGroupIndexSet(groupId1_p, index)
    groupEntry.groupId = uint32_tp_value(groupId1_p)

    groupBucket.groupId = groupEntry.groupId
    groupBucket.bucketIndex = 0
    groupBucket.referenceGroupId = refGroupId
    groupBucket.bucketData.l3Unicast.vlanId = (vlan | OFDPA_VID_PRESENT)
    MACAddress_set(groupBucket.bucketData.l3Unicast.srcMac, srcMac)
    MACAddress_set(groupBucket.bucketData.l3Unicast.dstMac, dstMac)
    return addGroupBucket(groupEntry, groupBucket)

# initialize vlan flow
def initializeVlanFlow(port, vlan, flow):
    ofdpaFlowEntryInit(OFDPA_FLOW_TABLE_ID_VLAN, flow)
    flow.flowData.vlanFlowEntry.match_criteria.inPort =  port
    flow.flowData.vlanFlowEntry.match_criteria.vlanId = (OFDPA_VID_PRESENT | vlan)
    flow.flowData.vlanFlowEntry.match_criteria.vlanIdMask = (OFDPA_VID_PRESENT | OFDPA_VID_EXACT_MASK)
    flow.flowData.vlanFlowEntry.setVlanIdAction = 0

# initialize termination mac flow
def initializeTermMacFlow(port, vlan, dstMac, etherType, flow):
    ofdpaFlowEntryInit(OFDPA_FLOW_TABLE_ID_TERMINATION_MAC, flow)
    flow.flowData.terminationMacFlowEntry.match_criteria.inPort =  port
    flow.flowData.terminationMacFlowEntry.match_criteria.inPortMask =  OFDPA_INPORT_EXACT_MASK
    flow.flowData.terminationMacFlowEntry.match_criteria.vlanId =  (OFDPA_VID_PRESENT | vlan)
    flow.flowData.terminationMacFlowEntry.match_criteria.vlanIdMask =  (OFDPA_VID_PRESENT | OFDPA_VID_EXACT_MASK)
    flow.flowData.terminationMacFlowEntry.match_criteria.etherType =  etherType
    MACAddress_set(flow.flowData.terminationMacFlowEntry.match_criteria.destMac, dstMac)
    MACAddress_set(flow.flowData.terminationMacFlowEntry.match_criteria.destMacMask, "ff:ff:ff:ff:ff:ff")

# initialize unicast routing flow
def initializeUnicastRoutingFlow(vrf, dstIp4, flow):
    ofdpaFlowEntryInit(OFDPA_FLOW_TABLE_ID_UNICAST_ROUTING, flow)
    flow.flowData.unicastRoutingFlowEntry.gotoTableId = OFDPA_FLOW_TABLE_ID_ACL_POLICY
    flow.flowData.unicastRoutingFlowEntry.match_criteria.etherType = 0x0800
    flow.flowData.unicastRoutingFlowEntry.match_criteria.vrf = vrf
    flow.flowData.unicastRoutingFlowEntry.match_criteria.vrfMask = OFDPA_VRF_VALUE_MASK
    flow.flowData.unicastRoutingFlowEntry.match_criteria.dstIp4 = dstIp4
    flow.flowData.unicastRoutingFlowEntry.match_criteria.dstIp4Mask = 0xffffffff

# initialize mpls flow
def initializeMplsFlow(mplsLabel, bos, newEthertype, flow):
    ofdpaFlowEntryInit(OFDPA_FLOW_TABLE_ID_MPLS_1, flow)
    flow.flowData.mplsFlowEntry.match_criteria.etherType = 0x8847
    flow.flowData.mplsFlowEntry.match_criteria.mplsBos = bos
    flow.flowData.mplsFlowEntry.match_criteria.mplsLabel = mplsLabel
    flow.flowData.mplsFlowEntry.decrementTtlAction = 1
    if newEthertype != 0:
        flow.flowData.mplsFlowEntry.popLabelAction = 1
        flow.flowData.mplsFlowEntry.newEtherType = newEthertype

