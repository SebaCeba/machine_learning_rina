const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export const apiService = {
  /**
   * Upload CSV file and get forecast
   * @param {File} file - CSV file
   * @param {number} forecastHorizon - Number of days to forecast (30-90)
   * @returns {Promise} Response with historical data, forecast, and stats
   */
  async uploadAndForecast(file, forecastHorizon = 60) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('forecast_horizon', forecastHorizon.toString());

    const response = await fetch(`${API_URL}/api/forecast`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Error uploading file');
    }

    return await response.json();
  },

  /**
   * Health check endpoint
   * @returns {Promise} Server health status
   */
  async healthCheck() {
    const response = await fetch(`${API_URL}/api/health`);
    
    if (!response.ok) {
      throw new Error('Server is not responding');
    }

    return await response.json();
  },
};

export default apiService;
