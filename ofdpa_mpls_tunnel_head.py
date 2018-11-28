#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 13:29:07 2018

@author: arne_goetje@edge-core.com


        Spine1
Leaf1 <        > Leaf2
        Spine2

Leaf1 and Leaf2 initiate two MPLS tunnels via Spine1 and Spine2 in each direction.

This is code for the leaf switches.

"""

from OFDPA_python import *
from ofdpa_lib import *

def main():
    rc = ofdpaClientInitialize("OFDPA_example")

    if rc == OFDPA_E_NONE:
        # variables used to set up routing scenario
        cust_port               = 33                    # port that connects to the leaf switch
        fabric_port1            = 49                    # fabric port 1 to Spine1
        fabric_port2            = 50                    # fabric port 2 to Spine2
        cust_vlan               = 80                    # tagged traffic entering the leaf switch (S-tag)
        tunnel1_vlan             = 4090                 # Tunnel 1 internal VLAN ID
        tunnel2_vlan             = 4091                 # Tunnel 2 internal VLAN ID
        vpn_label_init          = 0x12                  # VPN (inner MPLS) label from Leaf1 to Leaf2
        tunnel1_label_init      = 0x112a                # Tunnel (outer MPLS) label from Leaf1 to Spine1
        tunnel2_label_init      = 0x122a                # Tunnel (outer MPLS) label from Leaf1 to Spine2
        vpn_label_term          = 0x21                  # Incoming VPN (inner MPLS) label from Leaf2
        tunnel1_label_term      = 0x211b                # Incoming tunnel (outer MPLS) label from Spine1
        tunnel2_label_term      = 0x221b                # Incoming tunnel (outer MPLS) label from Spine2
        my_mac                  = "c4:39:3a:f4:5b:da"   # My Mac Address
        destination1_mac        = "cc:37:ab:d0:d2:20"   # Spine1 MAC address
        destination2_mac        = "cc:37:ab:d0:d4:28"   # Spine2 MAC address
        cust_mac                = "00:11:00:aa:bb:cc"   # Device that connects to cust_port MAC address
        vrf                     = 1                     # internal VRF (defaut 1)
        source_ip               = 0xa0a00101            # Leaf1 (source) IP: 10.10.1.1
        dest_ip                 = 0xa0a00102            # Leaf2 (dest) IP: 10.10.1.2
        BOS_FALSE               = 0
        BOS_TRUE                = 1

    # MPLS L3 VPN initiation flows
        # install groups
        l2InterfaceGroupId1_p = new_uint32_tp()
        rc = installL2InterfaceGroup(tunnel1_vlan, fabric_port1, l2InterfaceGroupId1_p)
        if rc != OFDPA_E_NONE:
            print "Installation of L2 interface group for Tunnel 1 failed. rc = %d" %(rc)
            return

        l2InterfaceGroupId2_p = new_uint32_tp()
        rc = installL2InterfaceGroup(tunnel2_vlan, fabric_port2, l2InterfaceGroupId2_p)
        if rc != OFDPA_E_NONE:
            print "Installation of L2 interface group for Tunnel 2 failed. rc = %d" %(rc)
            return

        mplsInterfaceGroupId1_p = new_uint32_tp()
        rc = installMplsInterfaceGroup(0, uint32_tp_value(l2InterfaceGroupId1_p), tunnel1_vlan, my_mac, destination1_mac, mplsInterfaceGroupId1_p)
        if rc != OFDPA_E_NONE:
            print "Installation of MPLS interface group for Tunnel 1 failed. rc = %d" %(rc)
            return

        mplsInterfaceGroupId2_p = new_uint32_tp()
        rc = installMplsInterfaceGroup(1, uint32_tp_value(l2InterfaceGroupId2_p), tunnel2_vlan, my_mac, destination2_mac, mplsInterfaceGroupId2_p)
        if rc != OFDPA_E_NONE:
            print "Installation of MPLS interface group for Tunnel 2 failed. rc = %d" %(rc)
            return

        mplsTunnelLabelGroupId1_p = new_uint32_tp()
        rc = installMplsLabelGroup(0, uint32_tp_value(mplsInterfaceGroupId1_p), BOS_FALSE, tunnel1_label_init, mplsTunnelLabelGroupId1_p, OFDPA_MPLS_TUNNEL_LABEL1)
        if rc != OFDPA_E_NONE:
            print "Installation of MPLS tunnel label group for Tunnel 1 failed. rc = %d" %(rc)
            return

        mplsTunnelLabelGroupId2_p = new_uint32_tp()
        rc = installMplsLabelGroup(1, uint32_tp_value(mplsInterfaceGroupId2_p), BOS_FALSE, tunnel2_label_init, mplsTunnelLabelGroupId2_p, OFDPA_MPLS_TUNNEL_LABEL1)
        if rc != OFDPA_E_NONE:
            print "Installation of MPLS tunnel label group for Tunnel 2 failed. rc = %d" %(rc)
            return

        # Set up MPLS ECMP group.  This configures the next hops in an ECMP group.

        mplsECMPGroupId = new_uint32_tp()

        ofdpaGroupTypeSet(mplsECMPGroupId, OFDPA_GROUP_ENTRY_TYPE_MPLS_FORWARDING)
        ofdpaGroupMplsSubTypeSet(mplsECMPGroupId, OFDPA_MPLS_ECMP)
        ofdpaGroupIndexSet(mplsECMPGroupId, index1)

        mplsECMPGroupEntry  = ofdpaGroupEntry_t()
        mplsECMPGroupEntry.groupId = uint32_tp_value(mplsECMPGroupId)

        mplsECMPGroupBucket1 = ofdpaGroupBucketEntry_t()
        mplsECMPGroupBucket1.groupId = mplsECMPGroupEntry.groupId
        mplsECMPGroupBucket1.bucketIndex = 0
        mplsECMPGroupBucket1.referenceGroupId = uint32_tp_value(mplsTunnelLabelGroupId1)

        mplsECMPGroupBucket2 = ofdpaGroupBucketEntry_t()
        mplsECMPGroupBucket2.groupId = mplsECMPGroupEntry.groupId
        mplsECMPGroupBucket2.bucketIndex = 1
        mplsECMPGroupBucket2.referenceGroupId = uint32_tp_value(mplsTunnelLabelGroupId2)

        rc = ofdpaGroupAdd(mplsECMPGroupEntry)
        if rc != OFDPA_E_NONE:
          print "Unable to add MPLS ECMP group. rc = %d " % (rc)
          return

        rc = ofdpaGroupBucketEntryAdd(mplsECMPGroupBucket1)
        if rc != OFDPA_E_NONE:
          print "Unable to add MPLS ECMP group 1st bucket. rc = %d " % (rc)
          return

        rc = ofdpaGroupBucketEntryAdd(mplsECMPGroupBucket2)
        if rc != OFDPA_E_NONE:
          print "Unable to add MPLS ECMP group 2nd bucket. rc = %d " % (rc)
          return

        # Inner VPN Label
        mplsL3VpnLabelGroupId_p = new_uint32_tp()
        rc = installMplsLabelGroup(0, uint32_tp_value(mplsECMPGroupId_p), BOS_TRUE, vpn_label_init, mplsL3VpnLabelGroupId_p, OFDPA_MPLS_L3_VPN_LABEL)
        if rc != OFDPA_E_NONE:
            print "Installation of MPLS L3 VPN label group failed. rc = %d" %(rc)
            return


        # vlan flow
        vlanPortFlow = ofdpaFlowEntry_t()
        initializeVlanFlow(cust_port, cust_vlan, vlanPortFlow)
        vlanPortFlow.flowData.vlanFlowEntry.vrfAction = 1
        vlanPortFlow.flowData.vlanFlowEntry.vrf = vrf
        vlanPortFlow.flowData.vlanFlowEntry.gotoTableId = OFDPA_FLOW_TABLE_ID_TERMINATION_MAC
        rc = ofdpaFlowAdd(vlanPortFlow)
        if rc != OFDPA_E_NONE:
            print "Installation of vlan flow failed. rc = %d" %(rc)
            return

        # termination mac flow
        terminationMacFlow = ofdpaFlowEntry_t()
        initializeTermMacFlow(cust_port, cust_vlan, my_mac, 0x0800, terminationMacFlow)
        terminationMacFlow.flowData.terminationMacFlowEntry.gotoTableId = OFDPA_FLOW_TABLE_ID_UNICAST_ROUTING
        rc = ofdpaFlowAdd(terminationMacFlow)
        if rc != OFDPA_E_NONE:
            print "Installation of termination mac flow failed. rc = %d" %(rc)
            return

        # unicast routing flow
        unicastRoutingFlow = ofdpaFlowEntry_t()
        initializeUnicastRoutingFlow(vrf, dest_ip, unicastRoutingFlow)
        unicastRoutingFlow.flowData.unicastRoutingFlowEntry.groupID = uint32_tp_value(mplsL3VpnLabelGroupId_p)
        rc = ofdpaFlowAdd(unicastRoutingFlow)
        if rc != OFDPA_E_NONE:
            print "Installation of unicast routing flow failed. rc = %d" %(rc)
            return

    # MPLS L3 VPN termination flows
        # install groups
        l2InterfaceGroupIdTerm_p = new_uint32_tp()
        rc = installL2InterfaceGroup(cust_vlan, cust_port, l2InterfaceGroupIdTerm_p)
        if rc != OFDPA_E_NONE:
            print "Installation L2 interface group failed. rc = %d" %(rc)
            return

        l3UnicastGroupIdTerm_p  = new_uint32_tp()
        rc = installL3UnicastGroup(0, uint32_tp_value(l2InterfaceGroupIdTerm_p), cust_vlan, my_mac, cust_mac, l3UnicastGroupIdTerm_p)
        if rc != OFDPA_E_NONE:
            print "Installation of L3 unicast group failed. rc = %d" %(rc)
            return

        # vlan flow
        vlanPortTermFlow = ofdpaFlowEntry_t()
        initializeVlanFlow(fabric_port1, tunnel1_vlan, vlanPortTermFlow)
        vlanPortTermFlow.flowData.vlanFlowEntry.gotoTableId = OFDPA_FLOW_TABLE_ID_TERMINATION_MAC
        rc = ofdpaFlowAdd(vlanPortTermFlow)
        if rc != OFDPA_E_NONE:
            print "Installation of vlan flow for MPLS L3 VPN termination flow for Tunnel 1 failed. rc = %d" %(rc)
            return

        # vlan flow
        vlanPortTermFlow = ofdpaFlowEntry_t()
        initializeVlanFlow(fabric_port2, tunnel2_vlan, vlanPortTermFlow)
        vlanPortTermFlow.flowData.vlanFlowEntry.gotoTableId = OFDPA_FLOW_TABLE_ID_TERMINATION_MAC
        rc = ofdpaFlowAdd(vlanPortTermFlow)
        if rc != OFDPA_E_NONE:
            print "Installation of vlan flow for MPLS L3 VPN termination flow for Tunnel 2 failed. rc = %d" %(rc)
            return

#==============================================================================
#         # termination mac flow
#         terminationMacTermFlow = ofdpaFlowEntry_t()
#         initializeTermMacFlow(net_port, tunnel1_vlan, my_mac, 0x8847, terminationMacTermFlow)
#         terminationMacTermFlow.flowData.terminationMacFlowEntry.gotoTableId = OFDPA_FLOW_TABLE_ID_MPLS_0
#         rc = ofdpaFlowAdd(terminationMacTermFlow)
#         if rc != OFDPA_E_NONE:
#             print "Installation of termination mac for MPLS L3 VPN termination flow failed. rc = %d" %(rc)
#             return
#
#==============================================================================
        # Set up Termination MAC flow entry. This configures the matching destination MAC, VLAN Id and ingress interface of the ingress packet to set it up for MPLS processing.
        termMacFlowEntry = ofdpaFlowEntry_t()
        ofdpaFlowEntryInit(OFDPA_FLOW_TABLE_ID_TERMINATION_MAC, termMacFlowEntry)
        termMacFlowEntry.flowData.terminationMacFlowEntry.gotoTableId = OFDPA_FLOW_TABLE_ID_MPLS_0
        termMacFlowEntry.flowData.terminationMacFlowEntry.match_criteria.vlanId = (OFDPA_VID_PRESENT | tunnel1_vlan)
        termMacFlowEntry.flowData.terminationMacFlowEntry.match_criteria.vlanIdMask = (OFDPA_VID_PRESENT | OFDPA_VID_EXACT_MASK)
        termMacFlowEntry.flowData.terminationMacFlowEntry.match_criteria.etherType = 0x8847
        MACAddress_set(termMacFlowEntry.flowData.terminationMacFlowEntry.match_criteria.destMac, localMacAddress)
        MACAddress_set(termMacFlowEntry.flowData.terminationMacFlowEntry.match_criteria.destMacMask, "ff:ff:ff:ff:ff:ff")

        rc = ofdpaFlowAdd(termMacFlowEntry)
        if rc != OFDPA_E_NONE:
          print "Unable to add Termination MAC flow entry for Tunnel 1. rc = %d " % (rc)
          return

        termMacFlowEntry = ofdpaFlowEntry_t()
        ofdpaFlowEntryInit(OFDPA_FLOW_TABLE_ID_TERMINATION_MAC, termMacFlowEntry)
        termMacFlowEntry.flowData.terminationMacFlowEntry.gotoTableId = OFDPA_FLOW_TABLE_ID_MPLS_0
        termMacFlowEntry.flowData.terminationMacFlowEntry.match_criteria.vlanId = (OFDPA_VID_PRESENT | tunnel2_vlan)
        termMacFlowEntry.flowData.terminationMacFlowEntry.match_criteria.vlanIdMask = (OFDPA_VID_PRESENT | OFDPA_VID_EXACT_MASK)
        termMacFlowEntry.flowData.terminationMacFlowEntry.match_criteria.etherType = 0x8847
        MACAddress_set(termMacFlowEntry.flowData.terminationMacFlowEntry.match_criteria.destMac, localMacAddress)
        MACAddress_set(termMacFlowEntry.flowData.terminationMacFlowEntry.match_criteria.destMacMask, "ff:ff:ff:ff:ff:ff")

        rc = ofdpaFlowAdd(termMacFlowEntry)
        if rc != OFDPA_E_NONE:
          print "Unable to add Termination MAC flow entry for Tunnel 2. rc = %d " % (rc)
          return

        # mpls tunnel flow
        mplsFirstTerm1Flow = ofdpaFlowEntry_t()
        initializeMplsFlow(tunnel1_label_term, BOS_FALSE, 0x8847, mplsFirstTerm1Flow)
        mplsFirstTerm1Flow.flowData.mplsFlowEntry.gotoTableId = OFDPA_FLOW_TABLE_ID_MPLS_2
        rc = ofdpaFlowAdd(mplsFirstTerm1Flow)
        if rc != OFDPA_E_NONE:
            print "Installation of MPLS tunnel flow for Tunnel 1 failed. rc = %d" %(rc)
            return

        # mpls tunnel flow
        mplsFirstTerm2Flow = ofdpaFlowEntry_t()
        initializeMplsFlow(tunnel2_label_term, BOS_FALSE, 0x8847, mplsFirstTerm2Flow)
        mplsFirstTerm2Flow.flowData.mplsFlowEntry.gotoTableId = OFDPA_FLOW_TABLE_ID_MPLS_2
        rc = ofdpaFlowAdd(mplsFirstTerm2Flow)
        if rc != OFDPA_E_NONE:
            print "Installation of MPLS tunnel flow for Tunnel 2 failed. rc = %d" %(rc)
            return

        # mpls l3 vpn flow
        mplsSecondTermFlow = ofdpaFlowEntry_t()
        initializeMplsFlow(vpn_label_term, BOS_TRUE, 0, mplsSecondTermFlow)
        mplsSecondTermFlow.flowData.mplsFlowEntry.gotoTableId = OFDPA_FLOW_TABLE_ID_MPLS_L3_TYPE
        mplsSecondTermFlow.flowData.mplsFlowEntry.vrf = vrf
        mplsSecondTermFlow.flowData.mplsFlowEntry.vrfAction = 1
        rc = ofdpaFlowAdd(mplsSecondTermFlow)
        if rc != OFDPA_E_NONE:
            print "Installation of MPLS VPN flow failed. rc = %d" %(rc)
            return

        # unicast routing flow
        unicastRoutingTermFlow = ofdpaFlowEntry_t()
        initializeUnicastRoutingFlow(vrf, source_ip, unicastRoutingTermFlow)
        unicastRoutingTermFlow.flowData.unicastRoutingFlowEntry.match_criteria.vrf = vrf
        unicastRoutingTermFlow.flowData.unicastRoutingFlowEntry.match_criteria.vrfMask = OFDPA_VRF_VALUE_MASK
        unicastRoutingTermFlow.flowData.unicastRoutingFlowEntry.groupID = uint32_tp_value(l3UnicastGroupIdTerm_p)
        rc = ofdpaFlowAdd(unicastRoutingTermFlow)
        if rc != OFDPA_E_NONE:
            print "Installation of unicast routing for MPLS L3 VPN flow failed. rc = %d" %(rc)
            return

        # if we are here flows were added in proper way
        print "MPLS L3 VPN flows are configured successfully"

        # clean up
        delete_uint32_tp(l2InterfaceGroupId1_p)
        delete_uint32_tp(l2InterfaceGroupId2_p)
        delete_uint32_tp(mplsInterfaceGroupId1_p)
        delete_uint32_tp(mplsInterfaceGroupId2_p)
        delete_uint32_tp(mplsTunnelLabelGroupId1_p)
        delete_uint32_tp(mplsTunnelLabelGroupId2_p)
        delete_uint32_tp(mplsL3VpnLabelGroupId_p)

        delete_uint32_tp(l2InterfaceGroupIdTerm_p)
        delete_uint32_tp(l3UnicastGroupIdTerm_p)

    else:
        print "Unable to initialize."


if __name__ == '__main__': main()
