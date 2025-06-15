import { useState } from 'react';
import axios from 'axios';

export default function Home() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [prediction, setPrediction] = useState("");
  const [searchResult, setSearchResult] = useState("");
  const [translated, setTranslated] = useState("");
  const [loading, setLoading] = useState(false);

  const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || '';

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
  };

  const handleUpload = async () => {
    if (!file) {
      alert("Please select an image first.");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(`${BACKEND_URL}/predict/`, formData);
      const predictedDisease = res.data.predicted_disease;
      setPrediction(predictedDisease);

      const search = await axios.get(`${BACKEND_URL}/search/`, {
        params: { query: `${predictedDisease} disease remedy and information` },
      });
      const item = search.data.items[0];
      setSearchResult(`${item.title}: ${item.snippet}`);

      const translate = await axios.get(`${BACKEND_URL}/translate/`, {
        params: { text: item.snippet },
      });
      setTranslated(translate.data.translated);

    } catch (err) {
      console.error(err);
      alert("Something went wrong!");
    }
    setLoading(false);
  };

  return (
    <div style={{ textAlign: 'center', padding: '30px', background: '#f0f4f7', minHeight: '100vh', fontFamily: 'Segoe UI, sans-serif' }}>
      <h1 style={{ fontSize: '3rem', marginBottom: '20px', color: '#1a4d2e' }}>🌱 Krishi Kavach</h1>

      <img 
        src="https://cdn-icons-png.flaticon.com/512/2909/2909766.png" 
        alt="Agriculture icon"
        style={{ width: '100px', marginBottom: '10px' }} 
      />

      <p style={{ fontSize: '1.2rem', color: '#444', marginBottom: '30px' }}>
        Empowering farmers with plant disease diagnosis and remedies 💡🌾
      </p>

      <img 
        src="https://cdn.pixabay.com/photo/2016/07/02/20/42/wheat-1495735_1280.jpg" 
        alt="Agriculture banner"
        style={{ width: '90%', borderRadius: '15px', marginBottom: '30px', boxShadow: '0 6px 15px rgba(0,0,0,0.1)' }} 
      />

      <input type="file" onChange={handleFileChange} accept="image/*" style={{ marginBottom: '20px' }} />
      <br />

      {preview && (
        <div style={{ marginBottom: '30px' }}>
          <h3>🖼 Uploaded Image Preview:</h3>
          <img src={preview} alt="Preview" style={{ width: '300px', borderRadius: '10px', boxShadow: '0 4px 10px rgba(0,0,0,0.1)' }} />
        </div>
      )}

      <button 
        onClick={handleUpload} 
        style={{ 
          padding: '15px 35px', 
          backgroundColor: '#1a4d2e', 
          color: '#fff', 
          fontSize: '1.1rem', 
          border: 'none', 
          borderRadius: '8px', 
          cursor: 'pointer',
          transition: 'all 0.3s ease'
        }}
        onMouseOver={(e) => e.target.style.backgroundColor = '#145237'}
        onMouseOut={(e) => e.target.style.backgroundColor = '#1a4d2e'}
      >
        🔍 Predict Disease
      </button>

      {loading && <p style={{ marginTop: '20px', fontSize: '1.1rem' }}>🔄 Analyzing image... Please wait</p>}

      {prediction && (
        <div style={{ backgroundColor: '#fff', borderRadius: '15px', padding: '25px', marginTop: '30px', boxShadow: '0 8px 18px rgba(0,0,0,0.1)', width: '85%', margin: '30px auto' }}>
          <h2 style={{ color: '#1a4d2e' }}>🧪 Prediction Result</h2>
          <h3 style={{ color: prediction.includes('healthy') ? '#28a745' : '#dc3545' }}>
            {prediction.includes('healthy') ? '✅ Healthy Plant' : `❌ ${prediction}`}
          </h3>
          <p><strong>🌐 Google Search:</strong> {searchResult}</p>
          <p><strong>🌏 Hindi Translation:</strong> {translated}</p>
        </div>
      )}

      <footer style={{ marginTop: '50px', fontSize: '0.9rem', color: '#888' }}>
        Made with ❤️ for Indian farmers | © 2025 Krishi Kavach
      </footer>
    </div>
  );
}
