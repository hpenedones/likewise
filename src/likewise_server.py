import argparse
import os
import operator
import random
import sys
import time
import logging

from scipy.spatial import distance
import numpy as np
from bottle import Bottle, route, run, static_file, request, template
from nextdoor.nextdoor import NearestNeighborsIndex

def perflog(func):
    def wrap(*args, **kwargs):
        started_at = time.time()
        result = func(*args, **kwargs)
        logging.debug("Method '%s' took %dms", func.__name__, int((time.time() - started_at)*1000))
        return result
    return wrap

app = Bottle()

@app.route('/images/<image_path:path>')
def send_image(image_path):
	return static_file(image_path, "/", mimetype='image/jpg')

@app.route('/random')
@app.route('/')
def random_sample():
	rand_key = random.randint(0, len(keymap))
	return nearest(rand_key, 20)

@app.route('/nearest/<n:int>/<image_key:int>')
@perflog
def nearest(image_key, n):
	nearest = index.knearest(index[image_key], n)
	
	images = []
	for i in nearest:
		image = {}
		image['key'] = i
		image['url'] = "/images/%s" % (keymap[i])
		image['distance'] = distance.euclidean(index[i], index[image_key])
		images.append(image)

	return template('likewise', images=images, pagination=(0,n))

@perflog
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

# set logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)-8s %(asctime)-26s %(message)s')

keymap, index = read_features(args.features_filepath, args.nfeat)

run(app, server='paste', host=args.hostname, port=args.port)
