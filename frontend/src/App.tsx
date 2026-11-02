import React, { useState, useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import { Header } from './components/Header';
import { OceanMap } from './map/OceanMap';
import { LayerControl } from './components/LayerControl';
import type { OceanLayer } from './components/LayerControl';
import { TimeSlider, TIME_STEPS } from './components/TimeSlider';
import { SideDashboard } from './components/SideDashboard';
import { EventDrawer } from './components/EventDrawer';
import { Legend } from './components/Legend';
import { SpillSimulatorModal } from './components/SpillSimulatorModal';
import { api } from './api/client';
import type {
  OceanEventFeature,
  RiskResponse,
  EcosystemSummaryResponse,
  SeaIceResponse,
  ForecastResponse,
  SpillSimResponse,
  TimeSeriesResponse
} from './api/client';
import { Clock, Play, Pause, AlertOctagon } from 'lucide-react';

export function App() {
  const [events, setEvents] = useState<OceanEventFeature[]>([]);
  const [riskData, setRiskData] = useState<RiskResponse | null>(null);
  const [ecosystemSummary, setEcosystemSummary] = useState<EcosystemSummaryResponse | null>(null);
  const [seaIceData, setSeaIceData] = useState<SeaIceResponse | null>(null);
  const [currentIceBasin, setCurrentIceBasin] = useState<'arctic' | 'antarctic'>('arctic');
  const [forecastData, setForecastData] = useState<ForecastResponse | null>(null);
  const [spillResult, setSpillResult] = useState<SpillSimResponse | null>(null);
  const [inspectedTelemetry, setInspectedTelemetry] = useState<TimeSeriesResponse | null>(null);

  const [activeLayer, setActiveLayer] = useState<OceanLayer>('risk_grid');
  const [timeStepIndex, setTimeStepIndex] = useState<number>(3); // Default 'Now'
  const [selectedEvent, setSelectedEvent] = useState<OceanEventFeature | null>(null);
  const [isSpillModalOpen, setIsSpillModalOpen] = useState(false);
  const [showSpillLayer, setShowSpillLayer] = useState(true);
  const [isMapPickMode, setIsMapPickMode] = useState(false);
  const [pickedSpillLat, setPickedSpillLat] = useState<number>(24.5);
  const [pickedSpillLon, setPickedSpillLon] = useState<number>(-45.0);
  const [spillPlaybackHour, setSpillPlaybackHour] = useState<number>(72);
  const [isSpillPlaying, setIsSpillPlaying] = useState<boolean>(false);
  const [landRejectionNotice, setLandRejectionNotice] = useState<string | null>(null);

  const [isRefreshing, setIsRefreshing] = useState(false);
  const [eventFilters, setEventFilters] = useState({
    heatwaves: true,
    earthquakes: true,
    cyclones: true,
    blooms: true
  });

  const mapRef = useRef<maplibregl.Map | null>(null);

  // Load Initial Datasets
  const loadData = async () => {
    try {
      setIsRefreshing(true);
      const [eventsRes, riskRes, ecoRes, iceRes, fcastRes] = await Promise.all([
        api.getEvents(),
        api.getRiskGrid(),
        api.getEcosystemSummary(),
        api.getSeaIce(currentIceBasin),
        api.getForecast(7)
      ]);

      setEvents(eventsRes.features || []);
      setRiskData(riskRes);
      setEcosystemSummary(ecoRes);
      setSeaIceData(iceRes);
      setForecastData(fcastRes);
    } catch (err) {
      console.error('Error loading ocean data:', err);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Update Sea-Ice data when basin switched
  const handleSwitchIceBasin = async (basin: 'arctic' | 'antarctic') => {
    setCurrentIceBasin(basin);
    try {
      const data = await api.getSeaIce(basin);
      setSeaIceData(data);
      if (basin === 'arctic') {
        handleFlyTo(82.0, 0.0, 3.2);
      } else {
        handleFlyTo(-75.0, 0.0, 3.2);
      }
    } catch (err) {
      console.error('Error loading sea ice basin:', err);
    }
  };

  // Automated particle animation loop when spill play is clicked
  useEffect(() => {
    let interval: any = null;
    if (isSpillPlaying && spillResult) {
      interval = setInterval(() => {
        setSpillPlaybackHour((prev) => {
          if (prev >= spillResult.duration_hours) {
            setIsSpillPlaying(false);
            return spillResult.duration_hours;
          }
          return prev + 6;
        });
      }, 700);
    }
    return () => clearInterval(interval);
  }, [isSpillPlaying, spillResult]);

  // Click on map handler
  const handleMapClick = async (lat: number, lon: number) => {
    if (isMapPickMode) {
      setPickedSpillLat(lat);
      setPickedSpillLon(lon);
      setIsMapPickMode(false);
      setIsSpillModalOpen(true);
      return;
    }

    // Query clicked ocean coordinates
    try {
      setLandRejectionNotice(null);
      const tsData = await api.getTimeSeries('sst', lat, lon);
      setInspectedTelemetry(tsData);
    } catch (err: any) {
      if (err.message && err.message.includes('continental land')) {
        setLandRejectionNotice(`Point (${lat.toFixed(2)}°, ${lon.toFixed(2)}°) is located on land. BLUECHAIN strictly monitors marine basins.`);
        setTimeout(() => setLandRejectionNotice(null), 5000);
      }
    }
  };

  // Filter events based on active drawer checkboxes
  const filteredEvents = events.filter((ev) => {
    const t = ev.properties.type;
    if (t === 'marine_heatwave' && !eventFilters.heatwaves) return false;
    if (t === 'earthquake' && !eventFilters.earthquakes) return false;
    if (t === 'cyclone' && !eventFilters.cyclones) return false;
    if (t === 'algal_bloom' && !eventFilters.blooms) return false;
    return true;
  });

  const handleToggleEventFilter = (key: 'heatwaves' | 'earthquakes' | 'cyclones' | 'blooms') => {
    setEventFilters((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const handleFlyTo = (lat: number, lon: number, zoom = 4.5) => {
    if (mapRef.current) {
      mapRef.current.flyTo({
        center: [lon, lat],
        zoom: zoom,
        speed: 1.2,
        curve: 1.4,
        essential: true
      });
    }
  };

  const handleSelectEvent = (event: OceanEventFeature) => {
    setSelectedEvent(event);
    handleFlyTo(event.properties.latitude, event.properties.longitude, 5.5);
  };

  const handleSimulationSuccess = (sim: SpillSimResponse) => {
    setSpillResult(sim);
    setShowSpillLayer(true);
    setSpillPlaybackHour(sim.duration_hours);
    handleFlyTo(sim.origin_lat, sim.origin_lon, 5.0);
  };

  const isForecastStep = TIME_STEPS[timeStepIndex].isForecast;

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      {/* Top Header */}
      <Header
        onOpenSpillModal={() => setIsSpillModalOpen(true)}
        onRefreshData={loadData}
        isRefreshing={isRefreshing}
        totalEventsCount={filteredEvents.length}
      />

      {/* Terrestrial Scope Rejection Toast */}
      {landRejectionNotice && (
        <div style={{
          position: 'absolute',
          top: 80,
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 35,
          background: 'rgba(239, 68, 68, 0.95)',
          color: '#ffffff',
          borderRadius: 8,
          padding: '8px 16px',
          fontSize: '12px',
          fontWeight: 600,
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          boxShadow: '0 0 20px rgba(239, 68, 68, 0.6)'
        }}>
          <AlertOctagon size={16} />
          <span>{landRejectionNotice}</span>
        </div>
      )}

      {/* Full-Screen MapLibre Map */}
      <OceanMap
        events={filteredEvents}
        riskData={riskData}
        forecastData={forecastData}
        activeLayer={activeLayer}
        spillResult={spillResult}
        showSpillLayer={showSpillLayer}
        spillPlaybackHour={spillPlaybackHour}
        isForecastTimeStep={isForecastStep}
        onSelectEvent={handleSelectEvent}
        onMapClickCoordinate={handleMapClick}
        mapRefExternal={mapRef}
      />

      {/* Left Control Drawer: Layers & Event Filters */}
      <LayerControl
        activeLayer={activeLayer}
        onSelectLayer={(l) => setActiveLayer(l)}
        eventFilters={eventFilters}
        onToggleEventFilter={handleToggleEventFilter}
        showSpillLayer={showSpillLayer}
        onToggleSpillLayer={() => setShowSpillLayer(!showSpillLayer)}
      />

      {/* Left Bottom Drawer: Active Marine Hazard Events */}
      <EventDrawer
        events={filteredEvents}
        selectedEventId={selectedEvent?.properties.event_id}
        onSelectEvent={handleSelectEvent}
      />

      {/* Bottom Center: Time-Slider (Observed to 7d/14d/30d Forecasts) */}
      <TimeSlider
        currentIndex={timeStepIndex}
        onChangeIndex={(idx) => setTimeStepIndex(idx)}
      />

      {/* Oil Spill Hour-by-Hour Trajectory Playback Widget */}
      {spillResult && showSpillLayer && (
        <div className="glass-panel" style={{
          position: 'absolute',
          bottom: 110,
          left: '50%',
          transform: 'translateX(-50%)',
          zIndex: 20,
          padding: '10px 18px',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          border: '1px solid #f59e0b',
          borderRadius: '10px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Clock size={16} color="#f59e0b" />
            <span style={{ fontSize: '12px', fontWeight: 700, color: '#fef3c7' }}>
              Spill Drift Step: Hour {spillPlaybackHour} / {spillResult.duration_hours}
            </span>
          </div>

          <button
            onClick={() => setIsSpillPlaying(!isSpillPlaying)}
            style={{
              padding: '4px 10px',
              borderRadius: 6,
              background: '#f59e0b',
              border: 'none',
              color: '#ffffff',
              fontSize: '11px',
              fontWeight: 700,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            {isSpillPlaying ? <Pause size={12} /> : <Play size={12} />}
            <span>{isSpillPlaying ? 'Pause' : 'Play 72h Drift'}</span>
          </button>

          <input
            type="range"
            min="0"
            max={spillResult.duration_hours}
            step="6"
            value={spillPlaybackHour}
            onChange={(e) => setSpillPlaybackHour(parseInt(e.target.value))}
            style={{ width: 140, accentColor: '#f59e0b' }}
          />

          <span style={{ fontSize: '11px', color: '#fde68a' }}>
            Affected Slick: {spillResult.area_km2.toFixed(1)} km²
          </span>
        </div>
      )}

      {/* Right Bottom: Dynamic Legend */}
      <Legend activeLayer={activeLayer} />

      {/* Right Sidebar: Intelligence Dashboard */}
      <SideDashboard
        ecosystemSummary={ecosystemSummary}
        seaIceData={seaIceData}
        forecastData={forecastData}
        inspectedCoordinateData={inspectedTelemetry}
        selectedRegionName={selectedEvent?.properties.title}
        onFlyToRegion={handleFlyTo}
        onSwitchIceBasin={handleSwitchIceBasin}
        currentIceBasin={currentIceBasin}
      />

      {/* Modal: 72h Lagrangian Oil Spill Drift Simulator */}
      <SpillSimulatorModal
        isOpen={isSpillModalOpen}
        onClose={() => setIsSpillModalOpen(false)}
        onSimulationSuccess={handleSimulationSuccess}
        onEnableMapPickMode={() => {
          setIsSpillModalOpen(false);
          setIsMapPickMode(true);
        }}
        pickedLat={pickedSpillLat}
        pickedLon={pickedSpillLon}
      />
    </div>
  );
}

export default App;
