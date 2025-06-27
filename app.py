from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import sys
import os
import json
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt

# Import the model
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from factor_fund_python_model_enhanced import FactorFundModelEnhanced

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/model/run', methods=['POST'])
def run_model():
    try:
        # Get parameters from request
        data = request.get_json()
        
        # Extract parameters with defaults
        fund_size = float(data.get('fund_size', 50.0))
        
        # Create model instance
        model = FactorFundModelEnhanced(fund_size=fund_size)
        
        # Allow customization of model parameters if provided
        if 'management_fee_rate' in data:
            model.management_fee_rate = float(data['management_fee_rate'])
        if 'carried_interest_rate' in data:
            model.carried_interest_rate = float(data['carried_interest_rate'])
        if 'fund_life' in data:
            model.fund_life = int(data['fund_life'])
        if 'investment_period' in data:
            model.investment_period = int(data['investment_period'])
        
        # Update investment parameters if provided
        if 'investment_params' in data:
            for category, params in data['investment_params'].items():
                if category in model.investment_params:
                    model.investment_params[category].update(params)
        
        # Recalculate derived values after parameter updates
        model.total_management_fees = model.fund_size * model.management_fee_rate * model.fund_life
        model.net_investable = model.fund_size - model.total_management_fees - model.operating_expenses
        model.total_deployable = model.net_investable + model.recycling_amount
        
        # Calculate results
        portfolio_returns = model.calculate_portfolio_returns()
        lp_returns = model.calculate_lp_returns(portfolio_returns)
        cash_flows = model.calculate_cash_flows()
        sensitivity = model.sensitivity_analysis(portfolio_returns)
        
        # Generate visualizations
        fig = model.create_visualizations()
        
        # Convert figure to base64 string
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        # Prepare response data
        response_data = {
            'fund_overview': {
                'fund_size': model.fund_size,
                'management_fees': model.total_management_fees,
                'operating_expenses': model.operating_expenses,
                'net_investable': model.net_investable,
                'recycling_amount': model.recycling_amount,
                'total_deployable': model.total_deployable
            },
            'portfolio_returns': portfolio_returns.to_dict('records'),
            'lp_returns': lp_returns,
            'cash_flows': cash_flows.to_dict('records'),
            'sensitivity_analysis': sensitivity.to_dict('records'),
            'visualization': image_base64,
            'model_parameters': {
                'management_fee_rate': model.management_fee_rate,
                'carried_interest_rate': model.carried_interest_rate,
                'fund_life': model.fund_life,
                'investment_period': model.investment_period
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/model/parameters', methods=['GET'])
def get_default_parameters():
    """Get default model parameters"""
    model = FactorFundModelEnhanced()
    
    return jsonify({
        'fund_size': model.fund_size,
        'management_fee_rate': model.management_fee_rate,
        'carried_interest_rate': model.carried_interest_rate,
        'fund_life': model.fund_life,
        'investment_period': model.investment_period,
        'investment_params': model.investment_params,
        'power_law_distributions': {
            'seed': model.power_law_seed,
            'series_a': model.power_law_series_a
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)