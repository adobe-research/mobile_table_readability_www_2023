/*************************************************************************
* ADOBE CONFIDENTIAL
* ___________________
*
* Copyright 2022 Adobe
* All Rights Reserved.
*
* NOTICE: All information contained herein is, and remains
* the property of Adobe and its suppliers, if any. The intellectual
* and technical concepts contained herein are proprietary to Adobe
* and its suppliers and are protected by all applicable intellectual
* property laws, including trade secret and copyright laws.
* Dissemination of this information or reproduction of this material
* is strictly forbidden unless prior written permission is obtained
* from Adobe.
**************************************************************************/


const fs = require('fs');
const fsPromises = require('fs.promises');
const buffer = require('buffer');
const express = require('express');

const root = __dirname; 

const public_dir = root + '/public';
const out_style_dir = root + "/style_out";
const out_preference_dir = root + "/preference_out";
const out_readability_dir = root + "/readability_results";
const task_version_config_root = root + '/task_versions'

const app = express();
app.use(express.json({limit: "50mb"})); // for parsing application/json
app.use(express.urlencoded({limit: "50mb", extended: true })); // for parsing application/x-www-form-urlencoded

app.use(express.static(public_dir));

// preload the tables
const table_htmls = {};
for (var i = 1; i <= 28; i++) {
	const filepath = public_dir + '/tables/' + String(i) + '.html';
	var contents = fs.readFileSync(filepath, 'utf8');
	table_htmls[i] = contents;
}

const view_result_suffixes = ['', '2'];
for (var k = 0; k < view_result_suffixes.length; k++) {
	view_result_suffix = view_result_suffixes[k];
	const endpoint = '/view_result' + view_result_suffix;
	const redirect_url =  '/view_table' + view_result_suffix + '.html'

	app.get(endpoint, async (req, res) => {
		try {
			const worker_id = req.query.worker_id;
			const table_id = req.query.table_id;
			if (/^[a-z0-9]+$/i.test(worker_id) && /^[0-9]+$/i.test(table_id)) {
				const date = req.query.date;
				var filename;
				if (date) {
					filename = out_style_dir + '/' + table_id + "_" + worker_id + "_" + date + ".json";
				} else {
					const prefix = table_id + "_" + worker_id + "_";
					var files = await fsPromises.readdir(out_style_dir);
					var latest_file;
					var latest = 0;
					for (var i = 0; i < files.length; i++) {
						var file = files[i];
						if (file.startsWith(prefix)) {
							var parts = file.split('_');
							var date_part = parts[2].slice(0,-5);
							if (date_part > latest) {
								latest = date_part;
								latest_file = file;
							}
						}
					}
					filename = out_style_dir + '/' + latest_file;
				}
				fs.readFile(filename, (err, file_contents) => {
					if (err) {
						res.send("Could not find result");
						return;
					}
					const style_dict = JSON.parse(file_contents);
					const query_params = new URLSearchParams(style_dict).toString();
					res.redirect(redirect_url + '?' + query_params);
				});
			} else {
				console.log("Could not find Worker ID: " + worker_id + " or table ID: " + table_id);
				res.send("Invalid Worker ID or Table ID");
			}
		} catch(err) {
			console.log(err);
			res.send("An error occurred");
		}
	});
}

app.post('/submit', async (req, res) => {
	try {
		const worker_id = req.body.worker_id;
		const table_id = req.body.table_id;
		if (/^[a-z0-9]+$/i.test(worker_id) && /^[a-z0-9]+$/i.test(table_id)) {
			const out_file = out_style_dir + '/' + table_id + "_" + worker_id + "_" + Date.now() + ".json";
			const str = JSON.stringify(req.body);
			fs.appendFile(out_file, str, function() {res.send("Success");});
		} else {
			console.log("Could not log Worker ID: " + worker_id + " or table ID: " + table_id);
			res.send("Invalid Worker ID or Table ID");
		}
	} catch(err) {
		console.log(err);
		res.send("An error occurred");
	}
});

app.post('/preference', async (req, res) => {
	try {
		const table_id = req.body.table_id;
		const all_designers = req.body.all_designers;
		const top_designers = req.body.top_designers;
		const out_file = out_preference_dir + '/' + table_id + "_" + Date.now() + ".json";
		const str = JSON.stringify(req.body);
		fs.appendFile(out_file, str, function() {res.send("Success");});
	} catch(err) {
		console.log(err);
		res.send("An error occurred");
	}
});

function shuffle(array) {
    let currentIndex = array.length,  randomIndex;

    // While there remain elements to shuffle...
    while (currentIndex != 0) {

      // Pick a remaining element...
      randomIndex = Math.floor(Math.random() * currentIndex);
      currentIndex--;

      // And swap it with the current element.
      [array[currentIndex], array[randomIndex]] = [
        array[randomIndex], array[currentIndex]];
    }

    return array;
}

