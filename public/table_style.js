
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

var check_box_ids = ['row_stripe', 'row_border', 'col_border', 'row_head_bold', 'row_head_back', 'row_head_frozen', 
					 'row_head_italic', 'row_head_under', 'col_head_bold', 'col_head_back', 'col_head_frozen', 
					 'col_head_italic', 'col_head_under'];
var other_ids = ['body_size', 'row_space', 'col_space', 'min_col_width', 'worker_id',
				 'body_horz_align', 'body_vert_align', 'min_row_height', 'body_font',
				 'row_head_size', 'row_head_horz_align', 'row_head_vert_align', 'row_head_font',
				 'col_head_size', 'col_head_horz_align', 'col_head_vert_align', 'col_head_font'];
var all_ids = [...check_box_ids, ...other_ids];
var table_id = '';

function is_style_tool() {
	return document.getElementById("controls") != null;
}


function default_style_dict() {
	var style_dict = {};
	for (ele_id of all_ids) {
		style_dict[ele_id] = 0;
	}
	style_dict['row_head_horz_align'] = 'left';
	style_dict['col_head_horz_align'] = 'center';
	style_dict['body_horz_align'] = 'center';
	style_dict['row_head_vert_align'] = 'middle';
	style_dict['col_head_vert_align'] = 'middle';
	style_dict['body_vert_align'] = 'middle';
	style_dict['row_head_size'] = 6;
	style_dict['col_head_size'] = 6;
	style_dict['body_size'] = 5.25;
	style_dict['min_row_height'] = 5;
	style_dict['min_col_width'] = 5;
	style_dict['row_head_font'] = 'Georgia';
	style_dict['col_head_font'] = 'Georgia';
	style_dict['body_font'] = 'Georgia';
	style_dict['worker_id'] = '';
	return style_dict;
}
const letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
function translate_to_short(s) {
	var pos = all_ids.indexOf(s);
	if (pos >= 0) {
		return letters[pos];
	} 
	return s
}
function translate_to_long(s) {
	if (letters.includes(s) && s.length == 1) {
		var pos = letters.indexOf(s);
		return all_ids[pos];
	}
	return s;
}
function translate_dict_to_short(d) {
	var d2 = {};
	for (var id in d) {
		var val = d[id];
		if (val === true) {
			val = 't';
		} else if (val === false) {
			val = 'f';
		}
		d2[translate_to_short(id)] = val;
	}
	return d2
}
function translate_dict_to_long(d) {
	var d2 = {};
	for (var id in d) {
		d2[translate_to_long[id]] = d[id];
	}
	return d2
}
function remove_default_values(style_dict) {
	var default_style = default_style_dict();
	for (var id in default_style) {
		if (id in style_dict && style_dict[id] == default_style[id]) {
			delete style_dict[id];
		}
	}
}
function get_iframe() {
	return document.getElementById("table_viewer");
}
function get_table() {
	const iframe = get_iframe();
	if (iframe == null) {
		return document.getElementsByTagName('table')[0];
	} else {
		return iframe.contentDocument.getElementsByTagName('table')[0];
	}
}
function get_trs() {
	return get_table().querySelectorAll('tr');
}
function get_even_trs() {
	var tab = get_table();
	var even_rows = [];
	for (var i = 0; i < tab.rows.length; i++) {
		if (i % 2 == 0) {
			var row = tab.rows[i];
			for (var k =0; k < row.cells.length; k++) {
				even_rows.push(row.cells[k]);
			}
		}
	}
	return even_rows;
}
function get_tds() {
	return get_table().querySelectorAll('tr td');
}
function get_ths_tds_first_cols(n) {
	first_cols = [];
	var table = get_table();
	for (var i = 0; i < table.rows.length; i++) {
		for (var j = 0; j < n; j++) {
			first_cols.push(table.rows[i].cells[j]);
		}
	}
	return first_cols;
}
function get_ths_tds_last_cols(n) {
	last_cols = [];
	var table = get_table();
	for (var i = 0; i < table.rows.length; i++) {
		for (var j = 0; j < n; j++) {
			last_cols.push(table.rows[i].cells[table.rows[i].cells.length-j-1]);
		}
	}
	return last_cols;
}
function get_ths_tds_first_rows(n) {
	first_rows = [];
	for (var i = 0; i < n; i++) {
		var cells = get_table().rows[i].cells;
		for (var j = 0; j < cells.length; j++) {
			first_rows.push(cells[j]);
		}
	}
	return first_rows;
}
function get_ths_tds_last_rows(n) {
	var last_rows = [];
	var table = get_table();
	for (var i = 0; i < n; i++) {
		var cells = table.rows[table.rows.length-i-1].cells;
		for (var j = 0; j < cells.length; j++) {
			last_rows.push(cells[j]);
		}
	}
	return last_rows;
}
function get_col_header_rows_ths() {
	return get_col_ths();
}
function get_row_header_cols_ths() {
	return get_table().querySelectorAll('th[scope="row"], th.stub');
}
function get_ths() {
	return get_table().querySelectorAll('th');
}

