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

import json

import tornado.ioloop
import tornado.web
import tornado.template

# Config path
CONFIG_PATH = r"../config"

# Max length of a filter
FILTER_LEN_LIMIT = 256

# Keep global config
CONFIG = {}

def load_config(path=CONFIG_PATH):
	with open(path, "r") as config_file:
		global CONFIG
		CONFIG = json.load(config_file)

def save_config(path=CONFIG_PATH):
	with open(path, "w") as config_file:
		json.dump(CONFIG, config_file)

class ListHandler(tornado.web.RequestHandler):
	def get(self):
		filter_list = []
		for filter in CONFIG["filters"]:
			filter_list.append({
				"regex": filter,
				"id": CONFIG["filters"].index(filter)
			})
		self.render("index.html", filter_list=filter_list)

class AddHandler(tornado.web.RequestHandler):
	def post(self):
		new_filter = self.get_argument("new_filter")
		if len(new_filter) <= FILTER_LEN_LIMIT:
			CONFIG["filters"].append(new_filter)
			print "add", new_filter
			save_config()
		self.redirect("/")
		
class DeleteHandler(tornado.web.RequestHandler):
	def get(self, filter_id):
		if filter_id.isdigit():
			filter_id = int(filter_id)
			if filter_id >= 0 and filter_id < len(CONFIG["filters"]):
				deleted_filter = CONFIG["filters"].pop(int(filter_id))
				print "delete", deleted_filter 
				save_config()
		self.redirect("/")
		
application = tornado.web.Application([
	(r"/", ListHandler),
	(r"/add", AddHandler),
	(r"/delete/(\d+)", DeleteHandler),
])

if __name__ == "__main__":
	load_config()
	application.listen(8888)
	tornado.ioloop.IOLoop.instance().start()
