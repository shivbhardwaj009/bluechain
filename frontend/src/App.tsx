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
  SpillSimResponse
} from './api/client';

export function App() {
  const [events, setEvents] = useState<OceanEventFeature[]>([]);
  const [riskData, setRiskData] = useState<RiskResponse | null>(null);
  const [ecosystemSummary, setEcosystemSummary] = useState<EcosystemSummaryResponse | null>(null);
  const [seaIceData, setSeaIceData] = useState<SeaIceResponse | null>(null);
  const [forecastData, setForecastData] = useState<ForecastResponse | null>(null);
  const [spillResult, setSpillResult] = useState<SpillSimResponse | null>(null);

  const [activeLayer, setActiveLayer] = useState<OceanLayer>('risk_grid');
  const [timeStepIndex, setTimeStepIndex] = useState<number>(3); // Default 'Now'
  const [selectedEvent, setSelectedEvent] = useState<OceanEventFeature | null>(null);
  const [isSpillModalOpen, setIsSpillModalOpen] = useState(false);
  const [showSpillLayer, setShowSpillLayer] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const [eventFilters, setEventFilters] = useState({
    heatwaves: true,
    earthquakes: true,
    cyclones: true,
    blooms: true
  });

  const mapRef = useRef<maplibregl.Map | null>(null);

  // Load initial ocean datasets
  const loadData = async () => {
    try {
      setIsRefreshing(true);
      const [eventsRes, riskRes, ecoRes, iceRes, fcastRes] = await Promise.all([
        api.getEvents(),
        api.getRiskGrid(),
        api.getEcosystemSummary(),
        api.getSeaIce('arctic'),
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
    handleFlyTo(sim.origin_lat, sim.origin_lon, 5.0);
  };

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh', overflow: 'hidden' }}>
      {/* Top Header */}
      <Header
        onOpenSpillModal={() => setIsSpillModalOpen(true)}
        onRefreshData={loadData}
        isRefreshing={isRefreshing}
      />

      {/* Full-Screen MapLibre Map */}
      <OceanMap
        events={filteredEvents}
        riskData={riskData}
        activeLayer={activeLayer}
        spillResult={spillResult}
        showSpillLayer={showSpillLayer}
        onSelectEvent={handleSelectEvent}
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

      {/* Right Bottom: Dynamic Legend */}
      <Legend activeLayer={activeLayer} />

      {/* Right Sidebar: Intelligence Dashboard (Recharts + Top Regions) */}
      <SideDashboard
        ecosystemSummary={ecosystemSummary}
        seaIceData={seaIceData}
        forecastData={forecastData}
        selectedRegionName={selectedEvent?.properties.title}
        onFlyToRegion={handleFlyTo}
      />

      {/* Modal: 72h Lagrangian Oil Spill Drift Simulator */}
      <SpillSimulatorModal
        isOpen={isSpillModalOpen}
        onClose={() => setIsSpillModalOpen(false)}
        onSimulationSuccess={handleSimulationSuccess}
      />
    </div>
  );
}

export default App;