function get_col_ths() {
	return get_table().querySelectorAll('th[scope="col"]');
}
function get_row_ths() {
	return get_table().querySelectorAll('th[scope="row"]');
}
function get_ths_tds() {
	return get_table().querySelectorAll('td, th');
}
function get_val(id) {
	if (check_box_ids.includes(id)) {
		return document.getElementById(id).checked;
	} else {
		return document.getElementById(id).value;
	}
}
function set_value(id, val) {
	if (check_box_ids.includes(id)) {
		document.getElementById(id).checked = val;
	} else {
		document.getElementById(id).value = val;
	}
}
function get_style_dict() {
	var style_dict = {};
	for (var id of all_ids) {
		style_dict[id] = get_val(id);
	}
	return style_dict;
}
function on_change() {
	update_style(get_style_dict());
	update_qr_code();
}
function set_row_stripe_css(val) {
	conditional_add_remove_class_to_collection(get_even_trs(), 'stripe', val);
}
function set_row_border_css(val) {
	conditional_add_remove_class_to_collection(get_trs(), 'rowborders', val);
}
function set_col_border_css(val) {
	conditional_add_remove_class_to_collection(get_ths_tds(), 'colborders', val);
}

function set_row_head_frozen_css(val) {
	conditional_add_remove_class_to_collection(get_row_header_cols_ths(), 'row_sticky', val);
	//conditional_add_remove_class_to_collection(get_row_ths(), 'row_sticky', val);
}
function set_col_head_frozen_css(val) {
	conditional_add_remove_class_to_collection(get_col_header_rows_ths(), 'col_sticky', val);
	//conditional_add_remove_class_to_collection(get_col_ths(), 'col_sticky', val);
}

function set_row_header_bold_css(val) {
	conditional_add_remove_class_to_collection(get_row_ths(), 'bold', val);
}
function set_col_header_bold_css(val) {
	conditional_add_remove_class_to_collection(get_col_ths(), 'bold', val);
}

function set_row_header_italic_css(val) {
	conditional_add_remove_class_to_collection(get_row_ths(), 'italic', val);
}
function set_col_header_italic_css(val) {
	conditional_add_remove_class_to_collection(get_col_ths(), 'italic', val);
}

function set_row_header_underline_css(val) {
	conditional_add_remove_class_to_collection(get_row_ths(), 'underline', val);
}
function set_col_header_underline_css(val) {
	conditional_add_remove_class_to_collection(get_col_ths(), 'underline', val);
}

function set_row_header_background_css(val) {
	conditional_add_remove_class_to_collection(get_row_ths(), 'row_background', val);
}
function set_col_header_background_css(val) {
	conditional_add_remove_class_to_collection(get_col_ths(), 'col_background', val);
}

function set_row_header_size_css(val) {
	set_css_to_collection(get_row_ths(), 'font-size', val + "vw");
}
function set_col_header_size_css(val) {
	set_css_to_collection(get_col_ths(), 'font-size', val + "vw");
}

function set_row_header_font_css(val) {
	set_css_to_collection(get_row_ths(), 'font-family', val);
}
function set_col_header_font_css(val) {
	set_css_to_collection(get_col_ths(), 'font-family', val);
}

