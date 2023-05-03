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

import os
import sys
import json
import collections
import scipy.stats
import numpy as np

DO_PRINT = False

def get_design_ids(task_config_file):
    design_ids = []
    config = json.load(open(task_config_file))
    for design_path in config['test_styles']:
        basename = os.path.basename(design_path)
        no_ext = os.path.splitext(basename)[0]
        design_ids.append(no_ext)
    return design_ids


def load_consolidated_jsons(manifest, root, override_exclude_all=False, z_scores=False, normals=None):
    consolidated_participants_data = []
    for line in open(manifest).readlines():
        fn = line.strip()
        path = os.path.join(root, fn)
        obj = json.load(open(path))
        if obj['exclude_all'] and not override_exclude_all:
            continue
        if z_scores:
            for table_idx in range(1, 29):
                table_idx = str(table_idx)
                if table_idx in obj:
                    response = obj[table_idx]
                    z_transform(response, normals[table_idx])
        consolidated_participants_data.append(obj)
    print("Loaded %s valid participants" % len(consolidated_participants_data))
    return consolidated_participants_data


def get_empty_aggregate_table_responses(table_groups):
    out = {}
    for key in table_groups:
        if key.startswith('_'):
            continue
        out[key] = get_empty_single_response()
    return out


def get_empty_single_response():
    return {'difficulty_correct': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0},
            'satisfaction_correct': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0},
            'times_taken_correct': [],
            'num_correct': 0,
            'num_incorrect': 0,
            'num_skip': 0,
            'difficulty_incorrect': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0},
            'satisfaction_incorrect': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0},
            'times_taken_incorrect': [],
            'difficulty_skip': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0},
            'satisfaction_skip': {'1': 0, '2': 0, '3': 0, '4': 0, '5': 0},
            'times_taken_skip': []
            }

def get_empty_pair_answer_aggregated_responses():
    d = {}
    for answer in ['correct_correct', 'correct_incorrect', 'incorrect_correct', 'incorrect_incorrect', 'all']:
        d[answer] = {'difficulty_diff': {'-4': 0, '-3': 0, '-2': 0, '-1': 0,'0': 0, '1': 0, '2': 0, '3': 0, '4': 0},
                    'satisfaction_diff': {'-4': 0, '-3': 0, '-2': 0, '-1': 0,'0': 0, '1': 0, '2': 0, '3': 0, '4': 0},
                    'times_taken_diff': [],
                    'num': 0
                    }
    return d


def get_empty_individual_table_responses():
    return {str(table_idx): get_empty_single_response() for table_idx in range(1, 29)}


def get_empty_aggregate_table_design_responses(design_ids, table_groups):
    return {design_id: get_empty_aggregate_table_responses(table_groups) for design_id in design_ids}


def get_empty_individual_table_design_responses(design_ids):
    return {str(table_idx): {design_id: get_empty_single_response() for design_id in design_ids} for table_idx in range(1, 29)}


def get_empty_pair_table_responses(design_ids):
    d = {}
    for table_id1 in range(1, 29):
        table_id1 = str(table_id1)
        d[table_id1] = {}
        for design_id1 in design_ids:
            d[table_id1][design_id1] = {}
            for design_id2 in design_ids:
                d[table_id1][design_id1][design_id2] = get_empty_pair_answer_aggregated_responses()
    return d


def get_empty_pair_table_design_responses(design_ids):
    d = {}
    for table_id1 in range(1, 29):
        table_id1 = str(table_id1)
        d[table_id1] = {}
        for design_id1 in design_ids:
            d[table_id1][design_id1] = get_empty_pair_answer_aggregated_responses()
    return d
            

def add_response_data(data, response):
    # data looks like the output of get_empty_aggregate_table_responses()
    # response is a dict
    difficulty = response['difficulty']
    satisfaction = response['satisfaction']
    time_taken = response['time_taken']
    if response['correct'] == 'correct':
        data['num_correct'] += 1
        suffix = '_correct'
    elif response['correct'] == 'skipped':
        data['num_skip'] += 1
        suffix = '_skip'
    else:
        data['num_incorrect'] += 1
        suffix = '_incorrect'

    data['difficulty' + suffix][str(difficulty)] += 1
    data['satisfaction' + suffix][str(satisfaction)] += 1
    data['times_taken' + suffix].append(time_taken)


def add_dicts(*ds):
    return {key: sum(map(lambda d: d[key], ds)) for key in ds[0].keys()}


