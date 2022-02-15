# case A
DISTANCE = 10  # km
NUM_TURBINES = 17

# # case B
# DISTANCE = 45  # km
# NUM_TURBINES = 14

VESSEL_RESOURCE_COUNT = 2

# SIM_TIME = 24 * 360 * 15  # Simulation time in hours(15 years)
SIM_TIME = 24 * 360 * 150  # Simulation time in hours(15 years)

MTTF_OFFSHORE_WIND = (1 / 8.273) * 360 * 24  # (hours)
BREAK_MEAN_WIND = 1 / MTTF_OFFSHORE_WIND
# MTTF_OFFSHORE_WIND = (1/15.84) * 360 * 24  # (hours)
# BREAK_MEAN_WIND = 1 / MTTF_OFFSHORE_WIND

MTTF_OFFSHORE_DC = 15000  # (hours) 通常の5倍程度 0.576 y
BREAK_MEAN_DC = 1 / MTTF_OFFSHORE_DC

MAINT_INTERVAL_WIND = 1 * 24
MAINT_INTERVAL_DC = 30 * 24

# vessel
VESSEL_SPEED_RANGE = (30, 48)  # km/h
VESSEL_CHARTER_COST = 2200  # random.randint(1500 / 24, 4000 / 24)  # $/h  TODO: set this to a single value

CORRECTIVE_WIND_WORK_TIME = 8  # h, 1 captain 3 Wf
CORRECTIVE_DC_WORK_TIME = 10  # h, 1 captain 3 dc
PREVENTIVE_TIME = 4  # h, 1 captain 1 wf 1 dc

# people
CORRECTIVE_WIND_WORKERS = 4
CORRECTIVE_DC_WORKERS = 4
PREVENTIVE_WORKERS = 3
CORRECTIVE_WIND_WAGE = 50  # $/h
CORRECTIVE_DC_WAGE = 30  # $/h
PREVENTIVE_WAGE = 20  # $/h