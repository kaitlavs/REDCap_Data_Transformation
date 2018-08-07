import pandas as pd
# import sys


def create_df(file_name):
    """ Returns a DataFrame from a cvs file """

    return pd.read_csv(file_name)


def return_matches_between_data_and_metadata(data_list, metadata_list):
    """ Returns a list of all items common to both metadata lists and data lists.

        data_list is either a list of the field names in the data_df or
        a list of values in a specified column in the data_df.

        metadata_list is either the values under the Variable / Field Name column in the metadata
        DataFrame or the choices found in the Choices, calculations, etc. column of the
        metadata DataFrame."""

    matches = list(set(metadata_list).intersection(data_list))
    return matches


def return_difference_between_data_and_metadata(data_list, metadata_list):
    """ Returns a list of all items found in the data list that
        is not found in the metadata list.

        data_list is either a list of the field names in the data_df or a list of values
        in a specified column in the data_df.

        metadata list is either the values under the Variable / Field Name column in the metadata
        DataFrame or the choices found in the Choices, calculations, etc. column of the
        metadata DataFrame."""

    difference = list(set(data_list).difference(metadata_list))
    return difference


def return_value_and_index_dict(data_values, source_list):
    """ Returns a dictionary that contains values in data_values as keys,
        and their index + 1 in source_list.

        This function is used to return erroneous data values (data values that do not match
        choices found in the metadata_df's column 'Choices, Calculations, OR Slider Labels
        Choices, Calculations, OR Slider Labels' and their index in the data_df.

        It is also used to return correct data values (data values that match choices found in
        the metadata_df's column: 'Choices, Calculations, OR Slider Labels
        Choices, Calculations, OR Slider Labels' and their index within this metadata column."""

    index_list = []
    for item in data_values:
            index_list.append(str(source_list.index(item)+1))
    error_values_and_index_dict = dict(zip(data_values, index_list))
    return error_values_and_index_dict


def error_message(ix_dict):
    """ Outputs an error message and a dictionary containing the value and the index of the
        difference in values between two lists."""

    print("These data field names do not match options found in the metadata:")
    print(ix_dict)


def return_data_df_containing_only_matching_cols(orig_data_df, matches_between_data_and_metadata):
    """ Returns a data DataFrame that only contains the columns that matched
        with the metadata_df's column 'Variable / Field Name'."""

    data_matches_df = orig_data_df[matches_between_data_and_metadata]
    return data_matches_df


def return_cleaned_data_values(data_values_list):
    """ Returns a list of strings with whitespace removed and all lowercase
        letters."""

    cleaned_data_values_list = []
    for count in range(len(data_values_list)):
        if type(data_values_list[count]) != str:
            v1 = str(data_values_list[count])
        else:
            v1 = data_values_list[count]
        v1 = v1.replace(' ', '')
        v1 = v1.lower()
        cleaned_data_values_list.append(v1)
    return cleaned_data_values_list


def parse_metadata_choices(metadata_choices_string, separator):
    """ Returns a list of strings parsed around the separator in metadata_choice_string"""

    pipe_num = metadata_choices_string.count(separator)
    parsed_list = []
    for count in range(pipe_num + 1):
        v1 = metadata_choices_string.split(separator)[count]
        v1 = v1.split(',')[1]
        v1 = v1.replace(' ', '')
        v1 = v1.lower()
        parsed_list.append(v1)
    return parsed_list


def return_index_of_data_values_in_metadata(data_values_list, all_meta_choices_and_their_index):
    """ Returns a list of number strings that replaces keys with their
        value in a dictionary. This list is used to update the values of the columns
        in the data DataFrame.

        data_values_list is a list of all the values in the data_df of a specified column.
        all_choices_and_their_index is a dictionary containing the metadata_df choices as keys and
        the index of these choices as values."""

    string_list = ', '.join(data_values_list)
    for i, j in all_meta_choices_and_their_index.items():
        string_list = string_list.replace(i, j)
    back2list = string_list.split(',')
    return back2list


