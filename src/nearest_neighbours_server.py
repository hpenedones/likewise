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


@app.route('/images/<image_index:int>')
def send_image(image_index):
	print (index[image_index])
	return static_file(index[image_index], "/", mimetype='image/jpg')

@app.route('/random')
def random_sample():
	rand_index = random.randint(0,len(index))
	return nearest(rand_index, 20)

@app.route('/nearest/<n:int>/<image_index:int>')
def nearest(image_index, n):
	start = time.time()
	distances = {}
	for i in range(len(index)):
		distances[i] = scipy.spatial.distance.cosine(features[i], features[image_index])
	k_keys_sorted_by_values = heapq.nsmallest(n, distances, key=distances.get)
	
	response = ""

	for i in k_keys_sorted_by_values:
		img_url = "/images/%d" % (i)
		nearest_url = "/nearest/%d/%d" % (n, i)
		response += "<a href=\"%s\"><img src=\"%s\"></a> %s\n" % (nearest_url, img_url, str(distances[i]))
		
	end = time.time()
	print str(end - start) + " secs"

	return response


def read_features(features_filepath, num_features):
	index = {} 
	features = {}
	img_num = 0
	for line in open(features_filepath):
		tokens = line.split(args.separator)
		filename = tokens[0]
		if len(tokens) -1 != num_features:
			print("%s has %d features instead of %d. Skipping it." % (filename, len(tokens)-1, num_features))
			continue 
		index[img_num] = filename
		features[img_num] = np.array(map(float, tokens[1:]))
		img_num += 1	
	return index, features

# command line arguments

parser = argparse.ArgumentParser(description='Image similarity and labeling web server')
parser.add_argument("--port", type=int, default=8080, help="tcp port to run server on")
parser.add_argument("--nfeat", type=int, default=3072, help="expected dimensionality of the feature vector")
parser.add_argument("--hostname", default="0.0.0.0", help="hostname of the machine where the webserver is running")
parser.add_argument("--separator", default="\t", help="token separator in input files")
parser.add_argument("features_filepath", help="path to file containing image paths followed by their feature vector")

args = parser.parse_args()

index, features = read_features(args.features_filepath, args.nfeat)

run(app, host=args.hostname, port=args.port)

