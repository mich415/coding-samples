import simpy
import random
import plotly.express as px
import pandas as pd
import numpy as np

from simulation import util
from simulation.markov import OceanMarkovChainSimulation


def run_simulation(debug: bool = False):
    if debug:
        random.seed(42)
    data_template = pd.DataFrame([["id", 0, 0, 0, 0, 0, 0, 0]],
                                 columns=["name", "event_start_time", "vessel_wait_time", "trip_time",
                                          "task_time", "sea_wait_time", "total_time", "down_time"])

    # Create an environment and start the setup process
    environment = simpy.Environment()

    # ocean state simulator
    sea_sim = OceanMarkovChainSimulation(environment)

    class WindTurbine(object):
        """A Wind turbine breaks unexpectedly sometimes.

        If it breaks, it requests a repair that uses a shared resource *vessel* and goes back to normal
        after the it is repaired.

        A machine has a *name* which corresponds to the id of it(is not used because shadowing).

        """

        sea_simulation = sea_sim

        def __init__(self, env: simpy.Environment, name: str, vessel: simpy.PriorityResource):
            self.env = env
            self.name = name
            self.broken = False  # track if the instance breaks
            self.data = data_template

            # Start "break_machine" processes for this turbine.
            env.process(self.break_turbine(vessel))

        def fix(self, vessel: simpy.PriorityResource):
            self.broken = True

            # Request a vessel for fixing. This will be P1.
            with vessel.request(priority=1) as req:
                # get access to vessel
                vessel_req_start_time = self.env.now
                yield req
                vessel_get_time = self.env.now
                vessel_wait_time = vessel_get_time - vessel_req_start_time

                # wait for sea to become stable
                mission_ideal_start_time = self.env.now
                while not WindTurbine.sea_simulation.check_sea_is_stable():
                    yield self.env.timeout(6)  # todo: this hours
                    print("sea was too stormy to operate!")
                mission_actual_start_time = self.env.now
                sea_wait_time = mission_actual_start_time - mission_ideal_start_time

                # vessel speed would vary by day
                speed = util.get_vessel_speed()
                trip_time = (util.DISTANCE / speed) * 2
                task_time = util.CORRECTIVE_WIND_WORK_TIME
                total_time = trip_time + task_time + sea_wait_time + vessel_wait_time
                down_time = total_time - (trip_time / 2)
                self.data = self.data.append(
                    {"name": self.name, "event_start_time": vessel_req_start_time,
                     "vessel_wait_time": vessel_wait_time, "trip_time": trip_time, "task_time": task_time,
                     "sea_wait_time": sea_wait_time, "total_time": total_time, "down_time": down_time
                     }, ignore_index=True
                )
                yield self.env.timeout(total_time)

            self.broken = False

        def break_turbine(self, vessel: simpy.PriorityResource):
            """Break the turbine every now and then."""
            while True:
                yield self.env.timeout(util.time_to_failure_wind())  # wait to break(if it does)
                if not self.broken:
                    # Only break the machine if it is currently working.
                    print("Repair requested for {} at {}".format(self.name, self.env.now))
                    yield self.env.process(self.fix(vessel))

    class OffshoreDataCenter(object):
        """The offshore data center breaks unexpectedly sometimes.

        If it breaks, it requests a repair that uses a shared resource *vessel* and goes back to normal
        after the it is repaired.

        A machine has a *name* which corresponds to the id of it(is not used because shadowing).

        """

        sea_simulation = sea_sim

        def __init__(self, env: simpy.Environment, vessel: simpy.PriorityResource):
            self.env = env
            self.broken = False  # track if the instance breaks
            self.data = data_template

            # Start "break_machine" processes for this turbine.
            env.process(self.break_dc(vessel))

        def fix(self, vessel: simpy.PriorityResource):
            self.broken = True

            # Request a vessel for fixing. This will be P1.
            with vessel.request(priority=1) as req:
                # get access to vessel
                start_time = self.env.now
                yield req
                get_time = self.env.now
                vessel_wait_time = get_time - start_time

                # wait for sea to become stable
                mission_ideal_start_time = self.env.now
                while not OffshoreDataCenter.sea_simulation.check_sea_is_stable():
                    yield self.env.timeout(6)  # todo: this hours
                    print("sea was too stormy to operate!")
                mission_actual_start_time = self.env.now
                sea_wait_time = mission_actual_start_time - mission_ideal_start_time

                # vessel speed would vary by day
                speed = util.get_vessel_speed()
                trip_time = (util.DISTANCE / speed) * 2
                task_time = util.CORRECTIVE_DC_WORK_TIME
                total_time = trip_time + task_time + sea_wait_time + vessel_wait_time
                down_time = total_time - (trip_time / 2)
                self.data = self.data.append(
                    {"name": "data center", "event_start_time": start_time, "vessel_wait_time": vessel_wait_time,
                     "trip_time": trip_time, "task_time": task_time, "sea_wait_time": sea_wait_time,
                     "total_time": total_time, "down_time": down_time
                     }, ignore_index=True
                )
                yield self.env.timeout(total_time)

            self.broken = False

        def break_dc(self, vessel: simpy.PriorityResource):
            """Break the data center every now and then."""
            while True:
                yield self.env.timeout(util.time_to_failure_dc())
                if not self.broken:
                    # Only break the machine if it is currently working.
                    print("Repair requested for data center at {}".format(self.env.now))
                    yield self.env.process(self.fix(vessel))

    class OffshoreMaintenance(object):

        def __init__(self, env: simpy.Environment, vessel: simpy.PriorityResource):
            self.env = env
            self.data = data_template

            # Start "break_machine" processes for this turbine.
            env.process(self.standard_maintenance(vessel))

        def standard_maintenance(self, vessel: simpy.PriorityResource):
            """The routine maintenance job. This prevetive operation does not consider sea state"""
            while True:
                # give at least 18 h between maintenance
                yield self.env.timeout(24)
                # Start a new routine maintenance
                speed = util.get_vessel_speed()
                trip_time = (util.DISTANCE / speed) * 2
                task_time = util.PREVENTIVE_TIME
                with vessel.request(priority=2) as req:
                    start_time = self.env.now
                    yield req
                    get_time = self.env.now
                    vessel_wait_time = get_time - start_time
                    total_time = trip_time + task_time + vessel_wait_time

                    self.data = self.data.append(
                        {"event_start_time": start_time, "vessel_wait_time": vessel_wait_time, "trip_time": trip_time,
                         "task_time": task_time, "sea_wait_time": 0, "total_time": total_time, "down_time": 0
                         }, ignore_index=True
                    )

    # Setup and start the simulation
    print('Offshore data center system maintenance simulation')

    # data for routine maintenance
    data_routine = data_template

    # vessel as a shared resource
    vessel = simpy.PriorityResource(environment, capacity=util.VESSEL_RESOURCE_COUNT)

    # set processes
    offshore_wind_farm = [WindTurbine(environment, 'Turbine{}'.format(i), vessel)
                          for i in range(util.NUM_TURBINES)
                          ]
    offshore_data_center = OffshoreDataCenter(environment, vessel)
    standard_maintenance = OffshoreMaintenance(environment, vessel)

    # Execute
    environment.run(until=util.SIM_TIME)

    print("__________")
    print("simulation ended")

    return offshore_wind_farm, offshore_data_center, standard_maintenance
