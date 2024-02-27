#nuclear_profile = "Historic"
nuclear_profile = "Idealised"

# Make an idealised nuclear profile based on a 1 month in 24 maintenance schedule, but only in Apr to September
# 0.9 comes fromm https://www.eia.gov/todayinenergy/detail.php?id=51978
# 0.8 is approximation of historic UK load factor
for idx, row in nuc_pv_demand_data.iterrows():
    if idx.month in [1, 2, 3, 10, 11, 12]:
        nuc_pv_demand_data.loc[idx, 'nuclear_norm'] = 0.8+1/12
    else:
        nuc_pv_demand_data.loc[idx, 'nuclear_norm'] = 0.8-1/12