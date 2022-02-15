import pandas as pd
import plotly.express as px
import simpy
from simulation.markov import OceanMarkovChainSimulation


def simulate_sea_state(env: simpy.Environment, time_list: [], state_list: []):
    while True:
        time_list.append(env.now / (24 * 30))
        if OceanMarkovChainSimulation(env).check_sea_is_stable():
            state_list.append("calm")
        else:
            state_list.append("stormy")
        yield env.timeout(6)


#

SIM_TIME = (24 * 30) * 12

time_data = []
state_data = []

# Create an environment and start the setup process
environment = simpy.Environment()
environment.process(simulate_sea_state(environment, time_data, state_data))
environment.run(until=SIM_TIME)

sea_state_data = pd.DataFrame(
    {
        "time": time_data,
        "state": state_data,
    }
)

fig = px.histogram(sea_state_data, x="time", color="state", marginal="rug")

fig.update_xaxes(
    title_text="Month of Year",
    title_font={"size": 20},
    linecolor="#BCCCDC",
    gridcolor="#BCCCDC",
)
# fig.update_yaxes(
#     title_standoff=10,
#     title_text="State",
#     title_font={"size": 20},
#     linecolor="#BCCCDC",
#     gridcolor="#BCCCDC",
# )
fig.update_layout(legend=dict(
    font=dict(size=20),
    orientation="h",
    yanchor="bottom",
    y=1,
    xanchor="right",
    x=0.95
    ),
    font_size=18,
    plot_bgcolor="#FFF",
)

fig.show()

print("静音率: {}".format(state_data.count("calm")/len(state_data)))
