from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import uuid
import mesa
# from ..layout_model import layout

app = Flask(__name__)
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
        # Store configuration in session
                
        ex_ent_placement = request.form.get('ex_ent_placement')
        wall_placement = request.form.get('wall_placement')

        session['config'] = {
            'warehouse_width': int(request.form.get('warehouse_width')),
            'warehouse_length': int(request.form.get('warehouse_length')),
            'aisle_width': int(request.form.get('aisle_width')),
            'ex_ent_placement': ex_ent_placement,
            'wall_placement': wall_placement,
            'model': request.form.get('model')
        }
        #session['layout'] = Layout()

        if wall_placement=='manual' or ex_ent_placement=='manual':
            return redirect(url_for('structure'))         
        else:
            return redirect(url_for('zones'))
        
    return render_template('config.html')

@app.route('/structure', methods=['GET', 'POST'])
def structure():
    """Configuration page for the structure"""
    if request.method == 'POST':
            layout_json = request.form.get('layout_data')
            layout = json.loads(layout_json)  # ← Parse JSON string into dic
  
            new_layout = {
                'wall':[],
                'loading':[],
                'ex':[],
                'ent':[],
                'ex_ent':[],
            }
            for coord in layout.keys():
                new_layout[layout[coord]].append(coord)

            session['layout'] = new_layout
            return redirect(url_for('zones'))
    return render_template('structure.html')

@app.route('/zones', methods=['GET', 'POST'])
def zones():
    """Configuration page for zones"""
    if request.method == 'POST':
        layout_json = request.form.get('layout_data')
        layout = json.loads(layout_json)  # ← Parse JSON string into dic

        new_layout = {
            'highTemp':[],
            'lowTemp':[],
            'highHumidity':[],
            'lowHumidity':[],
        }
        for coord in layout.keys():
            new_layout[layout[coord]].append(coord)

        session['layout'] = layout
        return redirect(url_for('utilities'))
    return render_template('zones.html')

@app.route('/utilities', methods=['GET', 'POST'])
def utilities():
    """Configuration page for entities like shelves and stations"""
    if request.method == 'POST':
        return redirect(url_for('entities'))
    return render_template('utilities.html')

@app.route('/entities', methods=['GET', 'POST'])
def entities():
    """Configuration page for entities like shelves and stations"""
    if request.method == 'POST':
        return redirect(url_for('place-entities'))
    return render_template('entities.html')

@app.route('/place-entities', methods=['GET', 'POST'])
def place_entities():
    """Configuration page for entities like shelves and stations"""
    if request.method == 'POST':
        return redirect(url_for('simulation'))
    return render_template('entities.html')

@app.route('/operations', methods=['GET', 'POST'])
def place_entities():
    """Configuration page for entities like shelves and stations"""
    if request.method == 'POST':
        return redirect(url_for('optimiser'))
    return render_template('operations.html')

@app.route('/optimiser', methods=['GET', 'POST'])
def place_entities():
    """Configuration page for entities like shelves and stations"""
    if request.method == 'POST':
        return redirect(url_for('simulation'))
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