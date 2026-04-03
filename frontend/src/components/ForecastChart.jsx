import PropTypes from 'prop-types';
import {
  LineChart,
  Line,
  Area,
  ComposedChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceDot
} from 'recharts';
import './ForecastChart.css';

function ForecastChart({ historical, forecast }) {
  if (!historical ||!forecast) return null;

  // Combinar datos históricos y forecast
  const historicalData = historical.map(item => ({
    date: item.ds,
    occupancy: item.y * 100,
    type: 'historical',
    is_holiday: item.is_holiday,
    is_weekend: item.is_weekend
  }));

  const forecastData = forecast.map(item => ({
    date: item.ds,
    forecast: item.yhat * 100,
    lowerBound: item.yhat_lower * 100,
    upperBound: item.yhat_upper * 100,
    type: 'forecast',
    is_holiday: item.is_holiday,
    is_weekend: item.is_weekend
  }));

  const allData = [...historicalData, ...forecastData];

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length > 0) {
      const data = payload[0].payload;
      return (
        <div className="custom-tooltip">
          <p className="tooltip-date">{data.date}</p>
          {data.type === 'historical' ? (
            <>
              <p className="tooltip-value historical">
                Ocupación: {data.occupancy === 100 ? 'Ocupado' : 'Libre'}
              </p>
            </>
          ) : (
            <>
              <p className="tooltip-value forecast">
                Pronóstico: {data.forecast.toFixed(1)}%
              </p>
              <p className="tooltip-range">
                Rango: {data.lowerBound.toFixed(1)}% - {data.upperBound.toFixed(1)}%
              </p>
            </>
          )}
          {data.is_holiday === 1 && (
            <p className="tooltip-badge holiday">🎉 Feriado</p>
          )}
          {data.is_weekend === 1 && (
            <p className="tooltip-badge weekend">📅 Fin de semana</p>
          )}
        </div>
      );
    }
    return null;
  };

  CustomTooltip.propTypes = {
    active: PropTypes.bool,
    payload: PropTypes.array,
  };

  return (
    <div className="chart-container">
      <h2 className="chart-title">Ocupación Histórica y Pronóstico</h2>
      <ResponsiveContainer width="100%" height={400}>
        <ComposedChart data={allData} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis
            dataKey="date"
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis
            label={{ value: 'Ocupación (%)', angle: -90, position: 'insideLeft' }}
            domain={[0, 100]}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          {/* Banda de confianza */}
          <Area
            type="monotone"
            dataKey="upperBound"
            stackId="1"
            stroke="none"
            fill="#c7d2fe"
            fillOpacity={0.3}
            name="Intervalo de confianza"
          />
          <Area
            type="monotone"
            dataKey="lowerBound"
            stackId="1"
            stroke="none"
            fill="#fff"
            fillOpacity={1}
          />
          
          {/* Línea histórica */}
          <Line
            type="stepAfter"
            dataKey="occupancy"
            stroke="#48bb78"
            strokeWidth={2.5}
            dot={false}
            name="Ocupación Histórica"
          />
          
          {/* Línea de pronóstico */}
          <Line
            type="monotone"
            dataKey="forecast"
            stroke="#667eea"
            strokeWidth={2.5}
            strokeDasharray="5 5"
            dot={false}
            name="Pronóstico"
          />
          
          {/* Marcar feriados y fines de semana */}
          {allData
            .filter(d => d.is_holiday === 1)
            .map((d, i) => (
              <ReferenceDot
                key={`holiday-${i}`}
                x={d.date}
                y={d.forecast || d.occupancy}
                r={6}
                fill="#ed8936"
                stroke="#fff"
                strokeWidth={2}
              />
            ))}
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}

ForecastChart.propTypes = {
  historical: PropTypes.arrayOf(PropTypes.object),
  forecast: PropTypes.arrayOf(PropTypes.object),
};

export default ForecastChart;
