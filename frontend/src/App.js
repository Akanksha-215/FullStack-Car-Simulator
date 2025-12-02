import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useDropzone } from 'react-dropzone';
import { FiUpload, FiImage, FiVideo, FiCheck, FiLoader } from 'react-icons/fi';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedParameters, setSelectedParameters] = useState([]);
  const [parameters, setParameters] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [backendConnected, setBackendConnected] = useState(false);

  // Team information
  const teamMembers = [
    "B.Yogeshwar",
    "D.Akanksha", 
    "M.Ashok",
    "K.Manish",
  ];
  const guideName = "Dr. Kiran Mannem";

  useEffect(() => {
    // Fetch available parameters from backend
    fetchParameters();
  }, []);

  const fetchParameters = async () => {
    try {
      const response = await axios.get('http://localhost:5000/api/parameters');
      setParameters(response.data);
      setBackendConnected(true);
    } catch (error) {
      console.error('Error fetching parameters:', error);
      setBackendConnected(false);
      // Fallback parameters if backend is not available
      setParameters([
        { id: 'lane_detection', name: 'Lane Detection' },
        { id: 'vehicle_detection', name: 'Vehicle Detection' },
        { id: 'traffic_sign_recognition', name: 'Traffic Sign Recognition' },
        { id: 'object_tracking', name: 'Object Tracking' },
        { id: 'distance_estimation', name: 'Distance Estimation' }
      ]);
    }
  };

  const onDrop = (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (file) {
      setSelectedFile(file);
      setError(null);
      setSuccess(null);
      setResult(null);
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif'],
      'video/*': ['.mp4', '.avi', '.mov', '.mkv']
    },
    multiple: false
  });

  const handleParameterToggle = (parameterId) => {
    setSelectedParameters(prev => {
      if (prev.includes(parameterId)) {
        return prev.filter(id => id !== parameterId);
      } else {
        return [...prev, parameterId];
      }
    });
  };

  const handleGenerate = async () => {
    if (!selectedFile || selectedParameters.length === 0) {
      setError('Please select a file and at least one parameter');
      return;
    }

    if (!backendConnected) {
      setError('Backend server is not connected. Please start the backend server first.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setSuccess(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      selectedParameters.forEach(param => {
        formData.append('parameters[]', param);
      });

      const response = await axios.post('http://localhost:5000/api/forward_port', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        setResult(response.data);
        setSuccess('Processing completed successfully!');
      } else {
        setError('Processing failed. Please try again.');
      }
    } catch (error) {
      console.error('Error processing file:', error);
      setError(error.response?.data?.error || 'An error occurred during processing');
    } finally {
      setIsLoading(false);
    }
  };

  const canGenerate = selectedFile && selectedParameters.length > 0 && !isLoading;
  const canGenerateWithBackend = canGenerate && backendConnected;

  return (
    <div className="App">
      {/* Navigation */}
      <nav className="navbar">
        <div className="container">
          <div className="navbar-content">
            <div className="project-title">
              Autonomous Vehicle Perception Simulation
            </div>
            <div className="team-info">
              <div><strong>Team Members:</strong> {teamMembers.join(', ')}</div>
              <div><strong>Guide:</strong> {guideName}</div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="main-content">
        <div className="container">
          {/* File Upload Section */}
          <section className="upload-section">
            <h2 className="section-title">Upload File</h2>
            <div
              {...getRootProps()}
              className={`dropzone ${isDragActive ? 'drag-active' : ''}`}
            >
              <input {...getInputProps()} />
              <div className="dropzone-text">
                {isDragActive ? (
                  <span>Drop the file here...</span>
                ) : (
                  <span>Drag & drop a file here, or click to select</span>
                )}
              </div>
              <div className="dropzone-subtext">
                Supports: Images (JPG, PNG, GIF) and Videos (MP4, AVI, MOV, MKV)
              </div>
            </div>

            {/* File Preview */}
            {selectedFile && (
              <div className="file-preview">
                {selectedFile.type.startsWith('image/') ? (
                  <img
                    src={URL.createObjectURL(selectedFile)}
                    alt="Preview"
                    style={{ maxWidth: '100%', maxHeight: '300px' }}
                  />
                ) : (
                  <video
                    src={URL.createObjectURL(selectedFile)}
                    controls
                    style={{ maxWidth: '100%', maxHeight: '300px' }}
                  />
                )}
                <p style={{ color: 'white', marginTop: '0.5rem' }}>
                  Selected: {selectedFile.name}
                </p>
              </div>
            )}
          </section>

          {/* Parameters Selection Section */}
          <section className="parameters-section">
            <h2 className="section-title">Select Processing Parameters</h2>
            
            {/* Backend Connection Status */}
            <div style={{ 
              textAlign: 'center', 
              marginBottom: '1rem',
              padding: '0.5rem',
              borderRadius: '8px',
              backgroundColor: backendConnected ? 'rgba(76, 175, 80, 0.2)' : 'rgba(255, 193, 7, 0.2)',
              border: backendConnected ? '1px solid rgba(76, 175, 80, 0.3)' : '1px solid rgba(255, 193, 7, 0.3)',
              color: backendConnected ? '#e8f5e8' : '#fff3cd'
            }}>
              <strong>
                {backendConnected ? '✅ Backend Connected' : '⚠️ Backend Not Connected - Using Demo Mode'}
              </strong>
              {!backendConnected && (
                <div style={{ fontSize: '0.9rem', marginTop: '0.5rem' }}>
                  Start the backend server to enable full functionality
                </div>
              )}
            </div>
            
            <div className="parameters-grid">
              {parameters.map((param) => (
                <div
                  key={param.id}
                  className={`parameter-item ${selectedParameters.includes(param.id) ? 'selected' : ''}`}
                  onClick={() => handleParameterToggle(param.id)}
                >
                  <input
                    type="checkbox"
                    className="parameter-checkbox"
                    checked={selectedParameters.includes(param.id)}
                    onChange={() => handleParameterToggle(param.id)}
                  />
                  <label className="parameter-label">
                    {param.name}
                  </label>
                </div>
              ))}
            </div>
          </section>

          {/* Generate Button */}
          <button
            className="generate-button"
            onClick={handleGenerate}
            disabled={!canGenerate}
            style={{
              opacity: canGenerateWithBackend ? 1 : 0.6,
              background: canGenerateWithBackend ? 'linear-gradient(45deg, #4CAF50, #45a049)' : 'linear-gradient(45deg, #ff9800, #f57c00)'
            }}
          >
            {isLoading ? (
              <>
                <span className="loading-spinner"></span>
                Processing...
              </>
            ) : (
              <>
                <FiCheck style={{ marginRight: '0.5rem' }} />
                {backendConnected ? 'Generate' : 'Generate (Demo Mode)'}
              </>
            )}
          </button>

          {/* Error Message */}
          {error && (
            <div className="error-message">
              <strong>Error:</strong> {error}
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="success-message">
              <strong>Success:</strong> {success}
            </div>
          )}

          {/* Results Section */}
          {result && (
            <section className="results-section">
              <h2 className="section-title">Processing Results</h2>
              
              {/* Main Combined Result */}
              <div className="main-result">
                <h3 className="result-subtitle">Combined Result (All Parameters)</h3>
                {result.type === 'image' ? (
                  <img
                    src={`data:image/jpeg;base64,${result.data}`}
                    alt="Combined processed result"
                    className="main-result-image"
                  />
                ) : (
                  <video
                    src={`data:video/mp4;base64,${result.data}`}
                    controls
                    className="main-result-video"
                  />
                )}
                <p className="result-description">
                  Processed with: {selectedParameters.map(id => 
                    parameters.find(p => p.id === id)?.name
                  ).join(', ')}
                </p>
              </div>

              {/* Individual Parameter Results */}
              {result.individual_results && result.type === 'image' && (
                <div className="individual-results">
                  <h3 className="result-subtitle">Individual Parameter Results</h3>
                  <div className="parameter-results-grid">
                    {selectedParameters.map(paramId => {
                      const param = parameters.find(p => p.id === paramId);
                      const paramImage = result.individual_results[paramId];
                      return (
                        <div key={paramId} className="parameter-result-item">
                          <h4 className="parameter-result-title">{param?.name}</h4>
                          <img
                            src={`data:image/jpeg;base64,${paramImage}`}
                            alt={`${param?.name} result`}
                            className="parameter-result-image"
                          />
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}
            </section>
          )}
        </div>
      </main>
    </div>
  );
}

export default App; 