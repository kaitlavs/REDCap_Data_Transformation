import pandas as pd
# import sys


def create_df(file_name):
    """ Returns a DataFrame from a cvs file """

    return pd.read_csv(file_name)


def return_patient_data_metadata_matches(patient_data_list, metadata_list):
    """ Returns a list of all items common to both metadata lists and patient data lists.
        patient_data_list is either a list of the field names of the patient DataFrame or
        a list of values in a specified column of the patient DataFrame.

        metadata_list is either the values under the Variable column in the metadata DataFrame or
        the choices found in the Choices, calculations, etc. column of the metadata DataFrame."""

    matches = list(set(metadata_list).intersection(patient_data_list))
    return matches


def return_patient_data_metadata_difference(patient_data_list, metadata_list):
    """ Returns a list of all items found in the patient data list that
        is not found in the metadata list."""

    difference = list(set(patient_data_list).difference(metadata_list))
    return difference


def return_error_value_and_index_dict(patient_error_values, meta_data_list):
    """ Returns a dictionary created from @error_values (these values
        are the keys in the dictionary) and ix (a list containing
        the index of items in error_values)"""

    index_list = []
    for item in patient_error_values:
        index_list.append(str(meta_data_list.index(item)+1))
    error_values_and_index_dict = dict(zip(patient_error_values, index_list))
    return error_values_and_index_dict


def error_message(ix_dict):
    """ Outputs an error message and a dictionary containing the value and the index of the
        uncommon values between two lists."""

    print("These patient data field names do not match options found in the metadata_source:")
    print(ix_dict)


def return_new_patient_df_containing_patient_field_name_matches(patient_df, patient_metadata_matches):
    """ Returns a new patient DataFrame that only contains the columns that have been properly
        matched with Variable values in the metadata DataFrame."""

    new_patient_matches_df = patient_df[patient_metadata_matches]
    return new_patient_matches_df


def return_cleaned_patient_values(patient_values_list):
    """ Returns a list of strings with whitespace removed and all lowercase
        letters."""

    cleaned_patient_values_list = []
    for count in range(len(patient_values_list)):
        if type(patient_values_list[count]) != str:
            v1 = str(patient_values_list[count])
        else:
            v1 = patient_values_list[count]
        v1 = v1.replace(' ', '')
        v1 = v1.lower()
        cleaned_patient_values_list.append(v1)
    return cleaned_patient_values_list


def parse_metadata_choices(sliced_metadata_choices_list):
    """ @sliced_metadata_choices_list: A list containing only one element of the
        metadata Choices, calculations, etc. values to be parsed into
        multiple elements.

        Returns a list of strings containing elements parsed from the original one element."""

    pipe_num = sliced_metadata_choices_list[0].count('|')
    parsed_list = []
    for count in range(pipe_num + 1):
        v1 = sliced_metadata_choices_list[0].split('|')[count]
        v1 = v1.split(',')[1]
        v1 = v1.replace(' ', '')
        v1 = v1.lower()
        parsed_list.append(v1)
    return parsed_list


def return_index_of_patient_values_in_metadata(patient_values_list, value_index_dict):
    """ Returns a list of number strings that replaces keys with their
        value in a dictionary. This list is used to update the values of the columns
        in the patient DataFrame."""

    strlist = ', '.join(patient_values_list)
    for i, j in value_index_dict.items():
        strlist = strlist.replace(i, j)
    back2list = strlist.split(',')
    return back2list


def date_validation(patient_values_list, current_patient_field_name):
    """ Validates the format of a list of strings and returns an error message
        if the date format is incorrect."""

    import datetime
    for str_date in patient_values_list:
        str_date = str(str_date)
        try:
            datetime.datetime.strptime(str_date, '%m/%d/%Y')
        except:
            print(current_patient_field_name + ": " + str_date + " is in incorrect date format, should be mm/dd/yy")


