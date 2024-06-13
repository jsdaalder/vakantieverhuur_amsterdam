import geopandas as gpd
import pandas as pd
from geopy.geocoders import Nominatim
from shapely.geometry import Point
import time

# Load the GeoJSON file into a GeoPandas DataFrame
geojson_path = 'geojson_corporatiewoningen.json'  # Replace with your file path
social_houses_gdf = gpd.read_file(geojson_path)

# Project to a suitable CRS for centroid calculation (e.g., UTM zone for Amsterdam)
social_houses_gdf = social_houses_gdf.to_crs(epsg=32633)  # EPSG:32633 is UTM zone 33N, suitable for Amsterdam

# Calculate the centroid for each polygon
social_houses_gdf['centroid'] = social_houses_gdf.geometry.centroid

# Project back to geographic coordinates (EPSG:4326)
social_houses_gdf = social_houses_gdf.to_crs(epsg=4326)

# Create a GeoDataFrame from the centroids
centroids_gdf = gpd.GeoDataFrame(geometry=social_houses_gdf['centroid'])

# Load the addresses data
addresses_df = pd.read_csv('amsterdam_vergunningen.csv')  # Adjust the path as needed

# Ask user for the number of addresses to process
num_addresses = int(input("Enter the number of addresses to analyze: "))
addresses_df = addresses_df.head(num_addresses)

# Function to geocode address with rate limiting
def geocode_with_delay(address):
    time.sleep(1)  # Delay for 1 second between requests
    geolocator = Nominatim(user_agent="your_specific_user_agent")  # Replace with a specific User-Agent
    location = geolocator.geocode(address)
    return Point(location.longitude, location.latitude) if location else None

# Geocode addresses
addresses_df['geometry'] = addresses_df['address'].apply(geocode_with_delay)
addresses_gdf = gpd.GeoDataFrame(addresses_df, geometry='geometry', crs='EPSG:4326')

# Ensure both GeoDataFrames are in the same CRS before the spatial join
addresses_gdf = addresses_gdf.to_crs(centroids_gdf.crs)

# Spatial join - find which addresses are within/close to the social houses
matched_gdf = gpd.sjoin(addresses_gdf, centroids_gdf, how="left", predicate='intersects')

# Add new columns to the original addresses_df
addresses_df['corporatiewoning'] = 'no'
addresses_df.loc[matched_gdf.index, 'corporatiewoning'] = 'yes'

# Extract latitudes and longitudes from the matched_gdf geometry
addresses_df.loc[matched_gdf.index, 'lat'] = matched_gdf.geometry.y
addresses_df.loc[matched_gdf.index, 'long'] = matched_gdf.geometry.x

# Fill NaNs for lat and long with empty strings if no match was found
addresses_df['lat'] = addresses_df['lat'].fillna('')
addresses_df['long'] = addresses_df['long'].fillna('')

# Save the updated DataFrame to a new CSV file
addresses_df.to_csv('corporatiewoningen_met_vergunning.csv', index=False)
