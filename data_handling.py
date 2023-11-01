import datetime
import pandas as pd
# Write results to CSV
# f_1 = objective function 1 (demand_met)
# f_2 = objective function 2 (cost)
def export_csv(res):
    results = {'% load met': [],
               'Max deficit (GW)': [],
               'Cost(£/MWh)': [],
               'CO2 (g/MWh)': [],
               'GW_nucl.': [],
               'GW_PV': [],
               'GW_wind': [],
               'GW_gas': [],
               'GW_LIB': [],
               'GW_PH': [],
               'GW_CAES': [],
               'GW_H2': [],
               'h_LIB': [],
               'h_PH': [],
               'h_CAES': [],
               'h_H2': [],
               'CV': []
               }

    for i in range(len(res.X)):
        results['% load met'] += [-res.F[i][0]]
        results['Max deficit (GW)'] += [res.F[i][1]]
        results['Cost(£/MWh)'] += [res.F[i][2]]
        results['CO2 (g/MWh)'] += [res.F[i][3]]
        results['GW_nucl.'] += [res.X[i][0]]
        results['GW_PV'] += [res.X[i][1]]
        results['GW_wind'] += [res.X[i][2]]
        results['GW_gas'] += [res.X[i][11]]  # Need to sort this ordering out so OCGT is with other generation
        results['GW_LIB'] += [res.X[i][3]]
        results['GW_PH'] += [res.X[i][4]]
        results['GW_CAES'] += [res.X[i][5]]
        results['GW_H2'] += [res.X[i][6]]
        results['h_LIB'] += [res.X[i][7]]
        results['h_PH'] += [res.X[i][8]]
        results['h_CAES'] += [res.X[i][9]]
        results['h_H2'] += [res.X[i][10]]
        results['CV'] += [res.CV[i]]
    print(results)
    pd.DataFrame(results).to_csv('grid_MOO_output_' +
                                 str(datetime.datetime.now().year) + '_' +
                                 str(datetime.datetime.now().month) + '_' +
                                 str(datetime.datetime.now().day) + '_' +
                                 str(datetime.datetime.now().hour) +
                                 str(datetime.datetime.now().minute) + '.csv')