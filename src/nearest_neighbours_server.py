import sys
import math
from bottle import Bottle, route, run, static_file, request
import operator
import heapq
import os
import time
import numpy as np
import scipy.spatial.distance
import random
import argparse

app = Bottle()


@app.route('/images/<filename:re:.*\.jpg>')
def send_image(filename):
	return static_file(filename, basepath, mimetype='image/jpg')

@app.route('/random')
def random_sample():
	random_image = os.path.basename(random.choice(features.keys()))
	return nearest(random_image, 20)

@app.route('/save_labels', method='POST')
def save_labels():
	resp = ""
	for k in request.forms.keys():
		if k in labels:
			new_label = request.forms[k]
			labels[k] = [new_label]
			resp += "Image %s labeled as %s<br>" % (k, new_label)
	return resp

@app.route('/nearest/<n>/<image>')
def nearest(image, n):
	start = time.time()
	n = int(n)
	distances = {}
	for img in features:
		distances[img] = scipy.spatial.distance.cosine(features[img], features[image])
	k_keys_sorted_by_values = heapq.nsmallest(n, distances, key=distances.get)
	
	response = "<form action=\"/save_labels\" method=\"post\">"

	tags = ["NA", "car", "person", "animal", "building", "sky", "clouds"]

		
	for i in k_keys_sorted_by_values:
		img_url = "http://%s:%s/images/%s" % (args.hostname, str(args.port), i)
		nearest_url = "http://%s:%s/nearest/%s/%s" % (args.hostname, str(args.port), str(n), i)
		response += "<a href=\"%s\"><img src=\"%s\"></a> %s\n" % (nearest_url, img_url, str(distances[i]))
		tags_select = ""
		for t in tags:		
			tags_select += "\n\t<option %s value=\"%s\">%s</option>" % ("selected=\"selected\"" if labels[i][0] == t else "", t, t)
		response += "<select name=\"%s\">%s\n</select><br>\n" % (i, tags_select)
		
	response += "<input type=\"submit\" name=\"submit\">"
	
	end = time.time()
	print str(end - start) + " secs"

	return response


def read_features(features_filepath):
	features = {}
	num_cols = 0
	is_first_sample = True
	for line in open(features_filepath):
		tokens = line.split(args.separator)
		filename = tokens[0]
		if is_first_sample:  # extract the images base folder from the first line of the dataset
			basepath = os.path.dirname(filename)
			num_cols = len(tokens)
			is_first_sample = False	
		else:
			if len(tokens) != num_cols:
				print("%s has %d features instead of %d. Skipping it." % (filename, len(tokens)-1, num_cols-1))
				continue 
		filename = os.path.basename(filename)
		features[filename] = np.array(map(float, tokens[1:]))	
	return features, basepath

def read_labels(labels_filepath):
	labels = {}
	for line in open(labels_filepath):
		line = line[:-1] # remove \n character
		tokens = line.split(args.separator)
		filename = tokens[0]
		labels[filename] = tokens[1:]
	return labels
	 
# command line arguments

parser = argparse.ArgumentParser(description='Image similarity and labeling web server')
parser.add_argument("--port", type=int, default=8080, help="tcp port to run server on")
parser.add_argument("--hostname", default="localhost", help="hostname of the machine where the webserver is running")
parser.add_argument("--separator", default="\t", help="token separator in input files")
parser.add_argument("features_filepath", help="path to file containing image paths followed by their feature vector")
parser.add_argument("labels_filepath", help="path to file containing image paths followed by their label")

args = parser.parse_args()

features, basepath = read_features(args.features_filepath)
labels = read_labels(args.labels_filepath)

run(app, host=args.hostname, port=args.port)

