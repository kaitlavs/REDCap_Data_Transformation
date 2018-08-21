# Author: Kaitlyn Lavan -- klavan@fordham.edu
# Title: REDCap Data Convert(Version 0.7)
# Last Updated: 08/21/2018
#
# This script receives either an excel spreadsheet or CSV file as input, and outputs a CSV
# file that is ready to be uploaded into REDCap. The script also requires a data dictionary
# (metadata) as input. The script parses through the data dictionary to find the
# associated code that REDCap recognizes and replaces the data value with its associated
# code.
#
# Errors are defined as values that do not match any associated codes from the parsed
# data dictionary, or missing data. If there are errors in the data, then a CVS file is not
# outputted. Instead, an excel file is outputted that is a duplicate of the original data,
# except the background of the cells with errors are flagged pink. The end user is expected
# to fix all the errors and re-run the script. When all the errors have been fixed, then
# the final output is a CVS file that will be ready to upload to REDCap.
#
# REDCap deals with five different field types: Text, Checkbox, Yesno, Radio, and Dropdown.
# Text field types sometimes require special validation, such as month-day-year date
# formatting, or floats rounded to two decimal places. This script looks through the data
# field type text data and checks for missing data and fixes incorrect data formatting if
# special validation is required. If there is no validation required and no missing data,
# all text values are assumed to be correct.
# Checkbox field types are unique because REDCap requires a separate column for each
# permissible value found in the data dictionary.  Each separate column is filled with 1
# or 0 depending on whether that value has been checked or not.
# Yesno field types do not have permissible values in the data dictionary, so it is
# assumed that 1 = no, 2 = yes.
# Radio and Dropdown field types do not have any special cases and are both handled in
# the same manor.


import pandas as pd
import datetime
import xlsxwriter


def create_df_from_csv(file_name):
    """ Returns a DataFrame from a cvs file """

    return pd.read_csv(file_name)


def create_df_from_excel(file_name):
    """ Returns a DataFrame from a excel file"""

    return pd.read_excel(file_name)


def return_matches_between_data_and_metadata(data_list, metadata_list):
    """ Returns a list of all items common to the data_list and the metadata_list.

        data_list is either a list of the field names in the target_data_df or
        a list of values in a specified column in the target_data_df.

        metadata_list is either the values under the Variable / Field Name column in the metadata
        DataFrame or the choices found in the Choices, calculations, etc. column of the
        metadata DataFrame."""

    matches = list(set(metadata_list).intersection(data_list))
    return matches


def return_difference_between_data_and_metadata(data_list, metadata_list):
    """ Returns a list of all items found in the data list that
        is not found in the metadata list.

        data_list is either a list of the field names in the target_data_df or a list of values
        in a specified column in the target_data_df.

        metadata list is either the values under the Variable / Field Name column in the metadata
        DataFrame or the choices found in the Choices, calculations, etc. column of the
        metadata DataFrame."""

    difference = list(set(data_list).difference(metadata_list))
    return difference


def return_data_values_and_their_index_in_metadata_choices_or_data(data_values, metadata_choices):
    """ Returns a dictionary containing correct data values (data values that match choices found in
        the metadata_df's column: 'Choices, Calculations, OR Slider Labels
        Choices, Calculations, OR Slider Labels' and their index within this metadata column.

        When used for error reporting, returns a dictionary containing error data values and their
        index in the list of all data values in a specified column."""

    index_list = []
    for item in data_values:
        index_list.append(str(metadata_choices.index(item) + 1))
    values_index_dict = dict(zip(data_values, index_list))
    return values_index_dict