def date_validation(data_values_list, date_format_string):
    """ Validates the format of a list of strings and returns a new list with correct
        date formats."""

    import datetime
    import dateutil.parser

    new_list = []
    if date_format_string == 'date_mdy':
        for str_date in data_values_list:
            str_date = str(str_date)
            try:
                formatted_date = datetime.datetime.strptime(str_date, '%m/%d/%Y').strftime('%m/%d/%Y')
                new_list.append(formatted_date)
            except:
                parsed_str_date = dateutil.parser.parse(str_date)
                reformatted_date = str(parsed_str_date.month).rjust(2, '0') + '/' + str(
                    parsed_str_date.day).rjust(2, '0') + '/' + str(parsed_str_date.year)
                new_list.append(reformatted_date)
    elif date_format_string == 'date_dmy':
        for str_date in data_values_list:
            str_date = str(str_date)
            try:
                formatted_date = datetime.datetime.strptime(str_date, '%d/%m/%Y').strftime('%d/%m/%Y')
                new_list.append(formatted_date)
            except:
                parsed_str_date = dateutil.parser.parse(str_date)
                reformatted_date = str(parsed_str_date.day).rjust(2, '0') + '/' + str(
                    parsed_str_date.month).rjust(2, '0') + '/' + str(parsed_str_date.year)
                new_list.append(reformatted_date)
    elif date_format_string == 'date_ymd':
        for str_date in data_values_list:
            str_date = str(str_date)
            try:
                formatted_date = datetime.datetime.strptime(str_date, '%Y/%m/%d').strftime('%Y/%m/%d')
                new_list.append(formatted_date)
            except:
                parsed_str_date = dateutil.parser.parse(str_date)
                reformatted_date = str(parsed_str_date.year) + '/' + str(parsed_str_date.month).rjust(2, '0') + '/' + str(
                    parsed_str_date.day).rjust(2, '0')
                new_list.append(reformatted_date)
    return new_list


def decimal_point_validation(data_values_list):
    """ Changes the format of a float or an integer to two decimal places."""

    new_list = ["{:.2f}".format(num) for num in data_values_list]
    return new_list


def integer_validation(data_values_list, data_field_name):
    """ Validates the format of a list of numbers and returns and a new
     list containing only integers."""

    new_list = []
    for x in data_values_list:
        if type(x) != int and type(x) != float:
            print(str(data_field_name) + ": Error. Value " + str(x) + " must be an integer")
        elif type(x) == float:
            new_x = int(x)
            new_list.append(new_x)
        else:
            new_list.append(x)
    return new_list


def return_checkbox_col_field_names(data_field_name, metadata_choices_list):
    """ Returns a list of the new column names for the checkbox columns. These new column names
        are named with the convention 'data field name'___'choice from metadata'."""

    new_list = []
    for count in range(len(metadata_choices_list)):
        name = data_field_name + '___' + metadata_choices_list[count]
        new_list.append(name)
    return new_list


def return_checkbox_col_values(metadata_choice, checkbox_data_values):
    """ Returns a list of 0s and 1 based on whether the metadata_choice passed in
        is found in each row of the checkbox_data_values.
        1 is added if the metadata_choice is found, 0 if not."""

    new_list = []
    for choice in checkbox_data_values:
        if choice.find(metadata_choice) != -1:
            new_list.append(1)
        else:
            new_list.append(0)
    return new_list


def update_data_df_with_checkbox_cols(orig_data_df, col_field_names, col_values):
    """ Adds the checkbox columns to the existing data_df naming them with col_field_names
        and fills the columns with col_values"""

    for i, j in zip(col_field_names, col_values):
        orig_data_df[i] = j


def return_list_of_properly_formatted_field_names(field_names):
    """ Returns a list of properly formatted field names. White space is removed,
        and replaced with '_'. '/' and ',' are removed as well."""

    new_list = []
    for name in field_names:
        v1 = name.lower()
        v1 = v1.replace(' ', '_')
        v1 = v1.replace(',', '')
        if v1.find('/') != -1:
            v1 = v1.replace('/', '')
            v1 = v1.replace('__', '_')
            new_list.append(v1)
        else:
            new_list.append(v1)
    return new_list


def return_list_containing_only_data_values_that_match_metadata_choices(
        difference_list, source_list):
    """ Returns a list of data values that have had all the mismatches between metadata choices
        and data_values removed."""

    diff_list = source_list[:]
    for item in difference_list:
        diff_list.remove(item)
    return diff_list


# data_source = sys.argv[1]
# metadata_source = sys.arg[2]

# variable names for the files
data_source = 'G:\\My Documents\Python Scripts\\fake.csv'
metadata_source = 'G:\My Documents\Python Scripts\\breastDMT.csv'

# Creates DataFrames from the data_source and metadata_source
data_df = create_df(data_source)
metadata_df = create_df(metadata_source)

# converts column field names from data_df to a list to be compared to values in first column of metadata_df
data_field_names = list(data_df.columns)
# checks data_field_names and changes to proper format
data_field_names = return_list_of_properly_formatted_field_names(data_field_names)
# changes data_df's field names to the list of properly formatted field names
data_df.columns = data_field_names

