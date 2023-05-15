# adapted from: https://github.com/SergioLlana/datatables-flask-serverside/tree/master

import re


class ServerSideTable(object):
    '''
    Retrieves the values specified by DataTables in the request and processes
    the data that will be displayed in the table (filtering, sorting, and
    selecting a subset of it).

    Attributes:
        request: Values specified by DataTables in the request.
        data: Data to be displayed in the table.
        column_list: Schema of the table that will be built. It contains
                     the name of each column (both in the data and in the
                     table), the default values (if available), and the
                     order in the HTML.
    '''
    def __init__(self, request, data, column_list):
        self.result_data = None
        self.cardinality_filtered = 0
        self.cardinality = 0

        self.request_values = request.values
        self.columns = sorted(column_list, key=lambda col: col['order'])

        rows = self._extract_rows_from_data(data)
        self._run(rows)

    def _run(self, data):
        '''
        Prepares the data and values that will be generated as output.
        It does the actual filtering, sorting, and paging of the data.

        Args:
            data: Data to be displayed by DataTables.
        '''
        self.cardinality = len(data)                       # Total num. of rows

        filtered_data = self._custom_filter(data)
        self.cardinality_filtered = len(filtered_data)    # Num. displayed rows

        sorted_data = self._custom_sort(filtered_data)
        self.result_data = self._custom_paging(sorted_data)

    def _extract_rows_from_data(self, data):
        '''
        Extracts the value of each column from the original data using the
        schema of the table.

        Args:
            data: Data to be displayed by DataTables.

        Returns:
            List of dicts that represents the table's rows.
        '''
        rows = []
        for x in data:
            row = {}
            for column in self.columns:
                default = column['default']
                data_name = column['data_name']
                column_name = column['column_name']
                row[column_name] = x.get(data_name, default)
            rows.append(row)
        return rows

    def _custom_filter(self, data):
        '''
        Filters out those rows that do not contain the values specified by the
        user using a case-insensitive regular expression.

        It takes into account only those columns that are 'searchable'.

        Args:
            data: Data to be displayed by DataTables.

        Returns:
            Filtered data.
        '''
        def check_row(row):
            ''' Checks whether a row should be displayed or not. '''
            for i in range(len(self.columns)):
                if self.columns[i]['searchable']:
                    value = row[self.columns[i]['column_name']]
                    regex = '(?i)' + self.request_values['search[value]']
                    if re.compile(regex).search(str(value)):
                        return True
            return False

        if self.request_values.get('search[value]', ""):
            return [row for row in data if check_row(row)]
        else:
            return data

    def _custom_sort(self, data):
        '''
        Sorts the rows taking into account the column (or columns) that the
        user has selected.

        Args:
            data: Filtered data.

        Returns:
            Sorted data by the columns specified by the user.
        '''
        if self.request_values.get('order[0][column]'):
            column_number = int(self.request_values['order[0][column]'])
            column_name = self.columns[column_number]['column_name']
            sort_direction = self.request_values['order[0][dir]']
            reverse = sort_direction == 'desc'
            key_fn = lambda x: x[column_name]
            if column_name == 'Title':
                # match based on actual title, not on link
                key_fn = lambda x: re.match(r'<a href=".*" class="scenario_link">(.*)</a>', x['Title']).group(1)
            data = sorted(data, key=key_fn, reverse=reverse)
        return data

    def _custom_paging(self, data):
        '''
        Selects a subset of the filtered and sorted data based on if the table
        has pagination, the current page, and the size of each page.

        Args:
            data: Filtered and sorted data.

        Returns:
            Subset of the filtered and sorted data that will be displayed by
            the DataTables if the pagination is enabled.
        '''
        if not self.request_values.get('start'):
            return data

        start = int(self.request_values['start'])
        length = int(self.request_values['length'])

        # if search returns only one page
        if len(data) <= length:
            # display only one page
            return data[start:]
        else:
            end = start + length
            return data[start:end]

    def output_result(self):
        '''
        Generates a dict with the content of the response. It contains the
        required values by DataTables (echo of the response and cardinality
        values) and the data that will be displayed.

        Returns:
            Content of the response.
        '''
        output = {}
        output['draw'] = int(self.request_values['draw'])
        output['recordsTotal'] = self.cardinality
        output['recordsFiltered'] = self.cardinality_filtered
        output['data'] = self.result_data
        return output

