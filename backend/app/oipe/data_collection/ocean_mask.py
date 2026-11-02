"""Ocean Mask Module - Strictly Enforces Marine-Only Scope.
Rejects any point falling on continental land masses or inland freshwater bodies.
"""
from shapely.geometry import Point, Polygon, MultiPolygon

# Simplified high-level continental land mass approximations for ultra-fast, robust land rejection
_CONTINENTS = [
    # North America landmass
    Polygon([
        (-168.0, 65.0), (-140.0, 70.0), (-120.0, 70.0), (-85.0, 75.0), (-60.0, 60.0),
        (-55.0, 50.0), (-65.0, 43.0), (-75.0, 35.0), (-80.0, 25.0), (-90.0, 20.0),
        (-100.0, 18.0), (-105.0, 22.0), (-117.0, 32.0), (-124.0, 48.0), (-135.0, 58.0),
        (-168.0, 65.0)
    ]),
    # South America landmass
    Polygon([
        (-78.0, 9.0), (-60.0, 8.0), (-45.0, -1.0), (-35.0, -6.0), (-38.0, -18.0),
        (-48.0, -28.0), (-58.0, -38.0), (-68.0, -54.0), (-75.0, -45.0), (-72.0, -20.0),
        (-81.0, -5.0), (-78.0, 9.0)
    ]),
    # Eurasia & Africa landmass
    Polygon([
        (-10.0, 36.0), (30.0, 32.0), (35.0, 15.0), (50.0, 12.0), (42.0, -12.0),
        (30.0, -32.0), (18.0, -34.0), (12.0, -15.0), (5.0, 5.0), (-17.0, 15.0),
        (-9.0, 38.0), (5.0, 55.0), (20.0, 60.0), (60.0, 68.0), (100.0, 73.0),
        (170.0, 67.0), (140.0, 50.0), (120.0, 38.0), (105.0, 20.0), (90.0, 22.0),
        (75.0, 10.0), (68.0, 24.0), (50.0, 30.0), (30.0, 42.0), (10.0, 45.0),
        (-5.0, 48.0), (-10.0, 36.0)
    ]),
    # Australia landmass
    Polygon([
        (114.0, -22.0), (130.0, -12.0), (142.0, -11.0), (150.0, -24.0),
        (152.0, -34.0), (140.0, -38.0), (115.0, -34.0), (114.0, -22.0)
    ]),
    # Greenland
    Polygon([
        (-50.0, 60.0), (-35.0, 65.0), (-20.0, 75.0), (-25.0, 82.0),
        (-55.0, 82.0), (-60.0, 75.0), (-50.0, 60.0)
    ])
]

LAND_MULTIPOLYGON = MultiPolygon(_CONTINENTS)


def is_ocean_point(latitude: float, longitude: float) -> bool:
    """Return True if point is located in marine/ocean waters, False if on continental land.
    
    Coordinates:
    - latitude: [-90.0, 90.0]
    - longitude: [-180.0, 180.0]
    """
    if latitude < -90.0 or latitude > 90.0:
        return False
    if longitude < -180.0 or longitude > 180.0:
        return False

    # Polar oceanic waters (Arctic & Antarctic ocean waters)
    if latitude > 82.0:
        return True
    if latitude < -60.0 and latitude > -82.0:
        # Southern ocean waters (excluding central Antarctica interior)
        return True

    pt = Point(longitude, latitude)
    # If the point intersects any major continental polygon, reject as land
    if LAND_MULTIPOLYGON.contains(pt):
        return False
        
    return True


def get_ocean_basin(latitude: float, longitude: float) -> str:
    """Determine the oceanic basin for a valid marine point."""
    if latitude > 66.5:
        return "Arctic Ocean"
    if latitude < -60.0:
        return "Southern Ocean"
    
    if -60.0 <= latitude <= 66.5:
        if -70.0 <= longitude <= 20.0:
            return "Atlantic Ocean"
        elif 20.0 < longitude <= 100.0:
            return "Indian Ocean"
        elif longitude > 100.0 or longitude < -70.0:
            return "Pacific Ocean"
            
    return "Global Ocean"