def return_checkbox_error_value_and_position_in_data(error_data_values, cleaned_values_list, orig_values_list):
    """ For field type checkbox, returns a dictionary containing erroneous data values (data values that do not match
        choices found in the metadata_df's column 'Choices, Calculations, OR Slider Labels'
        and their index within the list of values in a specified column in data_df.

        debug*** -- if an error value is a substring of a value in metadata_choices,
        and this metadata_choices value(a non-error value) is found in the list of data_values,
        then this non-error value is then reported as an error value.

        error value = axi
        metadata_choices value = axilla
        axilla will now be reported as an error value."""

    position_list = []
    for item in error_data_values:
        # creates a list of the indices where the error value appears in the cleaned_values_list
        error_index = [idx for idx, s in enumerate(cleaned_values_list) if item in s]
        # adds 1 to each value in error_index to represent the position
        position = [x + 1 for x in error_index]
        # extends position_list with the values in position
        position_list.extend(position)
        index_list = [x - 1 for x in position_list]
        result_list = [orig_values_list[i] for i in index_list]
    error_values_and_index_dict = dict(zip(result_list, position_list))
    return error_values_and_index_dict


def return_error_value_and_position_in_data(error_data_values, cleaned_values_list, orig_values_list):
    """ For all field types except checkbox, returns a dictionary containing erroneous data values
        (data values that do not match choices found in the metadata_df's column 'Choices, Calculations,
         OR Slider Labels' and their POSITION within the list of values in a specified in the data_df."""

    position_list = []
    for item in error_data_values:
        position_list.append(cleaned_values_list.index(item) + 1)
        index_list = [x - 1 for x in position_list]
        result_list = [orig_values_list[i] for i in index_list]
    error_values_and_index_dict = dict(zip(result_list, position_list))
    return error_values_and_index_dict


def return_error_field_name_and_index_in_data(error_data_values, cleaned_values_list, orig_values_list):
    """ For all field types except checkbox, returns a dictionary containing erroneous data values
        (data values that do not match choices found in the metadata_df's column 'Choices, Calculations,
         OR Slider Labels' and their INDEX within the list of values in a specified in the data_df."""
    index_list = []
    for item in error_data_values:
        index_list.append(cleaned_values_list.index(item))
        result_list = [orig_values_list[i] for i in index_list]
    error_values_and_index_dict = dict(zip(result_list, index_list))
    return error_values_and_index_dict


def error_message(ix_dict, log):
    """ Outputs an error message and a dictionary containing the value and the index of the
        difference in values between two lists."""

    log.write("These data field names do not match options found in the metadata:\n")
    log.write(str(ix_dict) + "\n")


def return_data_df_containing_only_matching_cols(orig_data_df, matches_between_data_and_metadata):
    """ Returns a data DataFrame that only contains the columns that matched
        with the metadata_df's column 'Variable / Field Name'."""

    data_matches_df = orig_data_df[matches_between_data_and_metadata]
    return data_matches_df


def return_cleaned_data_values(data_values_list):
    """ Returns a list of strings with whitespace at the beginning and end of a word removed,
        double spaces turned to one space, and all values made lowercase."""

    cleaned_data_values_list = []
    for count in range(len(data_values_list)):
        if type(data_values_list[count]) != str:
            if type(data_values_list[count]) == float:
                if not isnan(data_values_list[count]):
                    var1 = int(data_values_list[count])
                    var1 = str(var1)
                    cleaned_data_values_list.append(var1)
            else:
                var1 = str(data_values_list[count])
                var1 = var1.replace('  ', ' ')
                var1 = var1.strip()
                var1 = var1.lower()
                cleaned_data_values_list.append(var1)
    return cleaned_data_values_list


def parse_metadata_choices(metadata_choices_string, separator):
    """ Returns a list of strings parsed around the separator in metadata_choice_string.
        One string is passed in that contains all the metadata choices for a single column
        separated by the specified separator."""

    pipe_num = metadata_choices_string.count(separator)
    parsed_list = []
    for count in range(pipe_num + 1):
        var1 = metadata_choices_string.split(separator)[count]
        var1 = var1.split(',')[1]
        var1 = var1.strip()
        var1 = var1.replace('  ', ' ')
        var1 = var1.lower()
        parsed_list.append(var1)
    return parsed_list


def return_index_of_data_values_in_metadata(data_values_list, all_meta_choices_and_their_index):
    """ Returns a list of number strings that replaces keys with their
        value in a dictionary. This list is used to update the values of the columns
        in the data DataFrame.

        data_values_list is a list of all the values in the target_data_df of a specified column.
        all_choices_and_their_index is a dictionary containing the metadata_df choices as keys and
        the index of these choices as values."""

    string_list = ', '.join(data_values_list)
    for i, j in all_meta_choices_and_their_index.items():
        string_list = string_list.replace(i, j)
    back2list = string_list.split(',')
    return back2list


