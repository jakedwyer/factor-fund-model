# Factor Fund II Model

An interactive financial model for venture fund analysis with power law distributions and revenue share investments.

## Overview

This web application provides a comprehensive model for analyzing a $50M venture fund with:
- Multiple investment strategies (Seed, Shared SAFE, Series A, Incubation)
- Power law return distributions
- Revenue share and equity components
- Real-time visualization and sensitivity analysis

## Features

- **Interactive Dashboard**: Adjust fund parameters and see instant results
- **Portfolio Allocation**: Visual breakdown of investment strategies
- **Return Projections**: MOIC and IRR calculations for LPs
- **Cash Flow Analysis**: Year-by-year distribution projections
- **Sensitivity Analysis**: Downside, base, and upside scenarios
- **Export Capabilities**: Download results as Excel files

## Technology Stack

- **Backend**: Python Flask
- **Financial Modeling**: NumPy, Pandas, numpy-financial
- **Visualization**: Matplotlib, Seaborn
- **Frontend**: HTML5, JavaScript, Chart.js
- **Deployment**: Docker, DigitalOcean App Platform

## Local Development

1. Clone the repository:
```bash
git clone https://github.com/jakedwyer/factor-fund-model.git
cd factor-fund-model
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python app.py
```

5. Open your browser to `http://localhost:5000`

## Docker Deployment

Build and run with Docker:
```bash
docker build -t factor-fund-model .
docker run -p 8080:8080 factor-fund-model
```

## API Endpoints

- `GET /` - Main dashboard interface
- `GET /api/model/parameters` - Get default model parameters
- `POST /api/model/run` - Run model with custom parameters

### Example API Request:
```json
{
  "fund_size": 50.0,
  "management_fee_rate": 0.02,
  "carried_interest_rate": 0.20,
  "fund_life": 10
}
```

## Model Parameters

### Fund Structure
- **Fund Size**: $50M default (adjustable)
- **Management Fee**: 2% annual
- **Carried Interest**: 20% of profits
- **Fund Life**: 10 years

### Investment Strategies
1. **Seed Investments**: 10 companies at $1.5M average
2. **Shared SAFE**: 6 companies with revenue share + equity
3. **Series A**: 6 companies at $2M average
4. **Incubation**: Platform companies
5. **Recycled Capital**: Follow-on investments

## License

MIT License - See LICENSE file for details

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Contact

For questions or support, please open an issue on GitHub.