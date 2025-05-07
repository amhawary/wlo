from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import uuid
import mesa
from models import *
import optimiser as op

app = Flask(
    __name__,
    template_folder='app/templates',
    static_folder='app/static'
)
app.secret_key = 'warehouse_optimiser_secret_key'

# Store active simulations
simulations = {}

@app.route('/')
def index():
    """Landing page for the warehouse optimiser"""
    return render_template('index.html')

@app.route('/config', methods=['GET', 'POST'])
def config():
    """Configuration page for warehouse setup"""
    if request.method == 'POST':
        warehouse_width = int(request.form.get('warehouse_width'))
        warehouse_length = int(request.form.get('warehouse_length'))

        ex_ent_placement = request.form.get('ex_ent_placement')
        wall_placement = request.form.get('wall_placement')

        session['config'] = {
            'warehouse_width': warehouse_width,
            'warehouse_length': warehouse_length,
            'aisle_width': int(request.form.get('aisle_width')),
        }
        
        session['layout_obj'] = Layout(warehouse_width, warehouse_length).to_dict()
        session['initial_layout'] = session['layout_obj']['structure']

        return redirect(url_for('structure'))
         
    return render_template('config.html')

@app.route('/structure', methods=['GET', 'POST'])
def structure():
    """Configuration page for the structure"""
    if request.method == 'POST':
            layout = Layout.from_dict(session["layout_obj"])
            layout_json = request.form.get('layout_data')
            struct = json.loads(layout_json)  # ← Parse JSON string into dic
            
            layout.add_structure(struct)

            session['layout_obj'] = layout.to_dict()
            session['initial_layout'] = session['layout_obj']['structure']
            
            return redirect(url_for('zones'))
    return render_template('structure.html')

@app.route('/zones', methods=['GET', 'POST'])
def zones():
    """Configuration page for zones"""
    if request.method == 'POST':
        layout = Layout.from_dict(session["layout_obj"])
        layout_json = request.form.get('layout_data')
        zones = json.loads(layout_json)  # ← Parse JSON string into dic
        
        layout.add_zones(zones)

        session['layout_obj'] = layout.to_dict()
        session['initial_layout'] = session['layout_obj']['structure']

        return redirect(url_for('utilities'))
    return render_template('zones.html')

@app.route('/utilities', methods=['GET', 'POST'])
def utilities():
    """Configuration page for entities like shelves and stations"""
    if request.method == 'POST':
        layout = Layout.from_dict(session["layout_obj"])
        layout_json = request.form.get('layout_data')
        utilities = json.loads(layout_json)  # ← Parse JSON string into dic
        
        layout.add_utilities(utilities)

        session['layout_obj'] = layout.to_dict()
        session['initial_layout'] = session['layout_obj']['structure']

        return redirect(url_for('entities'))
    return render_template('utilities.html')

@app.route('/entities', methods=['GET', 'POST'])
def entities():
    """Configuration page for entities like shelves and stations"""
    if request.method == 'POST':
        layout = Layout.from_dict(session["layout_obj"])
        layout_json = request.form.get('entities_data')
        entities = json.loads(layout_json)  # ← Parse JSON string into dic

        layout.add_entities(entities)
        session['layout_obj'] = layout.to_dict()

        manual_placement = layout.manual_placed_entities
        print(manual_placement)

        # return redirect(url_for('optimiser'))
        
        if len(manual_placement) > 0:
            session['placing_entities'] = manual_placement
            return redirect(url_for('place_entities'))
        else:
            session['all_entities'] = layout.entities
            return redirect(url_for('operations'))
   
    return render_template('entities.html')

@app.route('/place-entities', methods=['GET', 'POST'])
def place_entities():
    """Configuration page for entities like shelves and stations"""
    if request.method == 'POST':
        layout = Layout.from_dict(session["layout_obj"])
        layout_json = request.form.get('layout_data')
        entities = json.loads(layout_json)  # ← Parse JSON string into dic

        layout.add_positions(entities)
        session['layout_obj'] = layout.to_dict()
        session['all_entities'] = layout.entities
        return redirect(url_for('operations'))
    return render_template('place-entities.html')

