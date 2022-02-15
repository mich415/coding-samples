import pandas as pd
import plotly.express as px

from simulation import util

FONT_SIZE = 20
FONT_SIZE_TITLE = 18


# region all_corrective_maintenance
def mkgraph_all_corrective_maintenance(corrective_data_vis: pd.DataFrame):
    time_fig = px.scatter(corrective_data_vis, x="year", y="total_time", color="name",
                          title='Corrective operation time by year per occurrence',
                          labels={"Turbine": "OffshoreWindFarm", "data center": "date center"},
                          category_orders={"name": ["data center", "OffshoreWindFarm"]})
    time_fig.update_xaxes(
        title_text="Timeline [y]",
        title_font={"size": FONT_SIZE},
        linecolor="#BCCCDC",
        gridcolor="#BCCCDC",
    )
    time_fig.update_yaxes(
        title_standoff=10,
        title_text="Maintenance operation time [h]",
        title_font={"size": FONT_SIZE},
        linecolor="#BCCCDC",
        gridcolor="#BCCCDC",
    )
    time_fig.update_layout(legend=dict(
        font=dict(size=FONT_SIZE),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1),
        legend_title="",
        font_size=FONT_SIZE_TITLE,
        plot_bgcolor="#FFF",
    )

    return time_fig
# endregion


# region corrective_trip_count
def mkgraph_corrective_trip_count(trip_count_vis: pd.DataFrame):
    trip_count_fig = px.line(trip_count_vis, x="discrete_year", y="trip_count", color="name",
                             title='count of corrective trips by year')
    trip_count_fig.update_traces(mode='markers+lines')
    trip_count_fig.update_xaxes(
        title_text="Year (discrete) [y]",
        title_font={"size": FONT_SIZE},
        linecolor="#BCCCDC",
        gridcolor="#BCCCDC",
    )
    trip_count_fig.update_yaxes(
        title_standoff=10,
        title_text="Number of corrective trips",
        title_font={"size": FONT_SIZE},
        linecolor="#BCCCDC",
        gridcolor="#BCCCDC",
    )
    trip_count_fig.update_layout(legend=dict(
        font=dict(size=FONT_SIZE),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1),
        legend_title="",
        font_size=FONT_SIZE_TITLE,
        plot_bgcolor="#FFF",
    )

    return trip_count_fig
# endregion


# region vessel_wait_time
def mkgraph_vessel_wait_time(df_total_opex: pd.DataFrame):
    vessel_wait_time_fig = px.bar(df_total_opex, x="discrete_year", y="vessel_wait_time",
                                  title='Vessel wait time by year')
    vessel_wait_time_fig.update_xaxes(
        title_text="Year (discrete) [y]",
        title_font={"size": FONT_SIZE},
        linecolor="#BCCCDC",
        gridcolor="#BCCCDC",
    )
    vessel_wait_time_fig.update_yaxes(
        title_text="Waiting time [h]",
        title_font={"size": FONT_SIZE},
        linecolor="#BCCCDC",
        gridcolor="#BCCCDC",
    )

    vessel_wait_time_fig.update_layout(
        font_size=FONT_SIZE_TITLE,
        plot_bgcolor="#FFF",
    )

    vessel_wait_time_fig.update_traces(marker_color="#176BA0")

    return vessel_wait_time_fig
# endregion


# region down_time_per_year
def mkgraph_down_time(df_corrective: pd.DataFrame):
    down_time_fig = px.line(df_corrective, x="discrete_year", y="down_time", color="name",
                            title='System down time by year (windfarm is sum of all turbines)')
    down_time_fig.update_traces(mode='markers+lines')
    down_time_fig.update_xaxes(
        title_text="Year (discrete) [y]",
        title_font={"size": FONT_SIZE},
        linecolor="#BCCCDC",
        gridcolor="#BCCCDC",
    )
    down_time_fig.update_yaxes(
        title_text="Down time [h]",
        title_font={"size": FONT_SIZE},
        linecolor="#BCCCDC",
        gridcolor="#BCCCDC",
    )
    down_time_fig.update_layout(legend=dict(
        font=dict(size=FONT_SIZE),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1),
        legend_title="",
        font_size=FONT_SIZE_TITLE,
        plot_bgcolor="#FFF",
    )

    return down_time_fig
# endregion


# region availability_per_year
def mkgraph_availability_by_year(df_corrective: pd.DataFrame):
    df_wind_avail = df_corrective[df_corrective["name"] == "OffshoreWindFarm"]
    df_dc_avail = df_corrective[df_corrective["name"] == "data center"]

    df_wind_avail["total_turbine_time"] = util.NUM_TURBINES * 8640
    df_wind_avail["available_percentage"] = \
        ((df_wind_avail["total_turbine_time"] - df_wind_avail["down_time"]) / df_wind_avail["total_turbine_time"]) * 100
    df_dc_avail["total_dc_time"] = 8640
    df_dc_avail["available_percentage"] = \
        ((df_dc_avail["total_dc_time"] - df_dc_avail["down_time"]) / df_dc_avail["total_dc_time"]) * 100
    df_avail_time = pd.concat([df_dc_avail, df_wind_avail])

    available_percentage_fig = px.line(df_avail_time, x="discrete_year", y="available_percentage", color="name",
                                       title='Available percentage for each system by year (windfarm is sum of all turbines)')
    available_percentage_fig.update_traces(mode='markers+lines')
    available_percentage_fig.update_xaxes(
        title_text="Year (discrete) [y]",
        title_font={"size": FONT_SIZE},
        linecolor="#BCCCDC",
        gridcolor="#BCCCDC",
    )
    available_percentage_fig.update_yaxes(
        title_text="Available percentage [%]",
        title_font={"size": FONT_SIZE},
        linecolor="#BCCCDC",
        gridcolor="#BCCCDC",
    )
    available_percentage_fig.update_layout(legend=dict(
        font=dict(size=FONT_SIZE),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1),
        legend_title="",
        font_size=FONT_SIZE_TITLE,
        plot_bgcolor="#FFF",
    )

    print("data center: {}, wind farm: {}".format(df_dc_avail["available_percentage"], df_wind_avail["available_percentage"].sum()/15))

    return available_percentage_fig
