import json
import datetime
import csv
import sys
import time
import pandas
import matplotlib
# psutil isn't used directly but it is required for plotly so I am adding it to help build requirements
import psutil
# Things break if you import the whole module and use relative delta, its a known upstream bug
# Also, the package is called python-dateutil not dateutil which the inspector doesn't like
# noinspection PyPackageRequirements
from dateutil import relativedelta as rd
# Save some typing later on :)
# noinspection PyUnresolvedReferences
from generic_request import generic_zoom_request as gr


def get_month_daily_report(year=None, month=None):
    """get the daily data for a given month"""
    params = {
        'year': year,
        'month': month
    }
    report = gr('report/daily', params)
    month_data = json.loads(report.content)['dates']
    return month_data


def get_month_webinars(year, month):
    """Get the webinars for a month"""
    target_date = datetime.datetime.strptime(str(year) + '-' + str(month) + '-01', "%Y-%m-%d")
    results = get_webinar_stats(target_date)
    return results


def initial_daily_report_run():
    """Get all the history we can (last 6 months)"""
    history_data = []
    webinar_data = {}
    current_date = datetime.datetime.today()
    year = current_date.year
    month = current_date.month
    month = month - 5
    if month <= 0:
        month += 12
        year -= 1
    for i in range(6):
        if month > 12:
            month = 1
            year += 1
        history_data += get_month_daily_report(year, month)
        webinar_data.update(get_month_webinars(year, month))
        month += 1
    history_data = combine_data(history_data, webinar_data)
    return history_data


def combine_data(daily, webinar):
    """Combine the data from daily reports and webinar reports"""
    for day in daily:
        if day['date'] in webinar:
            day.update(
                {'webinars': webinar[day['date'] + '_count'], 'total_webinar_participants': webinar[day['date']]})
    return daily


# noinspection SpellCheckingInspection
def matplot_plot_graph(x_data, y_data, ylabel='Y', xlabel='X', title='Title', filename='plot'):
    """Graph the data - with matplotlib"""
    matplotlib.use('Agg')
    from matplotlib import pyplot as plt
    plt.ticklabel_format(style='plain')
    plt.plot(x_data, y_data)
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.title(title)
    plt.savefig('output/' + filename + '.png', format='png')
    plt.clf()


# noinspection SpellCheckingInspection
def plotly_plot_graph(x_data, y_data, ylabel='Y', xlabel='X', title='Title', filename='plot'):
    """Graph the data - with plotly"""
    # noinspection PyUnresolvedReferences
    import plotly.express as px
    data_lists = list(zip(x_data, y_data))
    data_frame = pandas.DataFrame(data=data_lists, columns=[xlabel, ylabel])
    fig = px.line(data_frame, x=xlabel, y=ylabel, title=title, )
    fig.write_html('output/' + filename + '.html')
    fig.write_image('output/' + filename + '.png')


def plot_graph(x_data, y_data, y_label='Y', x_label='X', title='Title', filename='plot'):
    """Create Graphs using the engine of choice.  plotly requires a gui to render, but are prettier"""
    graph_engine = 'plotly'
    try:
        import plotly
    except ImportError:
        graph_engine = 'matplotlib'
    if graph_engine == 'matplotlib':
        matplot_plot_graph(x_data, y_data, y_label, x_label, title, filename)
    else:
        plotly_plot_graph(x_data, y_data, y_label, x_label, title, filename)
    html_create_html_redirect(graph_engine)


def html_create_html_redirect(target, index_filename='index'):
    """Create an HTML redirect"""
    index_file = open('output/' + index_filename + '.html', 'w')
    index_file.writelines("""
<!DOCTYPE html>
<html>
   <head>
      <title>HTML Meta Tag</title>
      <meta http-equiv = \"refresh" content = \"2; url = """ + target + """.html\" />
   </head>
   <body>
      <a href=\"""" + target + """.html\" >Please click here to go to the right page</a>
   </body>
</html>""")


def rearrange_data(source_data):
    """Sort the data into a dict of lists"""
    dates = []
    date_text = []
    new_users = []
    meetings = []
    participants = []
    minutes = []
    webinars = []
    total_webinar_participants = []
    for entry in source_data:
        dates.append(datetime.datetime.strptime(entry['date'], "%Y-%m-%d"))
        date_text.append(entry['date'])
        new_users.append(entry['new_users'])
        meetings.append(entry['meetings'])
        participants.append(entry['participants'])
        minutes.append(entry['meeting_minutes'])
        if 'webinars' not in entry:
            webinars.append(0)
            total_webinar_participants.append(0)
        else:
            webinars.append(int(entry['webinars']))
            total_webinar_participants.append(int(entry['total_webinar_participants']))
    return_data = {
        'dates': dates,
        'new_users': new_users,
        'meetings': meetings,
        'participants': participants,
        'minutes': minutes,
        'webinars': webinars,
        'total_webinar_participants': total_webinar_participants
    }
    return return_data


