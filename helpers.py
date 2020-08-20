__all__ = ['mouse_click', 'get_window', 'mouse_click']

# get mouse click position 
X, Y = None, None

def on_move(x, y):
    pass

def on_click(x, y, button, pressed):
    global X
    global Y
    X = x
    Y = y

    if not pressed:
        # On release button stop listener
        return False

def on_scroll(x, y, dx, dy):
    pass

def mouse_click():
	''' return cursor position after release any mouse button '''
	from pynput import mouse

	with mouse.Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
		listener.join()

	global X
	global Y
	return (X, Y)

# / get mouse click position 

def get_window(x1, y1, x2, y2):
	''' make screenshot, crop it with points P1(x1, y1) P2(x2, y2) and return '''

	# point (x1, y1) should be top-left
	# and point (x2, y2) should be bottom-right
	if x1 < x2 and y1 < y2:
		from pyautogui import screenshot
		
		# screenshot().crop([x1, y1, x2, y2]).save('11.png') # to test
		return screenshot().crop([x1, y1, x2, y2])
	else:
		return None

def get_contours(pil_image):
	''' recognize areas with digits at pil_image and returning ordered 
		list with (digit (coordinates of this digit)) '''
	from imutils import contours, resize, grab_contours
	from os import getpid, remove
	import numpy as np
	import pytesseract
	from PIL import Image
	import cv2
	
	opencvImage = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
	img = opencvImage
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	#cv2.imshow("Orig", gray)

	blurred = cv2.GaussianBlur(gray.copy(), (5, 5), 0)
	edged = cv2.Canny(blurred, 75, 200)
	#cv2.imshow("edged", edged)

	cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = grab_contours(cnts) # convert contours to OpenCV version 4 format
	numberCnts = []
	coords = []

	if len(cnts) > 0:
		cnts = sorted(cnts, key=cv2.contourArea, reverse=True)

		for c in cnts:
			(x, y, w, h) = cv2.boundingRect(c)
			ar = w / float(h)

			# keep only approximately square areas
			if ar >= 0.9 and ar <= 1.1:
				numberCnts.append(c)
				coords.append((x, y, w, h))
	else:
		#print('no countors find, returning')
		return 0

	# OCR all contours
	preprocess_method = 'thresh' # 'blur'
	if preprocess_method == 'thresh':
		gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
	elif preprocess_method == 'blur':
		gray = cv2.medianBlur(gray, 3)

	n = 0
	padding = 5
	numbers = []
	for c in coords:
		# walk through all contours and make ocr
		# tesseract library require write image to hdd
		# so, let's write image to file
		small = gray[coords[n][1]+padding:coords[n][1]+coords[n][3]-padding, coords[n][0]+padding:coords[n][0]+coords[n][2]-padding]
		filename = 'orig_images/'+ str(n) + str(getpid()) + '.png'
		#cv2.imshow("small", small)
		cv2.imwrite(filename, small)

		# try different setting --psm in heuristic order
		# we'll try different modes to make ocr successfully
		# successfully means that recognized text consist of digits or
		# empty string '' - when on the area no digits
		order = ['6', '7', '8', '9','10', '5', '4', '3']
		for psm in order:
			custom_oem_psm_config = r'--oem 1 --psm {} -c tessedit_char_whitelist=0123456789'.format(psm)
			text = pytesseract.image_to_string(Image.open(filename), lang='eng', config=custom_oem_psm_config)
			#print('psm:{}'.format(psm), 'text:{}:'.format(text))
			#cv2.waitKey(0)

			# check area for empty string ''
			if text == '':
				numbers.append(None)
				n += 1
				break

			# check area for allowed characters (digits)
			ocr_ok = True
			for i in text:
				if i in '0123456789':
					pass
				else:
					ocr_ok = False
					break

			# if all characters are allowed then break for psm loop
			# if not - try next psm setting
			if ocr_ok:
				numbers.append(int(text))
				n += 1
				break

		remove(filename)

	# filter out None items and 
	# contours bigger/smaller more then 20% then average size
	avg_width = 0
	avg_height = 0
	result = []
	for n, c in zip(numbers, coords): 
		if n != None: 
			result.append((n, c))
			avg_width += c[2]
			avg_height += c[3]
	avg_width = int(avg_width / len(result))
	avg_height = int(avg_height / len(result))

	result_filtered = []
	for i in result:
		if i[1][2] < int(1.2 * avg_width) \
				and i[1][2] > int(.8 * avg_width) \
				and i[1][3] < int(1.2 * avg_height) \
				and i[1][3] > int(.8 * avg_height):
			result_filtered.append(i)
	
	return sorted(result_filtered)

if __name__ == "__main__":		# python helpers.py
	#x1, y1 = mouse_click()
	#print('X1', x1)
	#print('Y1', y1)

	#get_window(0, 0, 100, 100)

	import cv2

	number_coord = get_contours(cv2.imread('orig_images/Click-Click_small.png'))
	print(number_coord)
	#pass