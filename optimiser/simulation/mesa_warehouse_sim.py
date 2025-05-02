import mesa
from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from ..function.__helpers import astar

class WarehouseAgent(Agent):
    """An agent that moves through the warehouse."""
    def __init__(self, unique_id, model, start_pos, end_pos):
        super().__init__(unique_id, model)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.current_pos = start_pos
        self.path = []
        self.finished = False

    def step(self):
        if self.finished:
            return
            
        if not self.path:
            # Calculate path if we don't have one
            self.path = self.model.find_path(self.current_pos, self.end_pos)
            if not self.path:
                self.finished = True
                return
                
        # Move to next position in path
        next_pos = self.path.pop(0)
        self.model.grid.move_agent(self, next_pos)
        self.current_pos = next_pos
        
        # Check if we've reached the destination
        if self.current_pos == self.end_pos:
            self.finished = True

class WarehouseModel(Model):
    """A model for simulating warehouse operations."""
    def __init__(self, layout, operations):
        super().__init__()
        self.width = layout.width
        self.height = layout.length
        self.grid = MultiGrid(self.width, self.height, True)
        self.schedule = RandomActivation(self)
        self.operations = operations
        self.agents = []
        self.current_operation = 0
        self.steps = 0
        self.max_steps = 1000  # Prevent infinite loops
        self.layout = layout  # Store layout for pathfinding
        
        # Initialize walls and aisles
        self.initialize_layout(layout)
        
        # Create agents for each operation
        self.create_agents()
        
        self.datacollector = DataCollector(
            agent_reporters={"Position": "pos"}
        )

    def initialize_layout(self, layout):
        """Initialize the grid with walls and aisles from the layout."""
        # Add walls
        for x, y in layout.structure.get('wall', []):
            # Convert 1-based coordinates to 0-based
            grid_x = x - 1
            grid_y = y - 1
            if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
                self.grid.place_agent(WallAgent(self.next_id(), self), (grid_x, grid_y))
            
        # Add aisles
        for x, y in layout.structure.get('aisle', []):
            self.grid.place_agent(AisleAgent(self.next_id(), self), (x, y))

    def create_agents(self):
        """Create agents for each operation."""
        for op in self.operations:
            # Convert 1-based coordinates to 0-based
            start_pos = (op.from_entity[0] - 1, op.from_entity[1] - 1)
            end_pos = (op.to_entity[0] - 1, op.to_entity[1] - 1)
            
            agent = WarehouseAgent(
                self.next_id(),
                self,
                start_pos,
                end_pos
            )
            self.agents.append(agent)
            self.schedule.add(agent)
            self.grid.place_agent(agent, start_pos)

    def find_path(self, start, end):
        """Find a path from start to end using A* algorithm."""
        # Convert 0-based coordinates to 1-based for A*
        start_1based = (start[0] + 1, start[1] + 1)
        end_1based = (end[0] + 1, end[1] + 1)
        
        # Use the existing A* implementation
        path = astar(start_1based, end_1based, self.layout, self.layout.aisle_width)
        
        if path:
            # Convert path back to 0-based coordinates
            return [(x-1, y-1) for x, y in path]
        return None

    def step(self):
        """Advance the model by one step."""
        self.steps += 1
        self.schedule.step()
        self.datacollector.collect(self)
        
        # Check if all agents have finished
        if all(agent.finished for agent in self.agents):
            return False
        if self.steps >= self.max_steps:
            return False
        return True


def run_simulation(layout):
    """Run the Mesa simulation and return a score."""
    model = WarehouseModel(layout, layout.operations)
    
    # Run simulation until completion or max steps
    while model.step():
        pass
    
    # Calculate simulation score based on:
    # 1. Number of completed operations
    # 2. Average time to complete operations
    # 3. Number of collisions/conflicts
    completed_ops = sum(1 for agent in model.agents if agent.finished)
    total_ops = len(model.operations)
    completion_rate = completed_ops / total_ops if total_ops > 0 else 0
    
    # Normalize to 0-1 range
    return completion_rate