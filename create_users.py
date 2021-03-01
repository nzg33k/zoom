import json
# noinspection PyUnresolvedReferences
from generic_request import generic_zoom_request as gr
# noinspection PyUnresolvedReferences
from zoom_groups import get_user_email_list_from_file
import zoom_groups


def create_users(users_list_file, user_type=2):
    """Add a user or users to a group"""
    user_list = get_user_email_list_from_file(users_list_file, False)
    results = []
    for user_email in user_list:
        params = {
            'action': "create",
            'user_info': {
                'email': user_email,
                'type': user_type
            }
        }
        params = json.dumps(params)
        result = gr('users/', params=params, request_type='post')
        results.append(result)
    return results


def add_users_to_groups_even_new(group_name, file_name=None, user_type=2, debug=False):
    if file_name is None:
        file_name = group_name + ".csv"
    create_results = create_users(file_name, user_type)
    add_to_group_results = zoom_groups.add_users_to_group_from_email_list_file(group_name, file_name)
    change_type_results = zoom_groups.change_user_type_for_group(group_name, user_type)
    if debug:
        for create_result in create_results:
            print(create_result.content)
        for add_to_group_result in add_to_group_results:
            print(add_to_group_result.content)
        print(change_type_results)