def post_process_data(data):
    data['difficulty_all'] = add_dicts(data['difficulty_correct'], data['difficulty_skip'], data['difficulty_incorrect'])
    data['difficulty_skip_and_correct'] = add_dicts(data['difficulty_correct'], data['difficulty_skip'])
    data['difficulty_skip_and_incorrect'] = add_dicts(data['difficulty_skip'], data['difficulty_incorrect'])
    data['difficulty_correct_and_incorrect'] = add_dicts(data['difficulty_correct'], data['difficulty_incorrect'])

    data['satisfaction_all'] = add_dicts(data['satisfaction_correct'], data['satisfaction_skip'], data['satisfaction_incorrect'])
    data['satisfaction_skip_and_correct'] = add_dicts(data['satisfaction_correct'], data['satisfaction_skip'])
    data['satisfaction_skip_and_incorrect'] = add_dicts(data['satisfaction_skip'], data['satisfaction_incorrect'])
    data['satisfaction_correct_and_incorrect'] = add_dicts(data['satisfaction_correct'], data['satisfaction_incorrect'])

    data['times_taken_all'] = data['times_taken_correct'] + data['times_taken_skip'] + data['times_taken_incorrect']
    data['times_taken_skip_and_correct'] = data['times_taken_correct'] + data['times_taken_skip']
    data['times_taken_skip_and_incorrect'] = data['times_taken_skip'] + data['times_taken_incorrect']
    data['times_taken_correct_and_incorrect'] = data['times_taken_correct'] + data['times_taken_incorrect']

    data['times_taken_correct'].sort()
    data['times_taken_incorrect'].sort()
    data['times_taken_skip'].sort()
    data['times_taken_all'].sort()
    data['times_taken_skip_and_correct'].sort()
    data['times_taken_skip_and_incorrect'].sort()
    data['times_taken_correct_and_incorrect'].sort()

    num = data['num_all'] = data['num_correct'] + data['num_skip'] + data['num_incorrect']
    data['perc_correct'] = 100 * data['num_correct'] / float(num) if num else 0
    data['perc_incorrect'] = 100 * data['num_incorrect'] / float(num) if num else 0
    data['perc_skip'] = 100 * data['num_skip'] / float(num) if num else 0
    data['perc_all'] = 100.


def z_transform(response, normal):
    mean = normal['mean']
    std = normal['std']
    time = response['time_taken']
    z_time = (time - mean) / std
    response['time_taken'] = z_time


def aggregate_response_data_non_paired(consolidated_participants_data, design_ids, table_groups):
    at = aggregated_tables = get_empty_aggregate_table_responses(table_groups)
    it = individual_tables = get_empty_individual_table_responses()
    atxd = aggregated_tables_x_designs = get_empty_aggregate_table_design_responses(design_ids, table_groups)
    itxd = individual_tables_x_designs = get_empty_individual_table_design_responses(design_ids)

    for participant_data in consolidated_participants_data:
        for table_idx in range(1, 29):
            table_idx = str(table_idx)
            if table_idx not in participant_data:
                print("Table %s not found for participant %s" % (table_idx, participant_data['metadata']['session_id']))
                continue
            response = participant_data[table_idx]
            assert table_idx == str(response['table_idx'])
            if response['exclude']:
                continue
            design_id = response['style_id']
            
            for group_name in table_groups:
                if group_name.startswith('_'):
                    continue
                if table_idx in table_groups[group_name]:
                    add_response_data(at[group_name], response)
                    add_response_data(atxd[design_id][group_name], response)

            add_response_data(it[table_idx], response)
            add_response_data(itxd[table_idx][design_id], response)

    # sort the times_taken fields
    for table_idx in range(1, 29):
        table_idx = str(table_idx)
        post_process_data(it[table_idx])
        for design_id in design_ids:
            post_process_data(itxd[table_idx][design_id])

    for key in at:
        post_process_data(at[key])
        for design_id in design_ids:
            post_process_data(atxd[design_id][key])
    return at, it, atxd, itxd


def invert_dict(d):
    t = {str(-1 * int(key)): val for key, val in d.items()}
    return t

def invert_times(times):
    return [-1 * time for time in times]

