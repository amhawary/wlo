from .agents import ShelfAgent, StationAgent, BoxAgent

def portrayal(agent):
    if agent is None:
        return None

    # Default portrayal settings
    portrayal = {"Shape": "rect", "w": 0.9, "h": 0.9, "Layer": 0, "Filled": True}

    if isinstance(agent, ShelfAgent):
        portrayal["Color"] = "#8B4513"  # Brown for shelves
        portrayal["Layer"] = 1
        # portrayal["text"] = "S"         # Label for ShelfAgent
        portrayal["text_color"] = "white"
    elif isinstance(agent, StationAgent):
        if agent.is_pickup:
            portrayal["Color"] = "#00FF00"  # Green for pickup stations
        else:
            portrayal["Color"] = "#FF0000"  # Red for dropoff stations
        portrayal["Layer"] = 1
        # portrayal["text"] = "ST"        # Label for StationAgent
        portrayal["text_color"] = "black"
    elif isinstance(agent, BoxAgent):
        if agent.delivered:
            portrayal["Color"] = "#00FF00"  # Green for delivered boxes
        else:
            portrayal["Color"] = "#FFFF00"  # Yellow for undelivered boxes
        portrayal["Layer"] = 2
        portrayal["w"] = 0.7
        portrayal["h"] = 0.7
        # portrayal["text"] = "B"         # Label for BoxAgent
        portrayal["text_color"] = "black"

    return portrayal
