#!/usr/bin/env python3

# Dependencies

# 	eSpeak:
# 		http://espeak.sourceforge.net/download.html
# 	Additional Data for Russian:
# 		http://espeak.sourceforge.net/data/

# -----------------------------------------------------------------------------

import os
import re
import subprocess

import argparse

pth = os.path.dirname( os.path.abspath(__file__) )

parser = argparse.ArgumentParser()

parser.add_argument('-i', '--input', default=pth + "/../data/corpus_orig", 
	help="Input dir")
parser.add_argument('-o', '--output', default=pth + "/../data/corpus_mark", 
	help="Output dir")

args = parser.parse_args()

# -----------------------------------------------------------------------------

symb_re = re.compile("[^\s\-а-яА-ЯёЁ.,!?;:]")
word_re = re.compile("[^\s\-а-яА-ЯёЁ]")
name_re = re.compile("(.*)\.txt")
unwanted_re = re.compile("(?<=[^а-яА-ЯёЁ])-")

if not os.path.exists(args.output):
	os.makedirs(args.output)

step = 800

for d in os.listdir(args.input):

	print(d)

	path_input = args.input + "/" + d
	path_output = args.output + "/" + d

	if not os.path.exists(path_output):
		os.makedirs(path_output)

	for f in os.listdir(path_input):
		print(f)
		
		with open(path_input + "/" + f, "r") as fin:
			name = name_re.match(f).group(1)
			data = re.split("[\n\.]+", fin.read())

			item = 0
			chunk = 0

			while chunk < len(data):
				limit = chunk + step if chunk + 2 * step < len(data) \
					else len(data)

				text = []
				trans = []

				for i in range(chunk, limit):
					sent = re.sub(' +', ' ', unwanted_re.sub(' ', 
						symb_re.sub(' ', data[i])))
					if sent != '':
						raw_text = re.sub('-', '', word_re.sub(' ', sent)).lower()

						bash_cmd = 'espeak -v ru -q --ipa '
						lst = bash_cmd.split()
						lst.append('\"' + raw_text + '\"')

						try:
							process = subprocess.Popen(lst, 
								stdout=subprocess.PIPE)
							output = process.communicate()[0]
							
							text.append(' '.join(sent.split()))
							trans.append(' '.join(
								output.decode('utf-8').split()))
						except Exception:
							pass # ~(o_o)~

				name_pref = path_output + "/" + name + " " + str(item)
				
				with open(name_pref, "tw") as fout:
					fout.write("\n".join(text) + "\n")

				with open(name_pref + " trans", "tw") as fout:
					fout.write("\n".join(trans) + "\n")

				chunk = limit
				item += 1

print("done.")