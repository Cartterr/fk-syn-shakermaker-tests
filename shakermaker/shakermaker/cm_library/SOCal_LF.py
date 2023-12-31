# -*- coding: utf-8 -*-
"""

"""
from shakermaker.crustmodel import CrustModel 
layers = [
    [1.88176,   0.86272,   2.11223,   0.03000,     18.15821,        8.80168],
    [2.40000,   1.20000,   2.20000,   0.07000,     40.00000,       20.00000],
    [2.80000,   1.40000,   2.30000,   0.20000,     50.00000,       25.00000],
    [3.10000,   1.60000,   2.40000,   0.20000,     50.00000,       25.00000],
    [3.40000,   1.80000,   2.45000,   0.20000,     60.00000,       30.00000],
    [3.70000,   2.10000,   2.50000,   0.30000,     60.00000,       30.00000],
    [4.40000,   2.40000,   2.60000,   2.00000,    200.00000,      100.00000],
    [5.10000,   2.80000,   2.70000,   2.00000,    280.00000,      140.00000],
    [5.60000,   3.15000,   2.75000,   1.00000,   2378.87280,     1189.43640],
    [6.15000,   3.60000,   2.82500,   5.00000,   2624.63080,     1312.31540],
    [6.32000,   3.65000,   2.85000,   5.00000,   2651.93720,     1325.96860],
    [6.55000,   3.70000,   2.90000,   5.00000,   2679.24370,     1339.62180],
    [6.80000,   3.80000,   2.95000,  10.00000,   2733.85650,     1366.92830],
    [7.80000,   4.50000,   3.20000,   0.00000,    450.00000,      225.00000],
]

def SOCal_LF():
    """ Crustal model for Southern California

    Returns:
    ==========
    :returns: :class:`shakermaker.CrustModel`

    References: 
    + SCEC BBP
    
    """

    #Initialize CrustModel
    model = CrustModel(len(layers))

    for k, props in enumerate(layers):
        vp=props[0]
        vs=props[1]
        rho=props[2]
        thickness=props[3]
        Qa=props[4]
        Qb=props[5]

        thickness=props[3]

        model.add_layer(thickness, vp, vs, rho, Qa, Qb)

    return model


