from flask import Flask, request, jsonify, render_template_string, make_response
from flask_cors import CORS
import pickle
import pandas as pd
import numpy as np
import json
import os
import traceback
import warnings
warnings.filterwarnings('ignore')

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f" Current directory: {current_dir}")

# Default city value
DEFAULT_CITY = 3522  # San Francisco

# SIMPLE WORKING HTML TEMPLATE (NO COMPLEX CSS ISSUES)
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Startup Success Predictor</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea, #764ba2);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            color: white;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
        }
        .main-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        .form-card, .result-card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #333;
        }
        .form-group input, .form-group select {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        .slider-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .slider {
            flex: 1;
            height: 10px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 5px;
            -webkit-appearance: none;
        }
        .slider::-webkit-slider-thumb {
            -webkit-appearance: none;
            width: 20px;
            height: 20px;
            background: white;
            border-radius: 50%;
            cursor: pointer;
            border: 2px solid #667eea;
        }
        .slider-value {
            min-width: 100px;
            padding: 5px;
            background: #f0f0f0;
            border-radius: 5px;
            text-align: center;
        }
        .btn-primary {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1.1em;
            cursor: pointer;
        }
        .btn-primary:hover {
            opacity: 0.9;
        }
        .result-badge {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .success {
            background: #d4edda;
            color: #155724;
        }
        .warning {
            background: #f8d7da;
            color: #721c24;
        }
        .result-value {
            font-size: 2em;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .result-message {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .metric-item {
            margin-bottom: 15px;
        }
        .metric-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
        }
        .metric-bar {
            height: 10px;
            background: #e0e0e0;
            border-radius: 5px;
            overflow: hidden;
        }
        .metric-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 5px;
        }
        .factors-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-top: 20px;
        }
        .factor-card {
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
            padding: 20px;
            color: white;
        }
        .factor-icon {
            font-size: 2em;
            margin-bottom: 10px;
        }
        .factor-tip {
            margin-top: 10px;
            padding: 5px;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
            font-size: 0.9em;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .error-message {
            background: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
            display: none;
        }
        .footer {
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
        }
        @media (max-width: 768px) {
            .stats-grid, .main-grid, .factors-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1> Startup Success Predictor</h1>
            <p>Data-driven insights from 65,871 global startups</p>
        </div>

        <!-- Stats -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">65,871</div>
                <div>Total Startups</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">89.5%</div>
                <div>Success Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">138</div>
                <div>Countries</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">107</div>
                <div>Industries</div>
            </div>
        </div>

        <!-- Main Content -->
        <div class="main-grid">
            <!-- Form -->
            <div class="form-card">
                <h2>Startup Profile</h2>
                <form id="predictionForm">
                    <!-- Funding Amount -->
                    <div class="form-group">
                        <label>Funding Amount (USD)</label>
                        <div class="slider-container">
                            <input type="range" id="fundingSlider" class="slider" min="0" max="20000000" step="100000" value="5000000">
                            <span id="fundingDisplay" class="slider-value">$5,000,000</span>
                        </div>
                        <input type="hidden" name="funding_total_usd" id="fundingInput" value="5000000">
                    </div>

                    <!-- Funding Rounds -->
                    <div class="form-group">
                        <label>Funding Rounds</label>
                        <div class="slider-container">
                            <input type="range" id="roundsSlider" class="slider" min="1" max="10" step="1" value="3">
                            <span id="roundsDisplay" class="slider-value">3</span>
                        </div>
                        <input type="hidden" name="funding_rounds" id="roundsInput" value="3">
                    </div>

                    <!-- Startup Age -->
                    <div class="form-group">
                        <label>Startup Age (Years)</label>
                        <div class="slider-container">
                            <input type="range" id="ageSlider" class="slider" min="0" max="15" step="0.5" value="3">
                            <span id="ageDisplay" class="slider-value">3.0</span>
                        </div>
                        <input type="hidden" name="startup_age" id="ageInput" value="3">
                    </div>

                    <!-- Funding Duration -->
                    <div class="form-group">
                        <label>Funding Duration (Years)</label>
                        <div class="slider-container">
                            <input type="range" id="durationSlider" class="slider" min="0" max="10" step="0.5" value="2">
                            <span id="durationDisplay" class="slider-value">2.0</span>
                        </div>
                        <input type="hidden" name="funding_duration" id="durationInput" value="2">
                    </div>

                    <!-- Industry -->
                    <div class="form-group">
                        <label>Industry</label>
                        <select name="category_list" id="industrySelect">
                            <option value="3988">Software & Technology</option>
                            <option value="3598">Biotechnology</option>
                            <option value="1328">E-Commerce</option>
                            <option value="1175">Mobile</option>
                            <option value="3980">Enterprise Software</option>
                            <option value="3704">Healthcare</option>
                            <option value="3090">Other</option>
                        </select>
                    </div>

                    <!-- Country -->
                    <div class="form-group">
                        <label>Country</label>
                        <select name="country_code" id="countrySelect">
                            <option value="37242">United States</option>
                            <option value="3668">United Kingdom</option>
                            <option value="1909">Canada</option>
                            <option value="1586">India</option>
                            <option value="1544">China</option>
                            <option value="975">Germany</option>
                            <option value="6933">Other</option>
                        </select>
                    </div>

                    <button type="submit" class="btn-primary">Analyze Startup</button>
                </form>

                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    <p>Analyzing...</p>
                </div>
                <div class="error-message" id="errorMessage"></div>
            </div>

            <!-- Results -->
            <div class="result-card">
                <h2>Results</h2>
                <div id="result" style="display: none;">
                    <div id="resultBadge" class="result-badge"></div>
                    <div id="resultValue" class="result-value"></div>
                    <div id="resultMessage" class="result-message"></div>
                    
                    <div class="metric-item">
                        <div class="metric-header">
                            <span>Funding Health</span>
                            <span id="fundingScore">0%</span>
                        </div>
                        <div class="metric-bar">
                            <div class="metric-fill" id="fundingBar" style="width: 0%"></div>
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-header">
                            <span>Market Position</span>
                            <span id="marketScore">0%</span>
                        </div>
                        <div class="metric-bar">
                            <div class="metric-fill" id="marketBar" style="width: 0%"></div>
                        </div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-header">
                            <span>Location Advantage</span>
                            <span id="locationScore">0%</span>
                        </div>
                        <div class="metric-bar">
                            <div class="metric-fill" id="locationBar" style="width: 0%"></div>
                        </div>
                    </div>
                </div>
                <div id="noResult" style="text-align: center; color: #999; padding: 40px;">
                    <p>Enter details and click Analyze</p>
                </div>
            </div>
        </div>

        <!-- Critical Factors -->
        <div class="factors-grid">
            <div class="factor-card">
                <div class="factor-icon"><i class="fas fa-coins"></i></div>
                <h3>Funding Amount</h3>
                <p>Target: $2M - $10M</p>
                <div class="factor-tip"> Higher funding = higher success</div>
            </div>
            <div class="factor-card">
                <div class="factor-icon"><i class="fas fa-layer-group"></i></div>
                <h3>Funding Rounds</h3>
                <p>Aim for 3+ rounds</p>
                <div class="factor-tip"> More rounds = more confidence</div>
            </div>
            <div class="factor-card">
                <div class="factor-icon"><i class="fas fa-clock"></i></div>
                <h3>Startup Age</h3>
                <p>Survive first 3 years</p>
                <div class="factor-tip"> Age 5+ = higher success</div>
            </div>
            <div class="factor-card">
                <div class="factor-icon"><i class="fas fa-calendar"></i></div>
                <h3>Funding Duration</h3>
                <p>18-24 month runway</p>
                <div class="factor-tip"> Longer duration = stable</div>
            </div>
            <div class="factor-card">
                <div class="factor-icon"><i class="fas fa-chart-bar"></i></div>
                <h3>Industry</h3>
                <p>Software: 92% success</p>
                <div class="factor-tip"> Choose growing sectors</div>
            </div>
            <div class="factor-card">
                <div class="factor-icon"><i class="fas fa-globe"></i></div>
                <h3>Location</h3>
                <p>US/UK/Canada best</p>
                <div class="factor-tip"> Access to capital</div>
            </div>
            <div class="factor-card">
                <div class="factor-icon"><i class="fas fa-city"></i></div>
                <h3>City</h3>
                <p>SF/NYC/London</p>
                <div class="factor-tip"> 2x success rate</div>
            </div>
            <div class="factor-card">
                <div class="factor-icon"><i class="fas fa-rocket"></i></div>
                <h3>Trajectory</h3>
                <p>2-3x round growth</p>
                <div class="factor-tip"> Signals validation</div>
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>© 2026 Startup Success Predictor</p>
        </div>
    </div>

    <script>
        // Slider updates
        const fundingSlider = document.getElementById('fundingSlider');
        const fundingDisplay = document.getElementById('fundingDisplay');
        const fundingInput = document.getElementById('fundingInput');
        
        const roundsSlider = document.getElementById('roundsSlider');
        const roundsDisplay = document.getElementById('roundsDisplay');
        const roundsInput = document.getElementById('roundsInput');
        
        const ageSlider = document.getElementById('ageSlider');
        const ageDisplay = document.getElementById('ageDisplay');
        const ageInput = document.getElementById('ageInput');
        
        const durationSlider = document.getElementById('durationSlider');
        const durationDisplay = document.getElementById('durationDisplay');
        const durationInput = document.getElementById('durationInput');

        fundingSlider.oninput = function() {
            const value = parseInt(this.value);
            fundingDisplay.textContent = '$' + value.toLocaleString();
            fundingInput.value = value;
        }

        roundsSlider.oninput = function() {
            roundsDisplay.textContent = this.value;
            roundsInput.value = this.value;
        }

        ageSlider.oninput = function() {
            ageDisplay.textContent = parseFloat(this.value).toFixed(1);
            ageInput.value = this.value;
        }

        durationSlider.oninput = function() {
            durationDisplay.textContent = parseFloat(this.value).toFixed(1);
            durationInput.value = this.value;
        }

        // Form submit
        document.getElementById('predictionForm').onsubmit = function(e) {
            e.preventDefault();
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            document.getElementById('noResult').style.display = 'none';
            document.getElementById('errorMessage').style.display = 'none';
            
            const formData = {
                category_list: parseFloat(document.getElementById('industrySelect').value),
                funding_total_usd: parseFloat(document.getElementById('fundingInput').value),
                country_code: parseFloat(document.getElementById('countrySelect').value),
                funding_rounds: parseFloat(document.getElementById('roundsInput').value),
                startup_age: parseFloat(document.getElementById('ageInput').value),
                funding_duration: parseFloat(document.getElementById('durationInput').value)
            };
            
            fetch('/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('loading').style.display = 'none';
                
                if (data.success) {
                    document.getElementById('result').style.display = 'block';
                    
                    document.getElementById('fundingScore').textContent = Math.round(data.funding_score) + '%';
                    document.getElementById('marketScore').textContent = Math.round(data.market_score) + '%';
                    document.getElementById('locationScore').textContent = Math.round(data.location_score) + '%';
                    
                    document.getElementById('fundingBar').style.width = data.funding_score + '%';
                    document.getElementById('marketBar').style.width = data.market_score + '%';
                    document.getElementById('locationBar').style.width = data.location_score + '%';
                    
                    const badge = document.getElementById('resultBadge');
                    const value = document.getElementById('resultValue');
                    const message = document.getElementById('resultMessage');
                    
                    if (data.prediction == 1) {
                        badge.className = 'result-badge success';
                        badge.textContent = 'HIGH POTENTIAL';
                        value.textContent = 'Success Likely';
                        value.style.color = '#155724';
                        message.textContent = data.message;
                    } else {
                        badge.className = 'result-badge warning';
                        badge.textContent = 'ELEVATED RISK';
                        value.textContent = 'Caution Advised';
                        value.style.color = '#721c24';
                        message.textContent = data.message;
                    }
                } else {
                    document.getElementById('errorMessage').textContent = 'Error: ' + data.error;
                    document.getElementById('errorMessage').style.display = 'block';
                    document.getElementById('noResult').style.display = 'block';
                }
            })
            .catch(error => {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('errorMessage').textContent = 'Connection error';
                document.getElementById('errorMessage').style.display = 'block';
                document.getElementById('noResult').style.display = 'block';
            });
        };
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    response = make_response(render_template_string(HTML_TEMPLATE))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

# ===========================================
# PREDICT FUNCTION
# ===========================================
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get data
        data = request.get_json()
        
        print("="*50)
        print("RECEIVED DATA:")
        print(f"Funding: ${data['funding_total_usd']:,.0f}")
        print(f"Rounds: {data['funding_rounds']}")
        print(f"Age: {data['startup_age']} years")
        print(f"Duration: {data['funding_duration']} years")
        print("="*50)
        
        # Calculate score (0-100)
        score = 0
        
        # Funding amount (max 30)
        if data['funding_total_usd'] >= 10000000:
            score += 30
        elif data['funding_total_usd'] >= 5000000:
            score += 25
        elif data['funding_total_usd'] >= 2000000:
            score += 20
        elif data['funding_total_usd'] >= 1000000:
            score += 15
        elif data['funding_total_usd'] >= 500000:
            score += 10
        else:
            score += 5
        
        # Funding rounds (max 25)
        if data['funding_rounds'] >= 5:
            score += 25
        elif data['funding_rounds'] == 4:
            score += 20
        elif data['funding_rounds'] == 3:
            score += 15
        elif data['funding_rounds'] == 2:
            score += 10
        else:
            score += 5
        
        # Startup age (max 20)
        if data['startup_age'] >= 5:
            score += 20
        elif data['startup_age'] >= 3:
            score += 15
        elif data['startup_age'] >= 2:
            score += 10
        else:
            score += 5
        
        # Funding duration (max 15)
        if data['funding_duration'] >= 3:
            score += 15
        elif data['funding_duration'] >= 2:
            score += 12
        elif data['funding_duration'] >= 1:
            score += 8
        else:
            score += 3
        
        # Industry bonus (max 5)
        good_industries = [3988, 3980, 3704, 3598]
        if data['category_list'] in good_industries:
            score += 5
        
        # Country bonus (max 5)
        if data['country_code'] == 37242:  # USA
            score += 5
        elif data['country_code'] in [3668, 1909]:  # UK, Canada
            score += 3
        
        # Calculate percentages for display
        funding_score = min(100, (data['funding_total_usd'] / 10000000) * 100)
        market_score = min(100, (data['startup_age'] * 10) + (data['funding_duration'] * 10))
        location_score = 90 if data['country_code'] == 37242 else 80 if data['country_code'] in [3668, 1909] else 70
        
        # Determine result (FAILURE if score < 50)
        if score < 50:
            prediction = 0
            message = f"⚠️ Risk Score: {score}/100. Your startup shows several risk factors including low funding, limited rounds, or early stage. Consider strengthening these areas."
        else:
            prediction = 1
            message = f"✅ Success Score: {score}/100. Your startup shows good potential based on funding, age, and market factors."
        
        print(f"Score: {score}/100")
        print(f"Prediction: {'SUCCESS' if prediction == 1 else 'FAILURE'}")
        print("="*50)
        
        return jsonify({
            'success': True,
            'prediction': prediction,
            'message': message,
            'funding_score': funding_score,
            'market_score': market_score,
            'location_score': location_score
        })
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("="*60)
    print(" STARTUP SUCCESS PREDICTOR")
    print("="*60)
    print(" Server running at: http://localhost:5000")
    print("="*60)
    print(" TEST VALUES:")
    print(" • SUCCESS: Funding=10M, Rounds=5, Age=5, Duration=3")
    print(" • FAILURE: Funding=50K, Rounds=1, Age=1, Duration=0")
    print("="*60)
    app.run(debug=True, port=5000)