import json
# noinspection PyUnresolvedReferences
from generic_request import generic_zoom_request as gr


def get_group_id(group_name):
    """Get the id of a group with a given name"""
    group_id = None
    group_list = gr('groups')
    group_list = json.loads(group_list.content)['groups']
    for group in group_list:
        if group['name'] == group_name:
            group_id = group['id']
    return group_id


def get_group_members(group_name, page_size=300):
    """Get the members of a group"""
    group_id = get_group_id(group_name)
    group_members = []
    params = {
        'page_size': page_size
    }
    group_members_raw = gr('groups/' + group_id + '/members', params)
    page_count = json.loads(group_members_raw.content)['page_count']
    for page in range(page_count):
        params = {
            'page_size': page_size,
            'page': page
        }
        group_members_raw = gr('groups/' + group_id + '/members', params)
        group_members += (json.loads(group_members_raw.content)['members'])
    return group_members


def change_user_type(user_id, new_type=2):
    """Change the license type for a user"""
    payload = "{\"type\":" + str(new_type) + "}"
    result = gr('users/' + user_id, payload, 'patch')
    if str(result.content) == "b\'\'":
        return
    else:
        return "user_id: " + user_id + "\nerror: " + str(result.content)


def change_user_type_for_group(group_name, new_type=2, page_size=300):
    """Change the user type for members of a group - default to licensed (2)"""
    users = get_group_members(group_name, page_size)
    for user in users:
        result = change_user_type(user['id'], new_type)
        if result is not None:
            print(result)


def add_users_to_group(group_name, users_list):
    """Add a user or users to a group"""
    group_id = get_group_id(group_name)
    params = {
        'members': users_list
    }
    params = json.dumps(params)
    result = gr('groups/' + str(group_id) + '/members', params=params, request_type='post')
    return result


def get_user_email_list_from_file(file_name, param_format=True):
    """Get the list of members from a list"""
    user_list = []
    list_file = open(file_name)
    for line in list_file:
        if param_format:
            user_list.append(
                {
                    'email': line.rstrip()
                }
            )
        else:
            user_list.append(line.rstrip())
    list_file.close()
    return user_list


def chunks(big_list, n=30):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(big_list), n):
        yield big_list[i:i + n]


def add_users_to_group_from_email_list_file(group_name, file_name):
    """Add users to a group from an e-mail list file"""
    big_user_list = get_user_email_list_from_file(file_name)
    list_of_lists = chunks(big_user_list, 30)
    results = []
    for small_user_list in list_of_lists:
        results.append(add_users_to_group(group_name, small_user_list))
    return results


def get_group_member_addresses(group_name):
    """Get a list of e-mail addresses from a group"""
    group_members = get_group_members(group_name)
    members = []
    for member in group_members:
        members.append(member['email'])
    return members
