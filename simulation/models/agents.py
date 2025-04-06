from mesa import Agent
import numpy as np

class ShelfAgent(Agent):
    """Represents a shelf in the warehouse"""
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = "shelf"
    
    def step(self):
        # Shelves don't take actions
        pass

class StationAgent(Agent):
    """Represents a pickup or dropoff station"""
    
    def __init__(self, unique_id, model, is_pickup=True):
        super().__init__(unique_id, model)
        self.type = "station"
        self.is_pickup = is_pickup  # True for pickup, False for dropoff
    
    def step(self):
        # Stations don't take actions by themselves
        pass

class BoxAgent(Agent):
    """Represents a box that needs to be moved from pickup to dropoff"""
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.type = "box"
        self.being_carried = False
        self.delivered = False
    
    def step(self):
        # Boxes don't take actions by themselves
        pass