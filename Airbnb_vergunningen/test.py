import pandas as pd
import os
from geopy.geocoders import Nominatim
from functools import partial
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="my_geocoder", timeout=10)
print(geocode("paris", language="en"))