def dp_validation(patient_values_list):
    """ Changes the format of a float or an integer to two decimal places."""

    new_list = ["{:.2f}".format(num) for num in patient_values_list]
    return new_list


def integer_validation(patient_values_list, current_patient_field_name):
    """ Validates the format of a list of numbers and returns and a new
     list containing only integers."""

    new_list = []
    for x in patient_values_list:
        if type(x) != int and type(x) != float:
            print(str(current_patient_field_name) + ": Error. Value " + str(x) + " must be an integer")
        elif type(x) == float:
            new_x = int(x)
            new_list.append(new_x)
        else:
            new_list.append(x)
    return new_list


def error_values(patient_value_errors_list, patient_values_list):
    """ Returns a dictionary containing the error value and its
        index in the list of all patient values from that specified column
        (if the value is not from the checkbox. If it is, returns
        an empty dictionary.).
        *** debug """

    for item in patient_value_errors_list:
        if item.find('|') == -1:
            dict1 = return_error_value_and_index_dict(patient_value_errors_list, patient_values_list)
        else:
            dict1 = {}
    return dict1


def return_new_checkbox_col_names(current_patient_field_name, metadata_choices_calcs_list):
    """ Returns a list of the new column names for the checkbox. These new column names
        are named with the convention 'patient field name'___'choice from metadata'."""

    new_list = []
    for count in range(len(metadata_choices_calcs_list)):
        name = current_patient_field_name + '___' + metadata_choices_calcs_list[count]
        new_list.append(name)
    return new_list


def return_patient_df_with_new_checkbox_cols_added(patient_df, col_fields, col_values):
    """ Creates new columns from a list of columns and adds the values from a col_values list."""

    for i, j in zip(col_fields, col_values):
        patient_df[i] = j


def return_checkbox_col_values(current_patient_field_name, checkbox_patient_values):
    """ Returns the values needed for the new checkbox columns"""

    new_list = []
    for choice in checkbox_patient_values:
        if choice.find(current_patient_field_name) != -1:
            new_list.append(1)
        else:
            new_list.append(0)
    return new_list


def iterations(metadata_list, patient_data_list):
    """ Iterates through the metadata_df list and calls return_cb_values
        to obtain the checkbox values."""

    for choice in metadata_list:
        new_list = return_checkbox_col_values(choice, patient_data_list)
    return new_list


def return_list_of_properly_formatted_field_names(field_names):
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


# variable names for the files
# patient_data_source = sys.argv[1]
# metadata_source = sys.arg[2]

patient_data_source = 'G:\\My Documents\Python Scripts\\breast_practice_patient.csv'
metadata_source = 'G:\\csv files\\BreastDMT.csv'

# Creates DataFrames from the patient_data_source and metadata_source
patient_data_df = create_df(patient_data_source)
metadata_df = create_df(metadata_source)

# converts column field names from patient_data_df to a list to be compared to values in first column of metadata_df
patient_data_field_names = patient_data_df.columns.tolist()
# checks patient_data_field_names and changes to proper format
patient_data_field_names = return_list_of_properly_formatted_field_names(patient_data_field_names)
# changes patient_data_df's field names to the list of properly formatted field names
patient_data_df.columns = patient_data_field_names

# converts column field names from metadata_df to a list
metadata_field_names = list(metadata_df.columns)
# checks metadata_field_names and changes to proper format
metadata_field_names = return_list_of_properly_formatted_field_names(metadata_field_names)
# changes metadata_df's field names to the list of properly formatted field names
metadata_df.columns = metadata_field_names

# converts values from metadata_source to a list to be compared to column field names in patient data
values_in_first_col_of_metadata_df = metadata_df.variable_field_name.tolist()

# list containing all the items in common between patient_data_field_names and values_in_first_col_of_metadata_df
patient_field_name_matches_from_meta_data_first_col_values = return_patient_data_metadata_matches(
    patient_data_field_names, values_in_first_col_of_metadata_df)

