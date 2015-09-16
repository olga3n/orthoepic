#!/usr/bin/env python3

import os
import re
import random

DATA_PATH = os.path.dirname( os.path.abspath(__file__) ) + "/../data/corpus_mark"

# -----------------------------------------------------------------------------

rhyme_cross = 1

patterns = {
	
	'ямб 3-х ст.': [['010101', '010101', '010101', '010101'], rhyme_cross],
	'ямб 3.5': [['0101010', '0101010', '0101010', '0101010'], rhyme_cross],
	'ямб 4-х ст.': [['01010101', '01010101', '01010101', '01010101'], rhyme_cross],
	'ямб 4.5': [['010101010', '010101010', '010101010', '010101010'], rhyme_cross],
	'ямб 5-и ст.': [['0101010101', '0101010101', '0101010101', '0101010101'], rhyme_cross],
	'ямб 5.5': [['01010101010', '01010101010', '01010101010', '01010101010'], rhyme_cross],

	#'считалка': [['1010', '1010', '1010', '1010'], rhyme_cross],
	
	'хорей 3-х ст.': [['101010', '101010', '101010', '101010'], rhyme_cross],
	'хорей 3.5': [['1010101', '1010101', '1010101', '1010101'], rhyme_cross],
	'хорей 4-х ст.': [['10101010', '10101010', '10101010', '10101010'], rhyme_cross],
	'хорей 4.5': [['101010101', '101010101', '101010101', '101010101'], rhyme_cross],
	'хорей 5-и ст.': [['1010101010', '1010101010', '1010101010', '1010101010'], rhyme_cross],
	'хорей 5.5': [['10101010101', '10101010101', '10101010101', '10101010101'], rhyme_cross],

	'дактиль 3-x ст.': [['100100100', '100100100', '100100100', '100100100'], rhyme_cross],
	'амфибрахий 3-х ст.': [['010010010', '010010010', '010010010', '010010010'], rhyme_cross],
	'анапест 3-х ст.': [['001001001', '001001001', '001001001', '001001001'], rhyme_cross],

	'дактиль 2-x ст.': [['100100', '100100', '100100', '100100'], rhyme_cross],
	'амфибрахий 2-х ст.': [['010010', '010010', '010010', '010010'], rhyme_cross],
	'анапест 2-х ст.': [['001001', '001001', '001001', '001001'], rhyme_cross],

	'пародия Маяковский': [[
			 '1001001001',
			  '0010010010',
			'01001001001',
			'01001010' 
		], rhyme_cross
	],
	'пародия Есенин 1': [[
			'010001010100',
			'0101010101',
			'010001010100',
			'0101010101'
		], rhyme_cross
	],
	'пародия Есенин 2': [[
			'01000101010',
			'010101010101',
			'01010101010',
			'0100010101'
		], rhyme_cross
	],
	'пародия Блок': [[
			'0010010010',
			'001001001',
			'0010010010',
			'001001001'
		], rhyme_cross
	],
	'частушка': [[
			'00100010',
			'0010101',
			'00100010',
			'0010101'
		], rhyme_cross
	],
	'пародия Лермонтов': [[
			'010101010',
			'01010101',
			'010101010',
			'01010101'
		], rhyme_cross
	],
	'марш': [[
			'00100100010010',
			'001001001001',
			'00100100010010',
			'001001001001'
		], rhyme_cross
	]
}

templates = {}

Nmax = 0

for k in patterns.keys():
	for i in range( 0, len(patterns[k][0]) ):

		l = len(patterns[k][0][i])

		if not l in templates.keys():
			templates[l] = []

		if not patterns[k][0][i] in templates[l]:
			templates[l].append(patterns[k][0][i])
				
		if l > Nmax:
			Nmax = l

# -----------------------------------------------------------------------------

name_re = re.compile("(.*) \d+( trans)?")

