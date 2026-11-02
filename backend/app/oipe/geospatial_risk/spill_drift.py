"""Lagrangian Marine Oil Spill Drift Simulator (72-Hour Horizon).
Implements particle advection and turbulent diffusion in marine surface waters:
1. Advection by surface ocean current vectors (u_curr, v_curr).
2. Windage drift: 3.0% of 10-meter surface marine wind vector (u_wind, v_wind).
3. Horizontal turbulent random-walk diffusion (Monte Carlo Brownian motion).
4. Spatial boundary validation (strictly marine waters).
5. Convex hull envelope and affected polygon generation via Shapely.
"""
import math
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple, Optional
from shapely.geometry import Point, MultiPoint, Polygon, mapping

from backend.app.oipe.data_collection.ocean_mask import is_ocean_point, get_ocean_basin


class LagrangianSpillSimulator:
    """Simulates 72-hour oil spill trajectory, weathering spread, and affected marine area."""

    # Earth radius in meters
    EARTH_RADIUS = 6371000.0

    @classmethod
    def simulate_spill(
        cls,
        origin_lat: float,
        origin_lon: float,
        volume_m3: float,
        start_time: Optional[datetime] = None,
        duration_hours: int = 72,
        particle_count: int = 120,
        oil_type: str = "Medium Crude",
        surface_current_u: float = 0.22,  # m/s eastward
        surface_current_v: float = -0.15, # m/s northward
        wind_speed_ms: float = 8.5,       # m/s
        wind_direction_deg: float = 230.0 # meteorological direction from SW
    ) -> Dict[str, Any]:
        """Run Lagrangian particle tracking over specified duration.
        
        Args:
            origin_lat: Release latitude
            origin_lon: Release longitude
            volume_m3: Spill volume in m3
            start_time: Simulation commencement time
            duration_hours: Horizon in hours (standard 72h)
            particle_count: Number of Lagrangian parcels
            oil_type: Type of petroleum product
            surface_current_u: East-west ocean velocity (m/s)
            surface_current_v: North-south ocean velocity (m/s)
            wind_speed_ms: Surface wind velocity (m/s)
            wind_direction_deg: Meteorological wind direction
        """
        if start_time is None:
            start_time = datetime.utcnow()

        # Enforce marine origin
        if not is_ocean_point(origin_lat, origin_lon):
            raise ValueError(f"Spill origin ({origin_lat}, {origin_lon}) is on land. Strictly marine scope enforced.")

        # Wind velocity components (wind blowing towards direction: dir + 180)
        wind_rad = math.radians((wind_direction_deg + 180.0) % 360.0)
        # 3% windage rule of thumb (standard oceanographic oil drift rule)
        wind_drift_factor = 0.03
        u_wind_drift = wind_speed_ms * wind_drift_factor * math.sin(wind_rad)
        v_wind_drift = wind_speed_ms * wind_drift_factor * math.cos(wind_rad)

        # Total deterministic advective velocity (m/s)
        u_total = surface_current_u + u_wind_drift
        v_total = surface_current_v + v_wind_drift

        dt_seconds = 3600.0  # 1 hour timestep
        diffusivity = 8.0   # Horizontal turbulent eddy diffusivity (m2/s)
        # Standard deviation of turbulent displacement in 1 hour: sqrt(2 * D * dt)
        sigma_diffusion = math.sqrt(2.0 * diffusivity * dt_seconds)

        # Initialize particles at origin with small initial release spread
        particles = []
        for i in range(particle_count):
            particles.append({
                "id": i,
                "lat": origin_lat + random.gauss(0, 0.002),
                "lon": origin_lon + random.gauss(0, 0.002)
            })

        hourly_snapshots = []
        all_final_points = []
        max_drift_km = 0.0

        # Initial snapshot (t = 0)
        hourly_snapshots.append({
            "hour": 0,
            "timestamp": start_time.isoformat(),
            "particles": [{"lat": round(p["lat"], 5), "lon": round(p["lon"], 5)} for p in particles[:40]]
        })

        current_time = start_time
        for h in range(1, duration_hours + 1):
            current_time += timedelta(hours=1)
            active_step_particles = []

            for p in particles:
                # Stochastic displacement in meters
                dx_turb = random.gauss(0, sigma_diffusion)
                dy_turb = random.gauss(0, sigma_diffusion)

                dx_total = u_total * dt_seconds + dx_turb
                dy_total = v_total * dt_seconds + dy_turb

                # Convert meter displacement to delta latitude & delta longitude
                dlat = (dy_total / cls.EARTH_RADIUS) * (180.0 / math.pi)
                lat_rad = math.radians(p["lat"])
                cos_lat = max(0.01, math.cos(lat_rad))
                dlon = (dx_total / (cls.EARTH_RADIUS * cos_lat)) * (180.0 / math.pi)

                new_lat = p["lat"] + dlat
                new_lon = p["lon"] + dlon

                # Ensure particles stay within plausible bounds
                new_lat = max(-89.0, min(89.0, new_lat))
                new_lon = (new_lon + 180.0) % 360.0 - 180.0

                p["lat"] = new_lat
                p["lon"] = new_lon
                active_step_particles.append({"lat": round(new_lat, 5), "lon": round(new_lon, 5)})

            # Sample every 6 hours or final hour to keep response crisp
            if h % 6 == 0 or h == duration_hours:
                hourly_snapshots.append({
                    "hour": h,
                    "timestamp": current_time.isoformat(),
                    "particles": active_step_particles[:40]  # Representative subset for frontend performance
                })

            if h == duration_hours:
                all_final_points = [Point(p["lon"], p["lat"]) for p in particles]

        # Calculate affected polygon via convex hull of all particles
        multi_pt = MultiPoint(all_final_points)
        hull = multi_pt.convex_hull

        # Buffer the hull slightly based on volume spread (Fay's gravity-viscous regime)
        # 1000 m3 ~ 1-2 km slick radius
        buffer_deg = 0.02 + min(0.15, (volume_m3 / 10000.0) * 0.05)
        slick_polygon = hull.buffer(buffer_deg)
        geojson_polygon = mapping(slick_polygon)

        # Estimate affected area in km2
        # 1 deg lat ~ 111 km
        lat_scale = 111.0
        lon_scale = 111.0 * math.cos(math.radians(origin_lat))
        approx_area_km2 = slick_polygon.area * lat_scale * lon_scale

        # Drift distance from origin to center of mass
        centroid = slick_polygon.centroid
        dist_km = math.sqrt(
            ((centroid.y - origin_lat) * lat_scale) ** 2 +
            ((centroid.x - origin_lon) * lon_scale) ** 2
        )

        sim_id = f"sim_{abs(int(origin_lat*100))}_{abs(int(origin_lon*100))}_{datetime.utcnow().strftime('%Y%m%d%H%M')}"
        basin = get_ocean_basin(origin_lat, origin_lon)

        return {
            "simulation_id": sim_id,
            "name": f"Lagrangian 72h Spill Drift ({basin})",
            "origin_lat": origin_lat,
            "origin_lon": origin_lon,
            "volume_m3": volume_m3,
            "oil_type": oil_type,
            "start_time": start_time,
            "duration_hours": duration_hours,
            "area_km2": round(approx_area_km2, 2),
            "drift_distance_km": round(dist_km, 2),
            "affected_polygon": geojson_polygon,
            "hourly_particle_tracks": hourly_snapshots,
            "beaching_risk": "Low (Offshore Open Pelagic)" if is_ocean_point(centroid.y, centroid.x) else "High Shoreline Interception",
            "status": "COMPLETED"
        }
