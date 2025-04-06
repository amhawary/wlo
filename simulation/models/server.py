import mesa

from .model import Farm
from .portrayal import portrayal
from .agents import NUMBER_OF_CELLS

SIZE_OF_CANVAS_IN_PIXELS_X = 400
SIZE_OF_CANVAS_IN_PIXELS_Y = 500

simulation_params = {
    "height": NUMBER_OF_CELLS, 
    "width": NUMBER_OF_CELLS,
    "populaion": mesa.visualization.Slider(
        'number of robots',
        2, #default
        1, #min
        10, #max
        1, #step
        "choose how many picker robots to include in the simulation"
    )
    ,
    "mutrate": 
        mesa.visualization.Slider(
        'number of drones',
        2, #default
        1, #min
        10, #max
        1, #step
        "choose how many drones to include in the simulation",
        
    )
    ,
        "mutstep": 
        mesa.visualization.Slider(
        'Initial Strawberries',
        10, #default
        5, #min
        50, #max
        5, #step
        "choose how many ready strawberry trees to begin with",
        
    )
    ,
    }

grid = mesa.visualization.CanvasGrid(portrayal, NUMBER_OF_CELLS, NUMBER_OF_CELLS, SIZE_OF_CANVAS_IN_PIXELS_X, SIZE_OF_CANVAS_IN_PIXELS_Y)


server = mesa.visualization.ModularServer(
    Farm, [grid], "Robot-Assisted Farming Basic Mode", simulation_params
)

server.launch()