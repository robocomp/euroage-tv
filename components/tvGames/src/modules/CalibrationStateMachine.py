import cv2
import numpy as np


def copy_roi(big_image, small, row, col):
	# initial number of rows and columns
	rows = small.shape[0]
	cols = small.shape[1]
	big_image[row:row + rows, col:col + cols, :] = small[:rows, :cols, :]
	return big_image


class GenericCalibrationStateMachine(object):
	def __init__(self, screen_width, screen_height):
		self.screen_height = screen_height
		self.screen_width = screen_width
		self._image = np.array(np.zeros((self.screen_height, self.screen_width, 3)), dtype=np.uint8)
		self._image[:] = (255, 255, 255)
		self._state = 0
		self._screen_points = []
		self._camera_points = []
		self._homography = None

	def update(self):
		pass

	@property
	def image(self):
		return self._image

	@image.setter
	def image(self, value):
		print("CalibrationStateMachine: calibration image cant be set externally")

	@property
	def state(self):
		return self._state

	@state.setter
	def state(self, value):
		self._state = value

	@property
	def homography(self):
		return self._homography

	@homography.setter
	def homography(self, value):
		print("CalibrationStateMachine: homography cant be set externally")


class ManualCalibrationStateMachine(GenericCalibrationStateMachine):
	def __init__(self, screen_width, screen_height):
		super(ManualCalibrationStateMachine, self).__init__(screen_width, screen_height)
		self._camera_points = [[50, 57], [50, 475], [570, 57], [570, 475]]
		self._screen_points = [[184, 0], [184, 1080], [1704, 0], [1704, 1080]]
		self._homography, _ = cv2.findHomography(np.array(self._camera_points),
												 np.array(self._screen_points))
		self._state = 4

	def update(self):
		return True


class MouseCalibrationStateMachine(GenericCalibrationStateMachine):
	def __init__(self, screen_width, screen_height):
		super(MouseCalibrationStateMachine, self).__init__(screen_width, screen_height)
		self._mouse_clicked = None
		# TODO: It would be calculated
		self._states_values = \
			{
				0:
					{
						"screen_x_pos": "5",
						"screen_y_pos": "5",
						"camera_x_pos": "0",
						"camera_y_pos": "0"

					},
				1:
					{
						"screen_x_pos": "5",
						"screen_y_pos": "self.screen_height-5",
						"camera_x_pos": "0",
						"camera_y_pos": "480"
					},
				2:
					{
						"screen_x_pos": "self.screen_width-5",
						"screen_y_pos": "5",
						"camera_x_pos": "640",
						"camera_y_pos": "0"
					},
				3:
					{
						"screen_x_pos": "self.screen_width - 5",
						"screen_y_pos": "self.screen_height - 5",
						"camera_x_pos": "640",
						"camera_y_pos": "480"
					}
			}

	def update(self, mouse_clicked):
		self._mouse_clicked = mouse_clicked
		if self._state > 4 or self._state < 0:
			return
		# draw image

		cal_state = self._states_values[self._state]
		# read wait for click
		if self._mouse_clicked != None:
			self._screen_points.append([self._mouse_clicked[0] - 1920, self._mouse_clicked[1]])
			self._camera_points.append([eval(cal_state["camera_x_pos"]),
										eval(cal_state["camera_y_pos"])])
			self._state = self._state + 1
			self._mouse_clicked = None
			if self._state == 4:
				self._homography, _ = cv2.findHomography(np.array(self._camera_points),
														 np.array(self._screen_points))
				return True
			return False
		else:
			return False


