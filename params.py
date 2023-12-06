#################
# Scalar params #
#################
# Annualised CAPEX for generation and storage, Key: [Name, £/kW annualised]
"""These are mostly annualised CAPEX calculated from levelised costs and capacity factors. E.g. OCGT from BEIS 2025 predicted
 LCOE of £199/MWh for a 600MW plant running 500h/year, of which £86/MWh is roughly CAPEX.
 £86/MWh * 500h/year = £43000/MW.year, or £43/kW.year.
 In the case of BECCS, because I have assumed it will run constantly (high CAPEX so it makes sense), so I can use the
 LCOE reported by Ricardo directly, as capacity factor is always 1. Hence CAPEX is set to 0."""
CAPEX_dict = {"Offshore_wind": [164, 0],
              "PV": [50, 0],
              "Nuclear": [852, 0],
              "BECCS": [0, 0],
              "OCGT": [43, 0],
              "LIB_type": [38, 42],
              "PHS_type": [73, 1],
             "CAES_type": [113, 0.34],
              "HES_type": [188, 0.2]}
# Params for generators that influence emissions
BECCS_dict = {"£_per_MWh": 181,
              "kg_CO2_per_MWh": -743 * 0.9}  # Divide 2020 emissions of 13.3e6tCO2 by generation of 2048 x 8760 MWh and assume 90% capture
OCGT_dict = {"£_ng_per_MWh": 44/0.3,
               "kg_CO2_per_MWh": 500}
# Energy storage params
"""Key: [Name, round trip efficiency, SOC]. The order in rows gives the dispatch priority, which in this case is highest
# RTE first"""
ESS_dict = [["LIB_type", 0.85, 0.5],
            ["PHS_type", 0.75, 0.5],
            ["CAES_type", 0.5, 0.5],
            ["HES_type", 0.4, 0.5]]

