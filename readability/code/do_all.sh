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

name=spacing
task_file=../../task_versions/v2/config.json
input_dir="../study_responses/spacing"

#name=borders
#task_file=../../task_versions/v3/config.json
#input_dir="../study_responses/borders"

#name=freeze
#input_dir="../study_responses/freeze"
#task_file=../../task_versions/v4/config.json

survey_results_file=../survey_responses.csv
participant_dir=../analyze_results/$name
group_file=table_groups.json
public_data_dir=../../public/data_for_viewing
mkdir -p $public_data_dir

outlier_file=data_files/${name}_outliers.json
normals_file=data_files/${name}_normals.json
out_file_time=out/${name}_time_data.json
out_file_zscore=out/${name}_zscore_data.json
out_plot_dir=out/${name}_plots
out_file_tmp=out/tmp.json
out_task_csv_file=out/${name}_tasks.csv
out_participant_csv_file=out/${name}_participants.csv

thisdir=`pwd`
log_file=`realpath data_files/${name}_log.txt`
err_file=`realpath data_files/${name}_err.txt`

# set these so that the loop will run at least twice. During the first iteration, num_exclusions may be 0
num_exclusions=-1
prev_num_exclusions=-2

# start with no outlier file and set it after the first loop
cur_outlier_filer=

# delete any existing intermediate and output files
rm -f $outlier_file $normals_file $out_file_time $out_file_zscore $out_file_tmp
rm -f $out_task_csv_file $out_participant_csv_file
rm -f $log_file $err_file
rm -rf $out_plot_dir
touch $log_file
touch $err_file

idx=1
while [ $num_exclusions -gt $prev_num_exclusions ]
do
	echo "Start loop $idx"
	echo "Start loop $idx" >> $log_file
	echo "Start loop $idx" >> $err_file
	echo $num_exclusions $prev_num_exclusions
	prev_num_exclusions=$num_exclusions

	rm -rf $participant_dir
	mkdir -p $participant_dir

	# get the participant data files
    for x in $input_dir/16*
    do
        b=`basename $x`
        outfile=${participant_dir}/${b}.json
        python3 consolodate_participants_core_info.py $x $task_file $outfile $cur_outlier_file >> $log_file 2>> $err_file
        if [ ! -f "$outfile" ]; then
            echo "Participant file $outfile was not created. exiting..."
            exit
        fi
    done

	# cur_outlier_file is empty the first iteration, but later iterations should use the outlier file
	cur_outlier_file=$outlier_file

	# make the manifest file
	cd $participant_dir
	$thisdir/find_exclusions.sh >> $log_file 2>> $err_file
	cd $thisdir

	manifest=$participant_dir/manifest.txt
	exclude_file=$participant_dir/exclude.txt
	num_part_exclusions=`wc -l $exclude_file | awk '{ print $1 }'`  # should be 0 for the first iter
	num_exclusions=`grep '"exclude": true' $participant_dir/*.json | wc -l | awk '{ print $1 }'`
	echo "Round $idx with $num_part_exclusions participants excluded and $num_exclusions tasks excluded"
	echo "Round $idx with $num_part_exclusions participants excluded and $num_exclusions tasks excluded" >> $log_file
	echo "Round $idx with $num_part_exclusions participants excluded and $num_exclusions tasks excluded" >> $err_file
	idx=$(( $idx + 1 ))

	# create the data file
	rm -f $out_file_tmp
	python3 generate_table_data.py $manifest $participant_dir $task_file $out_file_tmp $group_file >> $log_file 2>> $err_file
	if [ ! -f "$out_file_tmp" ]; then
		echo "Data file was not created. exiting..."
		exit
	fi

	# compute outliers file
	rm -f $outlier_file
	python3 compute_outlier_ranges.py $out_file_tmp $outlier_file >> $log_file 2>> $err_file
	if [ ! -f "$outlier_file" ]; then
		echo "Outlier file was not created. exiting..."
		exit
	fi

done

echo "Convergence" 
echo "Convergence" >> $log_file
echo "Convergence" >> $err_file

mv $out_file_tmp $out_file_time
cp $out_file_time $public_data_dir
echo python3 compute_normals.py $out_file_time $normals_file >> $log_file
python3 compute_normals.py $out_file_time $normals_file >> $log_file 2>> $err_file
if [ ! -f "$normals_file" ]; then
	echo "Normals file was not created. exiting..."
	echo "Normals file was not created. exiting..." >> $err_file
	exit
fi

echo python3 generate_table_data.py $manifest $participant_dir $task_file $out_file_zscore $group_file $normals_file >> $log_file
python3 generate_table_data.py $manifest $participant_dir $task_file $out_file_zscore $group_file $normals_file >> $log_file 2>> $err_file
if [ ! -f "$out_file_zscore" ]; then
	echo "Zscore data file was not created. exiting..."
	echo "Zscore data file was not created. exiting..." >> $err_file
	exit
fi
cp $out_file_zscore $public_data_dir

echo python3 create_csv_data.py $manifest $participant_dir $task_file $normals_file $survey_results_file $out_task_csv_file $out_participant_csv_file >> $log_file
python3 create_csv_data.py $manifest $participant_dir $task_file $normals_file $survey_results_file $out_task_csv_file $out_participant_csv_file >> $log_file 2>> $err_file
if [ ! -f "$out_task_csv_file" ]; then
	echo "Task CSV file was not created. exiting..."
	echo "Task CSV file was not created. exiting..." >> $err_file
	exit
fi
if [ ! -f "$out_participant_csv_file" ]; then
	echo "Participant CSV file was not created. exiting..."
	echo "Participant CSV file was not created. exiting..." >> $err_file
	exit
fi


