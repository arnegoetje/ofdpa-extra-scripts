#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 20 16:57:39 2018

@author: Arne Goetje <arne_goetje@edge-core.com>
"""

from OFDPA_python import *

"""
OFDPA_ERROR_t {
    OFDPA_E_NONE                 = 0    Success.
    OFDPA_E_RPC                  = -20  Error in RPC.
    OFDPA_E_INTERNAL             = -21  Internal error.
    OFDPA_E_PARAM                = -22  Invalid parameter.
    OFDPA_E_ERROR                = -23  Parameter constraint violated.
    OFDPA_E_FULL                 = -24  Maximum count is already reached or table full.
    OFDPA_E_EXISTS               = -25  Already exists.
    OFDPA_E_TIMEOUT              = -26  Operation Timeout.
    OFDPA_E_FAIL                 = -27  Operation Fail.
    OFDPA_E_DISABLED             = -28  Disabled.
    OFDPA_E_UNAVAIL              = -29  Parameter/feature not supported.
    OFDPA_E_NOT_FOUND            = -30  Parameter not found.
    OFDPA_E_EMPTY                = -31  Nothing to report or table is empty.
    OFDPA_E_REQUEST_DENIED       = -32  Request denied.
    OFDPA_NOT_IMPLEMENTED_YET    = -33  Not implemented.
}
"""

"""
OFDPA_FEATURE_t {
    OFDPA_FEATURE_INVALID = 0,
    OFDPA_FEATURE_VXLAN,                    /* If VXLAN is supported */
    OFDPA_FEATURE_ACLIPV6MAC,               /* IPv6 addresses plus MAC addresses in ACLs*/
    OFDPA_FEATURE_ROUTETOIFPNEXTHOP,        /* L3_ENTRY can forward to an IFP (type 6) next hop */
    OFDPA_FEATURE_MPLSTHREELABELS,          /* Able to pop three MPLS labels */
    OFDPA_FEATURE_MPLSSUPPORTED,            /* Is MPLS supported at all */
    OFDPA_FEATURE_MPLSECMP,                 /* Is MPLS ECMP supported */
    OFDPA_FEATURE_OAM,                      /* Is OAM supported */
    OFDPA_FEATURE_SERVICE_METER,            /* Is Service Meter supported */
    /* DOT1AG Features */
    OFDPA_DOT1AG_MPLS_TP_CCM_SUPPORT,
    OFDPA_DOT1AG_LTR_SORT_FEATURE_ID,

    OFDPA_FEATURE_MAX
}
"""

def testFeaturesSupported ():
    try:
        rc = ofdpaFeatureSupported(OFDPA_FEATURE_VXLAN)
        assert(rc == OFDPA_E_UNAVAIL, 'VXLAN is not supported.')
    except AssertionError: pass