# converts column field names from metadata_df to a list
metadata_field_names = list(metadata_df.columns)
# checks metadata_field_names and changes to proper format (metadata_df field names are referenced throughout the code)
metadata_field_names = return_list_of_properly_formatted_field_names(metadata_field_names)
# changes metadata_df's field names to the list of properly formatted field names
metadata_df.columns = metadata_field_names

# converts values from metadata_df's first column to a list to be compared to column field names in data_df
values_in_first_col_of_metadata_df = metadata_df.variable_field_name.tolist()

# list containing all the items in common between data_field_names and values_in_first_col_of_metadata_df
matches_between_data_field_names_and_metadata_first_col_values = return_matches_between_data_and_metadata(
    data_field_names, values_in_first_col_of_metadata_df)

# list containing items that were found in data_field_names but not the values_in_first_col_of_metadata_df
data_field_names_not_found_in_metadata_values = return_difference_between_data_and_metadata(
    data_field_names, values_in_first_col_of_metadata_df)

# a new data DataFrame that holds only the columns that matched the metadata_source
data_df_containing_only_matching_cols = return_data_df_containing_only_matching_cols(
    data_df, matches_between_data_field_names_and_metadata_first_col_values)
# a new metadata_source DataFrame that holds only the columns that matched the data
metadata_df_containing_only_matched_rows = \
    metadata_df.loc[metadata_df['variable_field_name'].isin(
        matches_between_data_field_names_and_metadata_first_col_values)]

# creates a list of all fields that are field type 'text' in the metadata_df
list_of_field_names_that_have_field_type_text_from_metadata_df = \
    list(metadata_df_containing_only_matched_rows.loc
         [metadata_df_containing_only_matched_rows['field_type'] == 'text', 'variable_field_name'])

# creates a list of all fields that are field type 'checkbox' in the metadata_df
list_of_field_names_that_have_field_type_checkbox_from_metadata_df = list(
    metadata_df_containing_only_matched_rows.loc[metadata_df_containing_only_matched_rows['field_type'] ==
                                                 'checkbox', 'variable_field_name'])

# Error reporting
# dictionary containing data_field_names that did not match the values_in_first_col_of_metadata_df
# and the index at which they are found in the data_df
data_dictionary_containing_error_value_and_index = return_value_and_index_dict(
    data_field_names_not_found_in_metadata_values, data_field_names)

if data_dictionary_containing_error_value_and_index:
    print('Field Name Errors')
    print('-----------------')
    # error message for fields that did not match between the data fields and metadata_source values
    error_message(data_dictionary_containing_error_value_and_index)

print()
print()
print('Value Errors')
print('---------------')
print("These values are not options found in the metadata_source:")

