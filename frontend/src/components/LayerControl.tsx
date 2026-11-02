import React from 'react';
import { Layers, Flame, Activity, Wind, Bug, Shield, AlertTriangle } from 'lucide-react';

export type OceanLayer = 'sst' | 'anomaly' | 'chlorophyll' | 'sea_ice' | 'risk_grid';

interface LayerControlProps {
  activeLayer: OceanLayer;
  onSelectLayer: (layer: OceanLayer) => void;
  eventFilters: {
    heatwaves: boolean;
    earthquakes: boolean;
    cyclones: boolean;
    blooms: boolean;
  };
  onToggleEventFilter: (key: 'heatwaves' | 'earthquakes' | 'cyclones' | 'blooms') => void;
  showSpillLayer: boolean;
  onToggleSpillLayer: () => void;
}

export const LayerControl: React.FC<LayerControlProps> = ({
  activeLayer,
  onSelectLayer,
  eventFilters,
  onToggleEventFilter,
  showSpillLayer,
  onToggleSpillLayer
}) => {
  return (
    <div className="glass-panel" style={{
      position: 'absolute',
      top: 92,
      left: 16,
      width: 250,
      zIndex: 15,
      padding: '16px',
      display: 'flex',
      flexDirection: 'column',
      gap: '14px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: '10px' }}>
        <Layers size={18} color="var(--accent-cyan)" />
        <span style={{ fontSize: '13px', fontWeight: 600, letterSpacing: '0.04em', textTransform: 'uppercase' }}>
          Ocean Overlays
        </span>
      </div>

      {/* Primary Gridded Layers */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
        <span style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 500 }}>PRIMARY OCEAN FIELD</span>

        <button
          onClick={() => onSelectLayer('risk_grid')}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '8px 10px',
            borderRadius: '6px',
            background: activeLayer === 'risk_grid' ? 'rgba(56, 189, 248, 0.2)' : 'transparent',
            border: activeLayer === 'risk_grid' ? '1px solid var(--accent-cyan)' : '1px solid transparent',
            color: activeLayer === 'risk_grid' ? '#ffffff' : 'var(--text-muted)',
            fontSize: '12px',
            fontWeight: 500,
            cursor: 'pointer',
            textAlign: 'left'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Shield size={14} color="#38bdf8" />
            <span>Ocean Risk Index (0-100)</span>
          </div>
          {activeLayer === 'risk_grid' && <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#38bdf8' }} />}
        </button>

        <button
          onClick={() => onSelectLayer('anomaly')}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '8px 10px',
            borderRadius: '6px',
            background: activeLayer === 'anomaly' ? 'rgba(239, 68, 68, 0.2)' : 'transparent',
            border: activeLayer === 'anomaly' ? '1px solid #ef4444' : '1px solid transparent',
            color: activeLayer === 'anomaly' ? '#ffffff' : 'var(--text-muted)',
            fontSize: '12px',
            fontWeight: 500,
            cursor: 'pointer',
            textAlign: 'left'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Flame size={14} color="#ef4444" />
            <span>SST Thermal Anomaly (ΔT)</span>
          </div>
          {activeLayer === 'anomaly' && <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#ef4444' }} />}
        </button>

        <button
          onClick={() => onSelectLayer('sst')}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '8px 10px',
            borderRadius: '6px',
            background: activeLayer === 'sst' ? 'rgba(56, 189, 248, 0.15)' : 'transparent',
            border: activeLayer === 'sst' ? '1px solid var(--accent-cyan)' : '1px solid transparent',
            color: activeLayer === 'sst' ? '#ffffff' : 'var(--text-muted)',
            fontSize: '12px',
            fontWeight: 500,
            cursor: 'pointer',
            textAlign: 'left'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={14} color="#38bdf8" />
            <span>NOAA OISST Sea Surface Temp</span>
          </div>
        </button>

        <button
          onClick={() => onSelectLayer('chlorophyll')}
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '8px 10px',
            borderRadius: '6px',
            background: activeLayer === 'chlorophyll' ? 'rgba(16, 185, 129, 0.2)' : 'transparent',
            border: activeLayer === 'chlorophyll' ? '1px solid #10b981' : '1px solid transparent',
            color: activeLayer === 'chlorophyll' ? '#ffffff' : 'var(--text-muted)',
            fontSize: '12px',
            fontWeight: 500,
            cursor: 'pointer',
            textAlign: 'left'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Bug size={14} color="#10b981" />
            <span>Chlorophyll-a (Copernicus)</span>
          </div>
        </button>
      </div>

      {/* Event Hazard Markers Toggles */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '10px' }}>
        <span style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 500 }}>HAZARD EVENT MARKERS</span>

        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#e2e8f0', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={eventFilters.heatwaves}
            onChange={() => onToggleEventFilter('heatwaves')}
            style={{ accentColor: '#f97316' }}
          />
          <Flame size={13} color="#f97316" />
          <span>Hobday Marine Heatwaves</span>
        </label>

        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#e2e8f0', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={eventFilters.earthquakes}
            onChange={() => onToggleEventFilter('earthquakes')}
            style={{ accentColor: '#ef4444' }}
          />
          <AlertTriangle size={13} color="#ef4444" />
          <span>Offshore Quakes / Tsunamis</span>
        </label>

        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#e2e8f0', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={eventFilters.cyclones}
            onChange={() => onToggleEventFilter('cyclones')}
            style={{ accentColor: '#38bdf8' }}
          />
          <Wind size={13} color="#38bdf8" />
          <span>IBTrACS Tropical Cyclones</span>
        </label>

        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#e2e8f0', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={eventFilters.blooms}
            onChange={() => onToggleEventFilter('blooms')}
            style={{ accentColor: '#10b981' }}
          />
          <Bug size={13} color="#10b981" />
          <span>Harmful Algal Blooms (HAB)</span>
        </label>
      </div>

      {/* Spill Layer Active Toggle */}
      <div style={{ borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '10px' }}>
        <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#fbbf24', cursor: 'pointer' }}>
          <input
            type="checkbox"
            checked={showSpillLayer}
            onChange={onToggleSpillLayer}
            style={{ accentColor: '#f59e0b' }}
          />
          <span>Show Active Spill Drift</span>
        </label>
      </div>
    </div>
  );
};
