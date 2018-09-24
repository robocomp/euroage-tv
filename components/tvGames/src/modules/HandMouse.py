import collections
from datetime import datetime
from datetime import timedelta

import numpy as np

start_time = datetime.now()

class MultiHandMouses:
	def __init__(self):
		self._mouses = {}

	def add_state(self, id, position, state):
		if id not in self._mouses.keys():
			self._mouses[id] = HandMouse()
		self._mouses[id].add_state(position, state)

	def is_open(self, id):
		return self._mouses[id].is_open()

	def is_closed(self, id):
		return self._mouses[id].is_closed()

	def is_valid(self, id):
		return self._mouses[id].is_valid()


class HandMouse:
	def __init__(self):
		self._buffer = collections.deque(maxlen=5)
		self._last_position = None
		self._last_update_time = None
		self._valid = False

	def add_state(self, position, is_open):
		current_time = datetime.now()
		if self._last_update_time is not None:
			elapsed_time = self._last_update_time - current_time
			if self._last_position is not None:
				dist = np.linalg.norm(np.array(self._last_position) - np.array(position))
				velocity = dist / (elapsed_time.microseconds/1000000.0)
				print("all: ",velocity)
				# TODO: velocity threshold should be configurable
				if velocity < 10:
					self._valid = True
					print("saved: ", velocity)
					self._buffer.append([position, is_open])
				else:
					self._valid = False
		self._last_position = position
		self._last_update_time = datetime.now()


	def is_open(self):
		return not self.is_closed()

	def is_closed(self):
		if len(self._buffer)<self._buffer.maxlen:
			return False
		for postion, is_open in self._buffer:
			if is_open:
				return False
		return True

	def is_valid(self):
		return self._valid


if __name__ == '__main__':
	a = HandMouse()
	for i in range(2):
		a.add_state((i, i + 1), "open")

		for i in range(2):
			a.add_state((i, i + 1), "fist")

	print a.is_open()
