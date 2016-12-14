
import os
import pandas as pd
import numpy as np


if os.environ.get('USER') == "vagrant":
    repo_dir = os.path.dirname(
        os.path.dirname(os.path.realpath(__file__)))
else:
    repo_dir = os.path.realpath(".")


def read_csv(path):
    '''read csv using pandas
    '''
    return pd.read_csv(path, quotechar='\"',
                       na_values='', keep_default_na=False,
                       encoding='utf-8')


# load main data
data_csv = "{0}/data_prep/merged_data.csv".format(repo_dir)
data_df = read_csv(data_csv)

# initialize treatment field as -1
# for each case:
#   actual treatments will be set to 1
#   actual controls will be set to 0
# then all remaining (-1) can be dropped
data_df['treatment'] = -1

# add gef_id of -1 to random control points
# so we can match on field without nan errors
data_df.loc[data_df['type'] == 'rand', 'gef_id'] = -1
data_df['gef_id'] = data_df['gef_id'].astype('int').astype('str')


# load ancillary data
ancillary_01_csv = "{0}/raw_data/ancillary/CD_MFA_CD_projects_sheet.csv".format(repo_dir)
ancillary_02_csv = "{0}/raw_data/ancillary/CD_MFA_MFA_projects_sheet.csv".format(repo_dir)
ancillary_03_csv = "{0}/raw_data/ancillary/GEF_MFA_AidData_Ancillary.csv".format(repo_dir)
ancillary_04_csv = "{0}/raw_data/ancillary/gef_projects_160726.csv".format(repo_dir)

ancillary_01_df = read_csv(ancillary_01_csv)
ancillary_02_df = read_csv(ancillary_02_csv)
ancillary_03_df = read_csv(ancillary_03_csv)
ancillary_04_df = read_csv(ancillary_04_csv)

# -------------------------------------

land_id_list_00 = list(data_df.loc[data_df['type'] == 'land', 'gef_id'])


# check GEF project records (if any column contains "LD")
cnames_01 = [i for i in list(ancillary_01_df.columns) if i != 'GEF ID']
matches_01 = ['LD' in list(ancillary_01_df.iloc[i])
              for i in range(len(ancillary_01_df))]
land_id_list_01 = list(ancillary_01_df.loc[matches_01, 'GEF ID'].astype('str'))


cnames_02 = [i for i in list(ancillary_02_df.columns) if i != 'GEF ID']
matches_02 = ['LD' in list(ancillary_01_df.iloc[i])
              for i in range(len(ancillary_01_df))]
land_id_list_02 = list(ancillary_02_df.loc[matches_02, 'GEF ID'].astype('str'))


# check aiddata ancillary ("Sub-Foci" column)
land_keywords = ["LD", "Sustainable", "SFM", "REDD", "LULUCF",
                 "Land", "Degradation", "Degredation", "Sustainable"]

raw_matches = ancillary_03_df['Sub-Foci'].str.contains('|'.join(land_keywords))
clean_matches = [
    False if np.isnan(x) else x
    for x in raw_matches
]
land_id_list_03 = list(ancillary_03_df.loc[clean_matches, 'GEF_ID']
    .astype('int').astype('str'))


# combine different land id lists
land_id_list = land_id_list_00 + land_id_list_01 + land_id_list_02 + land_id_list_03
land_id_list = list(set(land_id_list))

# -------------------------------------

# # check geocoded land degradation
# bio_id_list = list(data_df.loc[data_df['type'] == 'bio', 'gef_id'])


# # check GEF project records (if any column contains "BD")
# cnames_03 = [i for i in list(ancillary_01_df.columns) if i != 'GEF ID']
# matches_03 = ['BD' in list(ancillary_01_df.iloc[i])
#               for i in range(len(ancillary_01_df))]
# bio_id_list_01 = list(ancillary_01_df.loc[matches_01, 'GEF ID'].astype('str'))


