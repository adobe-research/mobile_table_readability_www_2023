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
import numpy as np

max_time = 120000
min_time = 0


def main(data_file, out_file):
    data = json.load(open(data_file))
    outlier_criteria = {}
    
    for table_idx in range(1, 29):
        table_idx = str(table_idx)
        times = data['individual_tables'][table_idx]['times_taken_correct']
        accuracy = data['individual_tables'][table_idx]['perc_correct']
        times = [t for t in times if t < max_time]
        q1 = np.percentile(times, 25)
        q3 = np.percentile(times, 75)
        print(table_idx, q1, q3)
        r = q3 - q1
        min_val = max(min_time, q1 - 1.5 * r)
        max_val = min(max_time, q3 + 1.5 * r)
        outlier_criteria[table_idx] = {'min': min_val, 'max': max_val}

    fd = open(out_file, 'w')
    json.dump(outlier_criteria, fd, indent=4, sort_keys=True)


if __name__ == "__main__":
    data_file = sys.argv[1]
    out_file = sys.argv[2]
    main(data_file, out_file)

