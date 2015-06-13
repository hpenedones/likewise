import overfeat
import numpy
from scipy.ndimage import imread
from scipy.misc import imresize
import sys

# command line arguments
network_path = sys.argv[1]
layer_index = int(sys.argv[2])


def read_image(image_path):
	# read image
	try:
		image = imread(image_path)
		
		# resize and crop into a 231x231 image
		h0 = image.shape[0]
		w0 = image.shape[1]
		d0 = float(min(h0, w0))
		image = image[int(round((h0-d0)/2.)):int(round((h0-d0)/2.)+d0),
        		      int(round((w0-d0)/2.)):int(round((w0-d0)/2.)+d0), :]
		image = imresize(image, (231, 231)).astype(numpy.float32)

		# numpy loads image with colors as last dimension, transpose tensor
		h = image.shape[0]
		w = image.shape[1]
		c = image.shape[2]
		image = image.reshape(w*h, c)
		image = image.transpose()
		image = image.reshape(c, h, w)
	except:
		return None
	return image

def print_features(image_path, features):
	line = image_path + '\t' + '\t'.join(map(str,features))
	print(line) 
	

# initialize overfeat. Note that this takes time, so do it only once if possible
overfeat.init(network_path, 0)

for image_path in sys.stdin:
 	image_path = image_path[:-1] # remove \n char
	image = read_image(image_path)
	# run overfeat on the image
	features = []
	if not image is None:
		b = overfeat.fprop(image)
		features = overfeat.get_output(layer_index).flatten()
		print_features(image_path, features)