def date_validation(data_values_list, date_format_string):
    """ Validates the format of a list of strings and returns a new list with correct
        date formats. First, checks for missing data, and replaces empty data with an empty
        string."""

    import dateutil.parser

    new_list = []
    for str_date in data_values_list:
        if isnan(str_date):
            new_list.append(None)
        else:
            str_date = str(str_date)
            parsed_str_date = dateutil.parser.parse(str_date)
            if date_format_string == 'date_mdy':
                reformatted_date = str(parsed_str_date.month).rjust(2, '0') + '/' + str(
                    parsed_str_date.day).rjust(2, '0') + '/' + str(parsed_str_date.year)
                new_list.append(reformatted_date)
            elif date_format_string == 'date_dmy':
                reformatted_date = str(parsed_str_date.day).rjust(2, '0') + '/' + str(
                    parsed_str_date.month).rjust(2, '0') + '/' + str(parsed_str_date.year)
                new_list.append(reformatted_date)
            elif date_format_string == 'date_ymd':
                reformatted_date = str(parsed_str_date.year) + '/' + str(
                    parsed_str_date.month).rjust(2, '0') + '/' + str(parsed_str_date.day).rjust(2, '0')
                new_list.append(reformatted_date)
    return new_list


def decimal_point_validation(data_values_list):
    """ Changes the format of a float or an integer to two decimal places."""

    new_list = [None if isnan(num) else "{:.2f}".format(num) for num in data_values_list]
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
        elif isnan(x):
            new_list.append(None)
        else:
            new_list.append(x)
    return new_list


def no_text_validation_error_values_for_df(data_values):
    """Checks for missing data for values that are type text but do not require text
    validation. If data is missing, then True is appended. If not data is missing, than
    False is appended."""

    new_list = []
    for item in data_values:
        if isnan(item):
            new_list.append(True)
        else:
            new_list.append(False)
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
    """ Adds the checkbox columns to the existing target_data_df naming them with col_field_names
        and fills the columns with col_values"""

    for i, j in zip(col_field_names, col_values):
        orig_data_df[i] = j


def return_list_of_properly_formatted_field_names(field_names):
    """ Returns a list of properly formatted field names. White space is removed,
        and replaced with '_'. '/' and ',' are removed as well."""

    new_list = []
    for name in field_names:
        var1 = name.lower()
        var1 = var1.replace(' ', '_').replace(',', '').replace('  ', '_').replace('__', '_')
        if var1.find('/') != -1:
            var1 = var1.replace('/', '').replace('__', '_')
            new_list.append(var1)
        else:
            new_list.append(var1)
    return new_list


def return_values_that_match_metadata_choices(
        difference_list, source_list):
    """ Returns a list of data values that contains only the values that have matched those within
        the metadata_choices. All the mismatches between metadata choices and data_values are removed."""

    match_list = source_list[:]
    for item in difference_list:
        match_list.remove(item)
    return match_list


def parse_checkbox_data_values(checkbox_value_string, separator):
    """ A single value from a checkbox column is passed in a parsed around the separator.
        The parsed checkbox value is used for error reporting."""

    parsed_list = []
    pipe_num = checkbox_value_string.count(separator)
    for count in range(pipe_num + 1):
        var1 = checkbox_value_string.split(separator)[count]
        var1 = var1.replace(' ', '')
        var1 = var1.lower()
        parsed_list.append(var1)
    return parsed_list


def change_cell_background_color(col_index_list, worksheet, formatting):
    """ col_index list is a list of the indices of erroneous field names within the
        data_df.
        worksheet is the name of the worksheet being used for xlsxwriter
        row_length is the number of values found in the specified column"""

    for index in col_index_list:
        worksheet.set_column(index, index, 20, formatting)


