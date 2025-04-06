from models.warehouse_model import WarehouseModel
from models.portrayal import portrayal

import mesa

SIZE_OF_CANVAS_IN_PIXELS_X = 400
SIZE_OF_CANVAS_IN_PIXELS_Y = 500

simulation_params = {
    # "grid_height": 20, 
    # "grid_width": 20,
    # "canvas_height": 500,
    # "canvas_width": 500 
    }


grid = mesa.visualization.CanvasGrid(portrayal, 20, 20, SIZE_OF_CANVAS_IN_PIXELS_X, SIZE_OF_CANVAS_IN_PIXELS_Y)


server = mesa.visualization.ModularServer(
    WarehouseModel, [grid], "Robot-Assisted Farming Basic Mode", simulation_params
)

server.launch()