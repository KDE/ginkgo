#!/usr/bin/env python
# -*- coding: utf-8 -*-

## This file may be used under the terms of the GNU General Public
## License version 2.0 as published by the Free Software Foundation
## and appearing in the file LICENSE included in the packaging of
## this file. 
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
## See the NOTICE file distributed with this work for additional
## information regarding copyright ownership.

# Cross platform MIME detection library
# Source: http://code.google.com/p/pydingo/ GPL
 
import mimetypes
from os.path import join, isfile, isdir
from os import listdir

import xdg.Mime
import xdg.IconTheme
import xdg.DesktopEntry

def get_mime(file):
	"""
	Return mime type of a file
	"""
	# xdg returns text/plain for everything on Windows, and application/executable on Mac :)
	if xdg and unicode(xdg.Mime.get_type('file.sql')) == u'text/x-sql':
		file = unicode(file)
		#try pyxdg linux/unix backed
		try:
			mime = xdg.Mime.get_type(file, name_pri=51)
		except:
			mime = False
	else:
		# fallback to python mimetypes module (on Windows/Mac)
		mimetypes.init()
		ext = u'.%s' % file.split('.')[-1]
		try:
			mime = mimetypes.types_map[ext]
		except:
			mime = False
	return mime

def is_plaintext(mimetype):
	"""
	Check if mime is plaintext
	"""
	# non text/* mimetypes that are used for text files
	plain_mimes = ['application/javascript', 'application/x-javascript', 'application/xml', 'application/x-csh', 'application/x-sh', 'application/x-shellscript',
		'application/javascript', 'application/x-perl', 'application/x-php', 'application/x-ruby']

	mimetype = unicode(mimetype)
	if plain_mimes.count(mimetype) > 0:
		return True
	elif mimetype.startswith('text'):
		return True
	
	return False

def get_icon(desktopFile):
	"""
	Try to get icon path for a given .desktop file
	"""
	desktopFile = desktopFile.split('-')[-1]
	desktopDirs = listdir('/usr/share/applications/')
	dst = [join('/usr/share/applications', desktopFile)]
	for d in desktopDirs:
		path = join('/usr/share/applications/', d)
		if isdir(path):
			dst.append(join(path, desktopFile))
	
	for desktopFile in dst:
		if isfile(desktopFile):
			de = xdg.DesktopEntry.DesktopEntry(filename=desktopFile)
			icon = xdg.IconTheme.getIconPath(de.getIcon())
			if icon:
				return icon
	return False

def get_icon_by_exec(executable):
	"""
	Try to get icon path for a given application executable
	"""
	icon = xdg.IconTheme.getIconPath(executable)
	if icon:
		return icon
	else:
		executable = executable.split('-')[0]
		icon = xdg.IconTheme.getIconPath(executable)
		if icon:
			return icon
	return False