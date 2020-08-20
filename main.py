from kivy.config import Config

Config.set('graphics', 'height', '700');
Config.set('graphics', 'minimum_width', '600')
Config.set('graphics', 'minimum_height', '600')

#Config.window_icon = "img/logo_small.png"
Config.set('kivy','window_icon','img/logo_small.png')

from kivy.app import App
from kivy.clock import Clock
#from kivy.uix.label import Label
#from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
#from kivy.graphics.texture import Texture
from kivy.core.image import Image


from kivy.properties import ObjectProperty

#from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout

from kivy.logger import Logger

#import re
import cv2
#import json
#import pprint
from io import BytesIO
#from time import time, perf_counter
#from datetime import datetime
#from numpy import array
#from queue import Queue
from os.path import join
from os.path import exists
from os import remove
#from os import getpid
#from threading import Thread
from pynput.mouse import Button as pynput_Button
from pynput.mouse import Controller as pynput_Controller
from time import sleep

from multiprocessing import Process
from multiprocessing import Queue as  multiprocessing_Queue

# custom modules

from config_params import ConfigParams
config = ConfigParams()

import logging.config
from logger import logger_config

from helpers import get_window, mouse_click #, get_contours
from click_click import ClickClick

# change default folder name for logging and interval for keeping log files
default_log_file = logger_config['handlers']['file_rotate']['filename']
logger_config['handlers']['file_rotate']['filename'] = \
	join(config.data[0]['path_to_log_file'], 'gamer.log')
logger_config['handlers']['file_rotate']['interval'] = \
	config.data[0]['keep_log_file_days']

# after python imported logger_config itcreated log file with default name. 
# remove this file
if exists(default_log_file):
	remove(default_log_file)

# creating logger with custom settings
logging.config.dictConfig(logger_config)
logger = logging.getLogger('app_logger')
debugger = logging.getLogger('app_debugger')


class DropDownList(DropDown):
	''' part of GUI; for details watch UML diagram '''
	pass

class Chooser(BoxLayout):
	''' part of GUI; Layout for first line in main Layout'''

	link_to_chooser_button = ObjectProperty(None)
	link_to_setings = ObjectProperty(None)

	def __init__(self, **kwargs):
		super(Chooser, self).__init__(**kwargs)
	
class Setings(BoxLayout):
	''' part of GUI; Layout for widget's settings; is part of Chooser Layout'''

	link_to_slider_label = ObjectProperty(None)
	link_to_check_box = ObjectProperty(None)

	def __init__(self, **kwargs):
		super(Setings, self).__init__(**kwargs)

		self.slider_delay = 0

	def on_slider_delay(self, value):
		string = str('{:.1f}').format(value) + ' seconds'
		self.link_to_slider_label.text = string
		self.slider_delay = value
		#print('on_slider_delay value:', string)

	def on_checkbox(self, active):
		pass
		#print('on_checkbox value:', active)

class ChooseGame(BoxLayout):
	''' part of GUI; Layout for Dropdown list - Game chooser '''
	def __init__(self, **kwargs):
		super(ChooseGame, self).__init__(**kwargs)
		
		dropdown = DropDownList()
		self.mainbutton = Button(text='')
		self.add_widget(self.mainbutton)
		self.mainbutton.bind(on_release=dropdown.open)
		dropdown.bind(on_select=self.on_dropdown_select)

	def on_dropdown_select(self, instance, text):
		setattr(self.mainbutton, 'text', text)
		# first parent - BoxLayout, second parent - Chooser, third parent - Container
		# reach the Container
		self.parent.parent.parent.enable_disable_area(text)

