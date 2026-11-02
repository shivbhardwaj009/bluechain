/**
 * BLUECHAIN Ocean Intelligence API Client
 */

const BASE_URL = import.meta.env.VITE_API_URL || '';

export interface OceanEventFeature {
  type: string;
  geometry: {
    type: string;
    coordinates: any;
  };
  properties: {
    id: number;
    event_id: string;
    type: string;
    title: string;
    severity: string;
    severity_score: number;
    start_time: string;
    end_time?: string;
    latitude: number;
    longitude: number;
    ocean_basin?: string;
    explanation: string;
    metadata?: Record<string, any>;
  };
}

export interface RiskResponse {
  hazard: string;
  time: string;
  mean_risk_score: number;
  max_risk_score: number;
  high_risk_cells_count: number;
  geojson: {
    type: string;
    features: Array<{
      type: string;
      geometry: any;
      properties: {
        region_name: string;
        ocean_basin: string;
        latitude: number;
        longitude: number;
        risk_index: number;
        severity_category: string;
        dominant_hazard: string;
        explanation: string;
        parameters: Record<string, any>;
      };
    }>;
  };
  top_risk_regions: Array<{
    region_name: string;
    ocean_basin: string;
    risk_score: number;
    dominant_hazard: string;
    latitude: number;
    longitude: number;
  }>;
}

export interface ForecastResponse {
  parameter: string;
  target_region: string;
  forecast_time: string;
  horizon_days: number;
  data_points: Array<{
    horizon_days: number;
    valid_time: string;
    predicted_value: number;
    uncertainty_lower: number;
    uncertainty_upper: number;
    baseline_value: number;
    latitude: number;
    longitude: number;
    model_version: string;
  }>;
  model_metadata: Record<string, any>;
  geojson: any;
}

export interface TimeSeriesResponse {
  parameter: string;
  unit: string;
  latitude: number;
  longitude: number;
  ocean_basin: string;
  data_points: Array<{
    time: string;
    value: number;
    parameter: string;
    unit: string;
    source: string;
    qc_flag: number;
  }>;
}

export interface SeaIceResponse {
  basin: string;
  latest_extent_million_km2: number;
  baseline_extent_million_km2: number;
  anomaly_percent: number;
  trend_description: string;
  monthly_historical: Array<{
    month: string;
    extent: number;
    baseline: number;
    anomaly: number;
  }>;
  monthly_projection: Array<{
    month: string;
    projected_extent: number;
    baseline: number;
    anomaly: number;
  }>;
}

export interface EcosystemSummaryResponse {
  overall_stress_index: number;
  mhw_bleaching_stress: number;
  algal_hypoxia_stress: number;
  acidification_stress: number;
  cyclone_hazard_stress: number;
  top_stressed_marine_ecoregions: Array<{
    region_name: string;
    ocean_basin: string;
    risk_score: number;
    dominant_hazard: string;
    latitude: number;
    longitude: number;
  }>;
}

export interface SpillSimResponse {
  simulation_id: string;
  name: string;
  origin_lat: number;
  origin_lon: number;
  volume_m3: number;
  oil_type: string;
  start_time: string;
  duration_hours: number;
  area_km2: number;
  drift_distance_km: number;
  affected_polygon: any;
  hourly_particle_tracks: Array<{
    hour: number;
    timestamp: string;
    particles: Array<{ lat: number; lon: number }>;
  }>;
  beaching_risk: string;
  status: string;
}

export const api = {
  async getEvents(type?: string, severity?: string): Promise<{ features: OceanEventFeature[]; total_count: number }> {
    const params = new URLSearchParams();
    if (type && type !== 'all') params.append('type', type);
    if (severity && severity !== 'all') params.append('severity', severity);
    const res = await fetch(`${BASE_URL}/api/events?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch ocean events');
    return res.json();
  },

  async getRiskGrid(hazard?: string): Promise<RiskResponse> {
    const params = new URLSearchParams();
    if (hazard && hazard !== 'all') params.append('hazard', hazard);
    const res = await fetch(`${BASE_URL}/api/risk?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch risk grid');
    return res.json();
  },

  async getForecast(horizon: number = 7): Promise<ForecastResponse> {
    const res = await fetch(`${BASE_URL}/api/forecast/sst?horizon=${horizon}`);
    if (!res.ok) throw new Error('Failed to fetch forecast');
    return res.json();
  },

  async getTimeSeries(parameter: string, lat: number, lon: number): Promise<TimeSeriesResponse> {
    const res = await fetch(`${BASE_URL}/api/parameters/${parameter}/timeseries?lat=${lat}&lon=${lon}`);
    if (!res.ok) throw new Error('Failed to fetch timeseries');
    return res.json();
  },

  async getSeaIce(basin: string = 'arctic'): Promise<SeaIceResponse> {
    const res = await fetch(`${BASE_URL}/api/ice/extent?basin=${basin}`);
    if (!res.ok) throw new Error('Failed to fetch sea ice data');
    return res.json();
  },

  async getEcosystemSummary(): Promise<EcosystemSummaryResponse> {
    const res = await fetch(`${BASE_URL}/api/risk/ecosystem-summary`);
    if (!res.ok) throw new Error('Failed to fetch ecosystem summary');
    return res.json();
  },

  async simulateSpill(payload: {
    latitude: number;
    longitude: number;
    volume_m3: number;
    oil_type?: string;
    duration_hours?: number;
    particle_count?: number;
  }): Promise<SpillSimResponse> {
    const res = await fetch(`${BASE_URL}/api/spill/simulate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to simulate spill');
    }
    return res.json();
  },

  async triggerIngest(source: string = 'all'): Promise<any> {
    const res = await fetch(`${BASE_URL}/api/ingest/${source}`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to trigger ingestion');
    return res.json();
  }
};
