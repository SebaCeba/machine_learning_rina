import { useState } from 'react';
import PropTypes from 'prop-types';
import { Download, ChevronUp, ChevronDown } from 'lucide-react';
import './DataTable.css';

function DataTable({ historical, forecast }) {
  const [activeTab, setActiveTab] = useState('forecast');
  const [sortColumn, setSortColumn] = useState(null);
  const [sortDirection, setSortDirection] = useState('asc');
  const [filterType, setFilterType] = useState('all');

  if (!historical || !forecast) return null;

  const handleSort = (column) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  const exportToCSV = (data, filename) => {
    const headers = Object.keys(data[0]);
    const csv = [
      headers.join(','),
      ...data.map(row => headers.map(header => row[header]).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getSortedAndFilteredData = (data, isHistorical) => {
    let filtered = data;

    // Aplicar filtro
    if (filterType !== 'all') {
      filtered = data.filter(item => item.day_type === filterType);
    }

    // Aplicar ordenamiento
    if (sortColumn) {
      filtered = [...filtered].sort((a, b) => {
        const aVal = a[sortColumn];
        const bVal = b[sortColumn];
        
        if (sortDirection === 'asc') {
          return aVal > bVal ? 1 : -1;
        } else {
          return aVal < bVal ? 1 : -1;
        }
      });
    }

    return filtered;
  };

  const historicalData = getSortedAndFilteredData(historical, true);
  const forecastData = getSortedAndFilteredData(forecast, false);

  const renderSortIcon = (column) => {
    if (sortColumn !== column) return null;
    return sortDirection === 'asc' ? <ChevronUp size={16} /> : <ChevronDown size={16} />;
  };

  return (
    <div className="data-table-container">
      <div className="table-header">
        <div className="tabs">
          <button
            className={`tab ${activeTab === 'historical' ? 'active' : ''}`}
            onClick={() => setActiveTab('historical')}
          >
            Histórico ({historical.length})
          </button>
          <button
            className={`tab ${activeTab === 'forecast' ? 'active' : ''}`}
            onClick={() => setActiveTab('forecast')}
          >
            Pronóstico ({forecast.length})
          </button>
        </div>

        <div className="table-controls">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="filter-select"
          >
            <option value="all">Todos los días</option>
            <option value="weekday">Días de semana</option>
            <option value="weekend">Fines de semana</option>
            <option value="holiday">Feriados</option>
            <option value="sandwich">Días sándwich</option>
          </select>

          <button
            className="export-button"
            onClick={() => exportToCSV(
              activeTab === 'historical' ? historicalData : forecastData,
              `${activeTab}-data.csv`
            )}
          >
            <Download size={18} />
            Exportar CSV
          </button>
        </div>
      </div>

      <div className="table-wrapper">
        <table className="data-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('ds')} className="sortable">
                Fecha {renderSortIcon('ds')}
              </th>
              <th onClick={() => handleSort(activeTab === 'historical' ? 'y' : 'yhat')} className="sortable">
                {activeTab === 'historical' ? 'Ocupación' : 'Probabilidad'} {renderSortIcon(activeTab === 'historical' ? 'y' : 'yhat')}
              </th>
              {activeTab === 'forecast' && (
                <>
                  <th>Límite Inferior</th>
                  <th>Límite Superior</th>
                </>
              )}
              <th>Tipo de Día</th>
              <th className="center-align">Feriado</th>
              <th className="center-align">Sándwich</th>
              <th className="center-align">Fin de Semana</th>
            </tr>
          </thead>
          <tbody>
            {(activeTab === 'historical' ? historicalData : forecastData).map((row, idx) => (
              <tr key={idx}>
                <td>{row.ds}</td>
                <td>
                  {activeTab === 'historical' ? (
                    <span className={`occupancy-badge ${row.y === 1 ? 'occupied' : 'free'}`}>
                      {row.y === 1 ? 'Ocupado' : 'Libre'}
                    </span>
                  ) : (
                    <span className="forecast-value">{(row.yhat * 100).toFixed(1)}%</span>
                  )}
                </td>
                {activeTab === 'forecast' && (
                  <>
                    <td className="confidence-bound">{(row.yhat_lower * 100).toFixed(1)}%</td>
                    <td className="confidence-bound">{(row.yhat_upper * 100).toFixed(1)}%</td>
                  </>
                )}
                <td>
                  <span className={`day-type-badge ${row.day_type || 'weekday'}`}>
                    {row.day_type || 'weekday'}
                  </span>
                </td>
                <td className="center-align">{row.is_holiday === 1 ? '✅' : '-'}</td>
                <td className="center-align">{row.is_sandwich === 1 ? '✅' : '-'}</td>
                <td className="center-align">{row.is_weekend === 1 ? '✅' : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="table-footer">
        Mostrando {(activeTab === 'historical' ? historicalData : forecastData).length} filas
      </div>
    </div>
  );
}

DataTable.propTypes = {
  historical: PropTypes.arrayOf(PropTypes.object),
  forecast: PropTypes.arrayOf(PropTypes.object),
};

export default DataTable;
