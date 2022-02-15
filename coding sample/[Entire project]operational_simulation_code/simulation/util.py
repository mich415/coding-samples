import simpy
import random
import numpy as np

from simulation.variables import *


def get_maint_interval_wind():
    """Return time for between maintenance."""
    return MAINT_INTERVAL_WIND


def time_to_failure_wind():
    """Return time(days) until next failure for a turbine."""
    return random.expovariate(BREAK_MEAN_WIND)


def get_vessel_speed():
    return random.randint(VESSEL_SPEED_RANGE[0], VESSEL_SPEED_RANGE[1])


def time_to_failure_dc():
    """Return time(days) until next failure for the data center."""
    return random.expovariate(BREAK_MEAN_DC)


# OPEX
get_vessel_cost = lambda x: x * VESSEL_CHARTER_COST

get_person_cost_wind = lambda x: x * CORRECTIVE_WIND_WORKERS * CORRECTIVE_WIND_WAGE

get_person_cost_dc = lambda x: x * CORRECTIVE_DC_WORKERS * CORRECTIVE_DC_WAGE

get_person_cost_preventive = lambda x: x * PREVENTIVE_WORKERS * PREVENTIVE_WAGE


# for markov

def get_month(time: simpy.Environment.now):
    simulation_year = np.ceil(time / (24 * 360))
    ytd = time - 24 * 360 * (simulation_year - 1)
    identifier = ytd / (24 * 30)

    if identifier < 1:
        return 1
    elif 1 <= identifier < 2:
        return 2
    elif 2 <= identifier < 3:
        return 3
    elif 3 <= identifier < 4:
        return 4
    elif 4 <= identifier < 5:
        return 5
    elif 5 <= identifier < 6:
        return 6
    elif 6 <= identifier < 7:
        return 7
    elif 7 <= identifier < 8:
        return 8
    elif 8 <= identifier < 9:
        return 9
    elif 9 <= identifier < 10:
        return 10
    elif 10 <= identifier < 11:
        return 11
    elif 11 <= identifier < 12:
        return 12
