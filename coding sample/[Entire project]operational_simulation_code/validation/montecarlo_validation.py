from simulation.operation_simulation import run_simulation
from simulation import data_compiling as dc

import pandas as pd
import numpy as np

SIM_YEAR = 150

offshore_wind_farm, offshore_data_center, standard_maintenance = run_simulation()

wind_farm_data = offshore_wind_farm[0].data
wind_farm_data = wind_farm_data[wind_farm_data["event_start_time"] != 0]
wind_farm_data["year"] = wind_farm_data["event_start_time"] / (24 * 360)
wind_farm_data["discrete_year"] = np.ceil(wind_farm_data["year"])
wind_farm_data["trip_count"] = 1
# wind_farm_data = wind_farm_data.groupby("discrete_year").count()

corrective_data_vis = dc.get_corrective_data(offshore_wind_farm, offshore_data_center)
trip_count_vis = dc.get_corrective_trip_count(corrective_data_vis)


df_dc_count = trip_count_vis[trip_count_vis["name"].isin(["data center"])]
wind_farm_data = wind_farm_data.groupby("discrete_year").count().reset_index()

average_dc = df_dc_count["trip_count"].sum()/SIM_YEAR  # TODO
average_wind = wind_farm_data["trip_count"].sum()/SIM_YEAR  # TODO

df_dc_count["ave"] = average_dc
wind_farm_data["ave"] = average_wind

df_dc_count["std"] = (df_dc_count["trip_count"] - df_dc_count["ave"])**2
wind_farm_data["std"] = (wind_farm_data["trip_count"] - wind_farm_data["ave"])**2

var_dc = df_dc_count["std"].sum()/SIM_YEAR  # TODO
var_wind = wind_farm_data["std"].sum()/SIM_YEAR  # TODO

print(average_dc, average_wind)
print("___")
print(var_dc, var_wind)

