import pandas as pd
import numpy as np

from simulation import util


# region corrective_data
def get_corrective_data(offshore_wind_farm, offshore_data_center):
    # compile wind data
    wind_farm_data = offshore_wind_farm[0].data
    for i in range(1, util.NUM_TURBINES):
        wind_farm_data = pd.concat([wind_farm_data, offshore_wind_farm[i].data])
    wind_farm_data = wind_farm_data[wind_farm_data["event_start_time"] != 0]

    # data center data
    dc_data = offshore_data_center.data
    data_center_data = dc_data[dc_data["event_start_time"] != 0]

    # corrective
    corrective_data = pd.concat([wind_farm_data, data_center_data])
    corrective_data["year"] = corrective_data["event_start_time"] / (24 * 360)
    corrective_data["discrete_year"] = np.ceil(corrective_data["year"])

    # total time

    corrective_data_vis = corrective_data.copy()
    corrective_data_vis.loc[corrective_data_vis["name"] != "data center", "name"] = "Turbine"

    return corrective_data_vis


# endregion


# region corrective_trip_count
def get_corrective_trip_count(corrective_data_vis: pd.DataFrame):
    # trip count
    corrective_data_vis["trip_count"] = 1

    # sum count
    df_dc = corrective_data_vis.groupby("name").get_group("data center")
    df_wind = corrective_data_vis.groupby("name").get_group("Turbine")

    dc_count_by_year = df_dc.groupby("discrete_year").count()
    dc_count_by_year["name"] = "data center"
    dc_count_by_year = dc_count_by_year.drop(columns=["event_start_time", "vessel_wait_time", "trip_time", "task_time",
                                                      "sea_wait_time", "total_time", "year"]).reset_index()
    wind_count_by_year = df_wind.groupby("discrete_year").count()
    wind_count_by_year["name"] = "OffshoreWindFarm"
    wind_count_by_year = wind_count_by_year.drop(
        columns=["event_start_time", "vessel_wait_time", "trip_time", "task_time",
                 "sea_wait_time", "total_time", "year"]).reset_index()

    trip_count_vis = pd.concat([dc_count_by_year, wind_count_by_year])

    return trip_count_vis


# region get_preventive_data (standard)
def get_standard_maintenance_data(standard_maintenance):
    # preventive data
    st_data = standard_maintenance.data
    standard_data = st_data[st_data["event_start_time"] != 0].sort_values("event_start_time")

    return standard_data


# endregion


# region get_data_by_discrete_year
def get_data_by_discrete_year(corrective_data_vis: pd.DataFrame):
    df_dc = corrective_data_vis.groupby("name").get_group("data center")
    df_wind = corrective_data_vis.groupby("name").get_group("Turbine")

    dc_by_year = df_dc.drop(columns=["event_start_time", "year"]).groupby("discrete_year").sum()
    dc_by_year["name"] = "data center"
    dc_by_year = dc_by_year.reset_index()
    dc_by_year["OPEX"] = dc_by_year["total_time"].map(util.get_person_cost_dc) + dc_by_year["total_time"].map(
        util.get_vessel_cost)

    wind_by_year = df_wind.drop(columns=["event_start_time", "year"]).groupby("discrete_year").sum()
    wind_by_year["name"] = "OffshoreWindFarm"
    wind_by_year = wind_by_year.reset_index()
    wind_by_year["OPEX"] = wind_by_year["total_time"].map(util.get_person_cost_wind) + wind_by_year["total_time"].map(
        util.get_vessel_cost)

    df_corrective = pd.concat([dc_by_year, wind_by_year])

    return df_corrective

    # endregion


# region total_opex
def get_total_opex_by_year(df_corrective, standard_data):
    standard_data["year"] = standard_data["event_start_time"] / (24 * 360)
    standard_data["discrete_year"] = np.ceil(standard_data["year"])
    standard_data = standard_data.drop(columns=["event_start_time", "year"]).groupby("discrete_year").sum()
    standard_data["name"] = "preventive"
    preventive_by_year = standard_data.reset_index()
    preventive_by_year["OPEX"] = preventive_by_year["total_time"].map(util.get_person_cost_preventive) + \
                                 preventive_by_year[
                                     "total_time"].map(util.get_vessel_cost)

    df_total_opex = pd.concat([df_corrective, preventive_by_year]).groupby(
        "discrete_year").sum().reset_index()

    return df_total_opex


# endregion

# region 15year opex
def get_all_time_opex(df_total_opex: pd.DataFrame):
    total_opex = df_total_opex["OPEX"].sum()

    return total_opex


def get_opex_value_by_category(df_opex_by_category: pd.DataFrame):
    opex = df_opex_by_category.groupby("name").sum()["total_OPEX"]

    return opex

# endregion


# region get_corrective_opex_by_category
def get_opex_by_category(corrective_data_vis: pd.DataFrame, standard_data: pd.DataFrame):

    df_dc = corrective_data_vis.groupby("name").get_group("data center")
    df_wind = corrective_data_vis.groupby("name").get_group("Turbine")

    dc_by_year = df_dc.drop(columns=["event_start_time", "year"]).groupby("discrete_year").sum()
    dc_by_year["name"] = "data center"
    dc_by_year = dc_by_year.reset_index()
    dc_by_year["OPEX_vessel"] = dc_by_year["total_time"].map(util.get_vessel_cost)
    dc_by_year["OPEX_personnel"] = dc_by_year["total_time"].map(util.get_person_cost_dc)
    dc_by_year["total_OPEX"] = dc_by_year["OPEX_vessel"] + dc_by_year["OPEX_personnel"]

    wind_by_year = df_wind.drop(columns=["event_start_time", "year"]).groupby("discrete_year").sum()
    wind_by_year["name"] = "OffshoreWindFarm"
    wind_by_year = wind_by_year.reset_index()
    wind_by_year["OPEX_vessel"] = wind_by_year["total_time"].map(util.get_vessel_cost)
    wind_by_year["OPEX_personnel"] = wind_by_year["total_time"].map(util.get_person_cost_dc)
    wind_by_year["total_OPEX"] = wind_by_year["OPEX_vessel"] + wind_by_year["OPEX_personnel"]

    standard_data["year"] = standard_data["event_start_time"] / (24 * 360)
    standard_data["discrete_year"] = np.ceil(standard_data["year"])
    standard_data = standard_data.drop(columns=["event_start_time", "year"]).groupby("discrete_year").sum()
    standard_data["name"] = "preventive"
    preventive_by_year = standard_data.reset_index()
    preventive_by_year["OPEX_vessel"] = preventive_by_year["total_time"].map(util.get_vessel_cost)
    preventive_by_year["OPEX_personnel"] = preventive_by_year["total_time"].map(util.get_person_cost_dc)
    preventive_by_year["total_OPEX"] = preventive_by_year["OPEX_vessel"] + preventive_by_year["OPEX_personnel"]

    df_opex_by_category = pd.concat([dc_by_year, wind_by_year, preventive_by_year])
    return df_opex_by_category

# endregion
