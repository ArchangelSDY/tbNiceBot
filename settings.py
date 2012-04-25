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

# Infos about monitoring
MONITOR_INFOS = [
	{
		'login_username': r'',
		'login_password': r'',
		'board_url': r''
	}
]

# For the below paths, absolute path may be better when used as a cron task.
# Config file path
CONFIG_PATH = r'config'

# Log path
LOG_PATH = r'tbNiceBot.log'

# No need to change settings below.
# Site info
SITE_DOMAIN = r'http://tieba.baidu.com'
TOPIC_DELETE_POINT = r'http://tieba.baidu.com/f/commit/thread/delete'
LOGIN_POINT = r'https://passport.baidu.com/?login'

# User agent
USER_AGENT = r'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:12.0) Gecko/20100101 Firefox/12.0'

# Keep changable config
CONFIG = {}