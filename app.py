from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import uuid
import mesa
from wlo.models import *
import optimiser

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
            'ex_ent_placement': ex_ent_placement,
            'wall_placement': wall_placement,
            'model': request.form.get('model')
        }
        
        session['layout_obj'] = Layout(warehouse_width, warehouse_length).to_dict()
        session['initial_layout'] = session['layout_obj']['structure']
        if wall_placement=='manual' or ex_ent_placement=='manual':
            return redirect(url_for('structure'))         
        else:
            return redirect(url_for('zones'))
        
    return render_template('config.html')

@app.route('/structure', methods=['GET', 'POST'])
def structure():
    """Configuration page for the structure"""
    if request.method == 'POST':
            layout = Layout.from_dict(session["layout_obj"])
            layout_json = request.form.get('layout_data')
            struct = json.loads(layout_json)  # ← Parse JSON string into dic
            
            layout.addStructure(struct)

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
        
        layout.addZones(zones)

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
        
        layout.addUtilities(utilities)

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

        layout.addEntities(entities)
        session['layout_obj'] = layout.to_dict()

        manual_placement = layout.manualPlacedEntities

        return redirect(url_for('optimiser'))
        if len(manual_placement) > 0:
            session['placing_entities'] = manual_placement
            return redirect(url_for('place_entities'))
        else:
            return redirect(url_for('operations'))
   
    return render_template('entities.html')

@app.route('/place-entities', methods=['GET', 'POST'])
def place_entities():
    """Configuration page for entities like shelves and stations"""
    if request.method == 'POST':
        return redirect(url_for('operations'))
    return render_template('place-entities.html')

@app.route('/operations', methods=['GET', 'POST'])
def operations():
    """Configuration page for entities like shelves and stations"""
    if request.method == 'POST':
        return redirect(url_for('optimiser'))
    return render_template('operations.html')

@app.route('/optimiser', methods=['GET', 'POST'])
def optimiser():
    """Configuration page for entities like shelves and stations"""
    if request.method == 'POST':
        optimiser.Optimiser()
    return render_template('optimiser.html')

@app.route('/hyperparameters')
def hyperparameters():
    """Page for advanced configuration parameters"""
    return render_template('advanced.html')

@app.route('/simulation')
def simulation():
    """Page displaying the Mesa visualization"""
    if 'config' not in session or 'entities' not in session:
        return redirect(url_for('index'))
    
    # Create unique ID for this simulation
    sim_id = str(uuid.uuid4())
    
    # Create model with configuration from session
    model_params = {
        **session.get('config', {}),
        **session.get('entities', {}),
        **session.get('parameters', {})
    }
    
    # Store model_params for later use in the Mesa server
    session['model_params'] = model_params
    
    return render_template('simulation.html', sim_id=sim_id)

@app.route('/api/start_simulation', methods=['POST'])
def start_simulation():
    """API endpoint to start a new simulation"""
    model_params = session.get('model_params', {})
    
    # Create visualization elements
    grid_size = int(model_params.get('warehouse_size', 20))
    grid = mesa.visualization.CanvasGrid(portrayal, 20, 20, 400, 400)

    # Add charts
    # efficiency_chart = ChartModule([
    #     {"Label": "Efficiency", "Color": "Black"}
    # ])
    
    # Create and store the server
    server = mesa.visualization.ModularServer(
        WarehouseModel,
        [grid],
        "Warehouse Layout Optimizer",
        model_params
    )
    
    # Generate a port number (this would need proper handling in production)
    port = 8521  # Mesa's default port
    
    # Start the server in a separate thread
    server.launch(port=port)
    
    return jsonify({
        "status": "success",
        "port": port,
        "message": "Simulation started successfully"
    })



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

if __name__ == '__main__':
    app.run(debug=True)