def merge_diff_entries(sub, *entries):
    if sub:
        difficulty_diffs = [entries[0]['difficulty_diff']] + list(map(lambda d: invert_dict(d['difficulty_diff']), entries[1:]))
        satisfaction_diffs = [entries[0]['satisfaction_diff']] + list(map(lambda d: invert_dict(d['satisfaction_diff']), entries[1:]))
        times_taken_diff = sum(map(lambda d: invert_times(d['times_taken_diff']), entries[1:]), entries[0]['times_taken_diff'])
    else:
        difficulty_diffs = list(map(lambda d: d['difficulty_diff'], entries))
        satisfaction_diffs = list(map(lambda d: d['satisfaction_diff'], entries))
        times_taken_diff = sum(map(lambda d: d['times_taken_diff'], entries), [])
    times_taken_diff.sort()
    return { 'difficulty_diff': add_dicts(*difficulty_diffs),
             'satisfaction_diff': add_dicts(*satisfaction_diffs),
             'times_taken_diff': times_taken_diff,
             'num': sum(map(lambda d: d['num'], entries))
             }


def merge_diff_entries_1(sub, *entries):
    out = {}
    if not entries:
        return {}
    for key in entries[0].keys():
        sub_entries = [entry[key] for entry in entries]
        out[key] = merge_diff_entries(sub, *sub_entries)
    return out


def merge_diff_entries_2(sub, *entries):
    out = {}
    if not entries:
        return {}
    for key in entries[0]:
        sub_entries = [entry[key] for entry in entries]
        out[key] = merge_diff_entries_1(sub, *sub_entries)
    return out


def merge_diff_entries_3(sub, *entries):
    out = {}
    if not entries:
        return {}
    for key in entries[0]:
        sub_entries = [entry[key] for entry in entries]
        out[key] = merge_diff_entries_2(sub, *sub_entries)
    return out


def merge_diff_entries_4(sub, *entries):
    out = {}
    if not entries:
        return {}
    for key in entries[0]:
        sub_entries = [entry[key] for entry in entries]
        out[key] = merge_diff_entries_3(sub, *sub_entries)
    return out


def merge_diff_entries_5(sub, *entries):
    # Recursion is hard, okay.  Don't judge
    out = {}
    if not entries:
        return {}
    for key in entries[0]:
        sub_entries = [entry[key] for entry in entries]
        out[key] = merge_diff_entries_4(sub, *sub_entries)
    return out

def merge_diff_entries_n(sub, *entries):
    # because who needs true recursion when you have a small recursion call limit
    # also, anybody who is nesting dictionaries much deeper than this probably wants to rethink
    # their solution.
    if DO_PRINT:
        print
        for entry in entries:
            print(entry)
    if not entries:
        return {}
    count = 0
    cur = entries[0]
    while True:
        if 'num' in cur:
            break
        else:
            count += 1
            key = list(cur.keys())[0]
            cur = cur[key]
    if DO_PRINT:
        print(count)
    if count == 0:
        return merge_diff_entries(sub, *entries)
    elif count == 1:
        return merge_diff_entries_1(sub, *entries)
    elif count == 2:
        return merge_diff_entries_2(sub, *entries)
    elif count == 3:
        return merge_diff_entries_3(sub, *entries)
    elif count == 4:
        return merge_diff_entries_4(sub, *entries)
    elif count == 5:
        return merge_diff_entries_5(sub, *entries)
    else:
        print("You probably did something very wrong.  Your dicts are nested > 5 levels")

                

def aggregate_pairs_by_design(data, design_ids):
    d = order_aggregated_pairs = {}
    for table_id1 in data.keys():
        d[table_id1] = {}
        for design_id1 in design_ids:
            d[table_id1][design_id1] = {}
            entries = list(data[table_id1][design_id1].values())
            combined_entry = merge_diff_entries_n(False, *entries)
            d[table_id1][design_id1] = combined_entry
    return d


def aggregate_pairs_by_table(data, table_groups):
    out = {}
    for key in table_groups:
        group_table_ids = table_groups[key]
        group_entries = [data[table_id] for table_id in group_table_ids]
        out[key] = merge_diff_entries_n(False, *group_entries)
    return out


def agg_answer(a1, a2):
    if a1 == 'skipped':
        a1 = 'incorrect'
    if a2 == 'skipped':
        a2 = 'incorrect'
    return a1 + '_' + a2


