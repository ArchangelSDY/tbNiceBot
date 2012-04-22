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
from HTMLParser import HTMLParser
import os
import re
import StringIO
import traceback
import urllib
import cPickle

import pycurl

# Monitor info
MONITOR_INFOS = [{
	'board_url': r'',
	'login_username': r'',
	'login_password': r'',
}, {
	'board_url': r'',
	'login_username': r'',
	'login_password': r'',
}]

# For the below paths, absolute path may be better when used as a cron task.
# Filters file path
FILTERS_FILE = r'filters'

# Log path
LOG_PATH = r'tbNiceBot.log'

# No need to change settings below.
# Site info
SITE_DOMAIN = r'http://tieba.baidu.com'
TOPIC_DELETE_POINT = r'http://tieba.baidu.com/f/commit/thread/delete'
LOGIN_POINT = r'https://passport.baidu.com/?login'

# User agent
USER_AGENT = r'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'


FILTERS = []

def log(info):
	with open(LOG_PATH, 'a+') as log_file:
		# print info
		time = datetime.datetime.now()
		log_file.write('%s: %s\n' % (time, info.encode('utf8')))

def read_filters():
	with open(FILTERS_FILE, "rb") as filters_file:
		return cPickle.load(filters_file)

def get_html(url, cookie_file=None):
	try:
		curl = pycurl.Curl()
		curl.setopt(pycurl.URL, str(url))

		# Ignore SSL.
		curl.setopt(pycurl.SSL_VERIFYPEER, False)

		# Follow redirection.
		curl.setopt(pycurl.FOLLOWLOCATION, True)

		# Set user agent
		curl.setopt(pycurl.USERAGENT, USER_AGENT)

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

class TopicParser(HTMLParser):
	"""Parse topics from page source"""
	def __init__(self):
		HTMLParser.__init__(self)
		self._in_topic_td = False
		self._in_topic_anchor = False
		self._topic_list = []
		self._current_topic = {}

	def handle_starttag(self, tag, attrs):
		if tag == 'td' and ('class', 'thread_title') in attrs:
			self._in_topic_td = True
		elif tag == 'a' and self._in_topic_td:
			self._in_topic_anchor = True
			for attr in attrs:
				if attr[0] == 'href':
					self._current_topic['href'] = attr[1]
					break

	def handle_data(self, data):
		if self._in_topic_td and self._in_topic_anchor:
			self._current_topic['title'] = data
			self._topic_list.append(self._current_topic)
			self._current_topic = {}

	def handle_endtag(self, tag):
		if tag == 'a' and self._in_topic_anchor:
			self._in_topic_anchor = False
		elif tag == 'td' and self._in_topic_td:
			self._in_topic_td = False

	def feed(self, data):
		try:
			HTMLParser.feed(self, data)
			return self._topic_list
		except Exception, e:
			log(unicode(traceback.format_exc()))
			return None

def get_topic_list(board_url):
	page_source = get_html(board_url.decode('utf8'))

	# Hack quotation marks
	page_source = page_source.replace('&quot;', '\"')

	if page_source is not None:
		topic_parser = TopicParser()
		return topic_parser.feed(page_source)
	else:
		return None

def is_title_match(title):
	for filter in FILTERS:
		title_regex = re.compile(filter)
		if title_regex.match(title) is not None:
			return True
		else:
			continue
	return False

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
			curl.setopt(pycurl.URL, LOGIN_POINT)

			# Ignore SSL.
			curl.setopt(pycurl.SSL_VERIFYPEER, False)

			# Follow redirection.
			curl.setopt(pycurl.FOLLOWLOCATION, True)

			# Set user agent
			curl.setopt(pycurl.USERAGENT, USER_AGENT)

			# POST
			curl.setopt(pycurl.POST, 1)
			post_params = [
				('username', username.decode('utf8').encode('gbk')),
				('password', password),
				('mem_pass', 'on'),
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
			curl.setopt(pycurl.URL, board_url)
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
			curl.setopt(pycurl.URL, TOPIC_DELETE_POINT)

			# Set referer
			curl.setopt(pycurl.REFERER, str(topic_url))

			# Ignore SSL.
			curl.setopt(pycurl.SSL_VERIFYPEER, False)

			# Follow redirection.
			curl.setopt(pycurl.FOLLOWLOCATION, True)

			# Set user agent
			curl.setopt(pycurl.USERAGENT, USER_AGENT)

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

def main():
	# Read filters list
	global FILTERS
	# Comment this line below if you do not want to use the web admin. Hard code filter expressions in 'FILTERS' instead.
	FILTERS = read_filters()

	for monitor_info in MONITOR_INFOS:
		try:
			# Get topic list
			topic_list = get_topic_list(monitor_info['board_url'])

			# Get spam topics
			topic_to_delete = []
			for topic in topic_list:
				if is_title_match(topic['title']):
					topic_to_delete.append(topic)
					log('Spam <%s> detected.' % topic['title'])

			# Delete spam topics
			if len(topic_to_delete) > 0:
				admin = Admin.login(
					monitor_info['login_username'], 
					monitor_info['login_password'], 
					monitor_info['board_url']
				)
				if admin is not None:
					for topic in topic_to_delete:
						full_href = SITE_DOMAIN + topic['href']
						admin.delete_topic(full_href)
					admin.clean()
		except Exception, e:
			log(unicode(traceback.format_exc()))
			continue

if __name__ == '__main__':
	main()
