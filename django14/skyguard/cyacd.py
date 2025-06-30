#!/usr/bin/env python
# -*- coding: utf-8 -*-

import struct

class BootloaderRow(object):
	def __init__(self):
		self.array_id = None
		self.row_number = None
		self.data = None

	@classmethod
	def read(cls, data, line=None):
		self = cls()
		if data[0] != ':':
			raise ValueError("Bootloader rows must start with a colon")
		#data = bytes.fromhex(data[1:])
		data = data[1:].decode('hex')
		self.array_id, self.row_number, data_length = struct.unpack('>BHH', data[:5])
		self.data = data[5:-1]
		if len(self.data) != data_length:
			raise ValueError("Row specified {0} bytes of data, but got {1}".format(data_length, len(self.data)))
		(checksum,) = struct.unpack('B', data[-1])
		data_checksum = (0x100 - (sum(ord(x) for x in data[:-1]) & 0xFF)) &0xFF
		if checksum != data_checksum:
			raise ValueError("Computed checksum of 0x{0:X}, but expected 0x{1:X} on line {2}".format(data_checksum, checksum, line))
		return self

	@property
	def checksum(self):
		"""Returns the data checksum. Should match what the bootloader returns."""
		# Python2
		#if (six.PY3): return 0xFF & (1 + ~sum(self.data))
		#return 0xFF & (1 + ~sum(ord(x) for x in self.data))
		return (0x100 - (sum(ord(x) for x in self.data[:-1]) & 0xFF)) &0xFF

	def __str__(self):
		x = "Array ID {0.array_id}, Row # {0.row_number}, Checksum: {0.checksum}".format(self)
		return x
		
class BootloaderData(object):
	def __init__(self):
		self.silicon_id = None
		self.silicon_rev = None
		self.checksum_type = None
		self.arrays = {}
		self.total_rows = 0
		self.rows = []

	@classmethod
	def read(cls, f):
		#header = bytes.fromhex(f.readline().strip())
		header = f.readline().strip().decode('hex')

		if len(header) != 6:
			raise ValueError("Expected 12 byte header line first, firmware file may be corrupt.")
		self = cls()
		self.silicon_id, self.silicon_rev, self.checksum_type = struct.unpack('>LBB', header)
		for i, line in enumerate(f):
			row = BootloaderRow.read(line.strip(), i + 2)
			self.rows.append(row)
			if row.array_id not in self.arrays:
				self.arrays[row.array_id] = {}
			self.arrays[row.array_id][row.row_number] = row
			self.total_rows += row.row_number;
		return self

	def __str__(self):
		x = "Silicon ID {0.silicon_id}, Silicon Rev. {0.silicon_rev}, Checksum type {0.checksum_type}, Arrays {1} total rows {2}".format(
			self, len(self.arrays), len(self.rows)
			)
		return x