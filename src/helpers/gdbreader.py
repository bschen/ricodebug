# ricodebug - A GDB frontend which focuses on visually supported
# debugging using data structure graphs and SystemC features.
#
# Copyright (C) 2011  The ricodebug project team at the
# Upper Austrian University Of Applied Sciences Hagenberg,
# Department Embedded Systems Design
#
# This file is part of ricodebug.
#
# ricodebug is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# For further information see <http://syscdbg.hagenberg.servus.at/>.

from PyQt4.QtCore import QThread, QMutex, QSemaphore, SIGNAL
from gdbresultparser import GdbResultParser
from gdboutput import GdbOutput
from collections import deque

class GdbReader(QThread):
	def __init__(self, connector, parent=None):
		QThread.__init__(self, parent)

		self.resultRecordQueue = deque()
		self.resultRecordMutex = QMutex()
		self.resultRecordSem = QSemaphore(0)
		self.asynQueue = deque()
		self.asynMutex = QMutex()
		self.asynSem = QSemaphore(0)
		self.streamQueue = deque()
		self.streamMutex = QMutex()
		self.streamSem = QSemaphore(0)

	def startReading(self, stdout):
		self.stdout = stdout
		self.start()

	def run(self):
		self.listener()

	def listener(self):
		lines = []
		while True:
			line = self.stdout.readline()
			if line.startswith("(gdb)"):
				#print "[Listener] got result: ", lines
				
				# Check if there is a multiple break
				if lines[0].startswith("&\"info break "):
					asString = "<Multiple Break>"
					for line in lines:
						asString += line
						print line
					self.forwardMultipleBreakPointInfo(asString)
				results = GdbResultParser.parse(lines)
				lines = []
				for res in results:
					self.forwardResult(res)
			else:
				lines.append(line)

	def forwardMultipleBreakPointInfo(self, lines):
		self.emit(SIGNAL("forwardMultipleBreakpointInfo(PyQt_PyObject)"), lines)

	def forwardResult(self, res):
		type_ = res.type_
		if type_ == GdbOutput.RESULT_RECORD:
			self.enqueueResult(res)
		elif type_ == GdbOutput.EXEC_ASYN or \
			 type_ == GdbOutput.STATUS_ASYN or \
			 type_ == GdbOutput.NOTIFY_ASYN:
			self.emit(SIGNAL("asyncRecordReceived(PyQt_PyObject)"), res)
		elif type_ == GdbOutput.CONSOLE_STREAM or \
			 type_ == GdbOutput.TARGET_STREAM or \
			 type_ == GdbOutput.LOG_STREAM:
			self.emit(SIGNAL("consoleRecordReceived(PyQt_PyObject)"), res)
		else:
			raise "Illegal type_!"

	def enqueueResult(self, gdbresult):
		# enqueueResult will be deprecated for other types
		assert(gdbresult.type_ == GdbOutput.RESULT_RECORD)
		q = self.resultRecordQueue
		m = self.resultRecordMutex
		s = self.resultRecordSem

		m.lock()
		q.append(gdbresult)
		m.unlock()
		s.release()
	
	def getResult(self, type_):
		# getResult will be deprecated for other types
		assert(type_ == GdbOutput.RESULT_RECORD)
		q = self.resultRecordQueue
		m = self.resultRecordMutex
		s = self.resultRecordSem

		s.acquire()
		m.lock()
		res = q.popleft()
		m.unlock()
		return res