def create_graphs(graph_data):
    """Create some graphs"""
    graph_dates = graph_data['dates']
    plot_graph(graph_dates, graph_data['new_users'], 'Number', 'Date', 'New Users', 'new_users')
    plot_graph(graph_dates, graph_data['meetings'], 'Number', 'Date', 'Meetings', 'meetings')
    plot_graph(graph_dates, graph_data['participants'], 'Number', 'Date', 'Meeting Participants',
               'meeting_participants')
    plot_graph(graph_dates, graph_data['minutes'], 'Number', 'Date', 'Meeting Minutes', 'minutes')
    plot_graph(graph_dates, graph_data['webinars'], 'Number', 'Date', 'Webinars', 'webinars')
    plot_graph(graph_dates, graph_data['total_webinar_participants'], 'Number', 'Date', 'Webinar participants',
               'webinar_participants')


def export_csv(csv_data, csv_filename='output/daily.csv', fieldnames=False):
    """Export data to a csv file"""
    if not fieldnames:
        fieldnames = ['date', 'new_users', 'meetings', 'participants', 'meeting_minutes',
                      'total_webinar_participants', 'webinars']
    if sys.version_info[0] >= 3:
        csv_file = open(csv_filename, 'w', newline='')
    else:
        csv_file = open(csv_filename, 'w')
    with csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)


def list_of_dict_to_csv(csv_data, csv_filename='output/LOfD.csv'):
    """Export a list of dictionaries to a csv file"""
    keys = set().union(*(dictionary.keys() for dictionary in csv_data))
    if sys.version_info[0] >= 3:
        csv_file = open(csv_filename, 'w', newline='', encoding="utf-8")
    else:
        csv_file = open(csv_filename, 'w', encoding="utf-8")
    with csv_file:
        writer = csv.DictWriter(csv_file, keys)
        writer.writeheader()
        writer.writerows(csv_data)


def date_add_zero(source_date):
    """Add a zero if needed"""
    if int(source_date) < 10:
        source_date = "0" + str(source_date)
    return str(source_date)


def datetime_to_string(source_date):
    """Turn a datetime into a date that the api likes"""
    year = str(source_date.year)
    month = date_add_zero(source_date.month)
    day = date_add_zero(source_date.day)
    new_date = year + "-" + month + "-" + day
    return new_date


def get_webinars(from_date, to_date=None, webinar_type='past', page_size=300):
    """Get stats around webinars"""
    if to_date is None:
        to_date = from_date + rd.relativedelta(months=1)
    from_date = datetime_to_string(from_date)
    to_date = datetime_to_string(to_date)
    params = {
        'type': webinar_type,
        'page_size': page_size,
        'from': from_date,
        'to': to_date
    }
    results = gr('/metrics/webinars', params)
    webinars = json.loads(results.content)
    if 'webinars' not in webinars:
        # Can only query so many times a minute
        sys.stdout.write('Querying faster than Zoom let us, sleeping for one minute.\n')
        sys.stdout.flush()
        time.sleep(60)
        results = gr('/metrics/webinars', params)
        webinars = json.loads(results.content)
    return webinars


def get_meetings(from_date, to_date=None, meeting_type='past', page_size=300):
    """Get stats around meetings"""
    if to_date is None:
        to_date = from_date + rd.relativedelta(months=1)
    from_date = datetime_to_string(from_date)
    to_date = datetime_to_string(to_date)
    params = {
        'type': meeting_type,
        'page_size': page_size,
        'from': from_date,
        'to': to_date,
        'next_page_token': "first_run"
    }
    all_meetings = []
    while params['next_page_token'] != "":
        if params['next_page_token'] == "first_run":
            params['next_page_token'] = ""
        results = gr('/metrics/meetings', params)
        meetings = json.loads(results.content)
        if 'meetings' not in meetings:
            # Can only query so many times a minute
            sys.stdout.write('Querying faster than Zoom let us, sleeping for one minute.\n')
            sys.stdout.flush()
            time.sleep(60)
            results = gr('/metrics/meetings', params)
            meetings = json.loads(results.content)
        params['next_page_token'] = meetings['next_page_token']
        all_meetings += meetings['meetings']
    return all_meetings


def get_webinar_stats(from_date, to_date=None, webinar_type='past', page_size=300):
    webinars = get_webinars(from_date, to_date, webinar_type, page_size)
    webinars = webinars['webinars']
    webinar_data = {}
    for webinar in webinars:
        webinar_date = webinar['start_time'].split('T')[0]
        participants = webinar['participants']
        if webinar_date in webinar_data:
            webinar_data[webinar_date] += participants
            webinar_data[webinar_date + '_count'] += 1
        else:
            webinar_data[webinar_date] = participants
            webinar_data[webinar_date + '_count'] = 1
    return webinar_data


def update_reporting(meetings=False):
    data = initial_daily_report_run()
    rearranged_data = rearrange_data(data)
    create_graphs(rearranged_data)
    export_csv(data)
    if meetings:
        meeting_data = get_meetings(datetime.datetime.now() - rd.relativedelta(months=1))
        list_of_dict_to_csv(meeting_data, "output/meeting_list_data.csv")


update_reporting()
