#!/usr/bin/python

import os, re
import MySQLdb
from openpyxl import load_workbook

class Report():

	def __init__(self):
		self.conn = MySQLdb.connect(
			host='localhost', 
			user='root', 
			passwd='123456', 
			port=3306)
		self.conn.select_db('FreeSpoon')
		self.sqlStatements = {}

	def generate(self, path):
		if not os.path.exists(path):
			return
		wb = load_workbook(path)
		if wb is None:
			return
		ws = wb.active
		wss = wb.create_sheet()
		r = 0
		position = 0
		while True:
			r = r + 1
			isEmpty = True
			repeatNum = 0
			for c in range(0, 26):
				cellName = chr(ord('A') + c) + str(r)
				val = ws[cellName]
				if val is None or len(val.strip()) == 0:
					continue
				isEmpty = False
					wss[cellName] = newVal
				else:
					wss[cellName] = val
			if isEmpty:
				break
		pass

	def calcExp(cellName, cellVal):
		# Database Column Name: SQL statement
		rexp = r'\{\{(.+)\}\}'
		matchGroup = re.search(rexp, cellVal, re.M|re.I)
		if matchGroup is None:
			exp = matchGroup.group(1)
			(result, repeatNum_) = calcExp(exp)
			repeatNum = repeatNum_ if repeatNum_ > repeatNum else repeatNum
			result = result if result is not None else ''
			newVal = re.sub(rexp, result, val)
		args = exp.split(':')
		if len(args) <> 2:
			return (None, 0)
		columnName = args[0]
		sqlStatement = args[1]
		sqlData = None
		if len(sqlStatement.strip()) == 0:
			columnIndex = ord(cellName[0])
			while (columnIndex < ord('A')):
				columnIndex = columnIndex - 1
				sqlData = self.sqlDatas.get(chr(columnIndex) + cellName[1], None)
				if sqlData is not None:
					self.sqlDatas[cellName] = sqlData
					break
		else:
			cur = self.conn.cursor(MySQLdb.cursors.DictCursor)
			cur.execute(sqlStatement)
			sqlData = cur.fetchall()
			self.sqlDatas[cellName] = sqlData
		if sqlData is None:
			return (None, 0)
		rowData = sqlData[0]
		val = rowData.get(columnName, None)
		return (val, len(sqlData))
			



