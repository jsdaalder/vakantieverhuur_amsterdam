import pandas as pd

def filter_and_sort_csv(input_csv, output_csv):
    # Read the input CSV file
    df = pd.read_csv(input_csv)

    # Filter out rows where municipality is not Amsterdam
    filtered_df = df[df['municipality'] != 'Amsterdam']

    # Sort the filtered data based on municipality
    sorted_df = filtered_df.sort_values(by='municipality')

    # Save the sorted data to the output CSV file
    sorted_df.to_csv(output_csv, index=False)

def main():
    input_csv = 'vergunningenscraper_output.csv'
    output_csv = 'filtered_sorted_output.csv'

    filter_and_sort_csv(input_csv, output_csv)
    print(f"Filtered and sorted data saved to {output_csv}")

if __name__ == "__main__":
    main()
