from pynput.mouse import Button as pynput_Button
from pynput.mouse import Controller as pynput_Controller
from time import sleep

# custom modules
from helpers import get_window, get_contours, mouse_click

class ClickClick():
	''' class make ocr and
		return coordinates with (digit, coordinates) or None if not found '''
	def __init__(self, p1=[None, None], p2=[None, None]):
		self.p1 = p1
		self.p2 = p2

		# queue for input information; items are dictionary with possible
		# fields {'click': int, 'terminate': Bool}
		# click - number clicks, terminate - clean queues and break main loop
		# in play_game()
		self.queue_input = None

		# queue for output information; items are dictionary with possible
		# fields {'ready': Bool, 'click': int}
		# ready - OCR successful, click - possible to click
		self.queue_output = None 

		self.img_PIL = None
		self.numbers_coords = None
		self.click_number = 0
		self.ready = False

		self.make_ocr()

	def make_ocr(self):
		self.img_PIL = get_window(self.p1[0], self.p1[1], self.p2[0], self.p2[1])

		self.numbers_coords = get_contours(self.img_PIL)
		if self.numbers_coords:
			for item in self.numbers_coords:
				pass#print(item)

		if self.numbers_coords is not None:
			self.click_number = len(self.numbers_coords)
			self.ready = True
		else:
			self.click_number = 0
			self.ready = False

	def play_game(self, queue_input, queue_output):
		#print('playing_game')
		self.queue_input = queue_input
		self.queue_output = queue_output

		input_info = None
		n_click = 0

		self.mouse = pynput_Controller()
		#print('sent msg to main loop, ready:{}, click_number{}'\
		#	.format(self.ready, self.click_number))

		# inform main loop about readiness
		self.queue_output.put({'ready': self.ready, 'click': self.click_number})

		# looping until will receive msg to terminate
		while True:
			
			if self.queue_input.qsize():
				input_info = self.queue_input.get()
				print('game process got info:', input_info)
				# handle situation to exit from while loop
				if input_info['terminate']:
					n = self.queue_input.qsize()
					for i in range(n):
						_ = self.queue_input.get()

					n = self.queue_output.qsize()
					for i in range(n):
						_ = self.queue_output.get()
					break

				n_click = input_info['click']

				# calculate middle of the digit area
				dx = int(self.numbers_coords[0][1][2] / 2)
				dy = int(self.numbers_coords[0][1][3] / 2)

				for i in range(n_click):
					# Set pointer position
					self.mouse.position = (self.p1[0] + self.numbers_coords[0][1][0] + dx, \
										   self.p1[1] + self.numbers_coords[0][1][1] + dy)
					self.mouse.click(pynput_Button.left, 1)

					self.numbers_coords.remove(self.numbers_coords[0])
					self.click_number -= 1
					#print('pressed')

				if self.click_number == 0:
					# handle situation when all steps are done

					# move mouse pointer to position (100, 100) because in current position
					# it can interfere make ocr
					self.mouse.position = (100, 100)

					# waite some time to refresh screen
					sleep(1.7)

					self.make_ocr()
					#print('remake_ocr sending msg to main loop, ready:{}, click_number{}'\
					#		.format(self.ready, self.click_number))
					
					# inform main loop about readiness
					self.queue_output.put({'ready': self.ready, 'click': self.click_number})

if __name__ == "__main__":		# python tic_toc.py
	from PIL import Image
	im = Image.open('orig_images/Click-Click_small.png')  
	#im.show() 

	obj = ClickClick()
	x, y = obj.coordinates(im, 1)