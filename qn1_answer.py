#import necessary libraries for computations and calculations
import numpy as np
from skyfield.api import load, EarthSatellite
from datetime import datetime, timedelta

#Tracker's TLE below is found out using the orbital parameters given in the Question number 1
epoch = datetime(2023, 3, 21, 0, 0, 0)
tle_line1 = f"1 00000U 00000A   {epoch.strftime('%y%j.00000000')}  .00000000  00000-0  00000-0 0  9991"
tle_line2 = f"2 00000 097.4000 269.8035 0000000 331.7425 000.0000 15.00000000    00"

# Space object's TLE (given directly in the question)
object_tle_line1 = "1 03386U 65082MY  23081.95345837  .00004143  00000-0  45959-3 0  9996"
object_tle_line2 = "2 03386  32.3737 289.5919 0008599 302.6285  57.3541 14.86044732 69107"

# Loading the timescale and creating a satellite object
ts = load.timescale()
tracker_sat = EarthSatellite(tle_line1, tle_line2, 'Tracker', ts)
object_sat = EarthSatellite(object_tle_line1, object_tle_line2, 'Object', ts)
eph = load('de421.bsp')

# Defining the field of view and visibility parameters
fov_angle = 30.0  # degrees
max_distance = 1000.0  # km

# Defining the time range for the analysis
t0 = ts.utc(epoch.year, epoch.month, epoch.day, epoch.hour, epoch.minute, epoch.second)
t1 = t0 + timedelta(days=1)
times = ts.linspace(t0, t1, num=1440)  # 1-minute intervals

# Function to check if a space object is in the field of view
def in_field_of_view(observer_pos, object_pos, fov_angle):
    angle = np.degrees(np.arccos(np.dot(observer_pos, object_pos) /
                                 (np.linalg.norm(observer_pos) * np.linalg.norm(object_pos))))
    return angle <= fov_angle / 2.0

# Function to check if a space object is within the distance limit
def within_distance(observer_pos, object_pos, max_distance):
    distance = np.linalg.norm(observer_pos - object_pos)
    return distance <= max_distance

# Function to check if a space object is sunlit. is_sunlit is an inbuilt function to check if object is sunlit or not
def is_sunlit(time, satellite):
    sunlit = satellite.at(time).is_sunlit(eph)   
    return sunlit

crossing_events = []
visible_events = []

# Check for crossings and visibility
for t in times:
    tracker_geocentric = tracker_sat.at(t)
    object_geocentric = object_sat.at(t)
    
    observer_pos = tracker_geocentric.position.km
    object_pos = object_geocentric.position.km
    
    if in_field_of_view(observer_pos, object_pos, fov_angle):
        crossing_events.append(t)
        if within_distance(observer_pos, object_pos, max_distance) and is_sunlit(t, tracker_sat):
            visible_events.append(t)

# Print crossing events
if crossing_events:
    print("Crossing events:")
    for t in crossing_events:
        print(f"Time: {t.utc_iso()}")
else:
    print("No crossing events found.")

# Print visible events
if visible_events:
    print("Visible events:")
    for t in visible_events:
        print(f"Time: {t.utc_iso()}")
else:
    print("No visible events found.")
