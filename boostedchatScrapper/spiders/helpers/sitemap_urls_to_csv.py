import xml.etree.ElementTree as ET
import csv

# List of XML files
xml_files = [
    '/home/martin/Documents/boostedchat-scrapper/sitemaps/https___www_mindbodyonline_com_explore_sitemap1_xml_gz.xml',
    '/home/martin/Documents/boostedchat-scrapper/sitemaps/https___www_mindbodyonline_com_explore_sitemap2_xml_gz.xml'
]

# Function to extract links from XML
def extract_links_from_xml(xml_files):
    all_links = []
    for xml_file in xml_files:
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            for url in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                all_links.append(url.text)
        except ET.ParseError as e:
            print(f"Error parsing XML file '{xml_file}': {e}")
    return all_links

# Function to write links to CSV
def write_links_to_csv(links, csv_file):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Link'])  # Write header
        for link in links:
            writer.writerow([link])

# Extract links from all XML files and write them to a single CSV file
all_links = extract_links_from_xml(xml_files)
if all_links:
    write_links_to_csv(all_links, 'all_links.csv')
    print('All links saved to all_links.csv')
else:
    print('No links found in the XML files.')


import pandas as pd

df = pd.read_csv("all_links.csv")
# First, we'll clean the links to remove the trailing newline character
df['links'] = df['Link'].str.rstrip()

# Then, we'll extract the locations
df['location'] = df['links'].str.extract(r'https://www.mindbodyonline.com/explore/locations/(.*)')

# Now, we'll filter the DataFrame to only include rows where 'location' is not NaN
df = df.loc[df['location'].notna()]
df.to_csv("all_links_cleaned.csv")
