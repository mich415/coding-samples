import dash
import dash_core_components as dcc
import dash_html_components as html

from simulation.operation_simulation import run_simulation
from simulation import data_compiling as dc
from simulation import data_visualization as dv


app = dash.Dash()

offshore_wind_farm, offshore_data_center, standard_maintenance = run_simulation(debug=True)
standard_data = dc.get_standard_maintenance_data(standard_maintenance)

corrective_data_vis = dc.get_corrective_data(offshore_wind_farm, offshore_data_center)
trip_count_vis = dc.get_corrective_trip_count(corrective_data_vis)
df_corrective = dc.get_data_by_discrete_year(corrective_data_vis)
df_opex_by_category = dc.get_opex_by_category(corrective_data_vis, standard_data)
df_total_opex = dc.get_total_opex_by_year(df_corrective, standard_data)

time_fig = dv.mkgraph_all_corrective_maintenance(corrective_data_vis)
trip_count_fig = dv.mkgraph_corrective_trip_count(trip_count_vis)
vessel_wait_time_fig = dv.mkgraph_vessel_wait_time(df_total_opex)
down_time_fig = dv.mkgraph_down_time(df_corrective)
available_percentage_fig = dv.mkgraph_availability_by_year(df_corrective)
corrective_opex_fig = dv.mkgraph_corrective_opex_per_year(df_corrective)
total_opex_fig = dv.mkgraph_total_opex_by_year(df_total_opex)
total_opex = dc.get_all_time_opex(df_total_opex)

corrective_opex_by_category_fig = dv.mkgraph_corrective_opex_by_category(df_opex_by_category)
all_opex_by_category_fig = dv.mkgraph_all_opex_by_category(df_opex_by_category)
# all_opex_by_source_fig = dv.mkgraph_all_opex_by_source(df_opex_by_category)

print("wind: {}, dc: {}, preventive: {}".format(
    dc.get_opex_value_by_category(df_opex_by_category)["OffshoreWindFarm"],
    dc.get_opex_value_by_category(df_opex_by_category)["data center"],
    dc.get_opex_value_by_category(df_opex_by_category)["preventive"])
)

app.layout = html.Div(children=[
    html.H1(
        children="Offshore data center operation simulation",
        style={'fontFamily': "Arial", 'paddingLeft': 20, 'paddingTop': 10}
    ),
    dcc.Graph(figure=time_fig),
    dcc.Graph(figure=trip_count_fig),
    dcc.Graph(figure=vessel_wait_time_fig),
    dcc.Graph(figure=down_time_fig),
    dcc.Graph(figure=available_percentage_fig),
    dcc.Graph(figure=corrective_opex_by_category_fig),
    dcc.Graph(figure=all_opex_by_category_fig),
    # dcc.Graph(figure=all_opex_by_source_fig),
    html.Div(
        children="15 year OPEX: {} USD".format(int(total_opex)),
        style={'fontSize': 30, 'fontFamily': "Arial", 'textAlign': "center", 'paddingTop': 10, 'paddingBottom': 30}
    )

], style={'textAlign': "center"})

app.run_server(debug=True)
