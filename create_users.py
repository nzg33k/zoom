import json
# noinspection PyUnresolvedReferences
from .generic_request import generic_zoom_request as gr
# noinspection PyUnresolvedReferences
from .zoom_groups import get_user_email_list_from_file, add_users_to_group_from_email_list_file
from .zoom_groups import change_user_type_for_group


# import zoom_groups

def create_user(user_email, user_type=2):
    """Add a single user to a group"""
    params = {
        'action': "create",
        'user_info': {
            'email': user_email,
            'type': user_type
        }
    }
    params = json.dumps(params)
    result = gr('users/', params=params, request_type='post')
    return result


def create_users(users_list_file, user_type=2):
    """Add a user or users to a group"""
    if isinstance(users_list_file, list):
        user_list = users_list_file
    else:
        user_list = get_user_email_list_from_file(users_list_file, False)
    results = []
    for user_email in user_list:
        results.append(create_user(user_email, user_type))
    return results


def add_users_to_groups_even_new(group_name, file_name=None, user_type=2, debug=False, even_new=True):
    if file_name is None:
        file_name = f"csvs/{group_name}.csv"
    if even_new:
        create_results = create_users(file_name, user_type)
    add_to_group_results = add_users_to_group_from_email_list_file(group_name, file_name)
    change_type_results = change_user_type_for_group(group_name, user_type)
    if debug:
        already_exist = []
        created = []
        added = []
        if even_new:
            # noinspection PyUnboundLocalVariable
            for create_result in create_results:
                result_content = json.loads(create_result.content)
                if 'email' in result_content:
                    created.append(result_content['email'])
                elif 'message' in result_content:
                    already_exist.append(result_content['message'].replace("User already in the account: ", ""))
        for add_to_group_result in add_to_group_results:
            result_content = json.loads(add_to_group_result.content)
            if 'ids' in result_content:
                if result_content['ids'] != "":
                    added.append(result_content['ids'])
        created_count = len(created)
        exist_count = len(already_exist)
        added_count = len(added)

        output = ""
        if already_exist:
            if len(already_exist) > 1:
                output += f"The following {exist_count} users already exist:\n"
            else:
                output += "The following user already exists:\n"
            for entry in already_exist:
                output += f"{entry}\n"
            output += "\n"
        if created:
            if len(created) > 1:
                output += f"The following {created_count} users have been invited:\n"
            else:
                output += "The following user has been invited:\n"
            for entry in created:
                output += f"{entry}\n"
            output += "\n"
        if added:
            if len(added) > 1:
                output += f"The following {added_count} user ids have been added to the group:\n"
            else:
                output += "The following user id has been added to the group:\n"
            for entry in added:
                output += f"{entry}\n"
            output += "\n"
        if change_type_results:
            output += "User type(s) were successfully updated\n"

        return output

# add_users_to_groups_even_new('Group Name', debug=True)