# list containing items that were found in patient data field names but not the metadata_source
patient_field_names_not_found_in_metadata_values = return_patient_data_metadata_difference(
    patient_data_field_names, values_in_first_col_of_metadata_df)

# Error reporting
# dictionary containing the field names from patient data that did not match the metadata_source values
patient_dictionary_containing_error_value_and_index = return_error_value_and_index_dict(
    patient_field_names_not_found_in_metadata_values, patient_data_field_names)

# a new patient DataFrame that holds only the columns that matched the metadata_source
new_patient_df_containing_only_matching_cols = return_new_patient_df_containing_patient_field_name_matches(
    patient_data_df, patient_field_name_matches_from_meta_data_first_col_values)
# a new metadata_source DataFrame that holds only the columns that matched the patient data
new_metadata_df_containing_only_matched_rows = \
    metadata_df.loc[metadata_df['variable_field_name'].isin(
        patient_field_name_matches_from_meta_data_first_col_values)]

# creates a list of all fields that are field type 'text'
list_of_field_names_that_have_field_type_text_from_metadata_df = \
    list(new_metadata_df_containing_only_matched_rows.loc
         [new_metadata_df_containing_only_matched_rows['field_type'] == 'text', 'variable_field_name'])

# creates a list of all fields that are field type 'checkbox'
list_of_field_names_that_have_field_type_checkbox_from_metadata_df = list(
    new_metadata_df_containing_only_matched_rows.loc[new_metadata_df_containing_only_matched_rows['field_type'] ==
                                                     'checkbox', 'variable_field_name'])


print('Field Name Errors')
print('-----------------')

# error message for fields that did not match between the patient data fields and metadata_source values
error_message(patient_dictionary_containing_error_value_and_index)

print()
print()
print('Value Errors')
print('---------------')
print("These values are not options found in the metadata_source:")

