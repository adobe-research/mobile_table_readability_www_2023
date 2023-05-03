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
import json
import os.path

exclude_thresh = 13

def validate(answer_d, meta_answer_d, time_d, task_idx, invariant):
    original_query, platform, session_id, user_agent = invariant
    same_attributes = ['original_query', 'platform', 'session_id', 'table_idx', 'task_id', 'task_idx', 'user_agent']

    assert original_query == answer_d['original_query']
    assert platform == answer_d['platform']
    assert session_id == answer_d['session_id']
    assert user_agent == answer_d['user_agent']
    assert task_idx == int(answer_d['task_idx'])
    for attr in same_attributes:
        assert answer_d[attr] == meta_answer_d[attr]
        assert answer_d[attr] == time_d[attr]


def get_answer_lookup(config):
    lookup = {}
    for practice_task in config['practice_tasks']:
        table_idx = int(practice_task['table_idx'])
        answer = practice_task['answer']
        lookup[table_idx] = answer

    for task_group in config['tasks']:
        for task in task_group:
            table_idx = int(task['table_idx'])
            answer = task['answer']
            lookup[table_idx] = answer
    return lookup


_difficulty_to_number = {'very_easy': 1, 'easy': 2, 'neither': 3, 'difficult': 4, 'very_difficult': 5}
_satisfaction_to_number = {'very_satisfied': 1, 'satisfied': 2, 'neutral': 3, 'dissatisfied': 4, 'very_dissatisfied': 5}

def read_json(fn):
    if not os.path.exists(fn):
        print("File does not exist %s" % fn)
        return {}
    try:
        d = json.load(open(fn))
        return d
    except:
        print("Could not parse %s as JSON" % fn)
        return {}

def process_task(task_idx, root, lookup, invariant, skip_text):
    prefix = str(task_idx) + '_'

    answer_fn = os.path.join(root, prefix + 'answer.json')
    answer_d = read_json(answer_fn)

    meta_answers_fn = os.path.join(root, prefix + 'meta_answers.json')
    meta_answers_d = read_json(meta_answers_fn)

    time_fn = os.path.join(root, prefix + 'time.json')
    time_d = read_json(time_fn)
    if not answer_d or not meta_answers_d or not time_d:
        return {}

    validate(answer_d, meta_answers_d, time_d, task_idx, invariant)

    style_id = answer_d['style_id']
    if style_id == 'row_borders':
        style_id = 'rowborders'
    if style_id == 'col_borders':
        style_id = 'colborders'
    table_idx = int(answer_d['table_idx'])

    given_answer = answer_d['answer']
    correct_answer = lookup[table_idx]
    if given_answer == skip_text:
        correct = 'skipped'
    elif given_answer == correct_answer:
        correct = 'correct'
    else:
        correct = 'incorrect'

    difficulty = meta_answers_d['difficult_answer']
    difficulty_score = _difficulty_to_number[difficulty]
    satisfaction = meta_answers_d['format_answer']
    satisfaction_score = _satisfaction_to_number[satisfaction]

    time_taken = time_d['time_taken']
    timeout_triggered = time_d['timeout_triggered']

    task_info = {'style_id': style_id, 'table_idx': table_idx, 'given_answer': given_answer, 'correct': correct,
            'difficulty': difficulty_score, 'satisfaction': satisfaction_score, 'time_taken': time_taken, 
            'timeout_triggered': timeout_triggered, 'task_idx': task_idx}
    return task_info


def get_invariant(root):
    d = None
    for idx in range(28):
        fn = os.path.join(root, '%d_answer.json' % idx)
        try:
            d = json.load(open(fn))
        except:
            print("Could not read %s" % fn)
            continue
    if d is None:
        raise Exception("Could not find any answer files in %s" % root)
    invariant = (d['original_query'], d['platform'], d['session_id'], d['user_agent'])
    return invariant


def get_final_questions(root):
    fn = os.path.join(root, 'final_questions.json')
    d = read_json(fn)
    final = {'general_comment': d.get('comments', ''), 'difficulty_comment': d.get('difficulty', ''), 
             'format_comment':  d.get('format', ''), 'total_time': d.get('total_time', -1)}
    return final


def main():
    root = sys.argv[1]
    config_file = sys.argv[2]
    out_file = sys.argv[3]
    try:
        outliers = json.load(open(sys.argv[4]))
    except:
        print("No outlier file.  Using no filtering")
        outliers = {str(t): {'min': -2000000000, 'max': 2000000000} for t in range(1, 29)}


    config = json.load(open(config_file))
    correct_answer_lookup = get_answer_lookup(config)
    skip_text = config['skip_text']
    invariant = get_invariant(root)

    final_obj = {}
    first = True
    score = 0

    exclude_num = 0
    for task_idx in range(0, 28):
        task_info = process_task(task_idx, root, correct_answer_lookup, invariant, skip_text)
        if not task_info:
            continue
        table_idx = str(task_info['table_idx']) # json needs str keys
        outlier_min_val = outliers[table_idx]['min']
        outlier_max_val = outliers[table_idx]['max']

        exclude = False
        exclude_for_total = False
        exclude_reason = ""
        if task_idx > 1:
            correct = task_info['correct']
            if correct == 'correct':
                score += 1
            elif correct == 'incorrect':
                score -= 0.33
                exclude_for_total = True
            else:
                exclude_for_total = True

            if task_info['timeout_triggered'] != 'not triggered':
                exclude_for_total, exclude = True, True
                exclude_reason += "timeout or interrupted;"

            time_taken = task_info['time_taken']
            if time_taken <= outlier_min_val: 
                exclude_for_total, exclude = True, True
                exclude_reason += "small outlier;"

            if time_taken >= outlier_max_val:
                exclude_for_total, exclude = True, True
                exclude_reason += "big outlier;"
            if exclude_for_total:
                exclude_num += 1

        task_info['exclude'] = exclude
        task_info['exclude_reason'] = exclude_reason
        final_obj[table_idx] = task_info  

    final_obj['final'] = get_final_questions(root)
    final_obj['score'] = score
    final_obj['metadata'] = {'platform': invariant[1], 'session_id': invariant[2], 'user_agent': invariant[3]}
    final_obj['exclude_all'] = exclude_num >= exclude_thresh
    final_obj['exclude_num'] = exclude_num

    fd = open(out_file, 'w')
    json.dump(final_obj, fd, indent=4, sort_keys=True)
    fd.close()


if __name__ == "__main__":
    main()



