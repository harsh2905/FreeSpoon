#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, re
import MySQLdb
from datetime import datetime
from openpyxl import load_workbook

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import pdb

class Report():

	def __init__(self):
		self.conn = MySQLdb.connect(
			host='localhost', 
			user='root', 
			passwd='123456', 
			port=3306,
			charset='utf8')
		self.conn.select_db('FreeSpoon')
		self.cellDatas = {}
		self.width = 2

	def generate(self, path):
		if not os.path.exists(path):
			return
		wb = load_workbook(path)
		if wb is None:
			return
		ws = wb.active
		wss = wb.create_sheet()
		r = 1
		position = 0
		while True:
			isEmpty = True
			repeatNum = 0
			for c in range(0, self.width):
				cellName = chr(ord('A') + c) + str(r)
				newCellName = chr(ord('A') + c) + str(r + position)
				val = ws[cellName].value
				val = val if val is not None else ''
				val = str(val)
				if val is None or len(val.strip()) == 0:
					continue
				isEmpty = False
				(newVal, repeatNum_) = self.calcExp(cellName, val)#TODO
				repeatNum = repeatNum_ if repeatNum_ > repeatNum else repeatNum
				pdb.set_trace()
				wss[newCellName] = newVal
			r = r + 1
			if repeatNum > 0:
				position = position + repeatNum
				for _ in range(0, repeatNum):
					for c in range(0, self.width):
						cellName_ = chr(ord('A') + c) + str(r + _)
						(newVal_, __) = self.calcExp(cellName_)
						wss[cellName_] = newVal_
			if isEmpty:
				break
		wb.save(path + '.' + datetime.strftime(datetime.now(), '%Y%m%d%H%M%S'))

	def calcExp(self, cellName, cellVal=None):
		# Database Column Name: SQL statement
		rexp = r'\{\{(.+)\}\}'
		if cellVal is None:
			#TODO
			rawRowIndex = int(cellName[1:])
			rowIndex = rawRowIndex
			while (rowIndex > 0):
				rowIndex = rowIndex - 1
				cellData = self.cellDatas.get(cellName[0] + str(rowIndex), None)
				if cellData is None:
					continue
				sqlData = cellData.get('sqlData', None)
				template = cellData.get('template', None)
				columnName = cellData.get('columnName', None)
				lineNum = rawRowIndex - rowIndex
				if len(sqlData) <= lineNum:
					return (template, 0)
				rowData = sqlData[lineNum]
				val = rowData.get(columnName, None)
				val = val if val is not None else '' # !
				newVal = re.sub(rexp, val, template)
				return (newVal, 0)
			return ('', 0)
		matchGroup = re.search(rexp, cellVal, re.M|re.I)
		if matchGroup is None:
			return (cellVal, 0)

		exp = matchGroup.group(1)

		args = exp.split(':')
		if len(args) <> 2:
			return (cellVal, 0)
		columnName = args[0]
		sqlStatement = args[1]
		sqlData = None
		if len(sqlStatement.strip()) == 0:
			columnIndex = ord(cellName[0])
			while (columnIndex > ord('A')):
				columnIndex = columnIndex - 1
				cellData = self.cellDatas.get(chr(columnIndex) + cellName[1:], None)
				if cellData is not None:
					sqlData = cellData.get('sqlData', None)
					break
		else:
			cur = self.conn.cursor(MySQLdb.cursors.DictCursor)
			cur.execute(sqlStatement)
			sqlData = cur.fetchall()
		if sqlData is None:
			return (cellVal, 0)
		cellData = {
			'sqlData': sqlData,
			'template': cellVal,
			'columnName': columnName
		}
		self.cellDatas[cellName] = cellData
		rowData = sqlData[0]
		val = rowData.get(columnName, None)
		val = val if val is not None else '' # !
		newVal = re.sub(rexp, val, cellVal)
		return (newVal, len(sqlData) - 1)


if __name__ == '__main__':
	r = Report()
	r.generate('../../1.xlsx')








