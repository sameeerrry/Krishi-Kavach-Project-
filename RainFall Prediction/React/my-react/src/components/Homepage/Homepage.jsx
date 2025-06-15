import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import Papa from 'papaparse';
import './Homepage.css';

const datasets = [
  { value: 'rainfall', label: 'Rainfall Data in India' },
  { value: 'drought', label: 'Drought Data in India' },
];

const ShowData = () => {
  const [data, setData] = useState([]);
  const [dataset, setDataset] = useState('rainfall');
  const [rangeStart, setRangeStart] = useState('2008');
  const [selectedState, setSelectedState] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [accuracy, setAccuracy] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      let url;
      let dataMapper;

      if (dataset === 'drought') {
        url = '/assets/India_Droughts_2014-2023.csv'; 
        dataMapper = (row) => ({
          year: parseInt(row['Year']),
          value: parseInt(row['Economic']),
          subdivision: row['Region'],
        });
      } else if (dataset === 'rainfall') {
        url = '/assets/Sub_Division_IMD_2017.csv'; 
        dataMapper = (row) => ({
          year: parseInt(row['YEAR']),
          value: parseFloat(row['JJAS']),
          subdivision: row['SUBDIVISION'],
        });
      }

      if (url) {
        try {
          const response = await fetch(url);
          if (!response.ok) throw new Error('Failed to fetch data');
          const csvText = await response.text();
          Papa.parse(csvText, {
            header: true,
            complete: (results) => {
              let rawData = results.data.map(dataMapper);

              rawData = rawData.filter((item) => !isNaN(item.value)); 
              rawData = rawData.filter((item) => item.year && item.subdivision); 
              rawData = rawData.reduce((acc, current) => {
                const existing = acc.find((item) => item.year === current.year && item.subdivision === current.subdivision);
                return existing ? acc : [...acc, current];
              }, []); 

              setData(rawData);
            },
          });
        } catch (error) {
          console.error('Error fetching data:', error);
        }
      }
    };

    fetchData();
  }, [dataset]);

  const handlePredict = async () => {
    if (selectedState) {
      setLoading(true); 
      try {
        const response = await fetch('http://localhost:5000/predict', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            state: selectedState,
            season: dataset === 'rainfall' ? 'JJAS' : 'Economic',
          }),
        });
  
        const result = await response.json();
        setPrediction(result.forecast); 
        setAccuracy(result.accuracy);
      } catch (error) {
        console.error('Error fetching prediction:', error);
      } finally {
        setLoading(false); 
      }
    }
  };
  
  const rangeEnd = (parseInt(rangeStart) + 9).toString();
  const filteredData = data.filter((item) => 
    item.year >= rangeStart && item.year <= rangeEnd && (selectedState ? item.subdivision === selectedState : true)
  );

  const chartData = [
    ...filteredData,
    ...(prediction || []).map(([year, value]) => ({ year, value }))
  ];

  return (
    <div className="show-data-container">
      <h2 className="show-data-header">
        {datasets.find(ds => ds.value === dataset)?.label}
      </h2>

      <div className="show-data-controls">
        <div>
          <select onChange={(e) => setDataset(e.target.value)} value={dataset}>
            {datasets.map(ds => (
              <option key={ds.value} value={ds.value}>
                {ds.label}
              </option>
            ))}
          </select>
          
          <select onChange={(e) => setRangeStart(e.target.value)} value={rangeStart}>
            {data.length > 0 && [...new Set(data.map(item => item.year))].sort((a, b) => a - b).map(year => (
              <option key={year} value={year}>
                {year} - {parseInt(year) + 9}
              </option>
            ))}
          </select>
          
          <select onChange={(e) => setSelectedState(e.target.value)} value={selectedState}>
            <option value="">All States</option>
            {[...new Set(data.map(item => item.subdivision))].map(state => (
              <option key={state} value={state}>
                {state}
              </option>
            ))}
          </select>
        </div>
      </div>
      
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="year" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="value" stroke="#8884d8" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {selectedState && (
        <div className="details-container">
          <div className="details-content">
            <h3>Details for {selectedState} from {rangeStart} to {rangeEnd}</h3>
            <ul>
              {filteredData.map((item, index) => (
                <li key={index}>
                  <span>Year: {item.year}</span>
                  <span>Average Rainfall: {item.value.toFixed(2)} mm</span>
                </li>
              ))}
            </ul>
            <button onClick={handlePredict} className='hbtn'>
              {loading ? 'Loading...' : 'Predict Avg Rainfall for 2025'}
            </button>
            {prediction && !loading && (
              <>
              <div className="prediction-container">
                <h4>Predicted Average Rainfall for {selectedState} in 2025: {prediction[prediction.length - 1][1].toFixed(2)} mm</h4>
              </div>
              <div className="prediction-container">
               {accuracy !== null && (
                  <h4>
                    Prediction Accuracy: {accuracy ? accuracy.toFixed(2) : 'N/A'}%
                  </h4>
                )}
              </div>
            </>
            )}
          </div>
          <div className="details-image">
            <img src={`../../../public/images/${selectedState}.jpg`} alt={`${selectedState} illustration`} />
          </div>
        </div>
      )}
    </div>
  );
};

export default ShowData;