function set_body_size_css(val) {
	set_css_to_collection(get_tds(), 'font-size', val + "vw");
}
function set_body_font_css(val) {
	set_css_to_collection(get_tds(), 'font-family', val);
}

function set_row_space_css(val) {
	set_css_to_collection(get_tds(), 'padding-top', val + "vw");
	set_css_to_collection(get_ths_tds(), 'padding-bottom', val + "vw");
	set_css_to_collection(get_ths_tds_first_rows(1), 'padding-top', Math.round(val / 3) + "vw");  // smaller top padding for first row
	set_css_to_collection(get_ths_tds_last_rows(1), 'padding-bottom', Math.round(val / 3) + "vw");  // smaller bottom padding for last row
}
function set_col_space_css(val) {
	set_css_to_collection(get_ths_tds(), 'padding-right', val + "vw");
	set_css_to_collection(get_ths_tds(), 'padding-left', val + "vw");
	set_css_to_collection(get_ths_tds_first_cols(1), 'padding-left', Math.round(val / 3) + "vw");
	set_css_to_collection(get_ths_tds_last_cols(1), 'padding-right', Math.round(val / 3) + "vw");
}

function set_min_col_width_css(val) {
	set_css_to_collection(get_ths_tds(), 'min-width', val + "vw");
}
function set_min_row_height_css(val) {
	set_css_to_collection(get_ths_tds(), 'height', val + "vw");
}

function set_row_head_horz_align_css(val) {
	set_css_to_collection(get_row_ths(), 'text-align', val);
}
function set_col_head_horz_align_css(val) {
	set_css_to_collection(get_col_ths(), 'text-align', val);
}
function set_body_horz_align_css(val) {
	set_css_to_collection(get_tds(), 'text-align', val);
}

function set_row_head_vert_align_css(val) {
	set_css_to_collection(get_row_ths(), 'vertical-align', val);
}
function set_col_head_vert_align_css(val) {
	set_css_to_collection(get_col_ths(), 'vertical-align', val);
}
function set_body_vert_align_css(val) {
	set_css_to_collection(get_tds(), 'vertical-align', val);
}

function conditional_add_remove_class_to_collection(collect, class_name, val) {
	for (var ele of collect) {
		if (val) {
			ele.classList.add(class_name);
		} else {
			ele.classList.remove(class_name);
		}
	}
}
function set_css_to_collection(collect, prop_name, val) {
	for (var ele of collect) {
		ele.style[prop_name] = val;
	}
}

