###
import json
import secrets
import sys

from zoomus import ZoomClient

# noinspection PyUnresolvedReferences
client = ZoomClient(secrets.API_KEY, secrets.API_SECRET)

output_file = open('output/zoom_users_features.csv', 'w', encoding="utf-8")
user_ids = set()

# 300 seems to be the maximum page size, less pages is faster
user_list_response = client.user.list(page_size=300)
page_count = json.loads(user_list_response.content)['page_count']
for page in range(page_count):
    user = 0
    user_list_response = client.user.list(page_number=page, page_size=300)
    user_list = json.loads(user_list_response.content)['users']
    for this_user in user_list:
        user += 1
        user_id = this_user['id']
        # This is cheating, the get function isn't meant to be a get settings function, but it works
        user_get_response = client.user.get(id=str(user_id)+"/settings")
        large_meeting_enabled = (json.loads(user_get_response.content)['feature']['large_meeting'])
        if large_meeting_enabled:
            output_file.write(str(user_id) + "\n")
        sys.stdout.write("\rPage: " + str(page+1) + "/" + str(page_count) + " User: " + str(user))
        sys.stdout.flush()

output_file.close()
