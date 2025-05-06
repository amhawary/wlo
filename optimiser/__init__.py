from .algorithm import ga
from .function import standard_layout_fitness, two_step_fitness
from .simulation import mesa_warehouse_sim, mapf

get_func = {
    "ga": ga.GA,
    "standard_layout_fitness": standard_layout_fitness.get_fitness,
    "two_step_function": two_step_fitness,
    "mesa_warehouse_sim": mesa_warehouse_sim.WarehouseModel,
    "mapf_sim": mapf
}


class Optimiser:
    def __init__(self, layout, algorithm, function, simulation, hyperparameters=None) -> None:
        self.layout=layout
        self.algorithm=get_func(algorithm)
        self.function=get_func(function)
        self.simulation=get_func(simulation)

    def run_optimisation(self):
        return self.algorithm(self.layout, self.function)

    def run_simulation(self):
        pass