import sys
import math
from bottle import Bottle, route, run, static_file, request
import operator
import os
import time
import numpy as np
from scipy.spatial import distance
import random
import argparse
from nextdoor.nextdoor import NearestNeighborsIndex

app = Bottle()


@app.route('/images/<image_index:int>')
def send_image(image_index):
	return static_file(keymap[image_index], "/", mimetype='image/jpg')

@app.route('/random')
def random_sample():
	rand_key = random.choice(index.keys())
	return nearest(rand_key, 20)

@app.route('/nearest/<n:int>/<image_key:int>')
def nearest(image_key, n):
	start = time.time()
	nearest = index.knearest(index[image_key], n)
	
	response = ""
	for i in nearest:
		img_url = "/images/%d" % (i)
		nearest_url = "/nearest/%d/%d" % (n, i)
		response += "<a href=\"%s\"><img src=\"%s\"></a> %s\n" %\
			(nearest_url,
			 img_url,
			 str(distance.euclidean(index[i], index[image_key])))
		
	end = time.time()
	print str(end - start) + " secs"

	return response


def read_features(features_filepath, num_features):
	index = NearestNeighborsIndex()
	keymap = {}
	for img_num, line in enumerate(open(features_filepath)):
		tokens = line.split(args.separator)
		filename = tokens[0]
		if len(tokens) -1 != num_features:
			print("%s has %d features instead of %d. Skipping it." % (filename, len(tokens)-1, num_features))
			continue 
		keymap[img_num] = filename
		index[img_num] = np.array(map(float, tokens[1:]))
	return keymap, index

# command line arguments

parser = argparse.ArgumentParser(description='Image similarity and labeling web server')
parser.add_argument("--port", type=int, default=8080, help="tcp port to run server on")
parser.add_argument("--nfeat", type=int, default=3072, help="expected dimensionality of the feature vector")
parser.add_argument("--hostname", default="0.0.0.0", help="hostname of the machine where the webserver is running")
parser.add_argument("--separator", default="\t", help="token separator in input files")
parser.add_argument("features_filepath", help="path to file containing image paths followed by their feature vector")

args = parser.parse_args()

keymap, index = read_features(args.features_filepath, args.nfeat)

run(app, host=args.hostname, port=args.port)

