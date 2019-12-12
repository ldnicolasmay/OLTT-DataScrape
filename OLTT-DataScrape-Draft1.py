#!/usr/bin/env python

# Import modules
import os
import re
import pandas as pd
from typing import List, Dict
from datetime import date

import helpers as hlps
import config as cfg
import helper as hlp


# Top-level directory to all OLTT data
oltt_path = "/Users/ldmay/Box/Documents/OLTTDataScrape/OLTT Data/"

# Regex patterns for extracting IDs
ptrn_id_from_path = re.compile(r'^.*\/(\d+)$', re.IGNORECASE)
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

# Column names in CSVs with data
# cols_dottest = [' total error cm', ' avg error cm', ' median error cm',
#                 ' total error px', ' avg error px', ' median error px',
#                 ' total time', ' average time', ' median time']
# cols_frcurcl = ['total error cm', ' avg error cm', ' median error cm',
#                 ' total error px', ' avg error px', ' median error px',
#                 ' total time', ' average time', ' median time']
# cols_recognt = [' total correct', ' total time', ' avg time', ' median time']
cols_dotrcll = [' avg error cm', ' average time']
cols_recognt = [' total correct', ' avg time']

file_sets: List[Dict] = []
# file_set = {'path': "", 'dottest': "", 'freercl': "", 'cuedrcl': "", 'recognt': ""}

records: List[Dict] = []
# record = {'ptid': None, 'visit_num': None,
#           'path': "", 'dottest': "", 'freercl': "", 'cuedrcl': "", 'recognt': "",
#           # OLTT Set 7A fields
#           'dot_cal_aerr': None, 'dot_cal_at': None,
#           'fr_aerr': None, 'fr_at': None,
#           'cr_aerr': None, 'cr_at': None,
#           'rt_correct': None, 'ra_time': None,
#           # OLTT Set 11A FIELDS
#           'dot_cal_aerr_11a': None, 'dot_cal_at_11a': None,
#           'fr_aerr_11a': None, 'fr_at_11a': None,
#           'cr_aerr_11a': None, 'cr_at_11a': None,
#           'rt_correct_11a': None, 'ra_time_11a': None}

# Walk over the directory tree to find OLTT data files
print("Recursing through directory tree to find CSVs with OLTT data...")
for path_dirs_files in os.walk(oltt_path):
# for path_dirs_files in list(os.walk(oltt_path))[0:30]:
    # print(path_dirs_files)
    path, files = path_dirs_files[0], path_dirs_files[2]

    file_set = {'path': path,
                'dottest': "",
                'freercl': "",
                'cuedrcl': "",
                'recognt': ""}

    df_set = {'dottest': pd.DataFrame(),
              'freercl': pd.DataFrame(),
              'cuedrcl': pd.DataFrame(),
              'recognt': pd.DataFrame()}

    for file in files:
        if re.match(ptrn_dottest, file):
            file_set['dottest'] = file
        if re.match(ptrn_freercl, file):
            file_set['freercl'] = file
        if re.match(ptrn_cuedrcl, file):
            file_set['cuedrcl'] = file
        if re.match(ptrn_recognt, file):
            file_set['recognt'] = file

    files_not_missing = file_set['dottest'] != "" and file_set['freercl'] != "" and \
                        file_set['cuedrcl'] != "" and file_set['recognt'] != ""

    # Print info about record -- for testing
    if files_not_missing:
        # print(f"{file_set['path']}; all files present")
        file_sets.append(file_set)