# endregion


# region corrective_opex_by_category
def mkgraph_corrective_opex_by_category(df_opex_by_category: pd.DataFrame):
    corrective_opex_by_category = px.bar(df_opex_by_category[df_opex_by_category["name"] != "preventive"],
                                      x="discrete_year", y="total_OPEX",
                                      title="Corrective OPEX by year with category breakdown", color="name",)
    corrective_opex_by_category.update_xaxes(
        title_text="Year (discrete) [y]",
        title_font={"size": FONT_SIZE},
        linecolor="#BCCCDC",
        gridcolor="#BCCCDC",
    )
    corrective_opex_by_category.update_yaxes(
        title_text="OPEX [USD]",
        title_font={"size": FONT_SIZE},
        linecolor="#BCCCDC",
        gridcolor="#BCCCDC",
    )
    corrective_opex_by_category.update_layout(legend=dict(
        font=dict(size=FONT_SIZE),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1),
        legend_title="",
        font_size=FONT_SIZE_TITLE,
        plot_bgcolor="#FFF",
    )

    return corrective_opex_by_category


# endregion

# region all opex by category
def mkgraph_all_opex_by_category(df_opex_by_category: pd.DataFrame):
    all_opex_by_category_fig = px.bar(df_opex_by_category, x="discrete_year", y="total_OPEX", title="Total OPEX by year with category breakdown",
                                      color="name",
                                      color_discrete_sequence=["rgb(101, 115, 247)", "rgb(237, 86, 66)", "#ffa600"])
    all_opex_by_category_fig.update_xaxes(
        title_text="Year (discrete) [y]",
        title_font={"size": FONT_SIZE},
        linecolor="#BCCCDC",
        gridcolor="#BCCCDC",
    )
    all_opex_by_category_fig.update_yaxes(
        title_text="OPEX [USD]",
        title_font={"size": FONT_SIZE},
        linecolor="#BCCCDC",
        gridcolor="#BCCCDC",
    )

    all_opex_by_category_fig.update_layout(legend=dict(
        font=dict(size=FONT_SIZE),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1),
        legend_title="",
        font_size=FONT_SIZE_TITLE,
        plot_bgcolor="#FFF",
    )

    return all_opex_by_category_fig


# endregion


# region all opex by source
# def mkgraph_all_opex_by_source(df_opex_by_category: pd.DataFrame):
#     all_opex_by_source_fig = px.bar(df_opex_by_category, x="discrete_year", y=["OPEX_vessel", "OPEX_personnel"],
#                                     title="Total OPEX by year with source breakdown",)
#     all_opex_by_source_fig.update_xaxes(
#         title_text="Year (discrete) [y]",
#         title_font={"size": FONT_SIZE},
#         linecolor="#BCCCDC",
#         gridcolor="#BCCCDC",
#     )
#     all_opex_by_source_fig.update_yaxes(
#         title_text="OPEX [USD]",
#         title_font={"size": FONT_SIZE},
#         linecolor="#BCCCDC",
#         gridcolor="#BCCCDC",
#     )
#
#     all_opex_by_source_fig.update_layout(legend=dict(
#         font=dict(size=FONT_SIZE),
#         orientation="h",
#         yanchor="bottom",
#         y=1.02,
#         xanchor="right",
#         x=1),
#         legend_title="",
#         font_size=FONT_SIZE_TITLE,
#         plot_bgcolor="#FFF",
#     )
#
#     return all_opex_by_source_fig


# endregion

# region corrective_opex_per_year
def mkgraph_corrective_opex_per_year(df_corrective: pd.DataFrame):
    corrective_opex_fig = px.line(df_corrective, x="discrete_year", y="OPEX", color="name",
                                  title='OPEX for corrective operations by year')
    corrective_opex_fig.update_traces(mode='markers+lines')
    corrective_opex_fig.update_xaxes(
        title_text="Year (discrete) [y]",
        title_font={"size": FONT_SIZE},
        linecolor="#BCCCDC",
        gridcolor="#BCCCDC",
    )
    corrective_opex_fig.update_yaxes(
        title_text="OPEX for corrective operations [USD]",
        title_font={"size": FONT_SIZE},
        linecolor="#BCCCDC",
        gridcolor="#BCCCDC",
    )
    corrective_opex_fig.update_layout(legend=dict(
        font=dict(size=FONT_SIZE),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1),
        legend_title="",
        font_size=FONT_SIZE_TITLE,
        plot_bgcolor="#FFF",
    )

    return corrective_opex_fig


# endregion


# region total_opex
def mkgraph_total_opex_by_year(df_total_opex: pd.DataFrame):
    total_opex_fig = px.bar(df_total_opex, x="discrete_year", y="OPEX", title='Total OPEX by year')
    total_opex_fig.update_xaxes(
        title_text="Year (discrete) [y]",
        title_font={"size": FONT_SIZE},
        linecolor="#BCCCDC",
        gridcolor="#BCCCDC",
    )
    total_opex_fig.update_yaxes(
        title_text="Total OPEX [USD]",
        title_font={"size": FONT_SIZE},
        linecolor="#BCCCDC",
        gridcolor="#BCCCDC",
    )

    total_opex_fig.update_layout(
        font_size=FONT_SIZE_TITLE,
        plot_bgcolor="#FFF",
    )

    return total_opex_fig
# endregion
