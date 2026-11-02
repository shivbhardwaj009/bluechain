import React from 'react';
import { Waves, ShieldAlert, RefreshCw, Compass, Droplet } from 'lucide-react';

interface HeaderProps {
  onOpenSpillModal: () => void;
  onRefreshData: () => void;
  isRefreshing: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  onOpenSpillModal,
  onRefreshData,
  isRefreshing
}) => {
  return (
    <header className="glass-panel" style={{
      position: 'absolute',
      top: 16,
      left: 16,
      right: 16,
      zIndex: 20,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '12px 20px',
      borderRadius: '12px'
    }}>
      {/* Brand & Scope */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
        <div style={{
          width: 40,
          height: 40,
          borderRadius: 10,
          background: 'linear-gradient(135deg, #0284c7, #06b6d4)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 15px rgba(56, 189, 248, 0.4)'
        }}>
          <Waves size={24} color="#ffffff" />
        </div>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h1 style={{ fontSize: '18px', fontWeight: 700, letterSpacing: '0.05em', color: '#ffffff' }}>
              BLUECHAIN
            </h1>
            <span style={{
              fontSize: '11px',
              fontWeight: 600,
              padding: '2px 8px',
              borderRadius: '999px',
              background: 'rgba(56, 189, 248, 0.15)',
              color: 'var(--accent-cyan)',
              border: '1px solid rgba(56, 189, 248, 0.3)'
            }}>
              OIPE v1.0
            </span>
          </div>
          <p style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
            AI-Powered Ocean Behaviour & Impact Prediction System • Strictly Marine
          </p>
        </div>
      </div>

      {/* Middle Pill: Scope Protection */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '6px 14px',
        background: 'rgba(15, 34, 56, 0.8)',
        borderRadius: '20px',
        border: '1px solid rgba(56, 189, 248, 0.2)',
        fontSize: '12px',
        color: '#bae6fd'
      }}>
        <Compass size={14} color="var(--accent-cyan)" />
        <span>Pelagic & Polar Basins Active</span>
        <span style={{ color: 'var(--text-dim)' }}>|</span>
        <span style={{ color: '#94a3b8' }}>Sample Data Mode (Offline Enabled)</span>
      </div>

      {/* Action Controls */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <button
          onClick={onOpenSpillModal}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            background: 'linear-gradient(135deg, #f59e0b, #d97706)',
            color: '#ffffff',
            border: 'none',
            borderRadius: '8px',
            padding: '8px 14px',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
            boxShadow: '0 0 12px rgba(245, 158, 11, 0.35)',
            transition: 'transform 0.15s ease'
          }}
          onMouseEnter={(e) => (e.currentTarget.style.transform = 'scale(1.03)')}
          onMouseLeave={(e) => (e.currentTarget.style.transform = 'scale(1.0)')}
        >
          <Droplet size={16} />
          <span>Simulate Oil Spill</span>
        </button>

        <button
          onClick={onRefreshData}
          disabled={isRefreshing}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: 'rgba(56, 189, 248, 0.12)',
            color: 'var(--accent-cyan)',
            border: '1px solid rgba(56, 189, 248, 0.3)',
            borderRadius: '8px',
            padding: '8px 12px',
            fontSize: '13px',
            fontWeight: 500,
            cursor: isRefreshing ? 'wait' : 'pointer'
          }}
        >
          <RefreshCw size={14} className={isRefreshing ? 'animate-spin' : ''} />
          <span>{isRefreshing ? 'Syncing...' : 'Sync Feeds'}</span>
        </button>
      </div>
    </header>
  );
};