def text_validation_values_for_error_df(updated_date_list):
    """ Appends False to a list if no error has been found, and appends True when an error has been
        found. This list is then added to the values in the corresponding column in the error_data_df."""

    new_list = []
    for choice in updated_date_list:
        if choice:
            new_list.append(False)
        else:
            new_list.append(True)
    return new_list


def checkbox_values_for_error_df(error_value_indices, data_values):
    """ Appends False to a list if no checkbox error has been found, and appends True when an error has
        been found. This list is then added to the values in the corresponding column in the
        error_data_df. """

    num_of_values = len(data_values)
    true_false_list = [False] * num_of_values
    for index in error_value_indices:
        true_false_list[index] = True
    return true_false_list


def isnan(num):
    """ Checks if a item in a list is NaN."""

    return num != num


def main():
    # variable names for the files
    data_source = 'G:\\My Documents\Python Scripts\\seizure - mytest.xlsx'
    metadata_source = 'G:\My Documents\Python Scripts\\GliomaDashboard_DataDictionary_2018-08-08.csv'

    # *** adds 1 to a list every time an error is experienced.
    total_error_count = []

    # open error log text file
    error_log = open("redcap_error_log.txt", "w+")
    # captures current data and time
    now = datetime.datetime.now()
    # writes now, and the files used to the error log
    error_log.write(str(now) + "\n")
    error_log.write("Data dictionary file used: " + metadata_source + "\n")
    error_log.write("Data file used: " + data_source + "\n")

    # Checks whether the data_source is a csv file or an excel file
    if data_source.endswith('.csv'):
        # Creates DataFrame from the data_source csv file
        data_df = create_df_from_csv(data_source)
    elif data_source.endswith('.xlsx') or data_source.endswith('.xls'):
        # Creates DataFrame from the data_source excel file
        data_source_excel = pd.ExcelFile(data_source)
        # If there is more than one sheet in the excel file, asks the user to specify which sheet
        if len(data_source_excel.sheet_names) > 1:
            print("There are multiple excel sheets within " + data_source + ". Please specify a sheet name.")
            excel_sheet = input("Enter sheet name: ")
            data_df = pd.read_excel(data_source, excel_sheet)
        else:
            data_df = create_df_from_excel(data_source)
    else:
        error_log.write("Incorrect file type. Only .csv, .xls, and .xlsx are supported.")

    # Checks whether the metadata_source is a csv file or an excel file
    if metadata_source.endswith('.csv'):
        # Creates DataFrame from the metadata_source csv file
        metadata_df = create_df_from_csv(metadata_source)
    elif metadata_source.endswith('.xlsx') or metadata_source.endswith('.xls'):
        # Creates DataFrame from the metadata_source excel file
        metadata_source_excel = pd.ExcelFile(metadata_source)
        # If there is more than one sheet in the excel file, asks the user to specify which sheet
        if len(metadata_source_excel.sheet_names) > 1:
            print("There are multiple excel sheets within " + metadata_source + ". Please specify a sheet name.")
            excel_sheet = input("Enter sheet name: ")
            metadata_df = pd.read_excel(metadata_source, excel_sheet)
    else:
        error_log.write("Incorrect file type. Only .csv, .xls, and .xlsx are supported.")

    # create a copy of data_df to update with correctly formatted values
    target_data_df = data_df.copy(deep=True)
    # create an empty DataFrame with the same dimensions as data_df for error reporting
    error_data_df = pd.DataFrame().reindex_like(data_df)

    # converts column field names from target_data_df to a list to be compared to values in first column of metadata_df
    data_field_names = list(target_data_df.columns)
    # checks data_field_names and changes to proper format
    reformatted_data_field_names = return_list_of_properly_formatted_field_names(data_field_names)

    # changes field names to the list of properly formatted field names
    target_data_df.columns = reformatted_data_field_names
    data_df.columns = reformatted_data_field_names
    error_data_df.columns = reformatted_data_field_names

    # converts column field names from metadata_df to a list
    metadata_field_names = list(metadata_df.columns)
    # checks metadata_field_names and changes to proper format because these field names
    # are referenced throughout the code
    metadata_field_names = return_list_of_properly_formatted_field_names(metadata_field_names)
    # changes metadata_df's field names to the list of properly formatted field names
    metadata_df.columns = metadata_field_names

    # converts values from metadata_df's first column to a list to be compared to column field names in data_df
    values_in_first_col_of_metadata_df = metadata_df.variable_field_name.tolist()

    # converts values from metadata_df's Field Label column to a list to be compared to column field
    # names in data_df
    field_label_metadata_values = metadata_df.field_label.tolist()
    # reformat reformatted_field_label_metadata_values
    reformatted_field_label_metadata_values = return_list_of_properly_formatted_field_names(field_label_metadata_values)
    metadata_df.field_label = reformatted_field_label_metadata_values

    # items in common between reformatted_data_field_names and values_in_first_col_of_metadata_df
    # matches_between_data_field_names_and_metadata_first_col_values = return_matches_between_data_and_metadata(
    #    reformatted_data_field_names, values_in_first_col_of_metadata_df)

    matches_between_data_field_names_and_metadata_field_label_values = return_matches_between_data_and_metadata(
        reformatted_data_field_names, reformatted_field_label_metadata_values)

    # items that were found in reformatted_data_field_names but not in values_in_first_col_of_metadata_df
    # data_field_names_not_found_in_metadata_first_col_values = return_difference_between_data_and_metadata(
    # reformatted_data_field_names, values_in_first_col_of_metadata_df)

    # items that were found in reformatted_data_field names but not in field label values in the metadata
    data_field_names_not_found_in_metadata_field_label = return_difference_between_data_and_metadata(
        reformatted_data_field_names, reformatted_field_label_metadata_values)

    # values_for_error_df is a list of 0s and 1s to be placed in the error_df. 1 means an error was
    # found, while 0 means no error was found.
    counter4 = 0
    while counter4 < len(data_field_names_not_found_in_metadata_field_label):
        error_data_df[data_field_names_not_found_in_metadata_field_label[counter4]] = True
        counter4 = counter4 + 1

    # add values_for_error_df to the error_df
    # error_data_df.columns = values_for_error_df

    # a new data DataFrame that holds only the columns that matched the metadata_source
    data_df_containing_only_matching_cols = return_data_df_containing_only_matching_cols(
        target_data_df, matches_between_data_field_names_and_metadata_field_label_values)
    # a new metadata_source DataFrame that holds only the columns that matched the data
    metadata_df_containing_only_matched_rows = \
        metadata_df.loc[metadata_df['field_label'].isin(
            matches_between_data_field_names_and_metadata_field_label_values)]

    # creates a list of all fields that are field type 'text' in the metadata_df
    list_of_field_names_that_have_field_type_text_from_metadata_df = \
        list(metadata_df_containing_only_matched_rows.loc
             [metadata_df_containing_only_matched_rows['field_type'] == 'text', 'field_label'])

    # creates a list of all fields that are field type 'checkbox' in the metadata_df
    list_of_field_names_that_have_field_type_checkbox = list(
        metadata_df_containing_only_matched_rows.loc[metadata_df_containing_only_matched_rows['field_type'] ==
                                                     'checkbox', 'field_label'])

    # Field Label error reporting

    # dictionary containing reformatted_data_field_names that did not match the values_in_first_col_of_metadata_df
    # and the position at which they are found in the target_data_df
    field_name_error_value_and_index = return_data_values_and_their_index_in_metadata_choices_or_data(
        data_field_names_not_found_in_metadata_field_label, reformatted_data_field_names)

    if field_name_error_value_and_index:
        total_error_count.append(1)
        error_log.write("\n")
        error_log.write('Field Name Errors\n')
        error_log.write('-----------------\n')
        # error message for fields that did not match between the data fields and metadata_source values
        error_message(field_name_error_value_and_index, error_log)
        error_log.write("Was expecting one of these values: \n")
        error_log.write(str(values_in_first_col_of_metadata_df))

    error_log.write("\n")
    error_log.write("\n")
    error_log.write('Value Errors\n')
    error_log.write('---------------\n')
    error_log.write("These values are not options found in the metadata_source:\n")

    # list of column names that have error values in them, used later to format
    # new excel spreadsheet with pink colored errors
    data_col_names_containing_errors = []

    # iterates over the field name's in the data_df that matched the field label values of the metadata_df
    for ix, current_data_field_name in enumerate(matches_between_data_field_names_and_metadata_field_label_values):

        # validate format of field type 'text'
        # Represents a list of items that are only 'text' field type in the metadata_df
        # and checks to make sure that the list is not empty
        if current_data_field_name in list_of_field_names_that_have_field_type_text_from_metadata_df:
            # Creates a series to check if the the 'text validation' column in the metadata_df is empty
            text_validation_values_series = \
                metadata_df_containing_only_matched_rows.loc[
                    metadata_df_containing_only_matched_rows['field_label'] ==
                    current_data_field_name, 'text_validation_type_or_show_slider_number']
            # if the check validation column is not empty, format validation is needed
            if text_validation_values_series.any():
                text_validation_values_that_are_not_nan_list = list(
                    metadata_df_containing_only_matched_rows.loc[metadata_df_containing_only_matched_rows[
                                                                     'field_label'] == current_data_field_name,
                                                                 'text_validation_type_or_show_slider_number'])

                # Checks valid format for date
                if 'date' in text_validation_values_that_are_not_nan_list[0]:
                    # list of all date values in a specified column
                    date_data_values_list = list(
                        data_df_containing_only_matching_cols[current_data_field_name])
                    # list of date values in correct data format
                    updated_date_format_values = date_validation(
                        date_data_values_list, text_validation_values_that_are_not_nan_list[0])
                    # list of Trues(error) and False(no error) based on errors found in date values
                    date_error_values_for_error_df = text_validation_values_for_error_df(updated_date_format_values)
                    # adds these True/False error values to the error_data_df
                    error_data_df[current_data_field_name] = date_error_values_for_error_df
                    # adds corrected data formats to target_data_df
                    target_data_df[current_data_field_name] = updated_date_format_values

                # checks and changes format to two decimal places
                elif text_validation_values_that_are_not_nan_list[0] == 'number_2dp':
                    # list of decimal point values in a specified column
                    data_values_with_decimal_point_text_validation_required = list(
                        data_df_containing_only_matching_cols[current_data_field_name])
                    # if all values are of type int or float, then update their format
                    if all(isinstance(x, (int, float)) for x in
                           data_values_with_decimal_point_text_validation_required):
                        updated_data_values_with_correct_decimal_point_format = decimal_point_validation(
                            data_values_with_decimal_point_text_validation_required)
                        # list of True(error) and False(no error) based on errors found within these values
                        decimal_point_error_values_for_error_df = text_validation_values_for_error_df(
                            updated_data_values_with_correct_decimal_point_format)
                        # adds these True/False error values to the error_data_df
                        error_data_df[current_data_field_name] = decimal_point_error_values_for_error_df
                        # adds corrected data formats to target_data_df
                        target_data_df[current_data_field_name] = updated_data_values_with_correct_decimal_point_format
                    else:
                        total_error_count.append(1)
                        data_col_names_containing_errors.append(current_data_field_name)
                        error_log.write("Error. Cannot convert column" + current_data_field_name +
                                        "to two decimal places.\n")

                # Validates if value is an integer
                elif text_validation_values_that_are_not_nan_list[0] == 'integer':
                    # list of values in a specified column
                    data_values_with_int_text_validation_required = list(
                        data_df_containing_only_matching_cols[current_data_field_name])
                    # converted values to type int
                    updated_data_values_as_integers = integer_validation(
                        data_values_with_int_text_validation_required, current_data_field_name)
                    integer_error_values_for_error_df = text_validation_values_for_error_df(
                        updated_data_values_as_integers)
                    error_data_df[current_data_field_name] = integer_error_values_for_error_df
                    # add updated values to target_data_df
                    target_data_df[current_data_field_name] = updated_data_values_as_integers

                else:
                    pass
            # if there is no text validation required, there are no errors to report
            elif not text_validation_values_series.any():
                no_text_validation_required_values = data_df[current_data_field_name]
                no_text_validation_error_values = no_text_validation_error_values_for_df(
                    no_text_validation_required_values)
                error_data_df[current_data_field_name] = no_text_validation_error_values
        else:
            # creates list of values found in the current_field_name column of the data_df
            orig_data_values_from_current_field_name_col = list(
                data_df_containing_only_matching_cols[current_data_field_name])

            # the number of values found within each column
            # number_of_values_in_each_col = len(orig_data_values_from_current_field_name_col)

            # cleans data_values_from_current_field_name_col for comparison metadata_source choices
            cleaned_data_values_from_current_field_name_col = return_cleaned_data_values(
                orig_data_values_from_current_field_name_col)

            # creates a DataFrame to check if cell is empty
            metadata_df_to_check_for_null_choices = metadata_df.loc[metadata_df['field_label'] ==
                                                                    current_data_field_name,
                                                                    'choices_calculations_or_slider_labels']

            # if cell is empty, metadata_source data comparison list becomes ['no', 'yes']
            # if it is not empty, than the choices must be parsed and cleaned so that
            # each item in the list is an individual choice
            if metadata_df_to_check_for_null_choices.dropna().empty:
                parsed_metadata_choices_list = ['no', 'yes']
            else:
                metadata_choices_for_one_row = list(metadata_df.loc[metadata_df['field_label'] ==
                                                                    current_data_field_name,
                                                                    'choices_calculations_or_slider_labels'])
                parsed_metadata_choices_list = parse_metadata_choices(metadata_choices_for_one_row[0], '|')

            # list of data values found in the metadata_df choices
            # data_values_that_match_metadata_choices = return_matches_between_data_and_metadata(
                # parsed_metadata_choices_list, cleaned_data_values_from_current_field_name_col)

            # list of data values not found in the metadata_df choices
            data_values_that_do_not_match_metadata_choices = return_difference_between_data_and_metadata(
                cleaned_data_values_from_current_field_name_col, parsed_metadata_choices_list)

            # checkbox
            if current_data_field_name in list_of_field_names_that_have_field_type_checkbox:
                # creates a list of column names that will be added to the target_df
                col_names_for_new_checkbox_cols = return_checkbox_col_field_names(
                    current_data_field_name, parsed_metadata_choices_list)

                values_for_new_checkbox_cols = []
                counter1 = 0
                # loops through the parsed metadata choices
                # and checks if that choice is an option in the data
                while counter1 < len(parsed_metadata_choices_list):
                    values_for_new_checkbox_cols.append(
                        return_checkbox_col_values(parsed_metadata_choices_list[counter1],
                                                   cleaned_data_values_from_current_field_name_col))
                    counter1 = counter1 + 1

                # check for errors
                counter2 = 0
                checkbox_values_that_do_not_match_metadata_choices = []
                # loops through orig_data_values_from_current_field_name_col and parses
                # these values so they can be compared to the parsed_metadata_choices_list
                while counter2 < len(orig_data_values_from_current_field_name_col):
                    parsed_checkbox_data_values = parse_checkbox_data_values(
                        orig_data_values_from_current_field_name_col[counter2], '|')
                    checkbox_values_one_row_non_matches = return_difference_between_data_and_metadata(
                        parsed_checkbox_data_values, parsed_metadata_choices_list)
                    if checkbox_values_one_row_non_matches:
                        checkbox_values_that_do_not_match_metadata_choices.append(checkbox_values_one_row_non_matches)
                    counter2 = counter2 + 1

                if checkbox_values_that_do_not_match_metadata_choices:
                    total_error_count.append(1)
                    data_col_names_containing_errors.append(current_data_field_name)
                    # flattens list of lists
                    checkbox_values_that_do_not_match_metadata_choices = [
                        val for sublist in checkbox_values_that_do_not_match_metadata_choices for val in sublist]
                    checkbox_error_values_and_index_dict = return_checkbox_error_value_and_position_in_data(
                        checkbox_values_that_do_not_match_metadata_choices,
                        cleaned_data_values_from_current_field_name_col, orig_data_values_from_current_field_name_col)
                    checkbox_error_index_list = list(checkbox_error_values_and_index_dict.values())
                    checkbox_error_index_list = [x - 1 for x in checkbox_error_index_list]
                    checkbox_error_values_for_error_df = checkbox_values_for_error_df(
                        checkbox_error_index_list, cleaned_data_values_from_current_field_name_col)
                    error_data_df[current_data_field_name] = checkbox_error_values_for_error_df
                    error_log.write(current_data_field_name + ": " + str(checkbox_error_values_and_index_dict))
                else:
                    # updates target_data_df with the new checkbox columns
                    update_data_df_with_checkbox_cols(
                        target_data_df, col_names_for_new_checkbox_cols, values_for_new_checkbox_cols)
                    # drops the current_data_field_name column in the new DataFrame
                    target_data_df = target_data_df.drop(current_data_field_name, 1)
            else:
                list_of_data_values_that_only_contain_matches_with_metadata_choices = \
                    return_values_that_match_metadata_choices(
                        data_values_that_do_not_match_metadata_choices,
                        cleaned_data_values_from_current_field_name_col)

                # if there are mismatches, then an error message is needed
                if data_values_that_do_not_match_metadata_choices:
                    total_error_count.append(1)
                    data_col_names_containing_errors.append(current_data_field_name)
                    data_error_values_and_index_dict = return_error_value_and_position_in_data(
                        data_values_that_do_not_match_metadata_choices, cleaned_data_values_from_current_field_name_col,
                        orig_data_values_from_current_field_name_col)
                    other_error_index_list = list(data_error_values_and_index_dict.values())
                    other_error_index_list = [x - 1 for x in other_error_index_list]
                    other_error_values_for_error_df = checkbox_values_for_error_df(
                        other_error_index_list, cleaned_data_values_from_current_field_name_col)
                    error_data_df[current_data_field_name] = other_error_values_for_error_df
                    error_log.write(current_data_field_name + ": " + str(data_error_values_and_index_dict) + "\n")
                elif not data_values_that_do_not_match_metadata_choices:
                    error_data_df[current_data_field_name] = False
                else:
                    # indexing
                    # dictionary containing the matched data values and their index from the metadata_source
                    matched_data_values_and_position_in_metadata_choices_dict = \
                        return_data_values_and_their_index_in_metadata_choices_or_data(
                            list_of_data_values_that_only_contain_matches_with_metadata_choices,
                            parsed_metadata_choices_list)
                    # replace list of values with the indexes from the metadata_source list
                    data_values_index_in_metadata_choices = return_index_of_data_values_in_metadata(
                        cleaned_data_values_from_current_field_name_col,
                        matched_data_values_and_position_in_metadata_choices_dict)
                    # update data DataFrame column values
                    target_data_df[current_data_field_name] = data_values_index_in_metadata_choices

    # if there are errors throughout the file, return an Excel file containing the
    # original data with error cells colored pink and a text file that explains the
    # the errors found
    if total_error_count:

        # Create a Pandas Excel writer using XlsxWriter as the engine.
        writer = pd.ExcelWriter('redcap_excel_errors.xlsx', engine='xlsxwriter')

        # Convert data_df to an XlsxWriter Object
        data_df.to_excel(writer, sheet_name='Sheet1', index=False)

        # Get the xlsxwriter objects from the DataFrame writer object
        data_workbook = writer.book
        data_worksheet = writer.sheets['Sheet1']

        formats = data_workbook.add_format()
        formats.set_bg_color('#FF00FF')

        error_cols = list(error_data_df.columns)
        for index, row in error_data_df.iterrows():
            if row.any():
                for j, col in enumerate(error_cols):
                    if error_data_df.iloc[index][col]:
                        if not isnan(data_df.iloc[index][col]):
                            target_string = data_df.iloc[index][col]
                        else:
                            target_string = 'NaN'
                        data_worksheet.write(index+1, j, target_string, formats)

        # Close the Pandas Excel writer and output the Excel file
        writer.save()
    else:
        # create new csv file from the updated data DataFrame containing the data transformations
        target_data_df.to_csv('G:\My Documents\Python Scripts\\new_test_patient1.csv', index=False)

    error_log.close()


if __name__ == "__main__":
    main()
