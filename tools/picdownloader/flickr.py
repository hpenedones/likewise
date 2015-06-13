import flickrapi
import urllib
import os
import threading

api_key = u'USE_YOURS'
api_secret = u'USE_YOURS'
user_id = '61139829@N00'
file_root = '/datasets/' + user_id + '/'

if not os.path.isdir(file_root):
	os.makedirs(file_root)

def background(f):
    def bg_f(*a, **kw):
        threading.Thread(target=f, args=a, kwargs=kw).start()
    return bg_f

@background
def download_set(flickr, photoset):
	set_id = photoset['id']
	print("downloading %s %s" % (s['title']['_content'], s['id']))
	photos = flickr.photosets.getPhotos(photoset_id=set_id, user_id=user_id)
	for p in photos['photoset']['photo']:
		photo_id = p['id']
		sizes = flickr.photos.getSizes(photo_id=photo_id)
		sizes = [x for x in sizes['sizes']['size'] if x['label'] == 'Small 320'] 
		if len(sizes) > 0:
			url = sizes[0]['source']
			file_path = file_root + url.split('/')[-1]
			if not os.path.exists(file_path):
				print("\tdownloading photo %s from %s" % (photo_id, url))
				photo_file = urllib.URLopener()
				photo_file.retrieve(url, file_path) 

flickr = flickrapi.FlickrAPI(api_key, api_secret, format='parsed-json')

sets = flickr.photosets.getList(user_id=user_id)

for s in sets['photosets']['photoset']:
	download_set(flickr, s)
