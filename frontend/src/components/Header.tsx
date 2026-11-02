import React from 'react';
import { Waves, RefreshCw, Compass, Droplet, ShieldCheck } from 'lucide-react';

interface HeaderProps {
  onOpenSpillModal: () => void;
  onRefreshData: () => void;
  isRefreshing: boolean;
  totalEventsCount: number;
}

export const Header: React.FC<HeaderProps> = ({
  onOpenSpillModal,
  onRefreshData,
  isRefreshing,
  totalEventsCount
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
      padding: '10px 18px',
      borderRadius: '12px'
    }}>
      {/* Brand & Scope */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
        <img
          src="/logo.png"
          alt="BLUECHAIN"
          style={{
            width: 42,
            height: 42,
            borderRadius: 10,
            boxShadow: '0 0 15px rgba(56, 189, 248, 0.45)',
            border: '1px solid rgba(56, 189, 248, 0.5)',
            objectFit: 'cover'
          }}
        />
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <h1 style={{ fontSize: '18px', fontWeight: 800, letterSpacing: '0.06em', color: '#ffffff' }}>
              BLUECHAIN
            </h1>
            <span style={{
              fontSize: '11px',
              fontWeight: 700,
              padding: '2px 8px',
              borderRadius: '999px',
              background: 'rgba(56, 189, 248, 0.15)',
              color: 'var(--accent-cyan)',
              border: '1px solid rgba(56, 189, 248, 0.35)'
            }}>
              OIPE v1.0 • ONLINE
            </span>
          </div>
          <p style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
            AI-Powered Ocean Behaviour & Impact Prediction System • Strictly Marine
          </p>
        </div>
      </div>

      {/* Middle Pill: Scope Enforcement Banner */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        padding: '6px 14px',
        background: 'rgba(15, 34, 56, 0.85)',
        borderRadius: '20px',
        border: '1px solid rgba(56, 189, 248, 0.25)',
        fontSize: '12px',
        color: '#bae6fd'
      }}>
        <ShieldCheck size={15} color="var(--accent-cyan)" />
        <span>Marine Land-Mask Active</span>
        <span style={{ color: 'var(--text-dim)' }}>|</span>
        <span style={{ color: '#38bdf8', fontWeight: 600 }}>{totalEventsCount} Active Events Detected</span>
        <span style={{ color: 'var(--text-dim)' }}>|</span>
        <span style={{ color: '#94a3b8' }}>Sample Data Mode</span>
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
            fontSize: '12px',
            fontWeight: 700,
            cursor: 'pointer',
            boxShadow: '0 0 12px rgba(245, 158, 11, 0.4)',
            transition: 'transform 0.15s ease'
          }}
          onMouseEnter={(e) => (e.currentTarget.style.transform = 'scale(1.03)')}
          onMouseLeave={(e) => (e.currentTarget.style.transform = 'scale(1.0)')}
        >
          <Droplet size={15} />
          <span>72h Oil Spill Tool</span>
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
            fontSize: '12px',
            fontWeight: 600,
            cursor: isRefreshing ? 'wait' : 'pointer'
          }}
        >
          <RefreshCw size={13} className={isRefreshing ? 'animate-spin' : ''} />
          <span>{isRefreshing ? 'Syncing...' : 'Sync Feeds'}</span>
        </button>
      </div>
    </header>
  );
};
