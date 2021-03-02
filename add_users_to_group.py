# noinspection PyUnresolvedReferences
import zoom_groups
import json

results = zoom_groups.add_users_to_group_from_email_list_file('Population Health', 'userlist')
for result in results:
    print(json.loads(result.content))

