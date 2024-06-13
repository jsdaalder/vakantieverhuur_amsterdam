import pandas as pd
import os
from geopy.geocoders import Nominatim

def find_latest_csv(directory, prefix='vergunningenscraper_output'):
    csv_files = [f for f in os.listdir(directory) if f.startswith(prefix) and f.endswith('.csv')]
    if not csv_files:
        return None
    return os.path.join(directory, sorted(csv_files)[-1])

def find_available_txt_filename(base_filename, directory):
    version = 1
    while True:
        txt_filename = f'{base_filename}_{version}.txt'
        if not os.path.exists(os.path.join(directory, txt_filename)):
            return txt_filename
        version += 1

def main():
    directory = '/Users/jandaalder/Downloads/Airbnb_vergunningen'
    latest_csv = find_latest_csv(directory)

    if latest_csv:
        df = pd.read_csv(latest_csv)

        # Calculate the amount of unique municipalities
        unique_municipalities_count = df['municipality'].nunique()

        # Get names of all unique municipalities
        unique_municipalities = df['municipality'].unique()

        # Calculate the top 10 municipalities with the highest number of permits
        top_10_municipalities = df['municipality'].value_counts().nlargest(10)

        # Calculate the number of permits per year in Amsterdam
        amsterdam_permits = df[df['municipality'] == 'Amsterdam']
        amsterdam_yearly_permits = amsterdam_permits['date'].str.extract(r'(\d{4})').value_counts().sort_index()

        # Calculate the number of permits per year in all other municipalities (excluding Amsterdam)
        other_municipalities_permits = df[df['municipality'] != 'Amsterdam']
        other_municipalities_yearly_permits = other_municipalities_permits['date'].str.extract(r'(\d{4})').value_counts().sort_index()

        # Find an available .txt filename
        txt_filename = find_available_txt_filename('analysis_results', directory)

        # Save the results to the .txt file
        with open(os.path.join(directory, txt_filename), 'w') as txt_file:
            txt_file.write(f"Amount of Unique Municipalities: {unique_municipalities_count}\n\n")
            txt_file.write("List of Unique Municipalities:\n")
            for municipality in unique_municipalities:
                txt_file.write(municipality + '\n')
            txt_file.write("\nTop 10 Municipalities with the Highest Number of Permits (Including Permit Count):\n")
            txt_file.write(top_10_municipalities.to_string() + '\n')
            txt_file.write("\nNumber of Permits per Year in Amsterdam:\n")
            txt_file.write(amsterdam_yearly_permits.to_string() + '\n')
            txt_file.write("\nNumber of Permits per Year in All Other Municipalities (Excluding Amsterdam):\n")
            txt_file.write(other_municipalities_yearly_permits.to_string() + '\n')

        print(f"Analysis results have been saved to {txt_filename}")
        
    else:
        print("No CSV file found in the specified directory.")

if __name__ == "__main__":
    main()
