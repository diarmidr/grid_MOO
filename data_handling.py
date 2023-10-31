import datetime
import pandas as pd
# Write results to CSV
# f_1 = objective function 1 (demand_met)
# f_2 = objective function 2 (cost)
def export_csv(res):
    results = {'X_0': [],
               'X_1': [],
               'X_2': [],
               'X_3': [],
               'X_4': [],
               'X_5': [],
               'X_6': [],
               'X_7': [],
               'X_8': [],
               'X_9': [],
               'X_10': [],
               'X_11': [],
               'f_1': [],
               'f_2': [],
               'f_3': [],
               'CV': []
               }

    for i in range(len(res.X)):
        results['X_0'] += [res.X[i][0]]
        results['X_1'] += [res.X[i][1]]
        results['X_2'] += [res.X[i][2]]
        results['X_3'] += [res.X[i][3]]
        results['X_4'] += [res.X[i][4]]
        results['X_5'] += [res.X[i][5]]
        results['X_6'] += [res.X[i][6]]
        results['X_7'] += [res.X[i][7]]
        results['X_8'] += [res.X[i][8]]
        results['X_9'] += [res.X[i][9]]
        results['X_10'] += [res.X[i][10]]
        results['X_11'] += [res.X[i][11]]
        results['f_1'] += [res.F[i][0]/1e9]
        results['f_2'] += [-res.F[i][1]]
        results['f_3'] += [res.F[i][2]]
        results['CV'] += [res.CV[i]]
    print(results)
    pd.DataFrame(results).to_csv('MOO_grid_output_' +
                                 str(datetime.datetime.now().year) + '_' +
                                 str(datetime.datetime.now().month) + '_' +
                                 str(datetime.datetime.now().day) + '_' +
                                 str(datetime.datetime.now().hour) +
                                 str(datetime.datetime.now().minute) + '.csv')