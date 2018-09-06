import argparse
from enum import Enum
import io
import os
import time
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw


class FeatureType(Enum):
	PAGE = 1
	BLOCK = 2
	PARA = 3
	WORD = 4
	SYMBOL = 5


def draw_boxes(image, bounds, color):
	draw = ImageDraw.Draw(image)

	for bound in bounds:
		draw.polygon([
			bound.vertices[0].x, bound.vertices[0].y,
			bound.vertices[1].x, bound.vertices[1].y,
			bound.vertices[2].x, bound.vertices[2].y,
			bound.vertices[3].x, bound.vertices[3].y], None, color)
	return image


def get_document_bounds(image_file, feature):
	client = vision.ImageAnnotatorClient()

	bounds = []

	with io.open(image_file, 'rb') as image_file:
		content = image_file.read()

	image = types.Image(content=content)

	response = client.document_text_detection(image=image)
	document = response.full_text_annotation

	for page in document.pages:
		for block in page.blocks:
			for paragraph in block.paragraphs:
				for word in paragraph.words:
					for symbol in word.symbols:
						if (feature == FeatureType.SYMBOL):
							bounds.append(symbol.bounding_box)

					if (feature == FeatureType.WORD):
						bounds.append(word.bounding_box)

				if (feature == FeatureType.PARA):
					bounds.append(paragraph.bounding_box)

			if (feature == FeatureType.BLOCK):
				bounds.append(block.bounding_box)

		if (feature == FeatureType.PAGE):
			bounds.append(block.bounding_box)

	# The list `bounds` contains the coordinates of the bounding boxes.

	return bounds


def render_doc_text(filein, fileout):
	image = Image.open(filein)

	client = vision.ImageAnnotatorClient()

	with io.open(filein, 'rb') as filein:
		content = filein.read()

	image2 = types.Image(content=content)

	response = client.document_text_detection(image=image2)
	document = response.full_text_annotation
	answers = ["", "", "", ""]
	qFound = -1
	for page in response.full_text_annotation.pages:
		for block in page.blocks:
			block_words = []
			for paragraph in block.paragraphs:
				block_words.extend(paragraph.words)

			block_text = ''
			block_symbols = []
			previousword = ""
			quotefound = 0
			for word in block_words:
				block_symbols.extend(word.symbols)
				word_text = ''
				for symbol in word.symbols:
					word_text = word_text + symbol.text

				word_text = word_text.replace('“', '"')
				if '"' in previousword and quotefound is not 1:
					block_text += word_text
					quotefound = 1
				else:
					block_text += ' ' + word_text

				previousword = word_text

			if qFound is not -1 and qFound is not 4:
				block_text = block_text.replace(' .', '.')
				block_text = block_text.replace(' ,', ',')
				block_text = block_text.replace(' :', ':')
				block_text = block_text.replace(" ' ", " ")
				answers[qFound] = block_text
				qFound = qFound + 1
			if '?' in block_text:
				block_text = block_text.replace(' ?', '?')
				block_text = block_text.replace(" ' ", "'")
				question = block_text
				qFound = 0

	print('Detected from image...')
	question = question.replace('“', '"')
	question = question.replace(' " ', '" ')
	question = question.replace('  ', ' ')
	question = question.replace(' , ', ', ')
	print(question)
	print(answers[0])
	print(answers[1])
	print(answers[2])
	question = question.replace('"', 'passquotemark')
	os.system("scraper.py" + " \"" + question.lstrip() + "\" \"" + answers[0].lstrip() + "\" \"" + answers[
		1].lstrip() + "\" \"" + answers[2].lstrip())


if __name__ == '__main__':
	start_time = time.time()
	parser = argparse.ArgumentParser()
	parser.add_argument('detect_file', help='The image for text detection.')
	parser.add_argument('-out_file', help='Optional output file', default=0)
	args = parser.parse_args()

	parser = argparse.ArgumentParser()
	render_doc_text(args.detect_file, args.out_file)

	elapsed_time = time.time() - start_time
	print("Completed in %.3f seconds" % elapsed_time)