class Area(BoxLayout):
	''' part of GUI;  Layout for area choose '''
	link_to_btn_p1 = ObjectProperty()
	link_to_btn_p2 = ObjectProperty()
	link_to_image = ObjectProperty()

	def __init__(self, **kwargs):
		super(Area, self).__init__(**kwargs)
		self.p1 = [None, None]
		self.p2 = [None, None]
		self.img = None

		self.ready = False
		
	def on_btn1_release(self, text):
		# top button responsible for taking mouse click position
		self.p1 = mouse_click()
		#print('on_btn1_release:', text, ' x:{}, y:{}'.format(self.p1[0], self.p1[1]))
		self.set_area()

	def on_btn2_release(self, text):
		# bottom button responsible for taking mouse click position
		self.p2 = mouse_click()
		#print('on_btn2_release:', text, ' x:{}, y:{}'.format(self.p2[0], self.p2[1]))
		self.set_area()

	def set_area(self):
		# working only if set two points: P1 (top-left), P2 (bottom-right)
		if self.p1[0] is not None and self.p1[1] is not None \
			and self.p2[0] is not None and self.p2[1] is not None:

			# taking printscreen
			self.img_PIL = get_window(self.p1[0], self.p1[1], self.p2[0], self.p2[1])
			#self.img.show('ttt')

			if self.img_PIL is None:
				#print('img_PIL is None')
				return
			
			# convert PIL image to kivy image
			#https://stackoverflow.com/questions/51806100/display-pil-image-on-kivy-canvas
			data = BytesIO()
			self.img_PIL.save(data, format='png')# save image as raw data
			data.seek(0)						# set pointer to start
			self.img_kivy = Image(BytesIO(data.read()), ext='png')
			# set this image to area
			self.link_to_image.texture = self.img_kivy.texture

			self.ready = True
			#print('readiness', self.ready)
			
	def set_text_P1(self, text):
		#print('set_text_P1', text)
		self.link_to_btn_p1.text = text

	def set_text_P2(self, text):
		#print('set_text_P2', text)
		self.link_to_btn_p2.text = text


