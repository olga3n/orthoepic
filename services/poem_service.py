#!/usr/bin/env python3

import sys, os, re
import socket, threading
import struct, copy
import random

pth = os.path.dirname( os.path.abspath(__file__) )

sys.path.append(pth + '/../generator')

import generator

SERVER_PORT = 12345
DATA_PATH = pth + '/../data/corpus_mark'

options = {}
name_re = re.compile("(.*) \d+( trans)?")

t_g = random.uniform(0, 1)
t_t = random.uniform(0, 1)
t_p = random.uniform(0, 1)
t_f = random.uniform(0, 1)

gen_options = {}
g = generator.gen_poem(t_g, t_t, t_p, -1)
poems = g.poems

def gen_next():

	global status
	global head
	global poem
	global options
	global gen_options
	global poems
	global g

	print("OPTIONS:", options)
	print("GEN_OPTIONS:", gen_options)

	if options["genre"][1] == gen_options["genre"][1] and \
		options["title"][1] == gen_options["title"][1] and \
		options["part"][1] == gen_options["part"][1]:

		if options["form"][1] == gen_options["form"][1] and \
			len(poems) > options["form"][1] and \
			len(poems[ options["form"][1] ]) > 1:
			
			### next with the same options

			options["form"][2] = len(poems) - 1
			options["form"][0] = options["form"][1] / (options["form"][2] + 1)
			options["form"][3] = poems[ options["form"][1] ][0]

			poem = poems[ options["form"][1] ].pop(1) + "\n"

			if len(poems[ options["form"][1] ]) == 1:
			 	poems.pop(options["form"][1])
			 	options["form"][2] = len(poems) - 1
			 	options["form"][1] = int(options["form"][0] * options["form"][2])
			 	if len(poems) > options["form"][1]:
			 		options["form"][3] = poems[ options["form"][1] ][0]

		else:

			### not exists with the same options

			if options["part"][1] < options["part"][2]:
				options["part"][1] += 1
			else:
				options["part"][1] = 0

			print("GEN with another part")

			gen_fail = 1

			while gen_fail == 1:

				gen_fail = 0

				g = generator.gen_poem (
					options["genre"][0], options["title"][0], options["part"][0], -1)
				poems = g.poems

				name = options["form"][3]
				
				i = -1
				for item in range(0, len(poems)):
					if name == poems[item][0]:
						i = item
						continue
				
				n = len(poems) - 1

				if i == -1 or len(poems[i]) < 2:
					
					if len(poems[i]) < 2: poems.pop(i)
					n = len(poems) - 1
					i = int(n * options["form"][0])

					if (len(poems) > i):
						name = poems[i][0]
					else:
						gen_fail = 1
						options["part"] = [0, 0, 0, 0]

			options["form"][1:4] = [i, n, name]
			
			poem = poems[ options["form"][1] ].pop(1) + "\n"

	else:

		print("GEN with new options")

		gen_fail = 1

		while gen_fail == 1:
			
			gen_fail = 0

			g = generator.gen_poem (
				options["genre"][0], options["title"][0], options["part"][0], -1)
			
			poems = g.poems

			name = options["form"][3]
			
			i = -1
			for item in range(0, len(poems)):
				if name == poems[item][0]:
					i = item
					continue
			
			n = len(poems) - 1

			if i == -1 or len(poems[i]) < 2:
				
				if len(poems[i]) < 2: poems.pop(i)
				
				n = len(poems) - 1
				i = int(n * options["form"][0])

				if (len(poems) > i):
					name = poems[i][0]
				else:
					gen_fail = 1
					options["part"] = [0, 0, 0, 0]

		options["form"][1:4] = [i, n, name]

		print("options:", options)

		poem = poems[i].pop(1) + "\n"

		if len(poems[i]) == 1:
			poems.pop(i)
			options["form"][2] = len(poems) - 1

	head = "%s\n%s\n%s\n%s\n" % (
		options["genre"][3], options["title"][3], options["part"][3], options["form"][3])

	print(head) ####
	print(poem) ####

	gen_options = copy.deepcopy(options)

	status = 1

