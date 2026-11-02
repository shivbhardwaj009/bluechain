import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import type { OceanEventFeature, RiskResponse, SpillSimResponse } from '../api/client';
import type { OceanLayer } from '../components/LayerControl';

interface OceanMapProps {
  events: OceanEventFeature[];
  riskData: RiskResponse | null;
  activeLayer: OceanLayer;
  spillResult: SpillSimResponse | null;
  showSpillLayer: boolean;
  onMapClickCoordinate?: (lat: number, lon: number) => void;
  onSelectEvent: (event: OceanEventFeature) => void;
  mapRefExternal?: React.MutableRefObject<maplibregl.Map | null>;
}

export const OceanMap: React.FC<OceanMapProps> = ({
  events,
  riskData,
  activeLayer,
  spillResult,
  showSpillLayer,
  onMapClickCoordinate,
  onSelectEvent,
  mapRefExternal
}) => {
  const mapContainer = useRef<HTMLDivElement>(null);
  const map = useRef<maplibregl.Map | null>(null);
  const markersRef = useRef<maplibregl.Marker[]>([]);

  // Initialize MapLibre
  useEffect(() => {
    if (!mapContainer.current || map.current) return;

    // Dark deep-ocean base style using free open carto tiles
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
          attribution: '&copy; <a href="https://carto.com/">CARTO</a> &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
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
      center: [20.0, 10.0],
      zoom: 2.2,
      maxZoom: 12,
      minZoom: 1.5
    });

    mapInstance.addControl(new maplibregl.NavigationControl({ showCompass: true }), 'top-right');

    mapInstance.on('load', () => {
      // 1. Source for Gridded Ocean Risk polygons
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
            40, 'rgba(56, 189, 248, 0.4)',
            65, 'rgba(245, 158, 11, 0.55)',
            85, 'rgba(239, 68, 68, 0.7)'
          ],
          'fill-outline-color': 'rgba(56, 189, 248, 0.6)'
        }
      });

      // 2. Source for Oil Spill affected area polygon
      mapInstance.addSource('spill-affected-polygon', {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] }
      });

      mapInstance.addLayer({
        id: 'spill-affected-fill',
        type: 'fill',
        source: 'spill-affected-polygon',
        paint: {
          'fill-color': 'rgba(245, 158, 11, 0.45)',
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
          'circle-radius': 4.5,
          'circle-color': '#fde047',
          'circle-stroke-width': 1.5,
          'circle-stroke-color': '#b45309'
        }
      });
    });

    // Map click handler
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

  // Update Gridded Risk Overlay
  useEffect(() => {
    if (!map.current || !map.current.isStyleLoaded()) return;
    const source = map.current.getSource('ocean-risk-grid') as maplibregl.GeoJSONSource;
    if (source && riskData?.geojson) {
      source.setData(riskData.geojson as any);
    }
  }, [riskData]);

  // Update Oil Spill Drift Polygon & Particles
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
        // Collect latest particle positions
        const latestStep = spillResult.hourly_particle_tracks[spillResult.hourly_particle_tracks.length - 1];
        const ptFeatures = latestStep.particles.map((p, idx) => ({
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
  }, [spillResult, showSpillLayer]);

  // Update Event Markers & Click Popups
  useEffect(() => {
    if (!map.current) return;

    // Clear existing markers
    markersRef.current.forEach(m => m.remove());
    markersRef.current = [];

    events.forEach(ev => {
      const props = ev.properties;
      const coords = [props.longitude, props.latitude] as [number, number];

      // Custom marker DOM element
      const el = document.createElement('div');
      el.className = 'ocean-event-marker';
      el.style.width = '24px';
      el.style.height = '24px';
      el.style.borderRadius = '50%';
      el.style.cursor = 'pointer';
      el.style.display = 'flex';
      el.style.alignItems = 'center';
      el.style.justifyContent = 'center';
      el.style.boxShadow = '0 0 12px rgba(0,0,0,0.8)';
      el.style.border = '2px solid #ffffff';

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

      const popupHtml = `
        <div style="font-family: var(--font-main); line-height: 1.4;">
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