def handle_paired(consolidated_participants_data, design_ids, table_groups):
    global DO_PRINT
    pair_data = get_empty_pair_table_responses(design_ids)
    pair_data_design_agg = get_empty_pair_table_design_responses(design_ids)

    for participant_data in consolidated_participants_data:
        for table_idx_cur in range(1, 29):
            if table_idx_cur < 15:
                table_idx_other = str(table_idx_cur + 14)
            else:
                table_idx_other = str(table_idx_cur - 14)
            table_idx_cur = str(table_idx_cur)
            if table_idx_cur not in participant_data:
                print("Table %s not found for participant %s" % (table_idx_cur, participant_data['metadata']['session_id']))
                continue
            if table_idx_other not in participant_data:
                print("Table %s not found for participant %s" % (table_idx_other, participant_data['metadata']['session_id']))
                continue
                        
            response_cur = participant_data[table_idx_cur]
            response_other = participant_data[table_idx_other]
            if response_cur['exclude'] or response_other['exclude']:
                continue

            time_taken_cur = response_cur['time_taken'] 
            time_taken_other = response_other['time_taken'] 

            time_taken_diff = time_taken_cur - time_taken_other
            difficulty_diff = response_cur['difficulty'] - response_other['difficulty']
            satisfaction_diff = response_cur['satisfaction'] - response_other['satisfaction']

            answer_cur = response_cur['correct']
            answer_other = response_other['correct']
            answer_agg = agg_answer(answer_cur, answer_other)
            design_id_cur = response_cur['style_id']
            design_id_other = response_other['style_id']

            ds = [pair_data[table_idx_cur][design_id_cur][design_id_other][answer_agg],
                  pair_data[table_idx_cur][design_id_cur][design_id_other]['all'],
                  pair_data_design_agg[table_idx_cur][design_id_cur][answer_agg],
                  pair_data_design_agg[table_idx_cur][design_id_cur]['all']
                  ]

            for d in ds:
                d['num'] += 1
                d['times_taken_diff'].append(time_taken_diff)
                d['satisfaction_diff'][str(satisfaction_diff)] += 1
                d['difficulty_diff'][str(difficulty_diff)] += 1

    for table_idx_cur in range(1, 29):
        table_idx_cur = str(table_idx_cur)
        for design_id1 in design_ids:
            for design_id2 in design_ids:
                for answer in ['correct_correct', 'correct_incorrect', 'incorrect_correct', 'incorrect_incorrect']:
                        pair_data[table_idx_cur][design_id1][design_id2][answer]['times_taken_diff'].sort()
                        pair_data_design_agg[table_idx_cur][design_id1][answer]['times_taken_diff'].sort()

    pair_data_table_agg = aggregate_pairs_by_table(pair_data, table_groups)
    pair_data_table_design_agg = aggregate_pairs_by_table(pair_data_design_agg, table_groups)
    return pair_data, pair_data_design_agg, pair_data_table_agg, pair_data_table_design_agg


def get_meta_info(consolidated_participants_data):
    scores = []
    user_agents = collections.Counter()
    platforms = collections.Counter()
    difficulty_comments = []
    format_comments = []
    general_comments = []
    total_times = []
    for participant_data in consolidated_participants_data:
        meta_data = participant_data['metadata']
        final = participant_data['final']
        platform = meta_data['platform']
        user_agent = meta_data['user_agent']
        score = participant_data['score']

        scores.append(score)
        user_agents[user_agent] += 1
        platforms[platform] += 1

        difficulty_comments.append(final['difficulty_comment'])
        format_comments.append(final['format_comment'])
        general_comments.append(final['general_comment'])
        total_times.append(final['total_time'] / 1000. / 60)  # minutes
    return scores, platforms, user_agents, difficulty_comments, format_comments, general_comments, total_times


def get_times_taken(participant_data, z_scores):
    times = []
    style_ids = []
    for key in participant_data:
        if key in ('1', '15'):
            continue
        try:
            time_taken = participant_data[key]['time_taken']
            style_id = participant_data[key]['style_id']
            if participant_data[key]['exclude'] or participant_data[key]['correct'] != 'correct':
                continue
            if z_scores:
                times.append(time_taken)
            else:
                times.append(time_taken / 1000.)
            style_ids.append(style_id)
        except:
            pass
    return times, style_ids