# iterates over the columns in the data_df that matched the first column of the metadata_df
for current_data_field_name in matches_between_data_field_names_and_metadata_first_col_values:

    # validate format of field type 'text'

    # Represents a list of items that are only 'text' field type and checks to make sure that the list is not empty
    if current_data_field_name in list_of_field_names_that_have_field_type_text_from_metadata_df:
        # Creates a series to check if the the text validation column is empty
        text_validation_values_series = \
            metadata_df_containing_only_matched_rows.loc[
                metadata_df_containing_only_matched_rows['variable_field_name'] ==
                current_data_field_name, 'text_validation_type_or_show_slider_number']

        # if the check validation column is not empty, format validation is needed
        if text_validation_values_series.any():
            text_validation_values_that_are_not_NaN_list = list(
                metadata_df_containing_only_matched_rows.loc[metadata_df_containing_only_matched_rows[
                                                                 'variable_field_name'] == current_data_field_name,
                                                             'text_validation_type_or_show_slider_number'])

            # Checks valid format for date
            if 'date' in text_validation_values_that_are_not_NaN_list[0]:
                date_data_values_list = list(
                    data_df_containing_only_matching_cols[current_data_field_name])
                updated_date_format_values = date_validation(
                    date_data_values_list, text_validation_values_that_are_not_NaN_list[0])
                data_df[current_data_field_name] = updated_date_format_values
                continue

            # checks and changes format to two decimal places
            elif text_validation_values_that_are_not_NaN_list[0] == 'number_2dp':
                data_values_with_decimal_point_text_validation_required = list(
                    data_df_containing_only_matching_cols[current_data_field_name])
                if all(isinstance(x, (int, float)) for x in
                       data_values_with_decimal_point_text_validation_required):
                    updated_data_values_with_correct_decimal_point_format = decimal_point_validation(
                        data_values_with_decimal_point_text_validation_required)
                    data_df[current_data_field_name] = updated_data_values_with_correct_decimal_point_format
                    continue
                else:
                    print("error ")

            # Validates if value is an integer
            elif text_validation_values_that_are_not_NaN_list[0] == 'integer':
                data_values_with_int_text_validation_required = list(
                    data_df_containing_only_matching_cols[current_data_field_name])
                updated_data_values_as_integers = integer_validation(
                    data_values_with_int_text_validation_required, current_data_field_name)
                data_df[current_data_field_name] = updated_data_values_as_integers
                continue

            else:
                pass
    else:
        # creates list of values found in the current_field_name column of the data_df
        orig_data_values_from_current_field_name_col = list(
            data_df_containing_only_matching_cols[current_data_field_name])

        # cleans data_values_from_current_field_name_col for comparison metadata_source choices
        cleaned_data_values_from_current_field_name_col = return_cleaned_data_values(
            orig_data_values_from_current_field_name_col)

        # creates a DataFrame to check if cell is empty
        metadata_df_to_check_for_null_choices = metadata_df.loc[metadata_df['variable_field_name'] ==
                                                                current_data_field_name,
                                                                'choices_calculations_or_slider_labels']

        # if cell is empty, metadata_source data comparison list becomes ['no', 'yes']
        # if it is not empty, than the choices must be parsed and cleaned so that
        # each item in the list is an individual choice
        if pd.isna(metadata_df_to_check_for_null_choices).bool():
            parsed_metadata_choices_list = ['no', 'yes']
        else:
            metadata_choices_for_one_row = list(metadata_df.loc[metadata_df['variable_field_name'] ==
                                                                current_data_field_name,
                                                                'choices_calculations_or_slider_labels'])
            parsed_metadata_choices_list = parse_metadata_choices(metadata_choices_for_one_row[0], '|')

        # list of data values found in the metadata_df choices
        data_values_that_match_metadata_choices = return_matches_between_data_and_metadata(
            parsed_metadata_choices_list, cleaned_data_values_from_current_field_name_col)

        # list of data values not found in the metadata_df choices
        data_values_that_do_not_match_metadata_choices = return_difference_between_data_and_metadata(
            cleaned_data_values_from_current_field_name_col, parsed_metadata_choices_list)

        # checkbox
        if current_data_field_name in list_of_field_names_that_have_field_type_checkbox_from_metadata_df:
            # creates a list of column names that will be added to the target df
            col_names_for_new_checkbox_cols = return_checkbox_col_field_names(
                current_data_field_name, parsed_metadata_choices_list)
            values_for_new_checkbox_cols = []
            counter = 0

            # while loop loops through the parsed metadata_source choices
            # and checks if that choice is an option in the data
            while counter < len(parsed_metadata_choices_list):
                values_for_new_checkbox_cols.append(
                    return_checkbox_col_values(parsed_metadata_choices_list[counter],
                                               cleaned_data_values_from_current_field_name_col))
                counter = counter + 1

            # updates data_df with the new checkbox columns
            update_data_df_with_checkbox_cols(
                data_df, col_names_for_new_checkbox_cols, values_for_new_checkbox_cols)
            # drops the current_data_field_name column in the new DataFrame
            data_df = data_df.drop(current_data_field_name, 1)
        else:
            list_of_data_values_that_only_contain_matches_with_metadata_choices = \
                return_list_containing_only_data_values_that_match_metadata_choices(
                    data_values_that_do_not_match_metadata_choices,
                    cleaned_data_values_from_current_field_name_col)

            # if there are mismatches, then an error message is needed
            if data_values_that_do_not_match_metadata_choices:
                data_error_values_and_index_dict = return_value_and_index_dict(
                    data_values_that_do_not_match_metadata_choices, cleaned_data_values_from_current_field_name_col)
                print(current_data_field_name + ": " + str(data_error_values_and_index_dict))

            # indexing
            # dictionary containing the matched data values and their index from the metadata_source
            matched_data_values_and_position_in_metadata_choices_dict = return_value_and_index_dict(
                list_of_data_values_that_only_contain_matches_with_metadata_choices,
                parsed_metadata_choices_list)
            # replace list of values with the indexes from the metadata_source list
            data_values_index_in_metadata_choices = return_index_of_data_values_in_metadata(
                cleaned_data_values_from_current_field_name_col,
                matched_data_values_and_position_in_metadata_choices_dict)
            # update data DataFrame column values
            data_df[current_data_field_name] = data_values_index_in_metadata_choices

# create new csv file from the updated data DataFrame containing the data transformations
data_df.to_csv('G:\My Documents\Python Scripts\\new_test_patient1.csv', index=False)