# iterates over the columns in the patient DataFame
for field_name_match in patient_field_name_matches_from_meta_data_first_col_values:

    # validate format of field type 'text'

    # Represents a list of items that are only 'text' field type
    # and checks to make sure that the list is not empty
    if field_name_match in list_of_field_names_that_have_field_type_text_from_metadata_df:
        # Creates a series to check if the the text validation column is empty
        text_validation_values_series = new_metadata_df_containing_only_matched_rows.loc[
            new_metadata_df_containing_only_matched_rows['field_type'] ==
            'text', 'text_validation_type_or_show_slider_number']

        # if the check validation column is not empty, format validation is needed
        if text_validation_values_series.any():
            text_validation_values_that_are_not_NaN_list = list(new_metadata_df_containing_only_matched_rows.loc[
                                     new_metadata_df_containing_only_matched_rows['variable_field_name'] ==
                                     field_name_match, 'text_validation_type_or_show_slider_number'])

            # Checks valid format for date
            if text_validation_values_that_are_not_NaN_list[0] == 'date_mdy':
                patient_values_with_date_text_validation_required = list(
                    new_patient_df_containing_only_matching_cols[field_name_match])
                date_validation(patient_values_with_date_text_validation_required, field_name_match)
                continue

            # Changes format to two decimal places
            elif text_validation_values_that_are_not_NaN_list[0] == 'number_2dp':
                patient_values_with_decimal_point_text_validation_required = list(
                    new_patient_df_containing_only_matching_cols[field_name_match])
                if all(isinstance(x, (int, float)) for x in
                       patient_values_with_decimal_point_text_validation_required):
                    updated_patient_values_with_correct_decimal_point_format = dp_validation(
                        patient_values_with_decimal_point_text_validation_required)
                    patient_data_df[field_name_match] = updated_patient_values_with_correct_decimal_point_format
                    continue
                else:
                    print("error ")

            # Validates if value is an integer
            elif text_validation_values_that_are_not_NaN_list[0] == 'integer':
                patient_values_with_int_text_validation_required = list(
                    new_patient_df_containing_only_matching_cols[field_name_match])
                updated_patient_values_as_integers = integer_validation(
                    patient_values_with_int_text_validation_required, field_name_match)
                patient_data_df[field_name_match] = updated_patient_values_as_integers
                continue

            else:
                pass
    else:
        # creates list of values found in the columns in patient data
        patient_values_from_field_name_match_col = list(new_patient_df_containing_only_matching_cols[field_name_match])

        # cleans patient_values_from_field_name_match_col for comparison metadata_source choices
        patient_values_from_field_name_match_col = return_cleaned_patient_values(
            patient_values_from_field_name_match_col)

        # creates a DataFrame to check if cell is empty
        metadata_df_to_check_for_null_choices = metadata_df.loc[metadata_df['variable_field_name'] == field_name_match,
                                                                'choices_calculations_or_slider_labels']

        # if cell is empty, metadata_source data comparison list becomes ['no', 'yes']
        # if it is not empty, than the choices must be parsed and cleaned
        # so that each item in the list is an individual choice
        if pd.isna(metadata_df_to_check_for_null_choices).bool():
            parsed_metadata_choices_list = ['no', 'yes']
        else:
            metadata_choices_list = list(metadata_df.loc[metadata_df['variable_field_name'] ==
                                                         field_name_match, 'choices_calculations_or_slider_labels'])
            parsed_metadata_choices_list = parse_metadata_choices(metadata_choices_list)

        # list of patient data values found in the metadata_source choices
        patient_values_that_match_metadata_choices = return_patient_data_metadata_matches(
            parsed_metadata_choices_list, patient_values_from_field_name_match_col)

        # list of patient data values not found in the metadata_source choices
        patient_values_that_do_not_match_metadata_choices = return_patient_data_metadata_difference(
            patient_values_from_field_name_match_col, parsed_metadata_choices_list)

        # if there are no mismatches, then an error message is not required.
        if patient_values_that_do_not_match_metadata_choices:
            patient_error_values_and_index_dict = error_values(
                patient_values_that_do_not_match_metadata_choices, patient_values_from_field_name_match_col)
            if patient_error_values_and_index_dict != {}:
                print(field_name_match + ": " + str(patient_error_values_and_index_dict))

        # checkbox
        if field_name_match in list_of_field_names_that_have_field_type_checkbox_from_metadata_df:
            # creates a list of column names that will be added to the target df
            col_names_for_new_checkbox_cols = return_new_checkbox_col_names(
                field_name_match, parsed_metadata_choices_list)
            values_for_new_checkbox_cols = []
            counter = 0

            # while loop loops through the parsed metadata_source choices
            # and checks if that choice is an option in the patient data
            while counter < len(parsed_metadata_choices_list):
                values_for_new_checkbox_cols.append(
                    return_checkbox_col_values(parsed_metadata_choices_list[counter],
                                               patient_values_from_field_name_match_col))
                counter = counter + 1

            # creates a new DataFrame with the new checkbox columns
            return_patient_df_with_new_checkbox_cols_added(
                patient_data_df, col_names_for_new_checkbox_cols, values_for_new_checkbox_cols)
            # drops the field_name_match column in the new DataFrame
            # *** add this to the function above
            patient_data_df = patient_data_df.drop(field_name_match, 1)
        else:

            # indexing
            # dictionary containing the matched patient values and their index from the metadata_source
            matched_patient_values_and_position_in_metadata_choices_dict = return_error_value_and_index_dict(
                patient_values_from_field_name_match_col, parsed_metadata_choices_list)
            # replace list of values with the indexes from the metadata_source list
            patient_values_index_in_metadata_choices = return_index_of_patient_values_in_metadata(
                patient_values_from_field_name_match_col,
                matched_patient_values_and_position_in_metadata_choices_dict)
            # update patient DataFrame column values
            patient_data_df[field_name_match] = patient_values_index_in_metadata_choices

# create new csv file from the updated patient DataFrame containing the data transformations
patient_data_df.to_csv('G:\My Documents\Python Scripts\\new_test_patient1.csv', index=False)