def get_participant_stats(consolidated_participants_data, design_ids, z_scores):
    stats = collections.defaultdict(list)
    if z_scores:
        stats['ordering'] = collections.defaultdict(list)
    for participant_data in consolidated_participants_data:
        times_taken, style_ids = get_times_taken(participant_data, z_scores)
        if len(times_taken) < 3:
            continue
        nobs, minmax, mean, var, skew, kurt = scipy.stats.describe(times_taken)
        median = np.median(times_taken)

        stats['num_observations'].append(nobs)
        stats['min'].append(minmax[0])
        stats['max'].append(minmax[1])
        stats['mean'].append(mean)
        stats['median'].append(median)
        stats['var'].append(var)
        stats['std'].append(var ** 0.5)
        stats['skew'].append(skew)
        stats['kurtosis'].append(kurt)

        stats['norm_shapiro_p'].append(scipy.stats.shapiro(times_taken)[1])

        for distribution in ['norm', 'gumbel_r', 'gumbel_l', 'logistic']: 
            a2, criticals, p_vals = scipy.stats.anderson(times_taken, distribution)
            p = np.interp(a2, criticals, p_vals, left=0.5) / 100.
            stats[distribution + '_anderson_p'].append(p)

        if z_scores:
            means = []
            for design_id in design_ids:
                times_in_style = [t for (t, s) in zip(times_taken, style_ids) if s == design_id]
                if times_in_style:
                    m = sum(times_in_style) / len(times_in_style)
                else:
                    m = 0
                means.append(m)
                stats["mean_" + design_id].append(m)
                stats["rel_mean_" + design_id].append(m - mean)
                stats["num_" + design_id].append(len(times_in_style))
                if design_id == "bad" and (m - mean) < -0.1:
                    print(participant_data['metadata']['session_id'], (m - mean))
            for idx, margin in enumerate((0.01, 0.025, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)):
                label = "%.2f" % margin
                combined = [(m, str(idx)) for idx,m in enumerate(means)]
                combined.sort(key=lambda tup: tup[0], reverse=True)
                stats['ordering'][label].append(get_preorder_str(combined, margin))
    return stats

def get_preorder_str(arr, margin):
    l_eles = []
    cur_eq_set = [arr[0][1]]
    for idx in range(1, len(arr)):
        diff = arr[idx-1][0] - arr[idx][0]
        if diff <= margin:
            cur_eq_set.append(arr[idx][1])
        else:
            l_eles.append(cur_eq_set)
            cur_eq_set = [arr[idx][1]]
    l_eles.append(cur_eq_set)
    set_strs = []
    for eq_set in l_eles:
        eq_set.sort()
        set_str = '='.join(eq_set)
        set_strs.append(set_str)
    return '>'.join(set_strs)


def main():
    manifest = sys.argv[1]
    root = sys.argv[2]
    task_config_file = sys.argv[3]
    out_file = sys.argv[4]
    try:
        table_groups = json.load(open(sys.argv[5]))
        print("Table Groups Loaded from", sys.argv[5])
    except:
        table_groups = json.load(open("metadata_files/table_groups.json"))

    try:
        normals = json.load(open(sys.argv[6]))
        z_scores = True
        print("Normals Loaded from", sys.argv[6])
    except:
        #normals = {str(t): {'mean': 0, 'std': 1} for t in range(1, 29)}  # default to no op
        normals = None
        z_scores = False
        print("Normals not loaded")

    design_ids = get_design_ids(task_config_file)
    consolidated_participants_data = load_consolidated_jsons(manifest, root, False, z_scores=z_scores, normals=normals)
    (scores, platforms, user_agents, difficulty_comments, format_comments, 
            general_comments, total_times) = get_meta_info(consolidated_participants_data)
    participant_stats = get_participant_stats(consolidated_participants_data, design_ids, z_scores)

    (aggregated_tables, individual_tables, aggregated_tables_x_designs, 
            individual_tables_x_designs) = aggregate_response_data_non_paired(consolidated_participants_data, design_ids, table_groups)

    pair_data, pair_data_design_agg, pair_data_table_agg, pair_data_table_design_agg = handle_paired(consolidated_participants_data, 
                                                                                                     design_ids, table_groups)

    final_obj = {'aggregated_tables': aggregated_tables,
                 'individual_tables': individual_tables,
                 'aggregated_tables_x_designs': aggregated_tables_x_designs,
                 'individual_tables_x_designs': individual_tables_x_designs,
                 'order_answer_aggregated_pairs': pair_data,
                 'order_answer_design_aggregated_pairs': pair_data_design_agg, 
                 'order_table_answer_design_aggregated_pairs': pair_data_table_design_agg,
                 'order_table_answer_aggregated_pairs': pair_data_table_agg, 
                 'design_ids': design_ids,
                 'scores': scores,
                 'platforms': platforms,
                 'user_agents': user_agents,
                 'participant_stats': participant_stats,
                 'total_times': total_times,
                 'difficulty_comments': difficulty_comments,
                 'format_comments': format_comments,
                 'general_comments': general_comments,
                 'is_z_scores': z_scores
                 }
    
    fd = open(out_file, 'w')
    json.dump(final_obj, fd, indent=4, sort_keys=True)
    fd.close()


if __name__ == "__main__":
    main()

