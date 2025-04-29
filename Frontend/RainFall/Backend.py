from flask import Flask, request, jsonify
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.metrics import mean_absolute_error
from flask_cors import CORS

app = Flask(__name__)
CORS(app) 

df = pd.read_csv('assets/Sub_Division_IMD_2017.csv')
df['YEAR'] = pd.to_datetime(df['YEAR'], format='%Y')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        subdivision = data.get('state')
        season = data.get('season')

        state_data = df[df['SUBDIVISION'] == subdivision].set_index('YEAR')

        state_data[season] = state_data[season].ffill()

        if len(state_data[season].dropna()) < 10:
            return jsonify({'error': 'Insufficient data for the selected subdivision and season.'}), 400

        try:
            model = SARIMAX(state_data[season], order=(2, 1, 2), seasonal_order=(1, 1, 1, 8), freq='YS')
            model_fit = model.fit(disp=False)

            forecast_steps = 19 
            forecast = model_fit.get_forecast(steps=forecast_steps)
            forecast_values = forecast.predicted_mean

            y_true = state_data[season].dropna().iloc[-1:] 
            y_pred = forecast_values[:1]
            mae = mean_absolute_error(y_true, y_pred)
            percentage_mae = (mae / y_true.mean()) * 100

            forecast_years = pd.date_range(start='2010', periods=forecast_steps, freq='YS').year
            forecast_data = list(zip(forecast_years, forecast_values))

            response = {
                'forecast': forecast_data,  
                'accuracy': 100 - percentage_mae  
            }

            return jsonify(response), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500

    except KeyError:
        return jsonify({'error': 'Invalid input data. Please provide state and season.'}), 400

if __name__ == '__main__':
    app.run(debug=True)
