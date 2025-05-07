from .algorithm import ga
from .function import standard_layout_fitness, two_step_fitness
from .simulation import mesa_warehouse_sim, mapf

get_func = {
    "ga": ga.GA,
    "standard_layout_fitness": standard_layout_fitness.get_fitness,
    "two_step_fitness": two_step_fitness,
    "mesa_warehouse_sim": mesa_warehouse_sim.WarehouseModel,
    "mapf_sim": mapf
}


class Optimiser:
    def __init__(self, layout, algorithm, function, simulation, hyperparameters=None) -> None:
        self.layout=layout
        self.algorithm=get_func[algorithm]
        self.function=get_func[function]
        self.simulation=get_func[simulation]
        
    def run_optimisation(self):
        a = self.algorithm(self.layout, self.function)
        a.run()

        self.layout1=a.layout1
        self.layout2=a.layout2
        self.layout3=a.layout3


    def run_simulation(self):
        a = self.simulation(self.layout1)
        a.run()

        self.results1 = a.results

        a = self.simulation(self.layout2)
        a.run()

        self.results2 = a.results

        a = self.simulation(self.layout3)
        a.run()

        self.results3 = a.results

    def to_dict(self):
        return {
        'length': self.length,
        'width': self.width,
        'entities': self.entities,
        'structure': self.structure,
        'zones': self.zones,
        'utilities': self.utilities,
        'operations':self.operations
        }
    
    def export_layouts(self):
        return [self.layout1, self.layout2, self.layout3]
    
    def import_layouts(self, layouts):
        self.layout1=layouts[0]
        self.layout2=layouts[1]
        self.layout3=layouts[2]