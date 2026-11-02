import React, { useState } from 'react';
import {
  AreaChart, Area, LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend as RechartLegend
} from 'recharts';
import {
  TrendingUp, AlertOctagon, Activity, ChevronRight, ChevronLeft, ShieldAlert, Thermometer, Droplets
} from 'lucide-react';
import type { EcosystemSummaryResponse, SeaIceResponse, ForecastResponse } from '../api/client';

interface SideDashboardProps {
  ecosystemSummary: EcosystemSummaryResponse | null;
  seaIceData: SeaIceResponse | null;
  forecastData: ForecastResponse | null;
  selectedRegionName?: string;
  onFlyToRegion: (lat: number, lon: number) => void;
}

export const SideDashboard: React.FC<SideDashboardProps> = ({
  ecosystemSummary,
  seaIceData,
  forecastData,
  selectedRegionName,
  onFlyToRegion
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [activeTab, setActiveTab] = useState<'forecast' | 'ice' | 'stress'>('forecast');

  // Chart data: forecast vs baseline with uncertainty band
  const forecastChartData = [
    { day: 'Day 0', observed: 2.9, forecast: 2.9, lower: 2.9, upper: 2.9, persistence: 2.9 },
    { day: 'Day 3', observed: 2.8, forecast: 2.75, lower: 2.45, upper: 3.05, persistence: 2.9 },
    { day: 'Day 7', observed: null, forecast: 2.65, lower: 2.20, upper: 3.10, persistence: 2.9 },
    { day: 'Day 14', observed: null, forecast: 2.40, lower: 1.85, upper: 2.95, persistence: 2.9 },
    { day: 'Day 21', observed: null, forecast: 2.15, lower: 1.50, upper: 2.80, persistence: 2.9 },
    { day: 'Day 30', observed: null, forecast: 1.85, lower: 1.10, upper: 2.60, persistence: 2.9 }
  ];

  // Sea ice trend data combining historical records + projections
  const seaIceChartData = seaIceData ? [
    ...seaIceData.monthly_historical.map(h => ({
      month: h.month,
      extent: h.extent,
      baseline: h.baseline,
      type: 'Observed'
    })),
    ...seaIceData.monthly_projection.map(p => ({
      month: p.month.split(' ')[0],
      extent: p.projected_extent,
      baseline: p.baseline,
      type: 'Projected'
    }))
  ] : [];

  return (
    <div style={{
      position: 'absolute',
      top: 92,
      right: 16,
      bottom: 24,
      width: isCollapsed ? 44 : 380,
      zIndex: 15,
      transition: 'width 0.25s ease',
      display: 'flex'
    }}>
      {/* Collapse Toggle Button */}
      <button
        onClick={() => setIsCollapsed(!isCollapsed)}
        style={{
          width: 24,
          height: 48,
          alignSelf: 'center',
          background: 'var(--bg-glass)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '6px 0 0 6px',
          color: 'var(--accent-cyan)',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
      >
        {isCollapsed ? <ChevronLeft size={16} /> : <ChevronRight size={16} />}
      </button>

      {/* Main Panel Content */}
      {!isCollapsed && (
        <div className="glass-panel" style={{
          flex: 1,
          height: '100%',
          overflowY: 'auto',
          padding: '16px',
          display: 'flex',
          flexDirection: 'column',
          gap: '16px'
        }}>
          {/* Header & Tabs */}
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <TrendingUp size={18} color="var(--accent-cyan)" />
                <span style={{ fontSize: '14px', fontWeight: 700, letterSpacing: '0.04em' }}>
                  OCEAN PREDICTION INTEL
                </span>
              </div>
              <span style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
                {selectedRegionName || 'Coral Sea / GBR'}
              </span>
            </div>

            <div style={{ display: 'flex', gap: '4px', background: 'rgba(5, 11, 20, 0.5)', padding: '3px', borderRadius: '8px' }}>
              <button
                onClick={() => setActiveTab('forecast')}
                style={{
                  flex: 1,
                  padding: '6px 4px',
                  borderRadius: '6px',
                  background: activeTab === 'forecast' ? 'rgba(56, 189, 248, 0.2)' : 'transparent',
                  border: 'none',
                  color: activeTab === 'forecast' ? '#ffffff' : 'var(--text-muted)',
                  fontSize: '11px',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                SST ML Forecast
              </button>
              <button
                onClick={() => setActiveTab('ice')}
                style={{
                  flex: 1,
                  padding: '6px 4px',
                  borderRadius: '6px',
                  background: activeTab === 'ice' ? 'rgba(56, 189, 248, 0.2)' : 'transparent',
                  border: 'none',
                  color: activeTab === 'ice' ? '#ffffff' : 'var(--text-muted)',
                  fontSize: '11px',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                Polar Sea-Ice
              </button>
              <button
                onClick={() => setActiveTab('stress')}
                style={{
                  flex: 1,
                  padding: '6px 4px',
                  borderRadius: '6px',
                  background: activeTab === 'stress' ? 'rgba(56, 189, 248, 0.2)' : 'transparent',
                  border: 'none',
                  color: activeTab === 'stress' ? '#ffffff' : 'var(--text-muted)',
                  fontSize: '11px',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                Ecosystem Risk
              </button>
            </div>
          </div>

          {/* TAB 1: SST ML Forecast with Uncertainty Envelope */}
          {activeTab === 'forecast' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', fontWeight: 600, color: '#bae6fd' }}>
                  SST Anomaly Forecast (°C) + Uncertainty Band
                </span>
                <span style={{ fontSize: '10px', color: '#94a3b8' }}>XGBoost v1 vs Persistence</span>
              </div>

              <div style={{ width: '100%', height: 190 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={forecastChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                    <XAxis dataKey="day" stroke="#64748b" fontSize={10} />
                    <YAxis stroke="#64748b" fontSize={10} domain={[0.5, 3.5]} />
                    <Tooltip contentStyle={{ background: '#0a1626', border: '1px solid #38bdf8', borderRadius: 8, fontSize: 11 }} />

                    {/* Uncertainty Envelope Band */}
                    <Area type="monotone" dataKey="upper" stroke="none" fill="rgba(56, 189, 248, 0.15)" />
                    <Area type="monotone" dataKey="lower" stroke="none" fill="rgba(10, 22, 38, 0.9)" />

                    {/* Model Forecast Curve */}
                    <Line type="monotone" dataKey="forecast" stroke="#38bdf8" strokeWidth={2.5} dot={{ r: 3 }} name="XGBoost Forecast" />
                    {/* Persistence Baseline Curve */}
                    <Line type="monotone" dataKey="persistence" stroke="#94a3b8" strokeDasharray="4 4" strokeWidth={1.5} name="Persistence Baseline" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div className="glass-card" style={{ padding: '10px', fontSize: '11px', lineHeight: 1.5, color: '#cbd5e1' }}>
                <div style={{ fontWeight: 600, color: 'var(--accent-cyan)', marginBottom: '4px' }}>
                  Model Evaluation (Time-Series Split):
                </div>
                <div>• 14-Day Skill Gain: <strong style={{ color: '#34d399' }}>+11.62%</strong> over persistence</div>
                <div>• 30-Day Skill Gain: <strong style={{ color: '#34d399' }}>+20.08%</strong> over persistence</div>
                <div style={{ color: 'var(--text-dim)', marginTop: '4px' }}>
                  Atmospheric cooling is predicted to decay current marine heatwave anomaly from +2.9°C to +1.85°C by Day 30.
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: Sea Ice Extent vs 1991-2020 Baseline */}
          {activeTab === 'ice' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', fontWeight: 600, color: '#bae6fd' }}>
                  Arctic Sea Ice Extent (Million km²)
                </span>
                <span style={{ fontSize: '10px', color: '#f87171' }}>-31.55% vs Baseline</span>
              </div>

              <div style={{ width: '100%', height: 190 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={seaIceChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                    <XAxis dataKey="month" stroke="#64748b" fontSize={10} />
                    <YAxis stroke="#64748b" fontSize={10} domain={[3, 15]} />
                    <Tooltip contentStyle={{ background: '#0a1626', border: '1px solid #38bdf8', borderRadius: 8, fontSize: 11 }} />
                    <Line type="monotone" dataKey="baseline" stroke="#94a3b8" strokeDasharray="4 4" strokeWidth={1.5} name="1991-2020 Baseline" />
                    <Line type="monotone" dataKey="extent" stroke="#06b6d4" strokeWidth={2.5} dot={{ r: 3 }} name="Current / Projected Extent" />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="glass-card" style={{ padding: '10px', fontSize: '11px', lineHeight: 1.5, color: '#cbd5e1' }}>
                <div style={{ fontWeight: 600, color: '#38bdf8', marginBottom: '2px' }}>
                  NSIDC Sea Ice Deficit Advisory:
                </div>
                <div>Current extent is 4.23 million km² vs 6.18 million km² climatology. Multi-year pack retreat in Beaufort and Chukchi Seas.</div>
              </div>
            </div>
          )}

          {/* TAB 3: Multi-Factor Ecosystem Stress Summary */}
          {activeTab === 'stress' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <span style={{ fontSize: '12px', fontWeight: 600, color: '#bae6fd' }}>
                Ocean Ecosystem Stress Summary
              </span>

              {/* Stress metric meters */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: '2px' }}>
                    <span>Marine Heatwave & Bleaching</span>
                    <strong style={{ color: '#ef4444' }}>88.5 / 100</strong>
                  </div>
                  <div style={{ width: '100%', height: 6, background: 'rgba(255,255,255,0.1)', borderRadius: 3 }}>
                    <div style={{ width: '88.5%', height: '100%', background: '#ef4444', borderRadius: 3 }} />
                  </div>
                </div>

                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: '2px' }}>
                    <span>Algal Hypoxia & Deoxygenation</span>
                    <strong style={{ color: '#f59e0b' }}>76.2 / 100</strong>
                  </div>
                  <div style={{ width: '100%', height: 6, background: 'rgba(255,255,255,0.1)', borderRadius: 3 }}>
                    <div style={{ width: '76.2%', height: '100%', background: '#f59e0b', borderRadius: 3 }} />
                  </div>
                </div>

                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: '2px' }}>
                    <span>Cyclone Marine Hazard Index</span>
                    <strong style={{ color: '#38bdf8' }}>82.0 / 100</strong>
                  </div>
                  <div style={{ width: '100%', height: 6, background: 'rgba(255,255,255,0.1)', borderRadius: 3 }}>
                    <div style={{ width: '82%', height: '100%', background: '#38bdf8', borderRadius: 3 }} />
                  </div>
                </div>

                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: '2px' }}>
                    <span>Ocean Acidification Stress</span>
                    <strong style={{ color: '#10b981' }}>64.0 / 100</strong>
                  </div>
                  <div style={{ width: '100%', height: 6, background: 'rgba(255,255,255,0.1)', borderRadius: 3 }}>
                    <div style={{ width: '64%', height: '100%', background: '#10b981', borderRadius: 3 }} />
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Top-10 Highest-Risk Marine Regions List */}
          <div style={{ borderTop: '1px solid rgba(255,255,255,0.08)', paddingTop: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
              <span style={{ fontSize: '12px', fontWeight: 600, color: '#f8fafc' }}>
                Top High-Risk Marine Ecoregions
              </span>
              <ShieldAlert size={14} color="#f97316" />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', maxHeight: 180, overflowY: 'auto' }}>
              {ecosystemSummary?.top_stressed_marine_ecoregions.map((reg, idx) => (
                <div
                  key={idx}
                  onClick={() => onFlyToRegion(reg.latitude, reg.longitude)}
                  className="glass-card"
                  style={{
                    padding: '8px 10px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    cursor: 'pointer'
                  }}
                >
                  <div>
                    <div style={{ fontSize: '12px', fontWeight: 600, color: '#ffffff' }}>
                      {reg.region_name}
                    </div>
                    <div style={{ fontSize: '10px', color: 'var(--text-dim)' }}>
                      {reg.ocean_basin} • {reg.dominant_hazard.replace('_', ' ')}
                    </div>
                  </div>
                  <div style={{
                    padding: '2px 8px',
                    borderRadius: 4,
                    background: reg.risk_score >= 80 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                    color: reg.risk_score >= 80 ? '#ef4444' : '#f59e0b',
                    fontSize: '11px',
                    fontWeight: 700
                  }}>
                    {reg.risk_score.toFixed(0)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