# Iterate over file_sets to extract IDs and Visit Numbers, and add those to the record
print("Extracting IDs and Visit Numbers...")
for file_set in file_sets:
    # print(file_set)

    # Extract IDs from different sources
    try:
        id_from_path = hlp.get_id_from_('path', file_set['path'])
        id_from_dottest = hlp.get_id_from_('dottest', file_set['dottest'])
        id_from_freercl = hlp.get_id_from_('freercl', file_set['freercl'])
        id_from_cuedrcl = hlp.get_id_from_('cuedrcl', file_set['cuedrcl'])
        id_from_recognt = hlp.get_id_from_('recognt', file_set['recognt'])
    except:
        id_from_path = None
        id_from_dottest = None
        id_from_freercl = None
        id_from_cuedrcl = None
        id_from_recognt = None
        raise ValueError(f"Not all IDs extractable for {file_set['path']}")

    ids_match = id_from_path is not None and \
                id_from_path == id_from_dottest and id_from_path == id_from_freercl and \
                id_from_path == id_from_cuedrcl and id_from_path == id_from_recognt

    # print(f"IDs -- path: {id_from_path}; dottest: {id_from_dottest}; "
    #       f"freercl: {id_from_freercl}; cuedrcl: {id_from_cuedrcl}; recognt: {id_from_recognt}")

    if ids_match:
        id_int = id_from_path
        id_is_old_cohort = 543 <= id_int <= 1041
    else:
        id_int = None
        id_is_old_cohort = None

    # Extract visit number from path
    if ids_match:
        try:
            re_visit_num_from_path = re.search(ptrn_visit_num_from_path, file_set['path'])
            visit_num_from_path = int(re_visit_num_from_path.group(1))
            adj_visit_num_from_path = visit_num_from_path + 1 if id_is_old_cohort else visit_num_from_path
            redcap_visit_str = "visit_" + str(adj_visit_num_from_path) + "_arm_1"
        except:
            raise ValueError(f"Visit Number not extractable from {file_set['path']}")
    else:
        visit_num_from_path = None
        adj_visit_num_from_path = None

    # print(f"Visit Nums -- path: {visit_num_from_path}; adjusted: {adj_visit_num_from_path}")

    # If IDs match and the Visit Number is extractable, add those, the path, and the filenames to the record
    if ids_match and visit_num_from_path:
        record = {'ptid': "UM" + "0"*(8-len(str(id_int))) + str(id_int),
                  'visit_num': visit_num_from_path,
                  'adj_visit_num': adj_visit_num_from_path,
                  'redcap_event_name': redcap_visit_str,
                  'path': file_set['path'], 'dottest': file_set['dottest'],
                  'freercl': file_set['freercl'], 'cuedrcl': file_set['cuedrcl'], 'recognt': file_set['recognt']}
        records.append(record)

# Iterate over records to extract OLTT Set string, read relevant CSVs to DFs, and get data from DFs
print("Retrieving data from CSVs:")
for record in records:
    # print(record['path'])

    try:
        oltt_set = hlp.get_oltt_set(record['path'])
    except:
        oltt_set = None
        raise ValueError(f"OLTT Set string not extractable from {record['path']}")

    if oltt_set:
        record['oltt_set'] = oltt_set

    print(f"    Retrieving data for ID {record['ptid']}, "
          f"REDCap visit number {record['adj_visit_num']}, "
          f"with OLTT Set {record['oltt_set']}...")

    # Read relevant data from CSV files to DFs
    try:
        df_dottest = pd.read_csv(record['path'] + "/" + record['dottest'],
                                 usecols=cols_dotrcll,
                                 skiprows=4).dropna().reset_index(drop=True)
        df_freercl = pd.read_csv(record['path'] + "/" + record['freercl'],
                                 usecols=cols_dotrcll,
                                 skiprows=4).dropna().reset_index(drop=True)
        df_cuedrcl = pd.read_csv(record['path'] + "/" + record['cuedrcl'],
                                 usecols=cols_dotrcll,
                                 skiprows=4).dropna().reset_index(drop=True)
        df_recognt = pd.read_csv(record['path'] + "/" + record['recognt'],
                                 usecols=cols_recognt,
                                 skiprows=4).dropna().reset_index(drop=True)
    except:
        raise ValueError(f"Could not read CSVs to DFs within {record['path']}")

    if record['oltt_set'] == "7A":
        # OLTT Set 7A fields
        if df_dottest.shape[0] > 0:
            record['dot_cal_aerr'] = df_dottest.loc[0, ' avg error cm']
            record['dot_cal_at'] = df_dottest.loc[0, ' average time']
        if df_freercl.shape[0] > 0:
            record['fr_aerr'] = df_freercl.loc[0, ' avg error cm']
            record['fr_at'] = df_freercl.loc[0, ' average time']
        if df_cuedrcl.shape[0] > 0:
            record['cr_aerr'] = df_cuedrcl.loc[0, ' avg error cm']
            record['cr_at'] = df_cuedrcl.loc[0, ' average time']
        if df_recognt.shape[0] > 0:
            record['rt_correct'] = int(df_recognt.loc[0, ' total correct'])
            record['ra_time'] = df_recognt.loc[0, ' avg time']
    elif record['oltt_set'] == "11A":
        # OLTT Set 11A FIELDS
        if df_dottest.shape[0] > 0:
            record['dot_cal_aerr_11a'] = df_dottest.loc[0, ' avg error cm']
            record['dot_cal_at_11a'] = df_dottest.loc[0, ' average time']
        if df_freercl.shape[0] > 0:
            record['fr_aerr_11a'] = df_freercl.loc[0, ' avg error cm']
            record['fr_at_11a'] = df_freercl.loc[0, ' average time']
        if df_cuedrcl.shape[0] > 0:
            record['cr_aerr_11a'] = df_cuedrcl.loc[0, ' avg error cm']
            record['cr_at_11a'] = df_cuedrcl.loc[0, ' average time']
        if df_recognt.shape[0] > 0:
            record['rt_correct_11a'] = int(df_recognt.loc[0, ' total correct'])
            record['ra_time_11a'] = df_recognt.loc[0, ' avg time']
    else:
        raise ValueError(f"OLTT Set is not either 7A or 11A; check {record['path']}")