class gen_poem():

	def __init__(self, 
			genre=random.uniform(0, 1), title=random.uniform(0, 1),
			part=random.uniform(0, 1), form=random.uniform(0, 1)):

		collection = {}

		for k in patterns.keys():
			for i in range( 0, len(patterns[k][0]) ):
				collection[patterns[k][0][i]] = {}

		# ---------------------------------------------------

		if genre > 1 or genre < 0: genre = random.uniform(0, 1)
		if title > 1 or title < 0: title = random.uniform(0, 1)
		if part > 1 or part < 0: part = random.uniform(0, 1)
		if (form > 1 or form < 0) and form != -1: form = random.uniform(0, 1)
		
		genre_n = len(os.listdir(DATA_PATH)) - 1
		genre_name = os.listdir(DATA_PATH)[int(genre_n * genre)]

		files = os.listdir(DATA_PATH + "/" + genre_name)
		titles = sorted(list(set([name_re.match(x).group(1) for x in files])))

		title_n = len(titles) - 1
		title_name = titles[int(title_n * title)]

		part_n = 0
		for f in files:
			if title_name in f: part_n += 1
		part_n = part_n / 2 - 1
		
		form_n = len(patterns.keys()) - 1

		filename = DATA_PATH + "/" + genre_name + "/" + title_name + " " + str(
			int(part_n * part))

		print("%s" % filename)

		data_text = ''
		data_trans = ''

		with open(filename, "r") as fin:
			data_sents = re.split("[\n]+", fin.read())

		with open(filename + " trans", "r") as fin:
			data_trans = re.split("[\n]+", fin.read())
			
		if data_sents[0] == '':
			data_sents.pop(0)

		if data_trans[0] == '':
			data_trans.pop(0)
		
		self.collect(collection, data_sents, data_trans)
		self.p = self.pair(collection)
		
		if form != -1: # ~(o_o)~
			self.poems = [self.generate(self.p, int(form_n * form))]
		else:
			self.poems = []
			for i in range(0, form_n):
				poems = self.generate(self.p, i)
				if len(poems) > 1:
					self.poems.append(poems)

	def collect(self, collection, data_sents, data_trans):

		# IPA for Russian vowels
		ipa_vowel_re = re.compile("ˈ?j?[ɑʌiaeuoyɪɛɵ]") 
		tail_re = re.compile(
				".*(ˈj?[ɑʌiaeuoyɪɛɵ].*ˈ?j?[ɑʌiaeuoyɪɛɵ].*|" + 
				"(?!ˈ)j?[ɑʌiaeuoyɪɛɵ][^ɑʌiaeuoyɪɛɵ]*ˈj?[ɑʌiaeuoyɪɛɵ][^ɑʌiaeuoyɪɛɵ]*)"
			) # ~(o_o)~

		ru_let_re = re.compile('[а-яА-ЯёЁ]')
		ru_vowel_re = re.compile('[аеёиоуыэюяАЕЁИОУЫЭЮЯ]')

		sents_i = 0
		sents_trans_i = 0

		while sents_i < len(data_sents):
	
			parts = data_sents[sents_i].split()
			trans = data_trans[sents_trans_i].split()

			parts_i = 0
			trans_i = 0

			let_flag = 0 # ~(o_o)~

			while parts_i < len(parts):
				
				phrase = ''
				phrase_tr = ''

				ni = 0
				parts_j = parts_i
				trans_j = trans_i

				first_sign_flag = 0 # ~(o_o)~
				
				while ni < Nmax and parts_j < len(parts):

					word = parts[parts_j]

					let = len(ru_let_re.findall(word))
					if let < 1: 
						if phrase == '':
							first_sign_flag += 1
						parts_j += 1
						continue
					elif let_flag == 0:
						let_flag = 1

					if phrase == '' and ( word.lower() == "же" or \
						word.lower() == "ли" or word.lower() == "бы"):

						trans_j += 1
						parts_j += 1
						continue

					phrase += word + ' '

					vowels = len(ru_vowel_re.findall(word))
					if vowels < 1: 
						trans_j += 1
						parts_j += 1
						continue

					phrase_tr += trans[trans_j] + ' '

					ni += len(ipa_vowel_re.findall(trans[trans_j]))

					if let > 2 and vowels > 1 and ni in templates.keys():

						m_tail = tail_re.match(phrase_tr)
						if not m_tail is None:
							tail = m_tail.group(1)

							code_str = ''.join( 
								map( # ~(o_o)~
									lambda x: '1' if 'ˈ' in x else '0', 
									ipa_vowel_re.findall(phrase_tr)
								))

							code = int(code_str, 2)

							for i in range(0, len(templates[ni])):
									
								code_i_str = templates[ni][i]
								code_i = int(code_i_str, 2)

								if code & code_i == code_i:
									if not tail in collection[code_i_str].keys():
										collection[code_i_str][tail] = {}
									if not word in collection[code_i_str][tail].keys():
										collection[code_i_str][tail][word] = []
									collection[code_i_str][tail][word].append(
										phrase[0].upper() + phrase[1:])

					parts_j += 1
					trans_j += 1

				parts_i += 1
				trans_i += 1

				if first_sign_flag != 0:
					parts_i += first_sign_flag

			if len(parts) == 0 or let_flag != 0:
				sents_trans_i += 1
			sents_i += 1

	def pair(self, collection):
		
		suff_re = re.compile(".*[^\-а-яА-Я]([\-а-яА-Я]+)[^\-а-яА-Я]*")

		pair_first = {}
		pair_second = {}

		for k in patterns.keys():

			pair_first[k] = []
			pair_second[k] = []

			if patterns[k][1] == rhyme_cross: # ~(o_o)~
				code_0 = patterns[k][0][0]
				code_1 = patterns[k][0][1]
				code_2 = patterns[k][0][2]
				code_3 = patterns[k][0][3]
			
			for tail in collection[code_0].keys():
				if tail in collection[code_2].keys():
					for last_0 in collection[code_0][tail].keys():
						one = collection[code_0][tail][last_0]

						for last_2 in collection[code_2][tail].keys():
							if last_0 != last_2 and not '-' in last_0 and \
								not '-' in last_2:
								three = collection[code_2][tail][last_2]

								l_0 = re.sub(r'[^а-яА-Я]', '', last_0).lower()
								l_2 = re.sub(r'[^а-яА-Я]', '', last_2).lower()

								# кеды-полукеды
								if not l_0 in l_2 and not l_2 in l_0:
									pair_first[k].append([tail, one, three])

			if code_0 == code_1 and code_1 == code_2 and code_2 == code_3:
				pair_second[k] = pair_first[k][0:-1:2]
				pair_first[k] = pair_first[k][1:-1:2]
			else: 
				for tail in collection[code_1].keys():
					if tail in collection[code_3].keys():
						for last_1 in collection[code_1][tail].keys():
							two = collection[code_1][tail][last_1]

							for last_3 in collection[code_3][tail].keys():
								if last_1 != last_3 and not '-' in last_1 and \
									not '-' in last_3:
									four = collection[code_3][tail][last_3]

									l_1 = re.sub(r'[^а-яА-Я]', '', last_1).lower()
									l_3 = re.sub(r'[^а-яА-Я]', '', last_3).lower()

									# кеды-полукеды
									if not l_1 in l_3 and not l_3 in l_1:
										pair_second[k].append([tail, two, four])

			random.shuffle(pair_first[k])
			random.shuffle(pair_second[k])

		return [pair_first, pair_second]

	def generate(self, pair, form):
		
		pair_first = pair[0]
		pair_second = pair[1]

		last_sign_re = re.compile("(.*[а-яА-ЯёЁ])[^а-яА-ЯёЁ]*$")

		k = sorted(list(patterns.keys()))[form]

		poems = [k]
			
		m = min( len(pair_first[k]), len(pair_second[k]) )

		for i in range(0, m):

			if pair_first[k][i][0] != pair_second[k][i][0]:

				random.shuffle(pair_first[k][i][1])
				random.shuffle(pair_first[k][i][2])
				random.shuffle(pair_second[k][i][1])
				random.shuffle(pair_second[k][i][2])

				if patterns[k][1] == rhyme_cross: # ~(o_o)~
					poem = "\n".join([
							pair_first[k][i][1][0], 
							pair_second[k][i][1][0],
							pair_first[k][i][2][0],
							last_sign_re.match(pair_second[k][i][2][0]).group(1) + "."
						])
					poems.append(poem)

		return poems

# -----------------------------------------------------------------------------

if __name__ == '__main__':

	import argparse

	parser = argparse.ArgumentParser()

	parser.add_argument('-g', '--genre', type=float, default=random.uniform(0, 1))
	parser.add_argument('-t', '--title', type=float, default=random.uniform(0, 1))
	parser.add_argument('-p', '--part', type=float, default=random.uniform(0, 1))
	parser.add_argument('-f', '--form', type=float, default=-1)

	args = parser.parse_args()

	g = gen_poem(args.genre, args.title, args.part, args.form)

	for i in range (0, len(g.poems)):
		for j in range (1, len(g.poems[i])):
			print ("<%s>\n%s\n\n" % (g.poems[i][0], g.poems[i][j]))
