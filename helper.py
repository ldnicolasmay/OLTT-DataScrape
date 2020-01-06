# helper.py

import re

# Regex patterns for extracting IDs
ptrn_id_from_path = re.compile(r'^.*\/(\d{3,4}).*$', re.IGNORECASE)
ptrn_id_from_dottest = re.compile(r'^(\d+)-dottest-\w{14}.csv$', re.IGNORECASE)
ptrn_id_from_freercl = re.compile(r'^(\d+)-Free Recall-\w{14}.csv', re.IGNORECASE)
ptrn_id_from_cuedrcl = re.compile(r'^(\d+)-Cued Recall-\w{14}.csv', re.IGNORECASE)
ptrn_id_from_recognt = re.compile(r'^(\d+)-Recognition-\w{14}.csv', re.IGNORECASE)

# # Regex pattern for extracting visit numbers
ptrn_visit_num_from_path = re.compile(r'.*\/Visit (\d{3})\/.*', re.IGNORECASE)

# Regex patterns for reading CSV files
ptrn_dottest = re.compile(r'^\d+-dottest-\w{14}.csv$', re.IGNORECASE)
ptrn_freercl = re.compile(r'^\d+-Free Recall-\w{14}.csv$', re.IGNORECASE)
ptrn_cuedrcl = re.compile(r'^\d+-Cued Recall-\w{14}.csv$', re.IGNORECASE)
ptrn_recognt = re.compile(r'^\d+-Recognition-\w{14}.csv$', re.IGNORECASE)

# Regex pattern for extracting OLTT Set string: "7A" or "11A"
ptrn_oltt_set = re.compile(r'^.*/Test Set (\d+A) data/.*$')


def ptrn_id_switch(ptrn_id_str):
    switcher = {
        'path': ptrn_id_from_path,
        'dottest': ptrn_id_from_dottest,
        'freercl': ptrn_id_from_freercl,
        'cuedrcl': ptrn_id_from_cuedrcl,
        'recognt': ptrn_id_from_recognt,
    }
    return switcher.get(ptrn_id_str)


def get_id_from_(ptrn_id_str, path):
    ptrn_id_from_ = ptrn_id_switch(ptrn_id_str)
    re_id_from_ = re.search(ptrn_id_from_, path)
    id_from_ = int(re_id_from_.group(1))
    return id_from_


def get_oltt_set(path):
    re_oltt_set_from_path = re.search(ptrn_oltt_set, path)
    oltt_set_from_path = re_oltt_set_from_path.group(1)
    return oltt_set_from_path


def collapse_df_rows(df, grouping_cols=None, left_cols=None, right_cols=None):
    df_left = df.loc[:, grouping_cols + left_cols].dropna(axis='index', subset=left_cols).set_index(grouping_cols)
    df_right = df.loc[:, grouping_cols + right_cols].dropna(axis='index', subset=right_cols).set_index(grouping_cols)
    df_join = df_left.join(df_right, on=grouping_cols, how="outer").reset_index()
    return df_join