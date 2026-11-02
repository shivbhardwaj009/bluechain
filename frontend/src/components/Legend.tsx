import React from 'react';
import type { OceanLayer } from './LayerControl';

interface LegendProps {
  activeLayer: OceanLayer;
}

export const Legend: React.FC<LegendProps> = ({ activeLayer }) => {
  return (
    <div className="glass-panel" style={{
      position: 'absolute',
      bottom: 24,
      right: 410,
      zIndex: 15,
      padding: '10px 14px',
      display: 'flex',
      flexDirection: 'column',
      gap: '6px',
      fontSize: '11px'
    }}>
      <div style={{ fontWeight: 600, color: 'var(--text-main)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
        {activeLayer === 'risk_grid' ? 'Ocean Risk Index (0 - 100)' :
         activeLayer === 'anomaly' ? 'SST Anomaly (ΔT °C)' :
         activeLayer === 'chlorophyll' ? 'Chlorophyll-a (mg/m³)' : 'Sea Surface Temp (°C)'}
      </div>

      {/* Gradient Bar */}
      <div style={{
        width: 180,
        height: 8,
        borderRadius: 4,
        background: activeLayer === 'anomaly' || activeLayer === 'risk_grid'
          ? 'linear-gradient(to right, #10b981, #38bdf8, #f59e0b, #ef4444)'
          : 'linear-gradient(to right, #0284c7, #10b981, #f59e0b, #dc2626)'
      }} />

      <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '10px' }}>
        <span>{activeLayer === 'anomaly' ? '0.0°C' : (activeLayer === 'risk_grid' ? '0 Low' : '0.1')}</span>
        <span>{activeLayer === 'anomaly' ? '+1.5°C' : (activeLayer === 'risk_grid' ? '50 Mod' : '5.0')}</span>
        <span>{activeLayer === 'anomaly' ? '+3.5°C' : (activeLayer === 'risk_grid' ? '100 Extreme' : '20.0+')}</span>
      </div>
    </div>
  );
};
