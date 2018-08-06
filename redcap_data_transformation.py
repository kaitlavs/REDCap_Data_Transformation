import pandas as pd


def create_df(file_name):
    """ Returns a DataFrame from a cvs file """
    return pd.read_csv(file_name)


def return_matches(a, b):
    """ Returns a list of matches between two lists
        s = [1, 2, 3]
        t = [1, 3, 4, 5]

        >> return_matches(s, t)
        [1, 3]
    """
    matches = []
    for name in a:
        for line in b:
            if name == line:
                matches.append(name)
    return matches


def return_mismatches(a, b):
    """ Returns a list of items that do not match between two lists
        s = [1, 2, 3]
        t = [1, 3, 4, 5]

        >> return_mismatches(s, t)
        [2, 4, 5]
    """
    mismatches = [i for i in a + b if i not in a or i not in b]
    return mismatches


def error_message_overlap(a):
    """ Prints out the list of mismatches so
    the user knows to fix the column names from the patient data and rows
    from the metadata_source.

    ***Later versions can distinguish which document the mismatch is from.
    """
    print('The following column names and rows are not compatible: ')
    print(a)


def return_new_column_df(df, column_descriptor):
    """ Returns a new DataFrame with the specified column name/names in descriptor

        matches = return_new_column_df(patient, matches)
     """
    new_column_df = df[column_descriptor]
    return new_column_df


def return_new_row_df(df, column_name1, row_descriptor1, column_name2, row_descriptor2):
    """ Returns a new DataFrame with a specified value within a specified column

        radio_button = metadata_df.loc[metadata_df['field type'] == ' radio']
    """
    row_condition1 = df[column_name1] == row_descriptor1
    row_condition2 = df[column_name2].isin(row_descriptor2)
    new_loc_df = df.loc[row_condition1 & row_condition2]
    return new_loc_df


def return_all_choices(column_descriptor, df):
    """ Returns a list. This list holds the value held in each row of the selected
    column_descriptor
    *** change 'label' and 'choices' to the correct column names
    """
    choices = []
    for item in column_descriptor:
        single_line = list(df.loc[df['label'] == item, 'choices'])
        choices.append(single_line)
    return choices


def slice_list(lst, index):
    """ Returns one element from a father list based on index."""
    slist = []
    slist.append(lst[index][0])
    return slist


def parse_choices(sliced_list):
    """ A list containing one element is passed in. Returns a list containing elements
        parsed from the original one element."""
    pipe_num = sliced_list[0].count('|')
    parsed_list = []
    for count in range(pipe_num + 1):
        v1 = sliced_list[0].split('|')[count]
        v1 = v1.split(',')[1]
        v1 = v1.replace(' ', '')
        v1 = v1.lower()
        parsed_list.append(v1)
    return parsed_list


def parse_patient(list1):
    """ Returns a list with the spaces removed and made lowercase
        so it can be compared to the choices."""
    new_list = []
    for count in range(len(list1)):
        if type(list1[count]) != str:
            v1 = str(list1[count])
        else:
            v1 = list1[count]
        v1 = v1.replace(' ', '')
        v1 = v1.lower()
        new_list.append(v1)
    return new_list


def index_list(list1, list2, value):
    """ Checks if an item in list2 is found in list1. If the item is found in list1,
        the index + 1 of the item in list1 is returned in a list.

         metalist = ['male', 'female']
         patientlist = ['female', 'male', 'female', 'male', 'male']

         >> patient_values_index_in_metadata_choices(metalist, patientlist)
         [2, 1, 2, 1, 1]
    """
    indexlist = []
    for types in list2:
        if types not in list1:
            print("This value from patient data, column '" + str(value) + "' does not match: " + str(types))
            indexlist.append('NaN')
        else:
            if list1 == ['no', 'yes']:
                indexlist.append(list1.index(types))
            else:
                indexlist.append(list1.index(types) + 1)
    return indexlist


# variable names for the files
patient_data = 'G:\\My Documents\Python Scripts\\patient1.csv'
metadata = 'G:\\My Documents\Python Scripts\\meta1.csv'

# calls create_df to create the DataFrames
patient = create_df(patient_data)
meta = create_df(metadata)

# converts column names from patient data to a list to be compared to values in first column of metadata_source
p_names = patient.columns.tolist()
# converts values from metadata_source data to a list to be compared to column names in patient data
m_names = meta.label.tolist()

# a list of matches from the columns names in patient data and the first row in metadata_source
p_m_matches = return_matches(p_names, m_names)

# a new patient DataFrame that holds only the columns that matched the metadata_source
new_patient_df = return_new_column_df(patient, p_m_matches)

# *** add if/elif/else statement

# new DataFrames that hold the individual field types from the metadata_source
# *** change the final version
radio_df = return_new_row_df(meta, 'field type', 'radio', 'label', p_m_matches)
dropdown_df = return_new_row_df(meta, 'field type', 'dropdown', 'label', p_m_matches)
yesno_df = return_new_row_df(meta, 'field type', 'yesno', 'label', p_m_matches)
# checkbox_df = return_new_row_df(metadata_df, 'field type', 'checkbox')
# text_df = return_new_row_df(metadata_df, 'field type', 'text')

# converts the values in column 'label' from the individual field type DataFrames
# to a list
# *** change for the final version to 'Variable / Field Name'
r_patient_list = radio_df['label'].tolist()
yn_patient_list = yesno_df['label'].tolist()
d_patient_list = dropdown_df['label'].tolist()

# A metadata_source list that holds all the choice values from the individual
# field types
radio_options = return_all_choices(r_patient_list, radio_df)
yesno_options = return_all_choices(yn_patient_list, yesno_df)
dropdown_options = return_all_choices(d_patient_list, dropdown_df)


# while loop to slice, and parse the 'radio' metadata_source
counter1 = 0
while counter1 < len(r_patient_list):
    # list of one value containing multiple choices
    r_option = slice_list(radio_options, counter1)
    # list containing the parsed choices
    r_parsed_option = parse_choices(r_option)
    # the individual column name ex. 'gender'
    r_value = r_patient_list[counter1]
    # non-parsed patient data values
    vlist = new_patient_df[r_value].tolist()
    # parsed patient data values
    nlist = parse_patient(vlist)
    # list containing the index's of matching items from
    # the metadata_source choices and the patient data values
    r_index = index_list(r_parsed_option, nlist, r_value)
    # changes the original DataFrame to contain the indexed values
    # instead of the patient values
    patient[r_value] = r_index
    counter1 += 1

counter2 = 0
while counter2 < len(yn_patient_list):
    yn_list = ['no', 'yes']
    yn_value = yn_patient_list[counter2]
    ynlist_patient1 = new_patient_df[yn_value].tolist()
    ynlist_patient2 = parse_patient(ynlist_patient1)
    yn_index = index_list(yn_list, ynlist_patient2, yn_value)
    patient[yn_value] = yn_index
    counter2 += 1

counter3 = 0
while counter3 < len(d_patient_list):
    d_option = slice_list(dropdown_options, counter3)
    d_parsed_option = parse_choices(d_option)
    d_value = d_patient_list[counter3]
    dlist_patient1 = new_patient_df[d_value].tolist()
    dlist_patient2 = parse_patient(dlist_patient1)
    d_index = index_list(d_parsed_option, dlist_patient2, d_value)
    patient[d_value] = d_index
    counter3 += 1

patient.to_csv('G:\My Documents\Python Scripts\\new_test_patient1.csv', index=False)
