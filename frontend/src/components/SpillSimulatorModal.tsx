import React, { useState } from 'react';
import { X, Droplet, Play, AlertTriangle, Crosshair, MapPin } from 'lucide-react';
import { api } from '../api/client';
import type { SpillSimResponse } from '../api/client';

interface SpillSimulatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSimulationSuccess: (simResult: SpillSimResponse) => void;
  onEnableMapPickMode: () => void;
  pickedLat?: number;
  pickedLon?: number;
}

export const SpillSimulatorModal: React.FC<SpillSimulatorModalProps> = ({
  isOpen,
  onClose,
  onSimulationSuccess,
  onEnableMapPickMode,
  pickedLat = 24.5,
  pickedLon = -45.0
}) => {
  const [lat, setLat] = useState(pickedLat);
  const [lon, setLon] = useState(pickedLon);
  const [volume, setVolume] = useState(5000);
  const [oilType, setOilType] = useState('Medium Crude');
  const [duration, setDuration] = useState(72);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Sync when user clicks on map
  React.useEffect(() => {
    if (pickedLat !== undefined && pickedLon !== undefined) {
      setLat(pickedLat);
      setLon(pickedLon);
    }
  }, [pickedLat, pickedLon]);

  if (!isOpen) return null;

  const handleRunSimulation = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await api.simulateSpill({
        latitude: lat,
        longitude: lon,
        volume_m3: volume,
        oil_type: oilType,
        duration_hours: duration,
        particle_count: 120
      });
      onSimulationSuccess(res);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Simulation error');
    } finally {
      setLoading(false);
    }
  };

  const applyPreset = (pLat: number, pLon: number) => {
    setLat(pLat);
    setLon(pLon);
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(5, 11, 20, 0.75)',
      backdropFilter: 'blur(8px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 50,
      padding: '16px'
    }}>
      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: '500px',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        boxShadow: '0 0 35px rgba(245, 158, 11, 0.25)'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: 36,
              height: 36,
              borderRadius: 10,
              background: 'linear-gradient(135deg, #f59e0b, #d97706)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              boxShadow: '0 0 15px rgba(245, 158, 11, 0.4)'
            }}>
              <Droplet size={20} color="#ffffff" />
            </div>
            <div>
              <h2 style={{ fontSize: '16px', fontWeight: 800, color: '#ffffff' }}>
                72h Lagrangian Oil Spill Drift Tool
              </h2>
              <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                Surface Current Vector + 3% Wind Advection & Brownian Diffusion
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            style={{ background: 'transparent', border: 'none', color: '#94a3b8', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Offshore Corridor Presets */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
            <span style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 600 }}>OFFSHORE CORRIDOR PRESETS:</span>
            <button
              type="button"
              onClick={onEnableMapPickMode}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                background: 'rgba(56, 189, 248, 0.15)',
                border: '1px solid rgba(56, 189, 248, 0.35)',
                color: '#38bdf8',
                borderRadius: 4,
                padding: '2px 8px',
                fontSize: '11px',
                cursor: 'pointer'
              }}
            >
              <Crosshair size={12} />
              <span>Pick on Map</span>
            </button>
          </div>
          <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
            <button
              type="button"
              onClick={() => applyPreset(26.5, -45.0)}
              style={{ padding: '4px 8px', borderRadius: 4, background: 'rgba(56, 189, 248, 0.12)', border: '1px solid rgba(56, 189, 248, 0.25)', color: '#bae6fd', fontSize: '11px', cursor: 'pointer' }}
            >
              North Atlantic Gyre
            </button>
            <button
              type="button"
              onClick={() => applyPreset(24.5, 58.5)}
              style={{ padding: '4px 8px', borderRadius: 4, background: 'rgba(56, 189, 248, 0.12)', border: '1px solid rgba(56, 189, 248, 0.25)', color: '#bae6fd', fontSize: '11px', cursor: 'pointer' }}
            >
              Gulf of Oman Tanker Route
            </button>
            <button
              type="button"
              onClick={() => applyPreset(28.7, -88.4)}
              style={{ padding: '4px 8px', borderRadius: 4, background: 'rgba(56, 189, 248, 0.12)', border: '1px solid rgba(56, 189, 248, 0.25)', color: '#bae6fd', fontSize: '11px', cursor: 'pointer' }}
            >
              Gulf of Mexico
            </button>
            <button
              type="button"
              onClick={() => applyPreset(-18.25, 149.5)}
              style={{ padding: '4px 8px', borderRadius: 4, background: 'rgba(56, 189, 248, 0.12)', border: '1px solid rgba(56, 189, 248, 0.25)', color: '#bae6fd', fontSize: '11px', cursor: 'pointer' }}
            >
              Coral Sea
            </button>
          </div>
        </div>

        <form onSubmit={handleRunSimulation} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ fontSize: '11px', color: '#cbd5e1', fontWeight: 600, display: 'block', marginBottom: 4 }}>
                Spill Latitude (°N)
              </label>
              <input
                type="number"
                step="0.01"
                min="-89.0"
                max="89.0"
                value={lat}
                onChange={(e) => setLat(parseFloat(e.target.value))}
                required
                style={{
                  width: '100%',
                  padding: '8px 10px',
                  borderRadius: 6,
                  background: 'rgba(10, 22, 38, 0.8)',
                  border: '1px solid var(--border-subtle)',
                  color: '#ffffff',
                  fontSize: '12px'
                }}
              />
            </div>
            <div>
              <label style={{ fontSize: '11px', color: '#cbd5e1', fontWeight: 600, display: 'block', marginBottom: 4 }}>
                Spill Longitude (°E)
              </label>
              <input
                type="number"
                step="0.01"
                min="-180.0"
                max="180.0"
                value={lon}
                onChange={(e) => setLon(parseFloat(e.target.value))}
                required
                style={{
                  width: '100%',
                  padding: '8px 10px',
                  borderRadius: 6,
                  background: 'rgba(10, 22, 38, 0.8)',
                  border: '1px solid var(--border-subtle)',
                  color: '#ffffff',
                  fontSize: '12px'
                }}
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ fontSize: '11px', color: '#cbd5e1', fontWeight: 600, display: 'block', marginBottom: 4 }}>
                Estimated Volume (m³)
              </label>
              <input
                type="number"
                min="50"
                max="150000"
                value={volume}
                onChange={(e) => setVolume(parseFloat(e.target.value))}
                required
                style={{
                  width: '100%',
                  padding: '8px 10px',
                  borderRadius: 6,
                  background: 'rgba(10, 22, 38, 0.8)',
                  border: '1px solid var(--border-subtle)',
                  color: '#ffffff',
                  fontSize: '12px'
                }}
              />
            </div>
            <div>
              <label style={{ fontSize: '11px', color: '#cbd5e1', fontWeight: 600, display: 'block', marginBottom: 4 }}>
                Petroleum Grade
              </label>
              <select
                value={oilType}
                onChange={(e) => setOilType(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 10px',
                  borderRadius: 6,
                  background: 'rgba(10, 22, 38, 0.8)',
                  border: '1px solid var(--border-subtle)',
                  color: '#ffffff',
                  fontSize: '12px'
                }}
              >
                <option value="Light Crude">Light Condensate</option>
                <option value="Medium Crude">Medium Crude</option>
                <option value="Heavy Fuel Oil">Heavy Bunker C Fuel Oil</option>
              </select>
            </div>
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', color: '#cbd5e1', fontWeight: 600, marginBottom: 4 }}>
              <span>Simulation Horizon:</span>
              <span style={{ color: 'var(--accent-cyan)' }}>{duration} Hours</span>
            </div>
            <input
              type="range"
              min="12"
              max="168"
              step="12"
              value={duration}
              onChange={(e) => setDuration(parseInt(e.target.value))}
              style={{ width: '100%', accentColor: 'var(--accent-cyan)' }}
            />
          </div>

          {error && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px',
              borderRadius: 6,
              background: 'rgba(239, 68, 68, 0.2)',
              border: '1px solid #ef4444',
              color: '#fca5a5',
              fontSize: '12px'
            }}>
              <AlertTriangle size={15} />
              <span>{error}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            style={{
              padding: '12px 18px',
              borderRadius: 8,
              background: 'linear-gradient(135deg, #0284c7, #06b6d4)',
              border: 'none',
              color: '#ffffff',
              fontSize: '13px',
              fontWeight: 800,
              cursor: loading ? 'wait' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              boxShadow: '0 0 18px rgba(56, 189, 248, 0.35)'
            }}
          >
            <Play size={16} />
            <span>{loading ? 'Advecting Lagrangian Parcels...' : 'Run 72h Dispersion Model'}</span>
          </button>
        </form>
      </div>
    </div>
  );
};
