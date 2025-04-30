from optimiser.algorithm import *
from optimiser.function import *
from optimiser.simulation import *

algorithms = {
    "": GA
}

functions = {

}

simulations = {

}


class Optimisation():
    def __init__(self, layout, algorithm, function, simulation, hyperparameters=None) -> None:
        self.layout = layout
        self.algorithm = algorithms[algorithm]
        self.function = functions[function]
        self.simulation = simulation[simulation]

    def start_optimisation():
        pass

    def start_simulation():
       pass 
