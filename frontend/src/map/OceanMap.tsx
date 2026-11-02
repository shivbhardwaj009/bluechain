import React, { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import type { OceanEventFeature, RiskResponse, SpillSimResponse, ForecastResponse } from '../api/client';
import type { OceanLayer } from '../components/LayerControl';

interface OceanMapProps {
  events: OceanEventFeature[];
  riskData: RiskResponse | null;
  forecastData: ForecastResponse | null;
  activeLayer: OceanLayer;
  spillResult: SpillSimResponse | null;
  showSpillLayer: boolean;
  spillPlaybackHour: number;
  isForecastTimeStep: boolean;
  onMapClickCoordinate?: (lat: number, lon: number) => void;
  onSelectEvent: (event: OceanEventFeature) => void;
  mapRefExternal?: React.MutableRefObject<maplibregl.Map | null>;
}

export const OceanMap: React.FC<OceanMapProps> = ({
  events,
  riskData,
  forecastData,
  activeLayer,
  spillResult,
  showSpillLayer,
  spillPlaybackHour,
  isForecastTimeStep,
  onMapClickCoordinate,
  onSelectEvent,
  mapRefExternal
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);
  const forecastMarkersRef = useRef<maplibregl.Marker[]>([]);

  // Initialize MapLibre GL
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    const darkOceanStyle: maplibregl.StyleSpecification = {
      version: 8,
      sources: {
        'carto-dark': {
          type: 'raster',
          tiles: [
            'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png',
            'https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png',
            'https://c.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png'
          ],
          tileSize: 256,
          attribution: '&copy; CARTO &copy; OpenStreetMap contributors'
        }
      },
      layers: [
        {
          id: 'carto-dark-layer',
          type: 'raster',
          source: 'carto-dark',
          minzoom: 0,
          maxzoom: 18
        }
      ]
    };

    const mapInstance = new maplibregl.Map({
      container: mapContainer.current,
      style: darkOceanStyle,
      center: [20.0, 15.0],
      zoom: 2.1,
      maxZoom: 12,
      minZoom: 1.5
    });

    mapInstance.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-right');
    mapInstance.addControl(new maplibregl.ScaleControl({ unit: 'metric' }), 'bottom-left');

    mapInstance.on('load', () => {
      // 1. Source for Gridded Ocean Risk Polygons
      mapInstance.addSource('ocean-risk-grid', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] }
      });

      mapInstance.addLayer({
        id: 'ocean-risk-grid-fill',
        type: 'fill',
        source: 'ocean-risk-grid',
        paint: {
          'fill-color': [
            'interpolate',
            ['linear'],
            ['get', 'risk_index'],
            0, 'rgba(16, 185, 129, 0.25)',
            35, 'rgba(56, 189, 248, 0.40)',
            65, 'rgba(245, 158, 11, 0.55)',
            80, 'rgba(239, 68, 68, 0.70)'
          ],
          'fill-outline-color': 'rgba(56, 189, 248, 0.75)'
        }
      });

      // 2. Source for Oil Spill affected polygon
      mapInstance.addSource('spill-affected-polygon', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] }
      });

      mapInstance.addLayer({
        id: 'spill-affected-fill',
        type: 'fill',
        source: 'spill-affected-polygon',
        paint: {
          'fill-color': 'rgba(245, 158, 11, 0.40)',
          'fill-outline-color': '#f59e0b'
        }
      });

      // 3. Source for Oil Spill Lagrangian drift particles
      mapInstance.addSource('spill-particles', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] }
      });

      mapInstance.addLayer({
        id: 'spill-particles-circle',
        type: 'circle',
        source: 'spill-particles',
        paint: {
          'circle-radius': 5.0,
          'circle-color': '#fbbf24',
          'circle-stroke-width': 1.5,
          'circle-stroke-color': '#78350f'
        }
      });
    });

    mapInstance.on('click', (e) => {
      if (onMapClickCoordinate) {
        onMapClickCoordinate(e.lngLat.lat, e.lngLat.lng);
      }
    });

    map.current = mapInstance;
    if (mapRefExternal) {
      mapRefExternal.current = mapInstance;
    }

    return () => {
      mapInstance.remove();
      map.current = null;
    };
  }, []);

  // Dynamic Layer Color Updates
  useEffect(() => {
    if (!map.current || !map.current.isStyleLoaded()) return;

    if (map.current.getLayer('ocean-risk-grid-fill')) {
      if (activeLayer === 'anomaly') {
        map.current.setPaintProperty('ocean-risk-grid-fill', 'fill-color', [
          'interpolate',
          ['linear'],
          ['get', 'risk_index'],
          0, 'rgba(37, 99, 235, 0.25)',
          30, 'rgba(56, 189, 248, 0.45)',
          60, 'rgba(245, 158, 11, 0.65)',
          80, 'rgba(239, 68, 68, 0.85)'
        ]);
      } else if (activeLayer === 'chlorophyll') {
        map.current.setPaintProperty('ocean-risk-grid-fill', 'fill-color', [
          'interpolate',
          ['linear'],
          ['get', 'risk_index'],
          0, 'rgba(5, 150, 105, 0.2)',
          40, 'rgba(16, 185, 129, 0.4)',
          70, 'rgba(52, 211, 153, 0.6)',
          85, 'rgba(234, 179, 8, 0.75)'
        ]);
      } else {
        // Standard Ocean Risk Index (0-100)
        map.current.setPaintProperty('ocean-risk-grid-fill', 'fill-color', [
          'interpolate',
          ['linear'],
          ['get', 'risk_index'],
          0, 'rgba(16, 185, 129, 0.25)',
          35, 'rgba(56, 189, 248, 0.40)',
          65, 'rgba(245, 158, 11, 0.55)',
          80, 'rgba(239, 68, 68, 0.70)'
        ]);
      }
    }
  }, [activeLayer]);

  // Update Gridded Risk Grid data
  useEffect(() => {
    if (!map.current || !map.current.isStyleLoaded()) return;
    const source = map.current.getSource('ocean-risk-grid') as maplibregl.GeoJSONSource;
    if (source && riskData?.geojson) {
      source.setData(riskData.geojson as any);
    }
  }, [riskData]);

  // Update Oil Spill Trajectory & Hourly Particle Tracks
  useEffect(() => {
    if (!map.current || !map.current.isStyleLoaded()) return;

    const polySource = map.current.getSource('spill-affected-polygon') as maplibregl.GeoJSONSource;
    const ptSource = map.current.getSource('spill-particles') as maplibregl.GeoJSONSource;

    if (showSpillLayer && spillResult) {
      if (polySource && spillResult.affected_polygon) {
        polySource.setData({
          type: 'Feature',
          geometry: spillResult.affected_polygon,
          properties: { name: spillResult.name, area: spillResult.area_km2 }
        } as any);
      }

      if (ptSource && spillResult.hourly_particle_tracks?.length) {
        // Find closest snapshot to current playback hour
        let targetSnap = spillResult.hourly_particle_tracks[0];
        for (const snap of spillResult.hourly_particle_tracks) {
          if (snap.hour <= spillPlaybackHour) {
            targetSnap = snap;
          }
        }

        const ptFeatures = targetSnap.particles.map((p, idx) => ({
          type: 'Feature',
          geometry: { type: 'Point', coordinates: [p.lon, p.lat] },
          properties: { id: idx }
        }));
        ptSource.setData({ type: 'FeatureCollection', features: ptFeatures } as any);
      }
    } else {
      if (polySource) polySource.setData({ type: 'FeatureCollection', features: [] });
      if (ptSource) ptSource.setData({ type: 'FeatureCollection', features: [] });
    }
  }, [spillResult, showSpillLayer, spillPlaybackHour]);

  // Forecast Anomaly Markers when in Forecast Mode
  useEffect(() => {
    if (!map.current) return;

    forecastMarkersRef.current.forEach(m => m.remove());
    forecastMarkersRef.current = [];

    if (isForecastTimeStep && forecastData?.data_points) {
      forecastData.data_points.forEach(fp => {
        const el = document.createElement('div');
        el.className = 'forecast-marker';
        el.style.padding = '4px 8px';
        el.style.borderRadius = '6px';
        el.style.background = 'rgba(99, 102, 241, 0.9)';
        el.style.border = '1px solid #c7d2fe';
        el.style.color = '#ffffff';
        el.style.fontSize = '11px';
        el.style.fontWeight = '700';
        el.style.boxShadow = '0 0 10px rgba(99, 102, 241, 0.6)';
        el.style.cursor = 'pointer';
        el.innerHTML = `🔮 +${fp.predicted_value.toFixed(1)}°C`;

        const popup = new maplibregl.Popup({ offset: 12 }).setHTML(`
          <div style="font-family: var(--font-main); padding: 4px;">
            <strong style="color: #c7d2fe; font-size: 13px;">ML Model SST Projection</strong>
            <div style="font-size: 11px; color: #94a3b8; margin: 4px 0;">Horizon: +${fp.horizon_days} Days</div>
            <div style="font-size: 12px; margin-bottom: 4px;">Predicted Anomaly: <strong style="color: #38bdf8;">+${fp.predicted_value.toFixed(2)}°C</strong></div>
            <div style="font-size: 11px; color: #cbd5e1;">Uncertainty (95% CI): [${fp.uncertainty_lower?.toFixed(2)}°C, ${fp.uncertainty_upper?.toFixed(2)}°C]</div>
            <div style="font-size: 10px; color: #94a3b8; margin-top: 4px;">Persistence Baseline: +${fp.baseline_value?.toFixed(2)}°C</div>
          </div>
        `);

        const marker = new maplibregl.Marker({ element: el })
          .setLngLat([fp.longitude, fp.latitude])
          .setPopup(popup)
          .addTo(map.current!);

        forecastMarkersRef.current.push(marker);
      });
    }
  }, [isForecastTimeStep, forecastData]);

  // Update Event Markers
  useEffect(() => {
    if (!map.current) return;

    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];

    events.forEach(ev => {
      const props = ev.properties;
      const coords = [props.longitude, props.latitude] as [number, number];

      const el = document.createElement('div');
      el.className = 'ocean-event-marker';
      el.style.width = '26px';
      el.style.height = '26px';
      el.style.borderRadius = '50%';
      el.style.cursor = 'pointer';
      el.style.display = 'flex';
      el.style.alignItems = 'center';
      el.style.justifyContent = 'center';
      el.style.boxShadow = '0 0 15px rgba(0,0,0,0.8)';
      el.style.border = '2px solid #ffffff';
      el.style.transition = 'transform 0.15s ease';

      if (props.type === 'marine_heatwave') {
        el.style.backgroundColor = '#f97316';
        el.innerHTML = '🔥';
      } else if (props.type === 'earthquake') {
        el.style.backgroundColor = '#ef4444';
        el.innerHTML = '🌊';
      } else if (props.type === 'cyclone') {
        el.style.backgroundColor = '#38bdf8';
        el.innerHTML = '🌀';
      } else if (props.type === 'algal_bloom') {
        el.style.backgroundColor = '#10b981';
        el.innerHTML = '🦠';
      } else {
        el.style.backgroundColor = '#06b6d4';
        el.innerHTML = '❄️';
      }

      el.addEventListener('mouseenter', () => (el.style.transform = 'scale(1.2)'));
      el.addEventListener('mouseleave', () => (el.style.transform = 'scale(1.0)'));

      const popupHtml = `
        <div style="font-family: var(--font-main); line-height: 1.45;">
          <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
            <strong style="color: #ffffff; font-size: 13px;">${props.title}</strong>
            <span style="font-size: 10px; font-weight: 700; color: #f59e0b; background: rgba(245,158,11,0.2); padding: 1px 6px; border-radius: 4px;">
              ${props.severity}
            </span>
          </div>
          <div style="font-size: 11px; color: #94a3b8; margin-bottom: 6px;">
            ${props.ocean_basin || 'Pelagic Ocean'} • ${new Date(props.start_time).toLocaleDateString()}
          </div>
          <p style="font-size: 11px; color: #cbd5e1; margin-bottom: 8px;">
            ${props.explanation}
          </p>
          <div style="font-size: 10px; color: #38bdf8; font-weight: 600;">
            CLICK TO INSPECT BASIN TELEMETRY
          </div>
        </div>
      `;

      const popup = new maplibregl.Popup({ offset: 15 }).setHTML(popupHtml);

      el.addEventListener('click', () => {
        onSelectEvent(ev);
      });

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat(coords)
        .setPopup(popup)
        .addTo(map.current!);

      markersRef.current.push(marker);
    });
  }, [events]);

  return (
    <div
      ref={mapContainer}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: '#050b14'
      }}
    />
  );
};
