import React, { useState } from 'react';
import { X, Droplet, Play, AlertTriangle, Compass, CheckCircle2 } from 'lucide-react';
import { api } from '../api/client';
import type { SpillSimResponse } from '../api/client';

interface SpillSimulatorModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSimulationSuccess: (simResult: SpillSimResponse) => void;
  initialLat?: number;
  initialLon?: number;
}

export const SpillSimulatorModal: React.FC<SpillSimulatorModalProps> = ({
  isOpen,
  onClose,
  onSimulationSuccess,
  initialLat = 24.5,
  initialLon = -45.0
}) => {
  const [lat, setLat] = useState(initialLat);
  const [lon, setLon] = useState(initialLon);
  const [volume, setVolume] = useState(5000);
  const [oilType, setOilType] = useState('Medium Crude');
  const [duration, setDuration] = useState(72);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
        particle_count: 100
      });
      onSimulationSuccess(res);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Simulation error');
    } finally {
      setLoading(false);
    }
  };

  const applyPreset = (pLat: number, pLon: number, name: string) => {
    setLat(pLat);
    setLon(pLon);
  };

  return (
    <div style={{
      position: 'fixed',
      inset: 0,
      background: 'rgba(5, 11, 20, 0.75)',
      backdropFilter: 'blur(6px)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 50,
      padding: '16px'
    }}>
      <div className="glass-panel" style={{
        width: '100%',
        maxWidth: '480px',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        gap: '18px'
      }}>
        {/* Modal Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div style={{
              width: 32,
              height: 32,
              borderRadius: 8,
              background: 'linear-gradient(135deg, #f59e0b, #d97706)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <Droplet size={18} color="#ffffff" />
            </div>
            <div>
              <h2 style={{ fontSize: '16px', fontWeight: 700, color: '#ffffff' }}>
                Lagrangian Oil Spill Drift Simulator
              </h2>
              <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
                72-Hour Surface Current + 3% Wind Advection & Diffusion
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

        {/* Preset Locations */}
        <div>
          <span style={{ fontSize: '11px', color: 'var(--text-dim)', fontWeight: 600 }}>PELAGIC PRESETS:</span>
          <div style={{ display: 'flex', gap: '6px', marginTop: '6px', flexWrap: 'wrap' }}>
            <button
              type="button"
              onClick={() => applyPreset(26.5, -45.0, 'North Atlantic')}
              style={{ padding: '4px 8px', borderRadius: 4, background: 'rgba(56, 189, 248, 0.12)', border: '1px solid rgba(56, 189, 248, 0.25)', color: '#bae6fd', fontSize: '11px', cursor: 'pointer' }}
            >
              North Atlantic Gyre
            </button>
            <button
              type="button"
              onClick={() => applyPreset(24.5, 58.5, 'Gulf of Oman')}
              style={{ padding: '4px 8px', borderRadius: 4, background: 'rgba(56, 189, 248, 0.12)', border: '1px solid rgba(56, 189, 248, 0.25)', color: '#bae6fd', fontSize: '11px', cursor: 'pointer' }}
            >
              Gulf of Oman Tanker Lane
            </button>
            <button
              type="button"
              onClick={() => applyPreset(-18.25, 149.5, 'Coral Sea')}
              style={{ padding: '4px 8px', borderRadius: 4, background: 'rgba(56, 189, 248, 0.12)', border: '1px solid rgba(56, 189, 248, 0.25)', color: '#bae6fd', fontSize: '11px', cursor: 'pointer' }}
            >
              Coral Sea Passage
            </button>
          </div>
        </div>

        <form onSubmit={handleRunSimulation} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            <div>
              <label style={{ fontSize: '11px', color: '#cbd5e1', fontWeight: 500, display: 'block', marginBottom: 4 }}>
                Latitude (°N)
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
              <label style={{ fontSize: '11px', color: '#cbd5e1', fontWeight: 500, display: 'block', marginBottom: 4 }}>
                Longitude (°E)
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
              <label style={{ fontSize: '11px', color: '#cbd5e1', fontWeight: 500, display: 'block', marginBottom: 4 }}>
                Spill Volume (m³)
              </label>
              <input
                type="number"
                min="50"
                max="100000"
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
              <label style={{ fontSize: '11px', color: '#cbd5e1', fontWeight: 500, display: 'block', marginBottom: 4 }}>
                Hydrocarbon Type
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
                <option value="Heavy Fuel Oil">Heavy Bunker C / Fuel Oil</option>
              </select>
            </div>
          </div>

          <div>
            <label style={{ fontSize: '11px', color: '#cbd5e1', fontWeight: 500, display: 'block', marginBottom: 4 }}>
              Drift Horizon: <strong>{duration} Hours</strong>
            </label>
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
              padding: '10px 16px',
              borderRadius: 8,
              background: 'linear-gradient(135deg, #0284c7, #06b6d4)',
              border: 'none',
              color: '#ffffff',
              fontSize: '13px',
              fontWeight: 700,
              cursor: loading ? 'wait' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              boxShadow: '0 0 15px rgba(56, 189, 248, 0.3)'
            }}
          >
            <Play size={16} />
            <span>{loading ? 'Running Lagrangian Advection...' : 'Execute 72h Drift Simulation'}</span>
          </button>
        </form>
      </div>
    </div>
  );
};
