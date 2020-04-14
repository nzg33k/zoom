###
import json
import secrets
import sys
import csv
from zoomus import ZoomClient

# noinspection PyUnresolvedReferences
client = ZoomClient(secrets.API_KEY, secrets.API_SECRET)

output_file = open('output/zoom_users-full.csv', 'w', encoding="utf-8")
user_full_list = []
headers = set()

# 300 seems to be the maximum page size, less pages is faster
user_list_response = client.user.list(page_size=300)
page_count = json.loads(user_list_response.content)['page_count']

for page in range(page_count):
    user_list_response = client.user.list(page_number=page, page_size=300)
    user_list = json.loads(user_list_response.content)['users']
    for this_user in user_list:
        sys.stdout.write("\rPage: " + str(page + 1) + "/" + str(page_count))
        sys.stdout.flush()
        user_full_list.append(this_user)
        for key in this_user.keys():
            headers.add(key)

csv_writer = csv.DictWriter(output_file, headers)
csv_writer.writeheader()
for this_user in user_full_list:
    csv_writer.writerow(this_user)
output_file.close()