class Container(BoxLayout):
	''' main GUI class. For details see UML diagram '''

	link_to_chooser = ObjectProperty()
	link_to_slider_delay = ObjectProperty()
	link_to_btn_start_stop = ObjectProperty()
	link_to_area1 = ObjectProperty()
	link_to_area2 = ObjectProperty()

	def __init__(self, **kwargs):
		super(Container, self).__init__(**kwargs)
		
		# set initial parameters from configuration file
		self.link_to_chooser.link_to_chooser_button.mainbutton.text = config.data[0]['game']
		self.link_to_chooser.link_to_setings.link_to_slider_label.text = str(config.data[0]['delay']) + ' seconds'
		self.link_to_chooser.link_to_setings.link_to_slider_delay.value = config.data[0]['delay']
		self.link_to_chooser.link_to_setings.link_to_check_box.active = config.data[0]['increase_latancy']

		self.game = config.data[0]['game']
		self.game_object = None
		self.ready_to_play = False				# readiness of main loop

		# queues to communicate with game process
		self.queue_input = None
		self.queue_output = None

		self.process_play_game = None
		#debugger.info('Enter in to the Container()')
		#debugger.error('Enter in to the Container()')
		#debugger.critical('Enter in to the Container()')

		# Click-Click, Twins require only one game area (bottomnes)
		# other games require two game areas
		# so, acording to selected game enable/disable appropriate areas
		self.enable_disable_area(self.game)

		# emulating ansynchronic work with event frequency
		self.event_frequency = 10.
		event = Clock.schedule_interval(self.callback_on_event, 1 / self.event_frequency)

		# simulating latency
		self.pass_number = int(float(config.data[0]['delay']) * self.event_frequency)
		self.pass_events = self.pass_number	# pass events to emulate latancy
		self.increase_latancy = 1

		# info from game process
		self.game_info = None
		self.game_readiness = False
		self.game_steps = 0

		# regular game continue 60 seconds
		# so, this event terminate a game
		# event starts on Start button
		self.event_to_finish_game = None

	def callback_on_event(self, arg):
		
		# check game_process readiness
		if not self.game_readiness:			
			if self.queue_output is not None and self.queue_output.qsize():	# check output queue
				self.game_info = self.queue_output.get()
				self.game_readiness = self.game_info['ready']
				self.game_steps = self.game_info['click']
				#print('switched to play, game_readiness:{}, click:{}'.\
				#	format(self.game_readiness, self.game_steps))

		# game switcher
		# these games using only second area to play
		if self.game == 'Click-Click' or self.game == 'Twins':
			if self.link_to_area2.ready:# enable/disable Start/Stop button
				self.link_to_btn_start_stop.disabled = False
			if self.link_to_btn_start_stop.text == 'Start':
				# in this case user did not started a game therefore just returning
				return

			# or user started a game

			if not self.ready_to_play:			# check main loop readiness
				#print('main loop not ready')
				return

			# emulating latency	
			if self.pass_events:
				self.pass_events -= 1
				return
			self.pass_events = int(self.link_to_chooser.link_to_setings.link_to_slider_delay.value * self.event_frequency)
			
			if self.link_to_chooser.link_to_setings.link_to_check_box.active:
				self.increase_latancy *= 1.05
			if self.increase_latancy > 2:
				self.pass_events += 1
				self.increase_latancy -= 1
			# /emulating latency

			# send info to game process to make a game steps
			if self.game_readiness and self.game_steps:
				self.queue_input.put({'click': 1, 'terminate': False})
				self.game_steps -= 1
				#print('sent info to game process')

			# handle situation when all steps are done
			if self.game_readiness and self.game_steps == 0:
				self.game_readiness = False


		else:		# using both areas
			if self.link_to_area1.ready and self.link_to_area2.ready:
				self.link_to_btn_start_stop.disabled = False
			if self.link_to_btn_start_stop.text == 'Start':
				return

			# or user started a game

			if not self.ready_to_play:			# check main loop readiness
				return

			# emulating latency	
			if self.pass_events:
				self.pass_events -= 1
				return
			self.pass_events = int(self.link_to_chooser.link_to_setings.link_to_slider_delay.value * self.event_frequency)
			
			if self.link_to_chooser.link_to_setings.link_to_check_box.active:
				self.increase_latancy *= 1.05
			if self.increase_latancy > 2:
				self.pass_events += 1
				self.increase_latancy -= 1
			# /emulating latency

	def callback_on_game_terminating(self, arg):
		#print('callback_on_game_terminating', arg)
		# check if app playing, because user maybe stopped the game
		if self.link_to_btn_start_stop.text == 'Stop':
			self.on_start_stop(self.link_to_btn_start_stop.text)
		

	def on_start_stop(self, text):

		# switch name and purpose of the button
		if self.link_to_btn_start_stop.text == 'Start':
			self.link_to_btn_start_stop.text = 'Stop'
			sleep(.3)					# need some time to change a text

			# disable buttons
			self.link_to_chooser.link_to_chooser_button.disabled = True
			
			if self.game == 'Twins' or self.game == 'Click-Click':
				self.link_to_area2.link_to_btn_p1.disabled = True
				self.link_to_area2.link_to_btn_p2.disabled = True
			else:
				self.link_to_area1.link_to_btn_p1.disabled = True
				self.link_to_area1.link_to_btn_p2.disabled = True
				self.link_to_area2.link_to_btn_p1.disabled = True
				self.link_to_area2.link_to_btn_p2.disabled = True
			# /disable buttons

			# queues to communicate with game process
			self.queue_input = multiprocessing_Queue()
			self.queue_output = multiprocessing_Queue()

			# create Game object
			if self.game == 'Click-Click':
				#print('starting Click-Click game')

				self.game_object = ClickClick(self.link_to_area2.p1, self.link_to_area2.p2)

				self.process_play_game = Process(target=self.game_object.play_game, \
						args=(self.queue_input, self.queue_output))
				self.process_play_game.start()


				self.ready_to_play = True

				self.event_to_finish_game = Clock.schedule_once(self.callback_on_game_terminating, 55)

				return

			if self.game == 'Twins':
				print('starting Twins game')
				#self.game_object = Twins()

				return
		else:							 # stop game
			self.ready_to_play = False
			self.link_to_btn_start_stop.text = 'Start'

			self.event_to_finish_game = None

			self.game_info = None
			self.game_readiness = False
			self.game_steps = 0

			# enable buttons
			self.link_to_chooser.link_to_chooser_button.disabled = False

			if self.game == 'Twins' or self.game == 'Click-Click':
				self.link_to_area2.link_to_btn_p1.disabled = False
				self.link_to_area2.link_to_btn_p2.disabled = False
			else:
				self.link_to_area1.link_to_btn_p1.disabled = False
				self.link_to_area1.link_to_btn_p2.disabled = False
				self.link_to_area2.link_to_btn_p1.disabled = False
				self.link_to_area2.link_to_btn_p2.disabled = False
			# /enable buttons

			# in case process is alive it cleans itself
			if self.process_play_game.is_alive():
				self.queue_input.put({'terminate': True})
			# othervise main process cleans queues
			else:
				self.clean_queues([self.queue_input, self.queue_output])
		
			self.queue_input.close()
			self.queue_output.close()
			self.queue_input.join_thread()
			self.queue_output.join_thread()

			self.process_play_game.join() # to join dead process is safe

			self.queue_input = None
			self.queue_output = None
			self.process_play_game = None

			self.game_object = None

	def clean_queues(self, queues):
		for queue in queues:
			while queue.qsize():
				_ = queue.get()
		

	def enable_disable_area(self, text):
		''' according to chosen game (text) enable or disable buttons at area1 area2 '''
		#print('Container: enable_disable_area:', text)
		self.game = text
		if self.game in ['Click-Click', 'Twins']:
			print('enable_disable_area: Click-Click')
			self.link_to_area1.set_text_P1('')
			self.link_to_area1.set_text_P2('')
			self.link_to_area1.link_to_btn_p1.disabled = True
			self.link_to_area1.link_to_btn_p2.disabled = True
			self.link_to_area2.set_text_P1('Set area\'s P1 at screen')
			self.link_to_area2.set_text_P2('Set area\'s P2 at screen')
		elif self.game == 'Find number':
			print('enable_disable_area: Find number')
			self.link_to_area1.set_text_P1('Set terget\'s P1 at screen')
			self.link_to_area1.set_text_P2('Set terget\'s P2 at screen')
			self.link_to_area1.link_to_btn_p1.disabled = False
			self.link_to_area1.link_to_btn_p2.disabled = False
			self.link_to_area2.set_text_P1('Set area\'s P1 at screen')
			self.link_to_area2.set_text_P2('Set area\'s P2 at screen')
		elif self.game == 'Find object':
			print('enable_disable_area: Find object')
			self.link_to_area1.set_text_P1('Set terget\'s P1 at screen')
			self.link_to_area1.set_text_P2('Set terget\'s P2 at screen')
			self.link_to_area1.link_to_btn_p1.disabled = False
			self.link_to_area1.link_to_btn_p2.disabled = False
			self.link_to_area2.set_text_P1('Set area\'s P1 at screen')
			self.link_to_area2.set_text_P2('Set area\'s P2 at screen')

class GamerApp(App):
	def build(self):
		logger.info('Enter in to the build()')
		self.icon = 'img/logo_small.png'
		
		self.container = Container()
		
		logger.info('Return from build()')
		return self.container

	def on_stop(self):
		config.data[0]['game'] = self.container.link_to_chooser.link_to_chooser_button.mainbutton.text
		config.data[0]['delay'] = float(self.container.link_to_chooser.link_to_setings.link_to_slider_label.text[0:3])
		config.data[0]['increase_latancy'] = int(self.container.link_to_chooser.link_to_setings.link_to_check_box.active)
		#print('on_stop')
		return True

			

if __name__ == "__main__":
	logger.info('\t---\tSTART APPLICATION\t---')	# custom logger
	Logger.info('Gamer\t: START APPLICATION')		# kivy logger
	'''try:
		GamerApp().run()
	except:
			logger.info('could not run Gamer application')'''
	GamerApp().run()

	config.config_save(file='config.json')

	logger.info('\t---\tEXIT APPLICATION\t---')