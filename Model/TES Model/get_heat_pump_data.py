
def heatpump_data(ir, life_H, capex_H, fixed_OM_H):
    # Heat pump:
    CRF_H = ir / (1 - (1 + ir) ** (-life_H))    # Calculate TES capital recovery factor
    p_HK = capex_H * CRF_H + fixed_OM_H         # TES power rating cost
    return p_HK
