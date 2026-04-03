import { Calendar, TrendingUp, BarChart3, Award } from 'lucide-react';
import PropTypes from 'prop-types';
import './StatsCards.css';

function StatsCards({ stats }) {
  if (!stats) return null;

  const cards = [
    {
      icon: <Calendar />,
      title: 'Días Históricos',
      value: stats.total_days,
      subtitle: `${stats.occupied_days} ocupados`,
      color: '#667eea'
    },
    {
      icon: <TrendingUp />,
      title: 'Tasa de Ocupación',
      value: `${stats.occupancy_rate}%`,
      subtitle: 'Histórico',
      color: '#48bb78'
    },
    {
      icon: <BarChart3 />,
      title: 'Pronóstico Promedio',
      value: `${stats.avg_forecast_occupancy}%`,
      subtitle: `${stats.forecast_days} días`,
      color: '#ed8936'
    },
    {
      icon: <Award />,
      title: 'Días Especiales',
      value: stats.holidays_in_forecast + stats.sandwiches_in_forecast,
      subtitle: `${stats.weekends_in_forecast} fines de semana`,
      color: '#9f7aea'
    }
  ];

  return (
    <div className="stats-grid">
      {cards.map((card, index) => (
        <div key={index} className="stat-card" style={{ borderLeftColor: card.color }}>
          <div className="stat-icon" style={{ color: card.color }}>
            {card.icon}
          </div>
          <div className="stat-content">
            <div className="stat-value">{card.value}</div>
            <div className="stat-title">{card.title}</div>
            <div className="stat-subtitle">{card.subtitle}</div>
          </div>
        </div>
      ))}
    </div>
  );
}

StatsCards.propTypes = {
  stats: PropTypes.shape({
    total_days: PropTypes.number,
    occupied_days: PropTypes.number,
    occupancy_rate: PropTypes.number,
    avg_forecast_occupancy: PropTypes.number,
    forecast_days: PropTypes.number,
    holidays_in_forecast: PropTypes.number,
    sandwiches_in_forecast: PropTypes.number,
    weekends_in_forecast: PropTypes.number,
  }),
};

export default StatsCards;