const max_retries = 20;
function shuffle_with_separation(array, groups, min_sep) {
    var current_index = array.length - 1;
	var groups_to_avoid = [];
	var retries = 0;
    while (current_index != 0) { // While there remain elements to shuffle...
		var candidate_indices = [];
		var cur_group = groups[current_index];
		for (var i = 0; i < current_index; i++) {
			var is_good = true;
			for (var j = 0; j < groups_to_avoid.length; j++) {
				if (groups[i] == groups_to_avoid[j]) {
					is_good = false;
					break;
				}
			}
			if (is_good) {
				candidate_indices.push(i);
			}
		}
		if (candidate_indices.length == 0) {
			// we have a problem and need to restart the process
			current_index = array.length - 1;
			groups_to_avoid = [];
			retries++;
			console.log("Restarting shuffle_with_separation.  Retries: ", retries);
			if (retries >= max_retries) {
				min_sep--;
				retries = 0;
			}
			continue;
		}
		// Pick a valid element...
		var candidate_index = Math.floor(Math.random() * candidate_indices.length);
		var random_index = candidate_indices[candidate_index];

        // And swap it with the current element.
        [array[current_index], array[random_index]] = [
          array[random_index], array[current_index]];
        [groups[current_index], groups[random_index]] = [
          groups[random_index], groups[current_index]];

		groups_to_avoid.push(cur_group);
		if (groups_to_avoid.length > min_sep) {
			groups_to_avoid.shift(cur_group);
		}
        current_index--;
    }

    return array;

}

function load_test_styles(config, root) {
	var test_styles = []
	for (var i = 0; i < config['test_styles'].length; i++) {
		const rel_path = config['test_styles'][i];
		const test_style_file = root + '/' + rel_path;

		const test_style = fs.readFileSync(test_style_file, 'utf8');
		test_styles.push(test_style);
	}
	return test_styles;
}

function load_practice_tasks(config, root) {
	const practice_tasks = [];
	for (var i = 0; i < config['practice_tasks'].length; i++) {
		const practice_task_config = config['practice_tasks'][i];
		const style_file = root + '/' + practice_task_config['style_file'];
		const style = fs.readFileSync(style_file, 'utf8');
		const table_idx = practice_task_config['table_idx'];
		const practice_task = {
			"context": practice_task_config["context"],
			"question": practice_task_config["question"],
			"answer_choices": practice_task_config['answer_choices'],
			"answer": practice_task_config['answer'],
			"table_idx": table_idx,
			"table_html": table_htmls[table_idx],
			"style": style,
			"task_id": practice_task_config["task_id"],
			"is_practice": true
		};
		practice_tasks.push(practice_task);
	}
	return practice_tasks;
}

function load_test_tasks(config, root, min_separation) {
	const global_styles = load_test_styles(config, root);
	var styles = [];

	const tasks = [];
	const task_groups = [];
	for (var i = 0; i < config['tasks'].length; i++) {
		const task_group = config['tasks'][i];
		if (task_group[0]['test_styles']) {
			// if the first task in the group has a list of test styles,
			// then override the global styles used
			styles = load_test_styles(task_group[0], root);
		} else {
			// no task_group specific styles
			styles = global_styles;
		}
		shuffle(styles);
		for (var j = 0; j < task_group.length; j++) {
			const task_config = task_group[j];
			const table_idx = task_config['table_idx'];
			const task = {
				"context": task_config["context"],
				"question": task_config["question"],
				"answer_choices": task_config['answer_choices'],
				"answer": task_config['answer'],
				"time_limit": task_config["time_limit"],
				"table_idx": table_idx,
				"table_html": table_htmls[table_idx],
				"style": styles[j % styles.length],
				"task_id": task_config["task_id"],
				"is_practice": false
			};
			tasks.push(task);
			task_groups.push(i);
		}
	}
	//shuffle_with_separation(tasks, task_groups, min_separation);
	shuffle(tasks);
	return tasks;
}

app.post('/readability_start', async (req, res) => {
	try {
		const version = req.body.version;
		const session_id = Date.now();
		console.log("Starting session", session_id);

		const out_dir = out_readability_dir + '/' + session_id;
		fs.mkdirSync(out_dir);

		const version_root = task_version_config_root + '/' + version + "/";
		const version_config = version_root + '/config.json';
		const config = require(version_config);

		const time_limit = config['time_limit'];
		const skip_text = config['skip_text'];

		const practice_tasks = load_practice_tasks(config, version_root);
		const test_tasks = load_test_tasks(config, version_root);
		
		const tasks = [...practice_tasks, ...test_tasks];
		const out_obj = {'session_id': session_id, 
			             'tasks': tasks, 
			             'time_limit': time_limit, 
			             'skip_text': skip_text};
		                 
		res.send(out_obj);
	} catch(err) {
		console.log(err);
		res.status(500);
		res.send("An error occurred");
	}
});

app.post('/readability_log', async (req, res) => {
	try {
		//console.log(req.body);
		const session_id = req.body.session_id;
		const fname = req.body.filename;
		const out_dir = out_readability_dir + '/' + session_id;
		const out_file = out_dir + '/' + fname + '.json';
		const str = JSON.stringify(req.body);
		fs.appendFile(out_file, str, function() {res.send("Success");});
	} catch(err) {
		console.log(err);
		res.status(500);
		res.send("An error occurred");
	}
});

app.listen(3002);
console.log("ready")

