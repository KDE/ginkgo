#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Source: http://code.google.com/p/pydingo/ GPL 
# Extract MIME and suggested applications for a file on a Linux/Unix OS using gnome-vfs-python

try:
	import gnomevfs
except:
	print '*Optional dependency missing* No gnome-vfs-python package. Install it if you use GNOME or related WM for application suggesting and mime detection'

def get_meta_info(filename):
	try:
		file_mimetype = gnomevfs.get_mime_type(filename)
	except:
		return False
	
	ret = {}
	ret['mime'] = file_mimetype
	ret['default_app'] = gnomevfs.mime_get_default_application(file_mimetype)
	ret['other_apps'] = gnomevfs.mime_get_all_applications(file_mimetype)
	if len(ret['other_apps']) > 0:
		del ret['other_apps'][0]
	ret ['description'] = gnomevfs.mime_get_description(file_mimetype)
	return ret