def get_name(t, value):

	global options
	global gen_options
	global poems
	global orig
	global mark

	if t == 1:
		n = len(os.listdir(DATA_PATH)) - 1
		i = int(n * value)
		name = os.listdir(DATA_PATH)[i]
		
		options["genre"] = [value, i, n, name]
		r_name = name

	if t <= 2:
		
		if t == 2: options["title"] = [value]

		files = os.listdir(DATA_PATH + "/" + options["genre"][3])
		titles = sorted(list(set([name_re.match(f).group(1) for f in files])))

		n = len(titles) - 1	
		i = int(n * options["title"][0])
		name = titles[i]

		options["title"][1:4] = [i, n, name]

		if t == 2: r_name = name

	if t <= 3:

		if t == 3: options["part"][0] = value
		
		n = 0
		for f in os.listdir(DATA_PATH + "/" + options["genre"][3]):
			if options["title"][3] in f: n += 1
		n = int(n / 2) - 1

		i = int(n * options["part"][0])
		name = str(i)

		options["part"][1:4] = [i, n, name]
		
		if t == 3: r_name = name

	if t <= 4:

		if t == 4: options["form"][0] = value

		n = len(poems) - 1
		i = int(n * options["form"][0])
		name = poems[i][0]

		options["form"][1:4] = [i, n, name]

		if t == 4: r_name = name

	return r_name

### init ###

genres = os.listdir(DATA_PATH)

n = len(genres) - 1
i = int(n * t_g)
name = genres[i]
options["genre"] = [t_g, i, n, name]

files = os.listdir(DATA_PATH + "/" + options["genre"][3])
titles = sorted(list(set([name_re.match(f).group(1) for f in files])))

n = len(titles) - 1
i = int(n * t_t)
name = titles[i]
options["title"] = [t_t, i, n, name]

n = 0
for f in files: 
	if options["title"][3] in f: n += 1
n = int(n / 2) - 1

i = int(n * t_p)
name = str(i)
options["part"] = [t_p, i, n, name]

n = len(poems) - 1
i = int(n * t_f)
name = poems[i][0]
options["form"] = [t_f, i, n, name]

gen_options = copy.deepcopy(options)

print(options)
print(gen_options)

head = "%s\n%s\n%s\n%s\n" % (
		options["genre"][3], options["title"][3], 
		options["part"][3], options["form"][3]
	)
poem = poems[i].pop(1) + "\n"

if len(poems[i]) == 1:
	poems.pop(i)
	options["form"][2] = len(poems) - 1

status = 1

class Server(threading.Thread):

	def __init__(self):

		threading.Thread.__init__(self)

		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server.bind(('localhost', SERVER_PORT))
		self.server.listen(5)

	def run_thread(self, conn, addr):

		global status
		global poem
		global head

		first = conn.recv(2).decode()

		if '1' in first: ### client: of
			conn.recv(1) # \0

			while True:
				try:
					message = conn.recv(2).decode()
					conn.recv(1) # \0

					if '1' in message: # poem request

						if status == 0:
							text = 'none\n'
							conn.sendall(text.encode())
						else:
							with lock:
								conn.sendall((head + poem).encode())
								status = 0

					elif '2' in message: # option request

						t = conn.recv(3)
						t = t[0] # byte
						
						value = conn.recv(7)
						value = value[0:4] # float

						with lock:
							name = get_name( int(t), struct.unpack('f', value)[0] ) + "\n"
							conn.send(name.encode())

				except Exception:
					pass # ~(o_o)~

			conn.close()
					
		elif '2' in first: ### client: tts

			with lock:
				gen_next()
				conn.sendall(poem.encode())
			
			conn.recv(5) # done\n
			conn.close()	

		else:
			conn.close()

	def run(self):

		print("listen...")

		print(head)
		print(poem)

		while True:
			conn, addr = self.server.accept()
			threading.Thread( target=self.run_thread, args=(conn, addr) ).start()

try:
	lock = threading.Lock()
	s = Server()
	s.run()

except KeyboardInterrupt:
	sys.exit()
	