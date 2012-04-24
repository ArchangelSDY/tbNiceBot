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

import os
import re
import StringIO
import traceback
import urllib

import pycurl

import settings
from utility import log, get_html

class Admin(object):
	"""Admin operations."""

	COOKIE_PATH = 'cookie.txt'

	def __call__(self):
		raise TypeError('Use login() to create an admin instance')

	def __init__(self):
		super(Admin, self).__init__()

	@classmethod
	def login(self, username, password, board_url):
		try:
			curl = pycurl.Curl()
			curl.setopt(pycurl.URL, str(settings.LOGIN_POINT))

			# Ignore SSL.
			curl.setopt(pycurl.SSL_VERIFYPEER, False)

			# Follow redirection.
			curl.setopt(pycurl.FOLLOWLOCATION, True)

			# Set user agent
			curl.setopt(pycurl.USERAGENT, settings.USER_AGENT)

			# POST
			curl.setopt(pycurl.POST, 1)
			post_params = [
				('username', username.encode('gbk')),
				('password', password.encode('gbk')),
				('tpl', 'tb'),
			]
			curl.setopt(pycurl.POSTFIELDS, urllib.urlencode(post_params))

			# Set cookie jar
			curl.setopt(pycurl.COOKIEJAR, Admin.COOKIE_PATH)

			# Set content buffer
			content = StringIO.StringIO()
			curl.setopt(pycurl.WRITEFUNCTION, content.write)

			# Set header buffer
			header = StringIO.StringIO()
			curl.setopt(pycurl.HEADERFUNCTION, header.write)

			curl.perform()

			# Visit board page to get related cookies
			curl.setopt(pycurl.URL, str(board_url))
			curl.perform()

			return Admin()
		except Exception, e:
			log(unicode(traceback.format_exc()))
			return None

	def delete_topic(self, topic_url):
		try:
			page_source = get_html(topic_url, Admin.COOKIE_PATH).encode('utf8')

			tbs = re.search('tbs\:\"(.+)\"', page_source).groups()[0]

			kw = re.search('forum_name\:\"(.+?)\"', page_source).groups()[0]

			fid = re.search('fid\:\'(.+?)\'', page_source).groups()[0]

			tid = re.search('tid\:\'(.+?)\'', page_source).groups()[0]

			post_params = [
				('ie', 'utf-8'),
				('tbs', tbs),
				('kw', kw),
				('fid', fid),
				('tid', tid),
			]

			curl = pycurl.Curl()
			curl.setopt(pycurl.URL, settings.TOPIC_DELETE_POINT)

			# Set referer
			curl.setopt(pycurl.REFERER, str(topic_url))

			# Ignore SSL.
			curl.setopt(pycurl.SSL_VERIFYPEER, False)

			# Follow redirection.
			curl.setopt(pycurl.FOLLOWLOCATION, True)

			# Set user agent
			curl.setopt(pycurl.USERAGENT, settings.USER_AGENT)

			# POST
			curl.setopt(pycurl.POST, 1)
			curl.setopt(pycurl.POSTFIELDS, urllib.urlencode(post_params))

			# Set custom header
			custom_header = [
				'X-Requested-With: XMLHttpRequest',
				'DNT: 1',
				'Accept:  application/json, text/javascript, */*; q=0.01',
    			'Accept-Language:  en-us,en;q=0.5',
    			'Accept-Encoding:  gzip, deflate',
    			'Pragma:  no-cache',
    			'Cache-Control:  no-cache',
    			'HeaderEnd: CRLF',
    			'Content-Type: application/x-www-form-urlencoded; charset=UTF-8',
			]
			curl.setopt(pycurl.HTTPHEADER, custom_header)

			# Set cookie file
			curl.setopt(pycurl.COOKIEFILE , Admin.COOKIE_PATH)

			# Set content buffer
			content = StringIO.StringIO()
			curl.setopt(pycurl.WRITEFUNCTION, content.write)

			# Set header buffer
			header = StringIO.StringIO()
			curl.setopt(pycurl.HEADERFUNCTION, header.write)

			curl.perform()

		except Exception, e:
			log(unicode(traceback.format_exc()))
			return

	def clean(self):
		if os.path.exists(Admin.COOKIE_PATH):
			os.unlink(Admin.COOKIE_PATH)