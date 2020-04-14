###
import json
import secrets
import sys

from zoomus import ZoomClient

# noinspection PyUnresolvedReferences
client = ZoomClient(secrets.API_KEY, secrets.API_SECRET)

output_file = open('output/zoom_users.csv', 'w', encoding="utf-8")

# 300 seems to be the maximum page size, less pages is faster
user_list_response = client.user.list(page_size=300)
page_count = json.loads(user_list_response.content)['page_count']
for page in range(page_count):
    user_list_response = client.user.list(page_number=page, page_size=300)
    user_list = json.loads(user_list_response.content)['users']
    for this_user in user_list:
        line = this_user['first_name'] + " " + this_user['last_name'] + "," + \
               this_user['email'] + "," + str(this_user['pmi']) + '\n'
        output_file.write(line)
        sys.stdout.write("\rPage: " + str(page+1) + "/" + str(page_count))
        sys.stdout.flush()

output_file.close()
