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
import os
import re
import traceback
from HTMLParser import HTMLParser
from operator import itemgetter

import pycurl

import settings
from account import Admin
from utility import load_config, save_config, log, get_html

class TopicParser(HTMLParser):
	"""Parse topics from page source"""
	def __init__(self):
		HTMLParser.__init__(self)
		self._in_topic_td = False
		self._in_topic_anchor = False
		self._topic_list = []
		self._current_topic = {
			'title': None,
			'url': None,
			'id': None
		}

	def handle_starttag(self, tag, attrs):
		if tag == 'td' and ('class', 'thread_title') in attrs:
			self._in_topic_td = True
		elif tag == 'a' and self._in_topic_td:
			self._in_topic_anchor = True
			for attr in attrs:
				if attr[0] == 'href':
					self._current_topic['url'] = settings.SITE_DOMAIN + attr[1]
					self._current_topic['id'] = int(re.search(
						'^.*\/(\d+)$', 
						self._current_topic['url']
					).groups()[0])
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
	for filter in settings.CONFIG['filters']:
		title_regex = re.compile(filter)
		if title_regex.match(title) is not None:
			return True
		else:
			continue
	return False

class TopicContentParser(HTMLParser):
	"""Parse topic content from page source"""
	def __init__(self):
		HTMLParser.__init__(self)
		self._in_content_paragraph = False
		self._is_first_floor = True
		self._topic_content = ''

	def handle_starttag(self, tag, attrs):
		if tag == 'p' and ('class', 'd_post_content') in attrs and self._is_first_floor == True:
			self._in_content_paragraph = True

	def handle_data(self, data):
		if self._in_content_paragraph:
			self._topic_content = ' '.join([self._topic_content, data])

	def handle_endtag(self, tag):
		if tag == 'p' and self._in_content_paragraph:
			self._in_content_paragraph = False
			self._is_first_floor = False

	def feed(self, data):
		try:
			HTMLParser.feed(self, data)
			return self._topic_content
		except Exception, e:
			log(unicode(traceback.format_exc()))
			return None

def get_topic_content(topic_url):
	page_source = get_html(topic_url.decode('utf8'))

	# Hack quotation marks
	page_source = page_source.replace('&quot;', '\"')

	if page_source is not None:
		topic_content_parser = TopicContentParser()
		return topic_content_parser.feed(page_source)
	else:
		return None

def is_topic_content_match(topic_url):
	log(unicode('Fetching %s' % topic_url))

	topic_content = get_topic_content(topic_url)

	if topic_content is not None:
		for filter in settings.CONFIG['filters']:
			topic_content_regex = re.compile(filter)
			if topic_content_regex.match(topic_content) is not None:
				return True
			else:
				continue
		return False
	else:
		return False

def get_new_topic_list(topic_list, board_url):
	sorted_topic_list = sorted(topic_list, key=itemgetter('id'))
	new_topic_list = []

	for topic_index in range(0, len(sorted_topic_list)):
		topic_id = sorted_topic_list[topic_index]['id']
		if  topic_id > settings.CONFIG['latest_topic_id'][board_url]:
			new_topic_list.append(sorted_topic_list[topic_index])
			settings.CONFIG['latest_topic_id'][board_url] = topic_id

	save_config(config=settings.CONFIG)

	return new_topic_list

def main():
	# Load config
	load_config()

	for monitor_info in settings.MONITOR_INFOS:
		try:
			# Get topic list
			topic_list = get_topic_list(monitor_info['board_url'])

			# Get new topic list
			new_topic_list = get_new_topic_list(topic_list, monitor_info['board_url'])

			# Get spam topics
			topic_to_delete = []
			for topic in new_topic_list:
				if is_title_match(topic['title']) or is_topic_content_match(topic['url']):
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
						admin.delete_topic(topic['url'])
					admin.clean()
		except Exception, e:
			log(unicode(traceback.format_exc()))
			continue

if __name__ == '__main__':
	main()
