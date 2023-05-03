#########################################################################
# ADOBE CONFIDENTIAL
# ___________________
#
# Copyright 2022 Adobe
# All Rights Reserved.
#
# NOTICE: All information contained herein is, and remains
# the property of Adobe and its suppliers, if any. The intellectual
# and technical concepts contained herein are proprietary to Adobe
# and its suppliers and are protected by all applicable intellectual
# property laws, including trade secret and copyright laws.
# Dissemination of this information or reproduction of this material
# is strictly forbidden unless prior written permission is obtained
# from Adobe.
##########################################################################


import sys
import csv
import json
import os.path
import collections
import statistics
import numpy as np
from generate_table_data import get_design_ids, load_consolidated_jsons

participant_field_names = ["session_id", "task_version", "exclude_session", "total_score", "is_iphone", "num_tasks_excluded",
               "session_avg_zscore_correct", "session_avg_zscore", 'age', 'is_woman', 'is_non_binary', 'is_native', 
               'learning_disibility', 'difficulty_seeing', 'corrected_vision', 'table_familiarity', 
               'default_font_right', 'default_font_small', 'phone_reading_diff',
               ]

task_field_names = ["session_id", "task_version", "exclude_session", "total_score", "is_iphone", "num_tasks_excluded",
               "session_avg_zscore_correct", "session_avg_zscore", 'age', 'is_woman', 'is_non_binary', 'is_native', 
               'learning_disibility', 'difficulty_seeing', 'corrected_vision', 'table_familiarity', 
               'default_font_right', 'default_font_small', 'phone_reading_diff',

               "style_id", "task_idx", "task_idx_frac", "is_first_half_task", "table_idx", "is_practice_task", "exclude_task", "correctness", 
               "task_time", "task_time_zscore", "difficulty_score", "satisfaction_score"]
task_csv_entry = collections.namedtuple("task_data", task_field_names)

def robust_mean(vals):
    if vals:
        return statistics.mean(vals)
    else:
        return 0.

def z_transform(time, normal):
    mean = normal['mean']
    std = normal['std']
    z_time = (time - mean) / std
    return z_time


_default_tup = tuple(12 * [None])
def load_survey_data(fn):
    session_id_to_survey_data = collections.defaultdict(lambda: _default_tup)
    with open(fn, newline='') as csvfile:
        r = csv.reader(csvfile)
        next(r) # skip header
        for row in r:
            session_id = row[5]
            age = int(row[6])
            is_woman = int(row[7] == 'Woman')
            is_non_binary = int(row[7] != 'Woman' and row[7] != 'Man')
            is_native = int(row[9] == 'True')
            learning_disibility = int(row[10] != 'No;')
            difficulty_seeing = int(row[11].startswith('Yes'))
            corrected_vision = int('even' in row[11] or 'because' in row[11])
            table_familiarity = int(row[17])
            default_font_right = int('right' in row[18])
            default_font_small = int('small' in row[18])
            phone_reading_diff = int(row[19])
            tup = (session_id, age, is_woman, is_non_binary, is_native, learning_disibility, difficulty_seeing, corrected_vision, table_familiarity,
                    default_font_right, default_font_small, phone_reading_diff)
            session_id_to_survey_data[session_id] = tup
    return session_id_to_survey_data

