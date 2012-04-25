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

import unittest
import os
import json
import re

import tbNiceBot
import settings

class TestTbBot(unittest.TestCase):
	def setUp(self):
		# Remove cookie file
		if os.path.exists(tbNiceBot.Admin.COOKIE_PATH):
			os.unlink(tbNiceBot.Admin.COOKIE_PATH)

		# Make filters file
		with open('config_test', 'w') as config_test_file:
			config_data = { 
				'filters': [
					r'^◆◇$',
					r'.*卡迪琳娜学院.*',
				],
				'latest_topic_id': {
					'http://tieba.baidu.com/f?kw=%D2%B9%C3%F7%C7%B0%B5%C4%C1%F0%C1%A7%C9%AB': 1539493000
				}
			}
			json.dump(config_data, config_test_file)

	def test_load_config(self):
		tbNiceBot.load_config('config_test')
		self.assertEqual(settings.CONFIG['filters'][0].encode('utf8'), '^◆◇$')

	def test_get_html(self):
		url = 'http://tieba.baidu.com/f?kw=%D2%B9%C3%F7%C7%B0%B5%C4%C1%F0%C1%A7%C9%AB'
		result = tbNiceBot.get_html(url)
		self.assertIsNotNone(result)

	def test_get_topic_list(self):
		board_url = 'http://tieba.baidu.com/f?kw=%D2%B9%C3%F7%C7%B0%B5%C4%C1%F0%C1%A7%C9%AB'
		topic_list = tbNiceBot.get_topic_list(board_url)
		self.assertIsNotNone(topic_list)

	def test_get_topic_content(self):
		topic_url = 'http://tieba.baidu.com/p/1549379482'
		topic_content = tbNiceBot.get_topic_content(topic_url)
		self.assertIsNotNone(topic_content)

	def test_is_topic_content_match(self):
		tbNiceBot.load_config('config_test')
		board_url = 'http://tieba.baidu.com/p/1549379482'
		self.assertEqual(tbNiceBot.is_topic_content_match(board_url), True)

	def test_admin_login(self):
		for monitor_info in settings.MONITOR_INFOS:
			admin = tbNiceBot.Admin.login(monitor_info['login_username'], monitor_info['login_password'], monitor_info['board_url'])
			with open(tbNiceBot.Admin.COOKIE_PATH, 'r') as cookie_file:
				cookie = cookie_file.read()
				bduss_regex = re.compile('BDUSS\s+([0-9a-zA-Z\-]+)')
				bduss = bduss_regex.search(cookie)
				self.assertNotEqual(len(bduss.groups()), 0)

	def tearDown(self):
		if os.path.exists(tbNiceBot.Admin.COOKIE_PATH):
			os.unlink(tbNiceBot.Admin.COOKIE_PATH)

		if os.path.exists('config_test'):
			os.unlink('config_test')

if __name__ == '__main__':
	unittest.main()