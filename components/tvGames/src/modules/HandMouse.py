import collections


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


class HandMouse:
	def __init__(self):
		self._buffer = collections.deque(maxlen=5)

	def add_state(self, position, is_open):
		self._buffer.append([position, is_open])

	def is_open(self):
		return not self.is_closed()

	def is_closed(self):
		if len(self._buffer)<self._buffer.maxlen:
			return False
		for postion, is_open in self._buffer:
			if is_open:
				return False
		return True


if __name__ == '__main__':
	a = HandMouse()
	for i in range(2):
		a.add_state((i, i + 1), "open")

		for i in range(2):
			a.add_state((i, i + 1), "fist")

	print a.is_open()
