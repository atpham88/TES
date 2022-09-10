
def storage_data(ir, life_T, capex_T, fixed_OM_T, p_T_fixed):
    # TES:
    CRF_T = ir / (1 - (1 + ir) ** (-life_T))    # Calculate TES capital recovery factor
    p_TK = capex_T * CRF_T + fixed_OM_T         # TES power rating cost
    p_TC = p_T_fixed * 1000 * 8760              # TES energy cost ($/kJ)
    return p_TK, p_TC