@app.route('/operations', methods=['GET', 'POST'])
def operations():
    """Configuration page for warehouse operations"""
    if request.method == 'POST':
        layout = Layout.from_dict(session["layout_obj"])
        operations_json = request.form.get('operations_data')
        operations = json.loads(operations_json)  # Parse JSON string into dict

        # Validate operations
        for op in operations:
            # Check if source and destination entities exist
            source_exists = any(str(entity.get('id')) == op['from_entity'] for entity in layout.entities)
            dest_exists = any(str(entity.get('id')) == op['to_entity'] for entity in layout.entities)
            
            if not source_exists or not dest_exists:
                return jsonify({
                    "status": "error",
                    "message": f"Invalid entity IDs in operation: source={op['from_entity']}, destination={op['to_entity']}"
                }), 400

        # Add operations to layout
        print(operations)
        layout.add_operations(operations)
        session['layout_obj'] = layout.to_dict()

        return redirect(url_for('optimiser'))
    
    return render_template('operations.html')

@app.route('/optimiser', methods=['GET', 'POST'])
def optimiser():
    """Configuration page for entities like shelves and stations"""
    if request.method == 'POST':
        layout = Layout.from_dict(session["layout_obj"])

        algorithm = request.form.get('algorithm')
        function = request.form.get('function')
        simulation = request.form.get('simulation')
        # session['optimiser'] = op.Optimiser(layout, algorithm, function, simulation)
        # session['results'] = session['optimiser'].run_optimisation()

        opti = op.Optimiser(layout, algorithm, function, simulation)
        opti.run_optimisation()

        session['algorithm'] = algorithm
        session['function'] = function
        session['simulation'] = simulation

        session['layout_results'] = opti.export_layouts()
        print(session['layout_results'])
        return redirect(url_for('optimiser_results'))
    return render_template('optimiser.html')

@app.route('/optimiser-results', methods=['GET', 'POST'])
def optimiser_results():
    """Configuration page for entities like shelves and stations"""
    layout = session['layout_results'][0]
    draw_text_layout(layout)

    if request.method == 'POST': 
        return redirect(url_for('simulation'))
    return render_template('optimiser-results.html')

@app.route('/hyperparameters')
def hyperparameters():
    """Page for advanced configuration parameters"""
    return render_template('advanced.html')

@app.route('/simulation')
def simulation():
    if request.method == 'GET': 
        layout = Layout.from_dict(session["layout_obj"])
        algorithm = session['algorithm'] 
        function = session['function']
        simulation=session['simulation']

        opti = op.Optimiser(layout, algorithm, function, simulation)
        opti.import_layouts(session['layout_results'])
 
        opti.run_simulation()
    return render_template('simulation.html')

@app.route('/api/update_parameter', methods=['POST'])
def update_parameter():
    """API endpoint to update simulation parameters in real-time"""
    data = request.json
    parameter = data.get('parameter')
    value = data.get('value')
    sim_id = data.get('sim_id')
    
    # In a real implementation, you would update the running model
    # For now, just return success
    return jsonify({
        "status": "success",
        "message": f"Updated {parameter} to {value}"
    })

def draw_text_layout(layout):
    height = layout['length']
    width = layout['width']
    
    # Initialize grid with dots
    grid = [['.' for _ in range(width+1)] for _ in range(height+1)]

    # Place walls
    for x, y in layout['structure']['wall']:
        if 0 <= x < height and 0 <= y < width:
            grid[x][y] = '#'

    # Place entities
    for entity in layout['entities']:
        symbol = entity['type'][0].upper()
        for x, y in entity['positions']:
            if 0 <= x < height and 0 <= y < width:
                grid[x][y] = symbol

    # Print grid with column headers
    print('   ' + ' '.join(f'{i:>2}' for i in range(width)))
    for i, row in enumerate(grid):
        print(f'{i:>2} ' + ' '.join(row))


if __name__ == '__main__':
    app.run(debug=True)