# cnames_04 = [i for i in list(ancillary_02_df.columns) if i != 'GEF ID']
# matches_04 = ['BD' in list(ancillary_01_df.iloc[i])
#               for i in range(len(ancillary_01_df))]
# bio_id_list_02 = list(ancillary_02_df.loc[matches_02, 'GEF ID'].astype('str'))


# # check aiddata ancillary ("Sub-Foci" column)
# bio_keywords = ["BD", "Biodiversity"]


# # combine different land id lists
# bio_id_list = bio_id_list_00 + bio_id_list_01 + bio_id_list_02 + bio_id_list_03
# bio_id_list = list(set(bio_id_list))

# -------------------------------------

# multi country
multicountry_id_list = list(set(ancillary_04_df.loc[ancillary_04_df["Country"].isin(["Regional", "Global"]), 'GEF_ID'].astype('int').astype('str')))

# multi agency
multiagency_id_list = list(set(ancillary_04_df.loc[ancillary_04_df["Secondary agency(ies)"].isnull(), 'GEF_ID'].astype('int').astype('str')))


# -----------------------------------------------------------------------------


def build_case(case_id, treatment, control):
    case_df = data_df.copy(deep=True)

    case_df.loc[treatment, 'treatment'] = 1
    case_df.loc[control, 'treatment'] = 0

    case_df = case_df.loc[case_df['treatment'] != -1]

    case_out = "{0}/data_prep/analysis_cases/{1}_data.csv".format(repo_dir, case_id)
    case_df.to_csv(case_out, index=False, encoding='utf-8')


print
# (M1)
#   Treatment:  Programmatic w/ LD objectives
#   Control:    Null Case Comparisons

m1t = (data_df['type'] == 'prog') & (data_df['gef_id'].isin(land_id_list))
m1c = (data_df['type'] == 'rand')
build_case('m1', m1t, m1c)


# (M2)
#   Treatment:  Programmatic w/ Biodiversity objectives
#   Control:    Null Case Comparisons

# m2t = (m2_df['type'] == 'prog') & (m2_df['gef_id'].isin(bio_id_list))
# m2c = (m2_df['type'] == 'rand')
# build_case('m2', m2t, m2c)


# (M3)
#   Treatment:  Programmatic w/ LD objectives
#   Control:    MFA w/ LD objectives

m3t = (data_df['type'] == 'prog') & (data_df['gef_id'].isin(land_id_list))
m3c = (data_df['type'] == 'mfa') & (data_df['gef_id'].isin(land_id_list))
build_case('m3', m3t, m3c)


# (M4)
#   Treatment:  Programmatic w/ Biodiversity objectives
#   Control:    MFA w/ Biodiversity objectives

# m4t = (m4_df['type'] == 'prog') & (m4_df['gef_id'].isin(bio_id_list))
# m4c = (m4_df['type'] == 'mfa') & (m4_df['gef_id'].isin(bio_id_list))
# build_case('m4', m4t, m4c)


# # (M5)
# #   Treatment:  Programmatic multi-country w/ LD objectives
# #   Control:    Non-programmatic single-country w/ LD objectives
# #               (aka: LD single-country)

m5t = ((data_df['type'] == 'prog')
       & (data_df['gef_id'].isin(land_id_list))
       & (data_df['gef_id'].isin(multicountry_id_list)))
m5c = ((data_df['type'] == 'land')
       & ~(data_df['gef_id'].isin(list(set(data_df.loc[data_df['type'] == "prog", 'gef_id']))))
       & ~(data_df['gef_id'].isin(multicountry_id_list)))
build_case('m5', m5t, m5c)


# # (M6)
# #   Treatment:  Programmatic multi-country w/ Biodiversity objectives
# #   Control:    Non-programmatic single-country w/ Biodiversity objectives
# #               (aka: Biodiversity single-country)

