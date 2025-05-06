import os
import subprocess
import tempfile
import json
from typing import List, Tuple, Dict, Optional

Layout = 0

class MAPFSolver:
    def __init__(self, cbs_executable: str = "cbs"):
        """
        Initialize the MAPF solver with the path to the CBSH2-RTC-CHBP executable
        Args:
            cbs_executable: Path to the CBSH2-RTC-CHBP executable
        """
        self.cbs_executable = cbs_executable

    def _create_map_file(self, layout: Layout) -> str:
        """
        Create a map file in the format required by CBSH2-RTC-CHBP
        Returns the path to the created map file
        """
        # Create a temporary file
        map_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.map')
        
        # Write the map header
        map_file.write(f"type octile\n")
        map_file.write(f"height {layout.length}\n")
        map_file.write(f"width {layout.width}\n")
        map_file.write("map\n")
        
        # Create the map grid
        grid = [['.' for _ in range(layout.width)] for _ in range(layout.length)]
        
        # Mark walls
        for wall in layout.structure['wall']:
            x, y = wall
            if 0 < x <= layout.width and 0 < y <= layout.length:
                grid[y-1][x-1] = '@'
        
        # Write the grid
        for row in grid:
            map_file.write(''.join(row) + '\n')
        
        map_file.close()
        return map_file.name

    def _create_scenario_file(self, layout: Layout, start_positions: List[Tuple[int, int]], 
                            goal_positions: List[Tuple[int, int]]) -> str:
        """
        Create a scenario file in the format required by CBSH2-RTC-CHBP
        Returns the path to the created scenario file
        """
        scenario_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.scen')
        
        # Write scenario header
        scenario_file.write(f"version 1\n")
        
        # Write agent start and goal positions
        for i, (start, goal) in enumerate(zip(start_positions, goal_positions)):
            scenario_file.write(f"{i}\t{layout.width}\t{layout.length}\t{start[0]}\t{start[1]}\t{goal[0]}\t{goal[1]}\t0\n")
        
        scenario_file.close()
        return scenario_file.name

    def solve(self, layout: Layout, start_positions: List[Tuple[int, int]], 
              goal_positions: List[Tuple[int, int]], time_limit: int = 60) -> Optional[Dict]:
        """
        Solve the MAPF problem using CBSH2-RTC-CHBP
        Args:
            layout: The layout object
            start_positions: List of (x,y) start positions for each agent
            goal_positions: List of (x,y) goal positions for each agent
            time_limit: Time limit in seconds for the solver
        Returns:
            Dictionary containing the solution paths for each agent, or None if no solution found
        """
        # Create temporary files
        map_file = self._create_map_file(layout)
        scenario_file = self._create_scenario_file(layout, start_positions, goal_positions)
        output_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv')
        output_file.close()

        try:
            # Run the CBSH2-RTC-CHBP solver
            cmd = [
                self.cbs_executable,
                "-m", map_file,
                "-a", scenario_file,
                "-o", output_file.name,
                "-k", str(len(start_positions)),
                "-t", str(time_limit),
                "--cluster_heuristic=CHBP"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Solver failed: {result.stderr}")
                return None

            # Parse the output file
            with open(output_file.name, 'r') as f:
                solution = self._parse_solution(f.read())
                
            return solution

        finally:
            # Clean up temporary files
            os.unlink(map_file)
            os.unlink(scenario_file)
            os.unlink(output_file.name)

    def _parse_solution(self, solution_text: str) -> Dict:
        """
        Parse the solution output from CBSH2-RTC-CHBP
        Returns a dictionary mapping agent IDs to their paths
        """
        paths = {}
        current_agent = None
        current_path = []
        
        for line in solution_text.split('\n'):
            if not line.strip():
                continue
                
            if line.startswith('Agent'):
                if current_agent is not None:
                    paths[current_agent] = current_path
                current_agent = int(line.split()[1])
                current_path = []
            else:
                # Parse position in format (x,y)
                x, y = map(int, line.strip('()').split(','))
                current_path.append((x, y))
                
        if current_agent is not None:
            paths[current_agent] = current_path
            
        return paths

def get_paths_for_operations(layout: Layout, operations: List[Dict]) -> Dict:
    """
    Get paths for all operations in the layout using MAPF
    Args:
        layout: The layout object
        operations: List of operations to find paths for
    Returns:
        Dictionary mapping operation IDs to their paths
    """
    solver = MAPFSolver()
    
    # Extract start and goal positions from operations
    start_positions = []
    goal_positions = []
    for op in operations:
        from_entity = next(e for e in layout.entities if e['id'] == op['from_entity'])
        to_entity = next(e for e in layout.entities if e['id'] == op['to_entity'])
        start_positions.append(from_entity['position'])
        goal_positions.append(to_entity['position'])
    
    # Solve the MAPF problem
    solution = solver.solve(layout, start_positions, goal_positions)
    
    if solution is None:
        return {}
        
    # Map the solution back to operation IDs
    operation_paths = {}
    for i, op in enumerate(operations):
        if i in solution:
            operation_paths[op['id']] = solution[i]
            
    return operation_paths


