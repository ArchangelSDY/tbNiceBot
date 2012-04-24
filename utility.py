#!/usr/bin/python
# -*- coding: utf8 -*-

# Copyright (C) <2012>  <Archangel.SDY@gmail.com>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import datetime
import json
import StringIO
import traceback

import pycurl

import settings

def load_config(path=settings.CONFIG_PATH):
	with open(path, 'r') as config_file:
		settings.CONFIG = json.load(config_file)

def save_config(config=settings.CONFIG, path=settings.CONFIG_PATH):
	with open(path, "w") as config_file:
		json.dump(config, config_file)

def log(info):
	with open(settings.LOG_PATH, 'a+') as log_file:
		print info
		time = datetime.datetime.now()
		log_file.write('%s: %s\n' % (time, info.encode('utf8')))

def get_html(url, cookie_file=None):
	try:
		curl = pycurl.Curl()
		curl.setopt(pycurl.URL, str(url))

		# Ignore SSL.
		curl.setopt(pycurl.SSL_VERIFYPEER, False)

		# Follow redirection.
		curl.setopt(pycurl.FOLLOWLOCATION, True)

		# Set user agent
		curl.setopt(pycurl.USERAGENT, settings.USER_AGENT)

		# Set cookie file
		if cookie_file is not None and os.path.exists(cookie_file):
			curl.setopt(pycurl.COOKIEFILE, cookie_file)

		# Set content buffer
		content = StringIO.StringIO()
		curl.setopt(pycurl.WRITEFUNCTION, content.write)

		curl.perform()

		code = curl.getinfo(pycurl.HTTP_CODE)
		if int(code) == 200:
			return content.getvalue().decode('gbk')
		else:
			return None
	except Exception, e:
		log(unicode(traceback.format_exc()))
		return None