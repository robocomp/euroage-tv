import cv2
import numpy as np

from modules.QImageWidget import QImageWidget


class PaintGame:
	def __init__(self, screen_height, screen_width, frame=None):
		self._tv_image = QImageWidget()
		self._screen_height = screen_height
		self._screen_width = screen_width
		self._pointer_tracks = {}
		self._current_postition = {}
		self._tv_canvas = np.zeros((self._screen_height, self._screen_width, 3), dtype="uint8")
		self._tv_canvas[::] = 255
		self._pointers_overlay = np.zeros((self._screen_height, self._screen_width, 3), dtype="uint8")
		self._pointers_overlay[::] = 255
		self._frame = frame
		self.generate_new_canvas()

	def init_game(self, value):
		self._pointer_tracks = {}
		self._current_postition = {}
		self._tv_canvas = np.zeros((self._screen_height, self._screen_width, 3), dtype="uint8")
		self._tv_canvas[::] = 255
		self._pointers_overlay = np.zeros((self._screen_height, self._screen_width, 3), dtype="uint8")
		self._pointers_overlay[::] = 255
		self._frame = None
		self.generate_new_canvas()

	def generate_new_canvas(self):
		if self._frame is None:
			self._tv_canvas = np.zeros((self._screen_height, self._screen_width, 3), dtype="uint8")
			self._tv_canvas[::] = 255
		else:
			self._tv_canvas = np.zeros((self._screen_height, self._screen_width, 3), dtype="uint8")
			cv2.fillPoly(self._tv_canvas, np.array([[self._frame]], dtype=np.int32), [255,255,255])


	def set_frame(self, frame):
		self._frame = [frame[0], frame[2], frame[3], frame[1]]
		self.generate_new_canvas()

	def show(self):
		self._tv_image.show_on_second_screen()

	def hide(self):
		self._tv_image.hide()



	def drag_to(self, pointer_id, point):
		if pointer_id in self._pointer_tracks:
			self._pointer_tracks[pointer_id].append(point)
		else:
			self._pointer_tracks[pointer_id] = [point]
		self._current_postition[pointer_id] = point
		self.paint()

	def move_to(self, pointer_id, point):
		self._pointer_tracks[pointer_id] = []
		self._current_postition[pointer_id] = point
		self.paint()

	def update_pointer(self, pointer_id, point_x, point_y, state):
		if not state:
			self.move_to(pointer_id, (point_x, point_y))
		else:
			self.drag_to(pointer_id, (point_x, point_y))

	def paint(self):
		self._pointers_overlay[::] = 255

		for pointer_id in self._pointer_tracks.keys():
			self._tv_canvas = self.draw_pointer_track(self._tv_canvas, pointer_id)

		for point in self._current_postition.values():
			pointers_overlay = self.draw_pointer(self._pointers_overlay, point)

		# if self.screen_factor != 1:
		# 	self._pointers_overlay = cv2.resize(self._pointers_overlay, None, fx=self.screen_factor, fy=self.screen_factor,
		# 						  interpolation=cv2.INTER_CUBIC)
		# 	asdf = cv2.resize(self._tv_canvas, None, fx=self.screen_factor, fy=self.screen_factor,
		# 						  interpolation=cv2.INTER_CUBIC)
		self._pointers_overlay = cv2.cvtColor(self._pointers_overlay, cv2.COLOR_RGB2RGBA)
		self._pointers_overlay[np.all(self._pointers_overlay == [0, 0, 0, 255], axis=2)] = [0, 0, 0, 0]
		asdf = cv2.cvtColor(self._tv_canvas, cv2.COLOR_RGB2RGBA)
		mixed = cv2.addWeighted(asdf, 0.4, self._pointers_overlay, 0.1, 0)
		mixed = cv2.cvtColor(mixed, cv2.COLOR_RGBA2RGB)
		self._tv_image.set_opencv_image(mixed, False)

	def draw_pointer(self, frame, point, color=[100, 0, 255]):
		if point is not None:
			# Draw center mass
			cv2.circle(frame, tuple(point), 7, color, 2)
		# cv2.putText(frame, 'Center', tuple(point), self.font, 0.5, (255, 255, 255), 1)
		return frame

	def draw_pointer_track(self, frame, pointer_id):
		pointer_track = self._pointer_tracks[pointer_id]
		if len(pointer_track) > 2:
			for i in np.arange(1, len(pointer_track)):
				p1 = pointer_track[i]
				p0 = pointer_track[i - 1]
				cv2.line(frame, tuple(p0), tuple(p1), (0, 0, 255), 3)
		return frame