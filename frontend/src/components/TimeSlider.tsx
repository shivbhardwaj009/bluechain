import React from 'react';
import { Calendar, Play, Pause, FastForward } from 'lucide-react';

export interface TimeStep {
  label: string;
  daysOffset: number;
  isForecast: boolean;
  dateStr: string;
}

export const TIME_STEPS: TimeStep[] = [
  { label: '-7d', daysOffset: -7, isForecast: false, dateStr: 'Oct 26 (Observed)' },
  { label: '-3d', daysOffset: -3, isForecast: false, dateStr: 'Oct 30 (Observed)' },
  { label: '-1d', daysOffset: -1, isForecast: false, dateStr: 'Nov 01 (Observed)' },
  { label: 'Now', daysOffset: 0, isForecast: false, dateStr: 'Nov 02 (Current Satellite)' },
  { label: '+7d', daysOffset: 7, isForecast: true, dateStr: 'Nov 09 (XGBoost Forecast)' },
  { label: '+14d', daysOffset: 14, isForecast: true, dateStr: 'Nov 16 (XGBoost Forecast)' },
  { label: '+30d', daysOffset: 30, isForecast: true, dateStr: 'Dec 02 (XGBoost Forecast)' }
];

interface TimeSliderProps {
  currentIndex: number;
  onChangeIndex: (index: number) => void;
}

export const TimeSlider: React.FC<TimeSliderProps> = ({ currentIndex, onChangeIndex }) => {
  const currentStep = TIME_STEPS[currentIndex];

  return (
    <div className="glass-panel" style={{
      position: 'absolute',
      bottom: 24,
      left: '50%',
      transform: 'translateX(-50%)',
      zIndex: 20,
      width: '640px',
      maxWidth: 'calc(100vw - 32px)',
      padding: '12px 20px',
      display: 'flex',
      flexDirection: 'column',
      gap: '10px'
    }}>
      {/* Top Header: Step Name and Observed vs Forecast Tag */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <Calendar size={15} color="var(--accent-cyan)" />
          <span style={{ fontSize: '13px', fontWeight: 600, color: '#f8fafc' }}>
            {currentStep.dateStr}
          </span>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '2px 10px',
          borderRadius: '12px',
          background: currentStep.isForecast ? 'rgba(99, 102, 241, 0.2)' : 'rgba(16, 185, 129, 0.2)',
          border: `1px solid ${currentStep.isForecast ? '#818cf8' : '#34d399'}`,
          fontSize: '11px',
          fontWeight: 600,
          color: currentStep.isForecast ? '#c7d2fe' : '#a7f3d0'
        }}>
          <span style={{
            width: 6,
            height: 6,
            borderRadius: '50%',
            background: currentStep.isForecast ? '#818cf8' : '#34d399'
          }} />
          <span>{currentStep.isForecast ? 'ML MODEL FORECAST HORIZON' : 'OBSERVED SATELLITE BLEND'}</span>
        </div>
      </div>

      {/* Discrete Step Buttons */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '6px' }}>
        {TIME_STEPS.map((step, idx) => {
          const isActive = idx === currentIndex;
          return (
            <button
              key={step.label}
              onClick={() => onChangeIndex(idx)}
              style={{
                flex: 1,
                padding: '8px 4px',
                borderRadius: '6px',
                background: isActive
                  ? (step.isForecast ? 'linear-gradient(135deg, #4f46e5, #6366f1)' : 'linear-gradient(135deg, #0284c7, #38bdf8)')
                  : 'rgba(15, 34, 56, 0.7)',
                border: isActive
                  ? '1px solid #ffffff'
                  : (step.isForecast ? '1px dashed rgba(99, 102, 241, 0.4)' : '1px solid rgba(255,255,255,0.06)'),
                color: isActive ? '#ffffff' : (step.isForecast ? '#a5b4fc' : '#94a3b8'),
                fontSize: '12px',
                fontWeight: isActive ? 700 : 500,
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              {step.label}
            </button>
          );
        })}
      </div>
    </div>
  );
};
