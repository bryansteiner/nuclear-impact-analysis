from requests_html import HTMLSession
import pprint

session = HTMLSession()
pp = pprint.PrettyPrinter()

# List of nuclear tests globally
global_url = 'https://en.wikipedia.org/wiki/List_of_nuclear_weapons_tests'
response = session.get(global_url)

# Nuclear weapons testing totals by country
totals_data = {}
totals_table = response.html.find('.wikitable, .sortable', first=True)

columns = totals_table.find('tr', first=True)
column_labels = [column.text.split('[')[0].rstrip()
                 for column in columns.find('th')][1:]
rows = totals_table.find('tr')[1:]

for i, row in enumerate(rows):

    country_name = row.find('th')[0].text.split('[')[0].rstrip()
    country_stats = row.find('td')

    if country_name and country_name != 'Totals':
        totals_data[country_name] = {}

        for link in row.find('th')[0].absolute_links:
            if 'List_of_nuclear_weapons_tests_of' in link:
                # List of nuclear testing series by country
                totals_data[country_name]['URL'] = link

        columns_label_index = 0
        for i, stat in enumerate(country_stats):
            # Ignore reference links
            if i != 1:
                totals_data[country_name][column_labels[columns_label_index]] = stat.text.split('[')[0].rstrip()
                columns_label_index += 1

# print('Nuclear weapons totals by country:\n')
# pp.pprint(totals_data)

# Nuclear weapons testing series by country
series_data = {}

for country_name, totals_stats in totals_data.items():
    response = session.get(totals_stats['URL'])

    series_table = response.html.find('.wikitable, .sortable', first=True)
    series_data[country_name] = []

    columns = series_table.find('tr', first=True)
    column_labels = [column.text.split('[')[0].rstrip()
                     for column in columns.find('th')]
    rows = series_table.find('tr')[1:]

    # USA, USSR, UK, France: indivudual nuclear tests listed @ url_depth=2
    if country_name in ['USA', 'USSR', 'UK', 'France']:
        for i, row in enumerate(rows):

            series_name = row.find('th')[0].text
            series_stats = row.find('th') + row.find('td')

            if series_name and series_name != 'Totals':
                dict_stats = {column_labels[i]: stat.text for i, stat in enumerate(series_stats)}
                dict_url = {'URL': link for link in row.find('th')[0].absolute_links}

                series_data[country_name].append({**dict_stats, **dict_url})

    # China, India, Pakistan, North Korea: indivudual nuclear tests listed @ url_depth=1
    elif country_name in ['China', 'India', 'Pakistan', 'North Korea']:
        series_data[country_name] = [{
            'Series or years': 'None',
            'URL': totals_data[country_name]['URL']}]

# print('Nuclear weapons test series by country:\n')
# pp.pprint(series_data)

# Nuclear weapons individual tests by country
tests_data = {}

for country_name, series_stats in series_data.items():
    tests_data[country_name] = []

    for stat in series_stats:
        response = session.get(stat['URL'])
        print(stat['URL'])

        try:
            if country_name != 'North Korea':
                tests_table = response.html.find('.wikitable, .sortable', first=True)
                table_caption = tests_table.find('caption', first=True).text

                columns = tests_table.find('tr', first=True)
                column_labels = [column.text.split('[')[0].rstrip()
                                 for column in columns.find('th')]
                rows = tests_table.find('tr')[1:]

                for i, row in enumerate(rows):
                    test_name = row.find('th')[0].text
                    test_stats = row.find('th') + row.find('td')

                    dict_stats = {
                        column_labels[i]: stat.text.replace(u'\n', u' ').replace(u'\xa0', u' ').replace(u'\ufeff', u'')
                        for i, stat in enumerate(test_stats)}
                    dict_series = {}

                    if 'Series or years' in stat:
                        dict_series = {'Series or years': stat['Series or years']}
                    elif 'Series' in stat:
                        dict_series = {'Series': stat['Series']}
                    elif 'Name' in stat:
                        dict_series = {'Name': stat['Name']}
                    elif 'Sequence' in stat:
                        dict_series = {'Sequence': stat['Sequence']}

                    tests_data[country_name].append({**dict_stats, **dict_series})
            else:
                # North Korea uses an extra row for notes rather than a column
                print('HELLO NORTH KOREA')
                tests_table = response.html.find('.wikitable, .sortable')[1]
                table_caption = tests_table.find('caption', first=True).text

                columns = tests_table.find('tr', first=True)
                column_labels = [column.text.split('[')[0].rstrip()
                                 for column in columns.find('th')]
                rows = tests_table.find('tr')[1:]
                print(column_labels)

                for i, row in enumerate(rows):
                    print(row.text)
                    if i % 2:
                        test_name = row.find('th')[0].text
                        test_stats = row.find('th') + row.find('td')

                        dict_stats = {
                            column_labels[i]: stat.text.replace(u'\n', u' ').replace(u'\xa0', u' ').replace(u'\ufeff',
                                                                                                            u'')
                            for i, stat in enumerate(test_stats)}
                        dict_series = {'Sequence': stat['Sequence']}
                        print(dict_series)
                    else:
                        dict_stats['Notes'] = row.text

                    tests_data[country_name].append({**dict_stats, **dict_series})

        except Exception as e:
            print(e)

print('Nuclear weapons individual tests by country:\n')
pp.pprint(tests_data)