class CalibrationStateMachine(GenericCalibrationStateMachine):
	def __init__(self, screen_width, screen_height):
		super(CalibrationStateMachine, self).__init__(screen_width, screen_height)
		self.tv_reduction = 0
		self.apriltag_size_factor = 0.2
		self.april_0 = cv2.imread('resources/april_0.png')
		self.april_0 = cv2.resize(self.april_0, None, fx=self.apriltag_size_factor, fy=self.apriltag_size_factor,
								  interpolation=cv2.INTER_CUBIC)
		self.april_1 = cv2.imread('resources/april_1.png')
		self.april_1 = cv2.resize(self.april_1, None, fx=self.apriltag_size_factor, fy=self.apriltag_size_factor,
								  interpolation=cv2.INTER_CUBIC)
		self.april_2 = cv2.imread('resources/april_2.png')
		self.april_2 = cv2.resize(self.april_2, None, fx=self.apriltag_size_factor, fy=self.apriltag_size_factor,
								  interpolation=cv2.INTER_CUBIC)
		self.april_3 = cv2.imread('resources/april_3.png')
		self.april_3 = cv2.resize(self.april_3, None, fx=self.apriltag_size_factor, fy=self.apriltag_size_factor,
								  interpolation=cv2.INTER_CUBIC)
		self.last_tags = []
		# TODO: It would be calculated
		self._homography_adjustment = 20
		self._states_values = \
			{
				0:
					{
						"tag": self.april_0,
						"roi_x_pos": "self.tv_reduction",
						"roi_y_pos": "self.tv_reduction",
						"orig_x_pos": "5+self.tv_reduction",
						"orig_y_pos": "5+self.tv_reduction",
						"ref_x_pos": "detected_tags[0].tx-self._homography_adjustment",
						"ref_y_pos": "detected_tags[0].ty-self._homography_adjustment"

					},
				1:
					{
						"tag": self.april_1,
						"roi_x_pos": "self.tv_reduction",
						"roi_y_pos": "self.screen_height - self.april_1.shape[0] - self.tv_reduction",
						"orig_x_pos": "5+self.tv_reduction",
						"orig_y_pos": "self.screen_height-self.tv_reduction",
						"ref_x_pos": "detected_tags[0].tx-self._homography_adjustment",
						"ref_y_pos": "detected_tags[0].ty+self._homography_adjustment"

					},
				2:
					{
						"tag": self.april_2,
						"roi_x_pos": "self.screen_width - self.april_2.shape[1] - self.tv_reduction",
						"roi_y_pos": "self.tv_reduction",
						"orig_x_pos": "self.screen_width-self.tv_reduction",
						"orig_y_pos": "5+self.tv_reduction",
						"ref_x_pos": "detected_tags[0].tx+self._homography_adjustment",
						"ref_y_pos": "detected_tags[0].ty-self._homography_adjustment"

					},
				3:
					{
						"tag": self.april_3,
						"roi_x_pos": "self.screen_width - self.april_3.shape[1] - self.tv_reduction",
						"roi_y_pos": "self.screen_height - self.april_3.shape[0] - self.tv_reduction",
						"orig_x_pos": "self.screen_width - self.tv_reduction",
						"orig_y_pos": "self.screen_height - self.tv_reduction",
						"ref_x_pos": "detected_tags[0].tx+self._homography_adjustment",
						"ref_y_pos": "detected_tags[0].ty+self._homography_adjustment"

					}
			}

	def update(self, detected_tags):
		if self._state > 4 or self._state < 0:
			return
		cal_state = self._states_values[self._state]
		try:
			self._image[:] = (255, 255, 255)
			copy_roi(self._image, cal_state["tag"], eval(cal_state["roi_y_pos"]), eval(cal_state["roi_x_pos"]))
		except:
			print("Calibration failed")
			self._state = -1
		if len(detected_tags) == 1:
			if detected_tags[0].id == self._state:
				self._screen_points.append([eval(cal_state["orig_x_pos"]), eval(cal_state["orig_y_pos"])])
				self._camera_points.append([eval(cal_state["ref_x_pos"]),
											eval(cal_state["ref_y_pos"])])
				self._state = self._state + 1
				cv2.waitKey(1000)
				self.tv_reduction = 0
				if self._state == 4:
					self._homography, _ = cv2.findHomography(np.array(self._camera_points),
															 np.array(self._screen_points))
					# self.admin_interface.statusBar().showMessage("Calibration ended")
					return True
			return False
		else:
			self.tv_reduction += 1
			return False