# Aggregate records into a DF
print("Aggregating records... ")
cols_redcap = ['ptid', 'redcap_event_name',
               "dot_cal_aerr", "dot_cal_at",
               "fr_aerr", "fr_at",
               "cr_aerr", "cr_at",
               "rt_correct", "ra_time",
               "dot_cal_aerr_11a", "dot_cal_at_11a",
               "fr_aerr_11a", "fr_at_11a",
               "cr_aerr_11a", "cr_at_11a",
               "rt_correct_11a", "ra_time_11a"]
# print(pd.DataFrame.from_records(records))
df_oltt_all = pd.DataFrame.\
    from_records(records)[cols_redcap].\
    sort_values(["ptid", "redcap_event_name"]).\
    reset_index(drop=True)

# Split the OLTT DF into initial- and follow-up-visit DFs
is_init_visit = df_oltt_all['redcap_event_name'] == 'visit_1_arm_1'
is_fllw_visit = (df_oltt_all['redcap_event_name'] != 'visit_1_arm_1') & df_oltt_all['redcap_event_name'].notnull()
df_oltt_iv = df_oltt_all[is_init_visit]
df_oltt_fv = df_oltt_all[is_fllw_visit]

# Filter aggregated records for those whose data is already entered in REDCap
print("Filtering the aggregated records by those whose forms are completed in REDCap UMMAP - UDS3...")

# Define IDs and fields to retrieve from REDCap, UMMAP - UDS3 project
ids_raw = df_oltt_all['ptid'].unique()
ids = ",".join(ids_raw)

fields_iv_raw = ["ptid",
                 "form_date",
                 "header_complete",
                 "ivp_a1_complete",
                 "ivp_a2_complete",
                 "ivp_a3_complete",
                 "ivp_a4_complete",
                 "ivp_a5_complete",
                 "ivp_b1_complete",
                 "ivp_b4_complete",
                 "ivp_b5_complete",
                 "ivp_b6_complete",
                 "ivp_b7_complete",
                 "ivp_b8_complete",
                 "ivp_b9_complete",
                 # "ivp_c2_complete",
                 "ivp_d1_complete",
                 "ivp_d2_complete"]
fields_iv = ",".join(fields_iv_raw)

fields_fv_raw = ["ptid",
                 "form_date",
                 "header_complete",
                 "fvp_a1_complete",
                 "fvp_a2_complete",
                 "fvp_a3_complete",
                 "fvp_a4_complete",
                 # "fvp_a5_complete",
                 "fvp_b1_complete",
                 "fvp_b4_complete",
                 "fvp_b5_complete",
                 "fvp_b6_complete",
                 "fvp_b7_complete",
                 "fvp_b8_complete",
                 "fvp_b9_complete",
                 # "fvp_c1_complete",
                 # "fvp_c2_complete",
                 "fvp_d1_complete",
                 "fvp_d2_complete"]
fields_fv = ",".join(fields_fv_raw)

fields = fields_iv + fields_fv

# Retrieve data from REDCap
print("Retrieving REDCap UMMAP - UDS3 data via API...")
df_u3 = hlps.export_redcap_records(uri=cfg.REDCAP_API_URI,
                                   token=cfg.REDCAP_API_TOKEN_UDS3n,
                                   fields=fields,
                                   records=ids)

# Define Boolean Series for filtering DFs
is_init_visit = df_u3['redcap_event_name'] == 'visit_1_arm_1'
is_fllw_visit = (df_u3['redcap_event_name'] != 'visit_1_arm_1') & df_u3['redcap_event_name'].notnull()

form_date_notnull = df_u3['form_date'].notnull()
header_comp = df_u3['header_complete'] == 2

ivp_a1_comp = df_u3['ivp_a1_complete'] == 2
ivp_a2_comp = df_u3['ivp_a2_complete'] == 2
ivp_a3_comp = df_u3['ivp_a3_complete'] == 2
ivp_a4_comp = df_u3['ivp_a4_complete'] == 2
ivp_a5_comp = df_u3['ivp_a5_complete'] == 2
ivp_b1_comp = df_u3['ivp_b1_complete'] == 2
ivp_b4_comp = df_u3['ivp_b4_complete'] == 2
ivp_b5_comp = df_u3['ivp_b5_complete'] == 2
ivp_b6_comp = df_u3['ivp_b6_complete'] == 2
ivp_b7_comp = df_u3['ivp_b7_complete'] == 2
ivp_b8_comp = df_u3['ivp_b8_complete'] == 2
ivp_b9_comp = df_u3['ivp_b9_complete'] == 2
# ivp_c2_comp = df_u3['ivp_c2_complete'] == 2
ivp_d1_comp = df_u3['ivp_d1_complete'] == 2

