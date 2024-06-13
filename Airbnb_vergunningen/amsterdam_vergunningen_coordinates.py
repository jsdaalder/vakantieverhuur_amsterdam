import pandas as pd
import os
import time
from geopy.geocoders import Nominatim

# Load the original CSV
print("Loading the original CSV...")
df = pd.read_csv('vergunningenscraper_output.csv')
print("Successfully loaded original CSV.")

# Filter for Amsterdam municipality
print("Filtering for Amsterdam municipality...")
df_amsterdam = df[df['municipality'] == "Amsterdam"]
print("Successfully filtered for Amsterdam.")

# Keep only the relevant columns
print("Keeping only relevant columns...")
df_amsterdam = df_amsterdam[['unique_id', 'date', 'address']]
print("Successfully kept relevant columns.")

# Append ', Amsterdam, Netherlands' to each address
print("Appending ', Amsterdam, Netherlands' to addresses...")
df_amsterdam['address'] = df_amsterdam['address'] + ', Amsterdam, Netherlands'
print("Successfully appended addresses.")

# Write the results to a CSV file
print("Writing results to amsterdam_vergunningen.csv...")
df_amsterdam.to_csv('amsterdam_vergunningen.csv', index=False)
print("Successfully wrote results to amsterdam_vergunningen.csv.")

# Load the large CSV
large_df = pd.read_csv('amsterdam_vergunningen.csv')

# Define the maximum number of rows per file
max_rows_per_file = 2000

# Create the 'Amsterdam_in_batches' subfolder if it doesn't exist
os.makedirs('Amsterdam_in_batches', exist_ok=True)

# Split the DataFrame into smaller DataFrames
split_dataframes = [large_df[i:i+max_rows_per_file] for i in range(0, len(large_df), max_rows_per_file)]

# Save each smaller DataFrame as a separate CSV
for i, small_df in enumerate(split_dataframes):
    csv_filename = f'Amsterdam_in_batches/amsterdam_batch_{i + 1}.csv'
    small_df.to_csv(csv_filename, index=False)

print("Successfully split and saved the CSV into batches.")


# Create a geocoder instance (you may need to specify a user agent)
print("Creating a geocoder instance...")
geolocator = Nominatim(user_agent="my_geocoder", timeout=10)
print("Successfully created a geocoder instance.")

# Define a function to get coordinates (latitude and longitude) for an address
def get_coordinates_for_amsterdam_addresses(df_amsterdam):
    # Get the list of addresses from the DataFrame
    addresses = df_amsterdam['address'].tolist()

    # Create a geocoder instance (you may need to specify a user agent)
    geolocator = Nominatim(user_agent="my_geocoder", timeout=10)

    # Initialize a list to store all coordinates
    all_coordinates = []

    # Define a function to batch geocode addresses
    def batch_geocode(addresses, max_retries=3):
        coordinates = []
        retry_count = 0

        for address in addresses:
            while retry_count < max_retries:
                try:
                    location = geolocator.geocode(address)
                    if location:
                        coordinates.append((location.latitude, location.longitude))
                        break  # Move to the next address
                except Exception as e:
                    print(f"Error geocoding address '{address}': {str(e)}")
                    retry_count += 1
                    time.sleep(1)  # Wait before retrying
            else:
                print(f"Max retries reached for address: {address}")

        return coordinates

    # Split addresses into batches (adjust batch size as needed)
    batch_size = 1000
    address_batches = [addresses[i:i+batch_size] for i in range(0, len(addresses), batch_size)]

    # Batch geocode addresses and append coordinates to the list
    for batch in address_batches:
        batch_coordinates = batch_geocode(batch)
        all_coordinates.extend(batch_coordinates)

    return all_coordinates

# Define a function to get postal code for an address
def get_postal_codes_for_amsterdam_addresses(df_amsterdam):
    # Get the list of addresses from the DataFrame
    addresses = df_amsterdam['address'].tolist()

    # Create a geocoder instance (you may need to specify a user agent)
    geolocator = Nominatim(user_agent="my_geocoder", timeout=10)

    # Initialize a list to store all postal codes
    all_postal_codes = []

    # Define a function to batch geocode addresses for postal codes
    def batch_geocode_postal_codes(addresses, max_retries=3):
        postal_codes = []
        retry_count = 0

        for address in addresses:
            while retry_count < max_retries:
                try:
                    location = geolocator.geocode(address)
                    if location and 'postcode' in location.raw['address']:
                        postal_code = location.raw['address']['postcode']
                        postal_codes.append(postal_code)
                        break  # Move to the next address
                except Exception as e:
                    print(f"Error geocoding address '{address}' for postal code: {str(e)}")
                    retry_count += 1
                    time.sleep(1)  # Wait before retrying
            else:
                print(f"Max retries reached for address (postal code): {address}")

        return postal_codes

    # Split addresses into batches (adjust batch size as needed)
    batch_size = 1000
    address_batches = [addresses[i:i+batch_size] for i in range(0, len(addresses), batch_size)]

    # Batch geocode addresses for postal codes and append postal codes to the list
    for batch in address_batches:
        batch_postal_codes = batch_geocode_postal_codes(batch)
        all_postal_codes.extend(batch_postal_codes)

    return all_postal_codes

def create_amsterdam_vergunningen_coordinates_csv(df_amsterdam, coordinates, postal_codes, version=1):
    # Add coordinates and postal codes to the DataFrame
    df_amsterdam['latitude'] = [coord[0] for coord in coordinates]
    df_amsterdam['longitude'] = [coord[1] for coord in coordinates]
    df_amsterdam['postal_code'] = postal_codes

    # Define the CSV filename
    csv_filename = f'amsterdam_vergunningen_coordinates{"_" + str(version) if version > 1 else ""}.csv'

    # Export the updated DataFrame to a new CSV
    df_amsterdam.to_csv(csv_filename, index=False)

    return csv_filename

coordinates = get_coordinates_for_amsterdam_addresses(df_amsterdam)
postal_codes = get_postal_codes_for_amsterdam_addresses(df_amsterdam)
create_amsterdam_vergunningen_coordinates_csv(df_amsterdam, coordinates, postal_codes, version=1)
