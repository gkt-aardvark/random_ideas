#!/usr/bin/env python3
#you'll need tesseract installed on your system

import os
import string
from pytesseract import image_to_string
from PIL import Image

#set this to wherever you have all your images
base_path = './Images/'

word_list = []

#just go through all images in the base_path, pass if there's an error
#this takes around 20 minutes for 10k images
#for each image, if it has text, then add to list
for file in os.listdir(base_path):
	try:
		data = image_to_string(Image.open(base_path + file))
		if not (data == ''):
			text = data.replace('\n', ' ').replace('"', '').split(' ')
			word_list.extend(text)
	except:
		pass

#not necessarily needed, but strip off some punctuation and white space		
word_list = [x.translate(str.maketrans('', '', string.punctuation)).strip() for x in word_list]

#dedup the word list and sort it
word_list = list(set(word_list))
word_list.sort()

#output to a text file, one word per line
with open('words.txt', 'w') as f:
	for word in word_list:
		f.write(f'{word}\n')