def main():
    try:
        manifest = sys.argv[1]
        root = sys.argv[2]
        task_config_file = sys.argv[3]
        normals = json.load(open(sys.argv[4]))
        survey_results_file = sys.argv[5]
        out_file1 = sys.argv[6]
        out_file2 = sys.argv[7]
    except:
        print("python3 %s manifest root task_config_file normal_file survey_results_file task_out_file participant_out_file" % __file__)
        exit(0)

    design_ids = get_design_ids(task_config_file)
    for design_id in design_ids:
        participant_field_names.append('correct_zscore_' + design_id)
        participant_field_names.append('zscore_' + design_id)
    participant_csv_entry = collections.namedtuple("participant_data", participant_field_names)
    task_config = json.load(open(task_config_file))
    l_jsons = load_consolidated_jsons(manifest, root, override_exclude_all=True)

    session_id_survey_response = load_survey_data(survey_results_file)

    task_version = task_config['version']
    task_entries = []
    participant_entries = []
    for obj in l_jsons:
        session_id = str(obj['metadata']['session_id'])
        (_, age, is_woman, is_non_binary, is_native, learning_disibility, difficulty_seeing, corrected_vision, table_familiarity,
            default_font_right, default_font_small, phone_reading_diff) = session_id_survey_response[session_id]

        total_score = round(obj['score'], 2)
        exclude_session = int(obj['exclude_all'])
        num_tasks_excluded = obj['exclude_num']
        is_iphone = int(obj['metadata']['platform'].split()[0] == 'iPhone')
        zscores_correct = {design_id: [] for design_id in design_ids}
        zscores = {design_id: [] for design_id in design_ids}
        session_entries = []
        for idx in range(1, 29):
            idx = str(idx)
            if idx in obj:
                task_obj = obj[idx]

                style_id = task_obj['style_id']
                exclude_task = int(task_obj['exclude'])
                task_idx = int(task_obj['task_idx'])
                task_idx_frac = (task_idx + 1) / 28.0
                is_first_half_task = int(task_idx < 15)
                table_idx = int(task_obj['table_idx'])
                is_practice_task = int(table_idx == 1 or table_idx == 15)
                correctness = task_obj['correct']
                task_time = task_obj['time_taken']
                task_time_zscore = z_transform(task_time, normals[str(table_idx)])
                difficulty_score = task_obj['difficulty']
                satisfaction_score = task_obj['satisfaction']
                entry = task_csv_entry( # participant specific info
                                  session_id=session_id, task_version=task_version, exclude_session=exclude_session, 
                                  total_score=total_score, is_iphone=is_iphone, num_tasks_excluded=num_tasks_excluded,
                                  session_avg_zscore_correct=-1, session_avg_zscore=-1, age=age, is_woman=is_woman,
                                  is_non_binary=is_non_binary, is_native=is_native, learning_disibility=learning_disibility,
                                  difficulty_seeing=difficulty_seeing, corrected_vision=corrected_vision,
                                  table_familiarity=table_familiarity, default_font_right=default_font_right,
                                  default_font_small=default_font_small, phone_reading_diff=phone_reading_diff,

                                  # task specific info
                                  style_id=style_id, task_idx=task_idx, task_idx_frac=task_idx_frac, 
                                  is_first_half_task=is_first_half_task, table_idx=table_idx, 
                                  is_practice_task=is_practice_task, exclude_task=exclude_task,
                                  correctness=correctness, task_time=task_time, task_time_zscore=task_time_zscore,
                                  difficulty_score=difficulty_score, satisfaction_score=satisfaction_score)
                session_entries.append(entry)
                if correctness == 'correct':
                    zscores_correct[style_id].append(task_time_zscore)
                zscores[style_id].append(task_time_zscore)

        # now get participant session averages
        all_zscores_correct = sum(zscores_correct.values(), [])
        all_zscores = sum(zscores.values(), [])

        session_avg_zscore_correct = robust_mean(all_zscores_correct)
        session_avg_zscore_all = robust_mean(all_zscores)
        # now update each task entry for the participant
        for idx, entry in enumerate(session_entries):
            entry = entry._replace(session_avg_zscore_correct=session_avg_zscore_correct)
            entry = entry._replace(session_avg_zscore=session_avg_zscore_all)
            session_entries[idx] = entry
        task_entries.extend(session_entries)

        # now get participant session average zscores per design
        avg_zscores_correct = {'correct_zscore_' + design_id: robust_mean(zscores_correct[design_id]) for design_id in zscores_correct}
        avg_zscores = {'zscore_' + design_id: robust_mean(zscores[design_id]) for design_id in zscores}
        entry = participant_csv_entry( # participant specific info
                          session_id=session_id, task_version=task_version, exclude_session=exclude_session, 
                          total_score=total_score, is_iphone=is_iphone, num_tasks_excluded=num_tasks_excluded,
                          age=age, is_woman=is_woman,
                          is_non_binary=is_non_binary, is_native=is_native, learning_disibility=learning_disibility,
                          difficulty_seeing=difficulty_seeing, corrected_vision=corrected_vision,
                          table_familiarity=table_familiarity, default_font_right=default_font_right,
                          default_font_small=default_font_small, phone_reading_diff=phone_reading_diff, 
                          session_avg_zscore_correct=session_avg_zscore_correct,
                          session_avg_zscore=session_avg_zscore_all,
                          **avg_zscores_correct, **avg_zscores)
        participant_entries.append(entry)

    with open(out_file1, 'w', newline='') as csvfile:
        wr = csv.DictWriter(csvfile, fieldnames=task_field_names)
        wr.writeheader()
        for entry in task_entries:
            wr.writerow(entry._asdict())
            
    with open(out_file2, 'w', newline='') as csvfile:
        wr = csv.DictWriter(csvfile, fieldnames=participant_field_names)
        wr.writeheader()
        for entry in participant_entries:
            wr.writerow(entry._asdict())
        


if __name__ == "__main__":
    main()
