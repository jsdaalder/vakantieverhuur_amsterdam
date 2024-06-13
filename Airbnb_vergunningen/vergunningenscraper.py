import requests
from bs4 import BeautifulSoup
from urllib.parse import parse_qs, urljoin, urlparse
import csv
import os

def find_highest_page_number(url):
    response = requests.get(url)
    if response.status_code != 200:
        print("Failed to fetch the URL")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    page_links = soup.find_all("a", id=lambda x: x and x.startswith('id-page-') and x[8:].isdigit())
    
    if not page_links:
        print("No page links found.")
        return None

    # Filter out the 'next' button and extract the highest number
    highest_page_number = max(int(link['id'].split('-')[-1]) for link in page_links if link['id'][8:].isdigit())
    return highest_page_number

def scrape_page(url, page_number):
    response = requests.get(url)
    if response.status_code == 200:
        # Extract the page number from the URL
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        page_number = query_params.get('pagina', [''])[0]

        print(f"Successfully scraped page {page_number} of the URL")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        results = []

        no_verleend_count = 0  # Initialize the counter for 'geen verleend'

        publications_container = soup.find("div", class_="result--list result--list--publications")
        if not publications_container:
            print("No publications container found.")
            return [], no_verleend_count

        for li in publications_container.find_all("li"):
            h2_element = li.find("h2", class_="result--title")
            title_element = li.find("a", class_="result--subtitle")

            if h2_element and title_element:
                unique_id = h2_element.find("a")['href'].split('.')[0] if h2_element.find("a") else "N/A"
                title = title_element.get_text(strip=True)

                if 'Verleend' in title:
                    approval_status = 'Verleend'
                    try:
                        # Replace non-breaking spaces with regular spaces
                        normalized_title = title.replace('\xa0', ' ')
                        address = normalized_title.split('Verleend ')[1]
                    except IndexError:
                        address = "N/A"
                else:
                    approval_status = "N/A"
                    address = "geen 'verleend'"
                    no_verleend_count += 1  # Increment the counter

                date_elements = li.find_all("dd")
                date = date_elements[0].get_text(strip=True) if date_elements else "N/A"
                municipality = date_elements[2].get_text(strip=True) if len(date_elements) > 2 else "N/A"
                pdf_link_element = li.find("a", class_="icon icon--download")
                pdf_link = urljoin(url, pdf_link_element['href']) if pdf_link_element else "N/A"

                results.append({
                    "unique_id": unique_id,
                    "title": title,
                    "approval_status": approval_status,
                    "address": address,
                    "date": date,
                    "municipality": municipality,
                    "pdf_link": pdf_link,
                    "page_number": page_number  # Add the page number
                })

        return results, no_verleend_count
    else:
        print(f"Failed to scrape the URL: {url}. Status code: {response.status_code}")
        return [], 0

def write_to_csv(filename, fieldnames, data):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"Successfully created the CSV file: {filename}")

def main():
    url_base = "https://zoek.officielebekendmakingen.nl/resultaten?svel=Publicatiedatum&svol=Aflopend&pg=1000&q=(c.product-area==%22officielepublicaties%22)and(cql.textAndIndexes=%22vergunning%22%20and%20cql.textAndIndexes=%22vakantieverhuur%22)%20AND%20w.publicatienaam==%22Gemeenteblad%22%20AND%20dt.type==%22andere%20vergunning%22&zv=vergunning%20vakantieverhuur&col=&pagina="
    all_results = []
    highest_page = find_highest_page_number(url_base + "1")

    if highest_page is None:
        print("Could not determine the highest page number. Exiting.")
        return

    for page in range(1, highest_page + 1):
        url = f"{url_base}{page}"
        results, no_verleend_count = scrape_page(url, page)  # Pass the page number correctly
        all_results.extend(results)

    # CSV File Handling
    filename = 'vergunningenscraper_output.csv'
    counter = 1
    while os.path.exists(filename):
        filename = f'vergunningenscraper_output_{counter}.csv'
        counter += 1

    fieldnames = ["unique_id", "page_number", "title", "approval_status", "address", "date", "municipality", "pdf_link"]
    write_to_csv(filename, fieldnames, all_results)

if __name__ == "__main__":
    main()
