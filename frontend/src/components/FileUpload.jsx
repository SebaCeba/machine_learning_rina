import { useState, useRef } from 'react';
import PropTypes from 'prop-types';
import { Upload, FileText, AlertCircle, Loader } from 'lucide-react';
import './FileUpload.css';

function FileUpload({ onUpload, isLoading }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [forecastHorizon, setForecastHorizon] = useState(60);
  const fileInputRef = useRef(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelection(e.dataTransfer.files[0]);

    }
  };

  const handleFileSelection = (file) => {
    if (file && file.name.endsWith('.csv')) {
      setSelectedFile(file);
    } else {
      alert('Por favor selecciona un archivo CSV válido');
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFileSelection(e.target.files[0]);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current.click();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (selectedFile && onUpload) {
      await onUpload(selectedFile, forecastHorizon);
    }
  };

  return (
    <div className="file-upload-container">
      <form onSubmit={handleSubmit} className="upload-form">
        <div
          className={`dropzone ${dragActive ? 'active' : ''} ${selectedFile ? 'has-file' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={handleButtonClick}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".csv"
            onChange={handleChange}
            style={{ display: 'none' }}
          />
          
          {selectedFile ? (
            <div className="file-selected">
              <FileText size={48} className="file-icon" />
              <p className="file-name">{selectedFile.name}</p>
              <p className="file-size">
                {(selectedFile.size / 1024).toFixed(2)} KB
              </p>
            </div>
          ) : (
            <div className="upload-prompt">
              <Upload size={48} className="upload-icon" />
              <p className="upload-text">
                Arrastra tu archivo CSV aquí o <span className="click-text">haz clic para seleccionar</span>
              </p>
              <p className="upload-hint">
                Formato esperado: check_in, check_out, noches
              </p>
            </div>
          )}
        </div>

        <div className="forecast-settings">
          <label htmlFor="forecast-horizon" className="setting-label">
            Días de pronóstico: <strong>{forecastHorizon}</strong>
          </label>
          <input
            id="forecast-horizon"
            type="range"
            min="30"
            max="90"
            value={forecastHorizon}
            onChange={(e) => setForecastHorizon(parseInt(e.target.value))}
            className="slider"
            disabled={isLoading}
          />
          <div className="range-labels">
            <span>30 días</span>
            <span>90 días</span>
          </div>
        </div>

        <button
          type="submit"
          className="submit-button"
          disabled={!selectedFile || isLoading}
        >
          {isLoading ? (
            <>
              <Loader className="spinner" size={20} />
              Procesando...
            </>
          ) : (
            <>
              <Upload size={20} />
              Subir y Generar Pronóstico
            </>
          )}
        </button>

        {selectedFile && !isLoading && (
          <div className="info-box">
            <AlertCircle size={16} />
            <span>El archivo será procesado con el modelo SARIMAX incluyendo feriados chilenos</span>
          </div>
        )}
      </form>
    </div>
  );
}

FileUpload.propTypes = {
  onUpload: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
};

export default FileUpload;
