from geopy.geocoders import Nominatim
import time
geolocator = Nominatim(user_agent="Geo")
with open('location_name.txt', 'r', encoding='utf-8') as f:
    final = []
    for i, p in enumerate(f):
        temp = geolocator.geocode(p)
        final.append(temp)
        print(i)
        time.sleep(0.5)