function update_style(style_dict) {
	console.log("update style");
	console.log(style_dict);
	for (var ele_id of all_ids) {
		if (ele_id in style_dict) {
			var value = style_dict[ele_id];
			var f = null;
			switch (ele_id) {
				case "row_stripe": f = set_row_stripe_css; break;
				case "row_border": f = set_row_border_css; break;
				case "col_border": f = set_col_border_css; break;
				case "row_head_frozen": f = set_row_head_frozen_css; break;
				case "col_head_frozen": f = set_col_head_frozen_css; break;
				case "row_head_bold": f = set_row_header_bold_css; break;
				case "col_head_bold": f = set_col_header_bold_css; break;
				case "row_head_italic": f = set_row_header_italic_css; break;
				case "col_head_italic": f = set_col_header_italic_css; break;
				case "row_head_under": f = set_row_header_underline_css; break;
				case "col_head_under": f = set_col_header_underline_css; break;
				case "row_head_back": f = set_row_header_background_css; break;
				case "col_head_back": f = set_col_header_background_css; break;
				case "row_head_size": f = set_row_header_size_css; break;
				case "col_head_size": f = set_col_header_size_css; break;
				case "row_head_font": f = set_row_header_font_css; break;
				case "col_head_font": f = set_col_header_font_css; break;
				case "row_head_vert_align": f = set_row_head_vert_align_css; break;
				case "col_head_vert_align": f = set_col_head_vert_align_css; break;
				case "row_head_horz_align": f = set_row_head_horz_align_css; break;
				case "col_head_horz_align": f = set_col_head_horz_align_css; break;
				case "body_size": f = set_body_size_css; break;
				case "body_font": f = set_body_font_css; break;
				case "row_space": f = set_row_space_css; break;
				case "col_space": f = set_col_space_css; break;
				case "min_col_width": f = set_min_col_width_css; break;
				case "min_row_height": f = set_min_row_height_css; break;
				case "body_horz_align": f = set_body_horz_align_css; break;
				case "body_vert_align": f = set_body_vert_align_css; break;
			}
			if (f != null) {
				f(value);
			}
		}
	}
}
function set_controls(style_dict) {
	for (var id of all_ids) {
		if (id in style_dict) {
			set_value(id, style_dict[id]);
		}
	}
}
function show_hide_header_controls() {
	var row_head_div = document.getElementById("row_head_div");
	if (get_row_ths().length > 0) {
		row_head_div.style.display = "block";
	} else {
		row_head_div.style.display = "none";
	}
	var col_head_div = document.getElementById("col_head_div");
	if (get_col_ths().length > 0) {
		col_head_div.style.display = "block";
	} else {
		col_head_div.style.display = "none";
	}
}
function get_view_url() {
	var style_dict = get_style_dict();
	style_dict['table_id'] = table_id;
	remove_default_values(style_dict);
	style_dict = translate_dict_to_short(style_dict);
	var urlParams = new URLSearchParams(style_dict);
	var query_param_str = urlParams.toString();
	return window.location.origin + '/view_table.html?' + query_param_str;
}
function view_preview() {
	window.open(get_view_url());
}
function update_qr_code() {
	clear_qr_code();
	new QRCode(document.getElementById("qr_code"), get_view_url());
}
function clear_qr_code() {
	document.getElementById("qr_code").innerHTML = '';
}
function start() {
	var urlParams = new URLSearchParams(window.location.search);
	if (urlParams.has('table_id')) {
		table_id = urlParams.get('table_id');
	} else {
		table_id = 'demo';
	}
	loadTable();
}
function postLoadTable() {
	var urlParams = new URLSearchParams(window.location.search);
	var style_dict = default_style_dict();
	for (ele_id of all_ids) {
		if (urlParams.has(ele_id) || urlParams.has(translate_to_short(ele_id))) {
			var val = '';
			if (urlParams.has(ele_id)) {
				val = urlParams.get(ele_id);
			} else {
				val = urlParams.get(translate_to_short(ele_id));
			}
			if (val == 'f' || val == 'false') {
				val = false;
			} else if (val == 't' || val == 'true') {
				val = true;
			}
			style_dict[ele_id] = val;
		}
	}
	set_css_to_collection(get_ths_tds(), 'padding', 0);  // override default padding
	if (is_style_tool()) {
		show_hide_header_controls();
		set_controls(style_dict);
		update_qr_code();
	}
	update_style(style_dict);
}

function loadTable() {
	if (is_style_tool()) {
		set_value('table_id', table_id);
	}
	const iframe = get_iframe();
	iframe.onload = function() { 
		let link = document.createElement("link");
		link.href = "table_style.css";   
		link.rel = "stylesheet";
		get_iframe().contentDocument.head.appendChild(link);
		postLoadTable();
	}
	iframe.src = "tables/" + table_id + ".html";
}

function on_submit() {
	var response_ele = document.getElementById("response")
	response_ele.innerHTML = '';
	var style_dict = get_style_dict();
	style_dict['table_id'] = table_id;

	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
		if (this.readyState == 4) {
			if (this.status == 200) {
				if (this.responseText == "Success") {
					response_ele.innerHTML = '<span style="color:green">Success</span>';
				} else {
					response_ele.innerHTML = '<span style="color:red">' + this.responseText + '</span>';
				}
			} else {
				response_ele.innerHTML = '<span style="color:red">Failed to Submit (' + this.status + ')</span>';
			}
	   }
	};
	xhttp.open("POST", "/submit", false); // synchronous
	xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
	xhttp.send(new URLSearchParams(style_dict).toString());
}

