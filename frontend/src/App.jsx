import { useState } from 'react';
import Header from './components/Header';
import FileUpload from './components/FileUpload';
import StatsCards from './components/StatsCards';
import ForecastChart from './components/ForecastChart';
import DataTable from './components/DataTable';
import apiService from './services/api';
import { AlertCircle, CheckCircle } from 'lucide-react';
import './App.css';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [data, setData] = useState(null);

  const handleFileUpload = async (file, forecastHorizon) => {
    setIsLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await apiService.uploadAndForecast(file, forecastHorizon);
      
      if (response.success) {
        setData(response);
        setSuccess(true);
        
        setTimeout(() => setSuccess(false), 3000);
      } else {
        setError(response.error || 'Error desconocido');
      }
    } catch (err) {
      setError(err.message || 'Error al procesar el archivo');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <Header />
      
      <main className="main-content">
        <div className="container">
          <FileUpload onUpload={handleFileUpload} isLoading={isLoading} />

          {error && (
            <div className="alert alert-error">
              <AlertCircle size={20} />
              <span>{error}</span>
            </div>
          )}

          {success && (
            <div className="alert alert-success">
              <CheckCircle size={20} />
              <span>¡Pronóstico generado exitosamente!</span>
            </div>
          )}

          {data && (
            <>
              <StatsCards stats={data.stats} />
              <ForecastChart 
                historical={data.historical} 
                forecast={data.forecast} 
              />
              <DataTable 
                historical={data.historical} 
                forecast={data.forecast} 
              />
            </>
          )}

          {!data && !isLoading && (
            <div className="empty-state">
              <p>
                Sube un archivo CSV con los datos del refugio para generar el pronóstico
              </p>
            </div>
          )}
        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <p>
            Refuge Occupancy Forecasting © 2026 | Modelo SARIMAX con calendario chileno
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
