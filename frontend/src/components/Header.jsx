import { Mountain } from 'lucide-react';
import './Header.css';

function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <div className="header-title">
          <Mountain size={32} className="header-icon" />
          <h1>Refuge Occupancy Forecasting</h1>
        </div>
        <p className="header-subtitle">
          Predicción de ocupación del refugio usando SARIMAX con contexto del calendario chileno
        </p>
      </div>
    </header>
  );
}

export default Header;
