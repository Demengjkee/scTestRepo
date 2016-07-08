#! /usr/bin/python

import requests
import sys
from collections import Counter
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys

def request(url, name, pw):
	headers = {'Content-Type': 'application/json'}
	r = requests.get(url + "2/search?jql=project = AT AND createdDate >= -30d", 
		auth = (name, pw), headers = headers)
	print "Status: " + str(r.status_code)
	try:
		return r.json()
	except ValueError:
		if r.status_code == 401:
			print "Wrong credentials"
		else:
			print "An error occurred"
		exit(1)

def parse_assignee(json):
	data = []
	for obj in json['issues']:
		data.append(obj['fields']['assignee']['displayName'])
	return data

def parse_task_specific(json):
	data = []
	for obj in json['issues']:
		ts_values = obj['fields']['customfield_12756']
		if ts_values != None:
			for ts_value in ts_values:
				data.append(ts_value['value'])
		else:
			data.append("None")
			
	return data
	
def parse_done(json):
	data = []
	for obj in json['issues']:
		status = obj['fields']['status']['name']
		if status == "In Validation" or status == "Closed":
			data.append(status)
	return data
	
def get_labels(data):
	labels = list(set(data))
	return labels

def create_report(data, report_name):
	counted = Counter(data)
	labels = get_labels(data)
	pies = []
	for label in labels:
		pies.append(counted[label])
	labels = map(lambda label, pie: label + ": " + str(pie), labels, pies) #creating cool labels =)
	plt.pie(pies, labels=labels, autopct='%1.1f%%', colors=colors,
		shadow=True, startangle=200)
	plt.axis('equal')
	plt.title(report_name)
	output_file_name = report_name + ".png"
	plt.savefig(output_file_name, bbox_inches='tight')
	plt.gcf().clear()
	print "Generated report, output: " + output_file_name


if __name__ == "__main__":
	url = "https://jira.devops.mnscorp.net/rest/api/"
	name = "mcharopkin"
	pw = sys.argv[1]
	json = request(url, name, pw)
	colors = ['darkgray', 'yellowgreen', 'blue', 'green', 'red', 'cyan', 'magenta', 'yellow',
		'white', 'seagreen', 'navy', 'slateblue', 'orchid', 'sienna']
	create_report(parse_assignee(json), "Assignee")
	create_report(parse_task_specific(json), "Task specific")
	create_report(parse_done(json), 'In Validation or Closed')
