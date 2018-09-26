import collections
from datetime import datetime
from datetime import timedelta

import numpy as np

start_time = datetime.now()


class MultiHandMouses:
	def __init__(self):
		self._mouses = {}

	def add_state(self, hand_id, position, state):
		if hand_id not in self._mouses.keys():
			self._mouses[hand_id] = HandMouse(hand_id)
		self._mouses[hand_id].add_state(position, state)
		return self._mouses[hand_id]

	def is_open(self, hand_id):
		return self._mouses[hand_id].is_open()

	def is_closed(self, hand_id):
		return self._mouses[hand_id].is_closed()

	def is_valid(self, hand_id):
		return self._mouses[hand_id].is_valid()


class HandMouse:
	def __init__(self, hand_id):
		self._id = hand_id
		self._buffer = collections.deque(maxlen=5)
		self._valid = False
		self._filter = MeanFilter()

	def add_state(self, position, is_open):

		self._valid, self._buffer = self._filter.filter_state(self._buffer, position, is_open)

		if not self._valid:
			print("Position discarded (%s - %s)" % (str(position), str(is_open)))


	def is_open(self):
		return not self.is_closed()

	def is_closed(self):
		if len(self._buffer) < self._buffer.maxlen:
			return False
		for postion, is_open in self._buffer:
			if is_open:
				return False
		return True

	def is_valid(self):
		return self._valid

	def last_pos(self):
		if len(self._buffer)>0:
			return self._buffer[-1][0]
		else:
			return None

	def last_state(self):
		if len(self._buffer)>0:
			return self._buffer[-1][1]
		else:
			return None

	def hand_id(self):
		return self._id

class MouseStateFilter:
	def filter_state(self):
		raise NotImplementedError('You need to define a filter_state method!')


class VelocityFilter(MouseStateFilter):
	def __init__(self):
		self._last_position = None
		self._last_update_time = None
		self._velocity_threshold = 10

	def filter_state(self, buffer, position, is_open):
		valid = False
		current_time = datetime.now()
		if self._last_update_time is not None:
			elapsed_time = self._last_update_time - current_time
			if self._last_position is not None:
				dist = np.linalg.norm(np.array(self._last_position) - np.array(position))
				velocity = dist / (elapsed_time.microseconds / 1000000.0)
				print("all: ", velocity)
				# TODO: velocity threshold should be configurable
				if velocity < self._velocity_threshold:
					buffer.append([position, is_open])
					valid= True
		self._last_position = position
		self._last_update_time = datetime.now()
		return valid, buffer


class MeanFilter(MouseStateFilter):
	def __init__(self):
		pass

	def filter_state(self, buffer, position, is_open):
		valid = False
		if len(buffer) > 1:
			new_position = np.average([buffer[-1][0], buffer[-2][0], position], axis=0)
			buffer.append([new_position, is_open])
			valid = True
		else:
			buffer.append([position, is_open])

		return valid, buffer


if __name__ == '__main__':
	a = HandMouse()
	for i in range(2):
		a.add_state((i, i + 1), "open")

		for i in range(2):
			a.add_state((i, i + 1), "fist")

	print a.is_open()
