from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import VisualizationElement
from models.agents import ShelfAgent, StationAgent, RobotAgent, BoxAgent

class WarehouseCanvas(CanvasGrid):
    """Custom visualization for the warehouse grid"""
    
    def __init__(self, grid_width=20, grid_height=20, canvas_width=500, canvas_height=500):
        # Use the portrayal_method from this class
        super().__init__(self.portrayal_method, grid_width, grid_height, canvas_width, canvas_height)

    @staticmethod
    def portrayal_method(agent):
        """Define how different agents are portrayed in the visualization"""
        if agent is None:
            return None
            
        portrayal = {"Shape": "rect", "w": 0.9, "h": 0.9, "Layer": 0}
            
        if isinstance(agent, ShelfAgent):
            portrayal["Color"] = "#8B4513"  # Brown for shelves
            portrayal["Layer"] = 1
            
        elif isinstance(agent, StationAgent):
            if agent.is_pickup:
                portrayal["Color"] = "#00FF00"  # Green for pickup stations
                portrayal["Layer"] = 1
            else:
                portrayal["Color"] = "#FF0000"  # Red for dropoff stations
                portrayal["Layer"] = 1
                
        elif isinstance(agent, RobotAgent):
            portrayal["Color"] = "#0000FF"  # Blue for robots
            portrayal["Layer"] = 3
            portrayal["Shape"] = "circle"
            portrayal["r"] = 0.8
            
        elif isinstance(agent, BoxAgent):
            if agent.delivered:
                portrayal["Color"] = "#00FF00"  # Green for delivered boxes
            else:
                portrayal["Color"] = "#FFFF00"  # Yellow for undelivered boxes
            portrayal["Layer"] = 2
            portrayal["w"] = 0.7
            portrayal["h"] = 0.7
            
        return portrayal