ivp_all_comp = ivp_a1_comp & ivp_a2_comp & ivp_a3_comp & ivp_a4_comp & ivp_a5_comp & \
               ivp_b1_comp & ivp_b4_comp & ivp_b5_comp & ivp_b6_comp & ivp_b7_comp & ivp_b8_comp & ivp_b9_comp & \
               ivp_d1_comp

fvp_a1_comp = df_u3["fvp_a1_complete"] == 2
fvp_a2_comp = df_u3["fvp_a2_complete"] == 2
fvp_a3_comp = df_u3["fvp_a3_complete"] == 2
fvp_a4_comp = df_u3["fvp_a4_complete"] == 2
# fvp_a5_comp = df_u3["fvp_a5_complete"] == 2
fvp_b1_comp = df_u3["fvp_b1_complete"] == 2
fvp_b4_comp = df_u3["fvp_b4_complete"] == 2
fvp_b5_comp = df_u3["fvp_b5_complete"] == 2
fvp_b6_comp = df_u3["fvp_b6_complete"] == 2
fvp_b7_comp = df_u3["fvp_b7_complete"] == 2
fvp_b8_comp = df_u3["fvp_b8_complete"] == 2
fvp_b9_comp = df_u3["fvp_b9_complete"] == 2
# fvp_c1_comp = df_u3["fvp_c1_complete"] == 2
# fvp_c2_comp = df_u3["fvp_c2_complete"] == 2
fvp_d1_comp = df_u3["fvp_d1_complete"] == 2
fvp_d2_comp = df_u3["fvp_d2_complete"] == 2

fvp_all_comp = fvp_a1_comp & fvp_a2_comp & fvp_a3_comp & fvp_a4_comp & \
               fvp_b1_comp & fvp_b4_comp & fvp_b5_comp & fvp_b6_comp & fvp_b7_comp & fvp_b8_comp & fvp_b9_comp & \
               fvp_d1_comp & fvp_d2_comp

# Filter UMMAP - UDS3 DFs for only those records that have completed forms
df_u3_iv_flt = df_u3[is_init_visit & form_date_notnull & header_comp & ivp_all_comp]
df_u3_fv_flt = df_u3[is_fllw_visit & form_date_notnull & header_comp & fvp_all_comp]

df_u3_iv_flt_sel = df_u3_iv_flt[['ptid', 'redcap_event_name']]
df_u3_fv_flt_sel = df_u3_fv_flt[['ptid', 'redcap_event_name']]

# Use merge to filter OLTT DFs for only those records that have completed forms
print("Filtering OLTT data for those records whose forms are completed in REDCap UMMAP - UDS3...")
df_oltt_iv_flt = pd.merge(df_u3_iv_flt_sel, df_oltt_iv,
                          how='inner', on=['ptid', 'redcap_event_name'],
                          left_index=False, right_index=False)
df_oltt_fv_flt = pd.merge(df_u3_fv_flt_sel, df_oltt_fv,
                          how='inner', on=['ptid', 'redcap_event_name'],
                          left_index=False, right_index=False)

# Combine the initial- and follow-up-visit OLTT DFs into on DF
print("Combining all OLTT data...")
df_oltt_flt = pd.concat([df_oltt_iv_flt, df_oltt_fv_flt], axis='rows').\
    sort_values(['ptid', 'redcap_event_name']).\
    reset_index(drop=True)

# Coerce count columns to int
df_oltt_flt['rt_correct'] = pd.Series(df_oltt_flt['rt_correct'], dtype='Int64')
df_oltt_flt['rt_correct_11a'] = pd.Series(df_oltt_flt['rt_correct_11a'], dtype='Int64')

# Add `oltt_complete` field and set to 2 (since a record's inclusion in this DF means it's complete)
df_oltt_flt['oltt_complete'] = 2

# Write the combined OLTT DF to CSV
print("Writing CSV file for REDCap import... ")

today = date.today()
today_str = f"{today.year}-{today.month}-{today.day}"
if not os.path.isdir("./oltt_data_to_import"):
    os.mkdir("./oltt_data_to_import")
if not os.path.isdir(f"./oltt_data_to_import/{today_str}"):
    os.mkdir(f"./oltt_data_to_import/{today_str}")
df_oltt_flt.to_csv(f"./oltt_data_to_import/{today_str}/oltt_data_to_import-{today_str}.csv", index=False)

print("Done.")
