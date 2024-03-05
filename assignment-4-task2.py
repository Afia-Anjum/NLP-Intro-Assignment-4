'''
Assignment 4: Task 2
'''

import spacy, json, random, re, glob

'''
Opens the json file with the passed in name, preprocesses the data and returns a list of sentences, each
item being a dictionary that contains the preprocessed sentence and its entity-surrogate mappings.
'''
def open_and_init_json(filepath):
	with open(filepath) as json_file:
		data = json.load(json_file)
		sentences = []
		i = 0
		for d in data:
			sent_data = {}
			sentence = d['sentence']
			sub = d['pair']['subject']['mid']
			obj = d['pair']['object']['mid']

			regex = re.findall(r"\[.*?\]]", sentence)

			s = sentence
			mappings = {} # dictionary mapping entities and their surrogates
			n = 1
			for group in regex:
				group_list = group.split()
				surr = group_list[len(group_list) - 2]

				if surr == sub:
					s = s.replace(group, 'SUBJECT')
					mappings['SUBJECT'] = group
				elif surr == obj:
					s = s.replace(group, 'OBJECT')
					mappings['OBJECT'] = group
				else:
					entity = 'ENTITY' + str(n)
					s = s.replace(group, entity)
					mappings[entity] = group
					n += 1

			sent_data['sentence'] = s
			sent_data['mappings'] = mappings

			sentences.append(sent_data)

	return sentences

'''
Function inspired from: https://towardsdatascience.com/find-lowest-common-ancestor-subtree-and-shortest-dependency-path-with-spacy-only-32da4d107d7a
Takes in spacy's document object for a sentence and the indices of the subject and object, and
returns the lowest common ancestor of a subject and an object, and paths from subject to the root, and
the object to the root.
'''
def lowest_common_ancestor(doc, subj_i, obj_i):
	lca_data = {}

	# Path from SUBJECT to root
	current_node = doc[subj_i]
	subj_path = [current_node]
	while current_node != current_node.head:
		current_node = current_node.head
		subj_path.append(current_node)

	# Path from root to OBJECT
	current_node = doc[obj_i]
	obj_path = [current_node]
	while current_node != current_node.head:
		current_node = current_node.head
		obj_path.append(current_node)

	# Find the lowest common ancestor
	lca = ''
	for sub_word in subj_path:
		for obj_word in obj_path:
			if sub_word.text == obj_word.text:
				lca = sub_word.text
				break
		if lca:
			break

	lca_data['subj_path'] = subj_path
	lca_data['obj_path'] = obj_path
	lca_data['lca'] = lca

	return lca_data

'''
Takes in Spacy's document object of a given sentence and returns a list of incides, [subject_index, object_index]
'''
def get_indices(doc):
	indices = [-1, -1]
	for i in range(len(doc)):
		word = doc[i]
		if word.text == 'SUBJECT':
			indices[0] = i
		elif word.text == 'OBJECT':
			indices[1] = i

		if indices[0] != -1 and indices[1] != -1:
			break

	return indices

'''
Takes in the data dictionary and filename, and creates the ouput files in the specified format
'''
def create_output_file(data, filename):
	with open(filename, 'w') as f:
		for d in data:
			sentence = d['sentence']
			mappings = d['mappings']
			subj_path = '->'.join([str(p) for p in d['lca_data']['subj_path']])
			obj_path = '->'.join([str(p) for p in d['lca_data']['obj_path']])
			lca = str(d['lca_data']['lca'])

			f.write(sentence + '\n')

			for k,v in mappings.items():
				f.write(k + ':' + v + '\n')

			f.write(subj_path + '\n')
			f.write(obj_path + '\n')
			f.write('LCA: ' + lca + '\n\n\n')

def main():
	nlp = spacy.load("en_core_web_sm")

	for filepath in glob.glob('a4_data/*'):

		sentences = open_and_init_json(filepath)
		random.seed(10)
		random.shuffle(sentences)
		subset = sentences[:100]

		lca_dict = {}
		without_lca = 0
		for i in range(len(subset)):
			doc = nlp(subset[i]['sentence'])
			indices = get_indices(doc)
			subset[i]['lca_data'] = lowest_common_ancestor(doc, indices[0], indices[1])

			# LCA counts (for report statistics)
			lca = subset[i]['lca_data']['lca']
			if not lca:
				without_lca += 1
			else:
				if lca not in lca_dict:
					lca_dict[lca] = 1
				else:
					lca_dict[lca] += 1

		f = re.search(r"/(.*)(.json)", filepath)
		filename = f.group(1) + '.txt'
		create_output_file(subset, filename)

		print(filename, without_lca, '\n', lca_dict, '\n')

	print("Success! Output text files generated in this directory.")
	return

main()
