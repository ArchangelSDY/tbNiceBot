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
import cPickle

import tbNiceBot

class TestTbBot(unittest.TestCase):
	def setUp(self):
		# Remove cookie file
		if os.path.exists(tbNiceBot.Admin.COOKIE_PATH):
			os.unlink(tbNiceBot.Admin.COOKIE_PATH)

		# Make filters file
		with open('filters', 'w') as filters_file:
			cPickle.dump(['^1$', '^123$'], filters_file)

	def test_read_filters(self):
		filters = tbNiceBot.read_filters()
		self.assertEqual(len(filters), 2)

	def test_get_html(self):
		url = 'http://tieba.baidu.com/f?kw=%D2%B9%C3%F7%C7%B0%B5%C4%C1%F0%C1%A7%C9%AB'
		result = tbNiceBot.get_html(url)
		self.assertIsNotNone(result)

	def test_get_topic_list(self):
		board_url = 'http://tieba.baidu.com/f?kw=%D2%B9%C3%F7%C7%B0%B5%C4%C1%F0%C1%A7%C9%AB'
		topic_list = tbNiceBot.get_topic_list(board_url)
		self.assertIsNotNone(topic_list)

	def test_admin_login(self):
		for monitor_info in tbNiceBot.MONITOR_INFOS:
			admin = tbNiceBot.Admin.login(monitor_info['login_username'], monitor_info['login_password'], monitor_info['board_url'])
			with open(tbNiceBot.Admin.COOKIE_PATH, 'r') as cookie_file:
				cookie = cookie_file.read()
				self.assertNotEqual(cookie.find('BDUSS'), -1)

	def tearDown(self):
		if os.path.exists(tbNiceBot.Admin.COOKIE_PATH):
			os.unlink(tbNiceBot.Admin.COOKIE_PATH)

if __name__ == '__main__':
	unittest.main()