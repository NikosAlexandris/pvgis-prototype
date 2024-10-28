import csv

csv_filename = "example_pv_estimation_output.csv"


def csv_to_list_of_dictionaries(csv_file):
    """Build a list of dictionaries from the records (lines) of a CSV file

    Parameters
    ----------
    csv_file :
        A string indicating the input CSV's file name

    Returns
    -------
    list_of_dictionaries :
        List of dictionaries

    Examples
    --------
    ..
    """
    csv_dictionary_reader = csv.DictReader(open(csv_file))
    dictionaries_list = []
    for line in csv_dictionary_reader:
        dictionaries_list.append(line)
    return dictionaries_list