# m6t = ((m6_df['type'] == 'prog')
#        & (m6_df['gef_id'].isin(bio_id_list))
#        & (m6_df['gef_id'].isin(multicountry_id_list)))
# m6c = ((m6_df['type'] == 'bio')
#        & ~(m6_df['gef_id'].isin(list(set(m6_df.loc[m6_df['type'] == "prog", 'gef_id']))))
#        & ~(m6_df['gef_id'].isin(multicountry_id_list)))
# build_case('m6', m6t, m6c)


# # (M7)
# #   Treatment:  Programmatic multi-agency w/ LD objectives
# #   Control:    Non-programmatic single-agency w/ LD objectives
# #               (aka: LD single-agency)

m7t = ((data_df['type'] == 'prog')
       & (data_df['gef_id'].isin(land_id_list))
       & (data_df['gef_id'].isin(multiagency_id_list)))
m7c = ((data_df['type'] == 'land')
       & ~(data_df['gef_id'].isin(list(set(data_df.loc[data_df['type'] == "prog", 'gef_id']))))
       & ~(data_df['gef_id'].isin(multiagency_id_list)))
build_case('m7', m7t, m7c)


# (M8)
#   Treatment:  Programmatic multi-agency w/ Biodiversity objectives
#   Control:    Non-programmatic single-agency w/ Biodiversity objectives
#               (aka: Biodiversity single-agency)

# m8t = ((data_df['type'] == 'prog')
#        & (data_df['gef_id'].isin(bio_id_list))
#        & (data_df['gef_id'].isin(multiagency_id_list)))
# m8c = ((data_df['type'] == 'bio')
#        & ~(data_df['gef_id'].isin(list(set(data_df.loc[data_df['type'] == "prog", 'gef_id']))))
#        & ~(data_df['gef_id'].isin(multiagency_id_list)))
# build_case('m8', m8t, m8c)


# (M9)
#   Treatment:  Programmatic multi-country w/ LD objectives
#   Control:    Programmatic single-country w/ LD objectives

m9t = ((data_df['type'] == 'prog')
       & (data_df['gef_id'].isin(land_id_list))
       & (data_df['gef_id'].isin(multicountry_id_list)))
m9c = ((data_df['type'] == 'prog')
       & (data_df['gef_id'].isin(land_id_list))
       & ~(data_df['gef_id'].isin(multicountry_id_list)))
build_case('m9', m9t, m9c)


# (M10)
#   Treatment:  Programmatic multi-country w/ Biodiversity objectives
#   Control:    Programmatic single-country w/ Biodiversity objectives

# m10t = ((data_df['type'] == 'prog')
#        & (data_df['gef_id'].isin(bio_id_list))
#        & (data_df['gef_id'].isin(multicountry_id_list)))
# m10c = ((data_df['type'] == 'prog')
#        & (data_df['gef_id'].isin(bio_id_list))
#        & ~(data_df['gef_id'].isin(multicountry_id_list)))
# build_case('m10', m10t, m10c)


# (M11)
#   Treatment:  Programmatic multi-agency w/ LD objectives
#   Control:    Programmatic single-agency w/ LD objectives

m11t = ((data_df['type'] == 'prog')
       & (data_df['gef_id'].isin(land_id_list))
       & (data_df['gef_id'].isin(multiagency_id_list)))
m11c = ((data_df['type'] == 'prog')
       & (data_df['gef_id'].isin(land_id_list))
       & ~(data_df['gef_id'].isin(multiagency_id_list)))
build_case('m11', m11t, m11c)


# (M12)
#   Treatment:  Programmatic multi-agency w/ Biodiversity objectives
#   Control:    Programmatic single-agency w/ Biodiversity objectives

# m12t = ((data_df['type'] == 'prog')
#        & (data_df['gef_id'].isin(bio_id_list))
#        & (data_df['gef_id'].isin(multiagency_id_list)))
# m12c = ((data_df['type'] == 'prog')
#        & (data_df['gef_id'].isin(bio_id_list))
#        & ~(data_df['gef_id'].isin(multiagency_id_list)))
# build_case('m12', m12t, m12c)


