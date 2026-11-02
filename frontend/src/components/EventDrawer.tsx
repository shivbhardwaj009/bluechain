import React from 'react';
import { AlertCircle, Flame, Activity, Wind, Bug, ArrowRight } from 'lucide-react';
import type { OceanEventFeature } from '../api/client';

interface EventDrawerProps {
  events: OceanEventFeature[];
  selectedEventId?: string;
  onSelectEvent: (event: OceanEventFeature) => void;
}

export const EventDrawer: React.FC<EventDrawerProps> = ({
  events,
  selectedEventId,
  onSelectEvent
}) => {
  const getIcon = (type: string) => {
    switch (type) {
      case 'marine_heatwave':
        return <Flame size={14} color="#f97316" />;
      case 'earthquake':
        return <Activity size={14} color="#ef4444" />;
      case 'cyclone':
        return <Wind size={14} color="#38bdf8" />;
      case 'algal_bloom':
        return <Bug size={14} color="#10b981" />;
      default:
        return <AlertCircle size={14} color="#fbbf24" />;
    }
  };

  const getSeverityColor = (sev: string) => {
    switch (sev.toLowerCase()) {
      case 'extreme': return '#ef4444';
      case 'severe': return '#f97316';
      case 'strong': return '#f59e0b';
      case 'moderate': return '#38bdf8';
      default: return '#10b981';
    }
  };

  return (
    <div className="glass-panel" style={{
      position: 'absolute',
      bottom: 24,
      left: 16,
      width: 320,
      maxHeight: 280,
      zIndex: 15,
      padding: '14px',
      display: 'flex',
      flexDirection: 'column',
      gap: '8px'
    }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <AlertCircle size={15} color="var(--accent-cyan)" />
          <span style={{ fontSize: '13px', fontWeight: 600 }}>Active Marine Events ({events.length})</span>
        </div>
      </div>

      <div style={{ overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '6px', paddingRight: '4px' }}>
        {events.map((ev) => {
          const props = ev.properties;
          const isSelected = props.event_id === selectedEventId;
          const sevColor = getSeverityColor(props.severity);

          return (
            <div
              key={props.event_id}
              onClick={() => onSelectEvent(ev)}
              className="glass-card"
              style={{
                padding: '8px 10px',
                cursor: 'pointer',
                borderColor: isSelected ? 'var(--accent-cyan)' : undefined,
                background: isSelected ? 'rgba(56, 189, 248, 0.15)' : undefined
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  {getIcon(props.type)}
                  <span style={{ fontSize: '12px', fontWeight: 600, color: '#f8fafc' }}>
                    {props.title}
                  </span>
                </div>
                <span style={{
                  fontSize: '10px',
                  fontWeight: 700,
                  color: sevColor,
                  border: `1px solid ${sevColor}`,
                  borderRadius: 3,
                  padding: '1px 5px'
                }}>
                  {props.severity}
                </span>
              </div>

              <p style={{
                fontSize: '11px',
                color: 'var(--text-muted)',
                lineHeight: 1.4,
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden'
              }}>
                {props.explanation}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
};
