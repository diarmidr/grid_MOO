import numpy as np
import pandas as pd
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.core.problem import ElementwiseProblem
from multiprocessing.pool import ThreadPool
from pymoo.core.problem import StarmapParallelization
from pymoo.optimize import minimize
from pymoo.visualization.scatter import Scatter
from data_handling import export_csv
from params import CAPEX_dict, OCGT_dict, ESS_dict
import objective_functions as obj_funcs
####################
# Time series data #
####################
t_data = pd.read_csv("data/generator_profiles.csv")
###########################
# System level parameters #
###########################
demand_scaling = 1  # I'm fixing demand at current levels, no point scaling it as it will also change shape
# Variable key:
# P_nuclear, P_PV, P_wind_offshore, P_ESS_1, P_ESS_2, P_ESS_3, P_ESS_4, dur_ESS_1, dur_ESS_2, dur_ESS_3, dur_ESS_4, P_OCGT

class GridMOOProblem(ElementwiseProblem):

    def __init__(self, **kwargs):
        super().__init__(n_var=12,
                         n_obj=4,
                         n_ieq_constr=2,
                         xl=np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
                         xu=np.array([75, 100, 200, 100, 10, 100, 100, 12, 1000, 1000, 1000, 55]), **kwargs)

    #return fuel_cost, percentage_demand_met, co2_emissions

    def _evaluate(self, x, out, *args, **kwargs):
        # Dispatch function returns fuel cost (£), demand met 9%) and CO2 emissions (kg/MWh).

        f1, f2, f3, f4 = obj_funcs.dispatch_v2(t_data, x, CAPEX_dict, ESS_dict, OCGT_dict, graph=False)


        # Constraints, in format < 0
        g1 = x[4] * x[8] - 700  # PHS Energy rating less than 700Gwh (with power < 10GW set in bounds above)
        g2 = x[3] + x[4] + x[5] + x[6] - 100  # Total storage power < 100GW
        print("Objectives", f1, f2, f3, f4)
        out["F"] = [f1, f2, f3, f4]
        out["G"] = [g1, g2]

# initialize the thread pool and create the runner
n_threads = 4
pool = ThreadPool(n_threads)
runner = StarmapParallelization(pool.starmap)

problem = GridMOOProblem(elementwise_runner=runner)

algorithm = NSGA2(pop_size=20)

res = minimize(problem,
               algorithm,
               termination=("n_gen", 5),
               verbose=True,
               return_least_infeasible=True,
               seed=1)
pool.close()
print("execution time", res.exec_time)
export_csv(res)
plot = Scatter()
plot.add(res.F, edgecolor="red", facecolor="none")
plot.show()