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
import statistics
import scipy.stats
import numpy as np


def main(data_file, out_file):
    data = json.load(open(data_file))
    stats = {}
    
    for table_idx in range(1, 29):
        table_idx = str(table_idx)
        times = data['individual_tables'][table_idx]['times_taken_correct']

        m = statistics.mean(times)
        std = statistics.stdev(times)
        stats[table_idx] = {'mean': m, 'std': std}

        nobs, minmax, mean, var, skew, kurt = scipy.stats.describe(times)
        median = np.median(times)

        stats[table_idx]['times'] = times
        stats[table_idx]['num_observations'] = nobs
        stats[table_idx]['min'] = int(minmax[0])
        stats[table_idx]['max'] = int(minmax[1])
        stats[table_idx]['median'] = int(median)
        stats[table_idx]['var'] = float(var)
        stats[table_idx]['skew'] = float(skew)
        stats[table_idx]['kurtosis'] = float(kurt)

        stats[table_idx]['norm_shapiro_p'] = float(scipy.stats.shapiro(times)[1])

        for distribution in ['norm', 'gumbel_r', 'gumbel_l', 'logistic']: 
            a2, criticals, p_vals = scipy.stats.anderson(times, distribution)
            p = np.interp(a2, criticals, p_vals, left=0.5) / 100.
            stats[table_idx][distribution + '_anderson_p'] = float(p)

    fd = open(out_file, 'w')
    json.dump(stats, fd, indent=4, sort_keys=True)


if __name__ == "__main__":
    data_file = sys.argv[1]
    out_file = sys.argv[2]
    main(data_file, out_file)

