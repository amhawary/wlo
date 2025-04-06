from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import uuid
import mesa
# from models.warehouse_model import WarehouseModel
# from models.portrayal import portrayal

app = Flask(__name__)
app.secret_key = 'warehouse_optimizer_secret_key'

# Store active simulations
simulations = {}

@app.route('/')
def index():
    """Landing page for the warehouse optimizer"""
    return render_template('index.html')

@app.route('/config', methods=['GET', 'POST'])
def config():
    """Configuration page for warehouse setup"""
    if request.method == 'POST':
        # Store configuration in session
        session['config'] = {
            'warehouse_type': request.form.get('warehouse_type'),
            'warehouse_size': request.form.get('warehouse_size'),
            'shapes': request.form.get('shapes'),
            'model': request.form.get('model')
        }
        return redirect(url_for('entities'))
    return render_template('config.html')

@app.route('/entities', methods=['GET', 'POST'])
def entities():
    """Configuration page for entities like shelves and stations"""
    if request.method == 'POST':
        # Store entity configuration in session
        session['entities'] = {
            'shelves': int(request.form.get('shelves', 4)),
            'stations': int(request.form.get('stations', 2)),
        }
        session['parameters'] = {
            'pace': int(request.form.get('pace', 50)),
            'num_boxes': int(request.form.get('num_boxes', 50)),
            'num_agents': int(request.form.get('num_agents', 5))
        }
        return redirect(url_for('simulation'))
    return render_template('entities.html')

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