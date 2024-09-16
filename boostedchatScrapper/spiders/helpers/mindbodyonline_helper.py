import csv
import json
from boostedchatScrapper.models import ScrappedData
from collections import Counter,defaultdict
# Open CSV file for writing
records = ScrappedData.objects.filter(name__icontains='mindbodyonline/instructors/')

with open('staff_per_record.csv', 'w', newline='') as csvfile:
    fieldnames = ['Record ID', 'Number of Staff']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Write data to CSV
    for record in records:
        json_data = record.response
        num_staff = len(json_data.get('data', []))
        writer.writerow({'Record ID': record.name, 'Number of Staff': num_staff})

total_staff_count = sum(len(record.response.get('data', [])) for record in records)
total_records = records.count()
average_staff_count = total_staff_count / total_records if total_records else 0

# Write average staff count to CSV
with open('average_staff_count.csv', 'w', newline='') as csvfile:
    fieldnames = ['Average Number of Staff']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({'Average Number of Staff': average_staff_count})


total_staff_count = sum(len(record.response.get('data', [])) for record in records)
total_records = records.count()
average_staff_count = total_staff_count / total_records if total_records else 0

# Write average staff count to CSV
with open('average_staff_count.csv', 'w', newline='') as csvfile:
    fieldnames = ['Average Number of Staff']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerow({'Average Number of Staff': average_staff_count})

gender_counter = Counter()
for record in records:
    json_data = record.response
    for item in json_data.get('data', []):
        gender = item.get('attributes', {}).get('gender', {}).get('name')
        gender_counter[gender] += 1

# Write gender distribution to CSV
with open('gender_distribution.csv', 'w', newline='') as csvfile:
    fieldnames = ['Gender', 'Count']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for gender, count in gender_counter.items():
        writer.writerow({'Gender': gender, 'Count': count})


category_counter = Counter()
for record in records:
    json_data = record.response
    for item in json_data.get('data', []):
        categories = item.get('attributes', {}).get('categories', [])
        category_counter.update(categories)

# Write most common categories to CSV
with open('most_common_categories.csv', 'w', newline='') as csvfile:
    fieldnames = ['Category', 'Count']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for category, count in category_counter.most_common():
        writer.writerow({'Category': category, 'Count': count})



location_staff_count = defaultdict(int)
for record in records:
    json_data = record.response
    for item in json_data.get('data', []):
        locations = item.get('attributes', {}).get('locationNames', [])
        for location in locations:
            location_staff_count[location] += 1

# Write number of staff per location to CSV
with open('staff_per_location.csv', 'w', newline='') as csvfile:
    fieldnames = ['Location', 'Number of Staff']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for location, staff_count in location_staff_count.items():
        writer.writerow({'Location': location, 'Number of Staff': staff_count})
