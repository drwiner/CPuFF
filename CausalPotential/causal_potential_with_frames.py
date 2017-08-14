"""
create dictionary cp_dict[<verb,frame>] with two keys, 0 for before, and 1 for after,
whose values are <verb,frame> events in the same segment, ordered before or after the key.

CP = log(P(e1,e2)/P(e1)P(e2)) + log(P(e1 < e2) / P(e2 < e1))

"""

from os import listdir
from os.path import isfile, join

from collections import defaultdict, namedtuple, Counter
import math
import json
import pickle

from clockdeco import clock

Event = namedtuple("Event", 'verb frame')

@clock
def sum_joint_instances(db3):
	num_inst = sum(sum(db3[e][0].values()) + sum(db3[e][1].values()) for e in db3.keys())
	return num_inst/2

# @clock
def PMI(triple, e1, e2, all_joint_instances, event_probs):
	if e2 not in triple[e1][1].keys():
		num_e1_first = 1
	else:
		num_e1_first = triple[e1][1][e2] #sum(e2 == inst for inst in cp_dict[e1][1])

	if e2 not in triple[e1][0].keys():
		num_e2_first =  1
	else:
		num_e2_first = triple[e1][0][e2]

	# gather all instances of e1 and e2 joint reference
	# all_e1 = sum(triple[e1][0].values()) + sum(triple[e1][1].values())
	# all = all_e1.extend(cp_dict[e2][0].extend(cp_dict[e2][1])
	p_e1_e2 = (num_e1_first + num_e2_first) / all_joint_instances

	p_e1 = event_probs[e1]
	p_e2 = event_probs[e2]

	denom = (p_e1 * p_e2)
	if denom == 0:
		return 0

	before_log = p_e1_e2 / (p_e1 * p_e2)

	if before_log == 0:
		return 0

	return math.log(before_log)


# @clock
def log_prob_of_ordering(triple, e1, e2):
	if e2 not in triple[e1][1].keys():
		num_e1_first = 1
	else:
		num_e1_first = triple[e1][1][e2] #sum(e2 == inst for inst in cp_dict[e1][1])

	if e2 not in triple[e1][0].keys():
		num_e2_first = 1
	else:
		num_e2_first = triple[e1][0][e2] #sum(e2 == inst for inst in cp_dict[e1][0])

	before_log = num_e1_first / num_e2_first

	if before_log == 0:
		return 0

	return math.log(before_log)


@clock
def calc_CP_per_event(e1, triple, sji, probs_dict, cp_scores):
	# cmpr = set(cp_dict[e1][0]).union(set(cp_dict[e1][1]))
	cmpr = set(triple[e1][0].keys()).union(triple[e1][1].keys())
	for e2 in cmpr:
		if e2 not in probs_dict.keys():
			continue
		if Event(e1, e2) in cp_scores.keys() or Event(e2, e1) in cp_scores.keys():
			continue
		# for e2 in list(cp_dict.keys()):
		# print(e1, e2)
		pmi = PMI(triple, e1, e2, sji, probs_dict)
		ordering = log_prob_of_ordering(triple, e1, e2)
		cp_scores[(e1, e2)] = pmi + ordering

		ordering2 = log_prob_of_ordering(triple, e2, e1)
		cp_scores[(e2, e1)] = pmi + ordering2


def calculate_CP(tripDB, event_counter):
	cp_scores = {}
	print('summing joint instances')
	sji = sum_joint_instances(tripDB)
	total_val = sum(event_counter.values())
	e_probs = {e: e_count / total_val for e, e_count in event_counter.items() if e_count > 1}

	for e1, prob in e_probs.items():
		if e1 not in event_counter.keys():
			continue
		if e1 not in tripDB.keys():
			continue
		print(e1)
		calc_CP_per_event(e1, tripDB, sji, e_probs, cp_scores)

	return cp_scores


def make_triple_database(cp_dict):
	tripleDB = defaultdict(lambda: {0: 0, 1: 0})
	for e1 in list(cp_dict.keys()):
		tripleDB[e1][0] = dict(Counter(cp_dict[e1][0]))
		tripleDB[e1][1] = dict(Counter(cp_dict[e1][1]))
	return dict(tripleDB)


def load_cp_dict(sps, cp_dict, event_counter):

	if sps is None or sps == '' or sps == 'none' or sps == []:
		return None
	seen = []
	for item in sps:
		if item is None:
			continue

		verb, frame, _, _ = item

		frame_name, frame_id = frame
		e = Event(verb, frame_name)
		event_counter[e] += 1
		for event in seen:
			cp_dict[e][0].append(event)
			cp_dict[event][1].append(e)
		seen.append(e)


def get_seg_pairs(mseg):
	last = None
	seg_pairs = []
	for seg in mseg:
		if 'sense_profile' not in seg.keys():
			continue
		sps = seg['sense_profile']
		if sps is None or sps == '' or sps == 'none' or sps == []:
			continue

		if last is None or last == []:
			last = sps
			continue
		else:
			if list(sps)[0] is None:
				continue
			combine = list()
			combine.extend(last)
			combine.extend(sps)
			seg_pairs.append(combine)
			last = sps

	if (seg_pairs is None or seg_pairs == []) and last is not None and last != []:
		return [last]

	return seg_pairs


@clock
def process_screenplay(data, CP_dict, CP_2seg_dict, event_count, seg_event_counter):
	# seg_pairs for each master seg
	seg_pairs = [get_seg_pairs(mseg) for mseg in data]
	segs = [seg['sense_profile'] for mseg in data for seg in mseg if
	        'sense_profile' in seg.keys() and seg['sense_profile'] != []]
	for seg in segs:
		load_cp_dict(seg, CP_dict, event_count)
	for seg_pair in seg_pairs:

		if seg_pair == []:
			continue
		for sp in seg_pair:
			if sp == []:
				continue
			load_cp_dict(sp, CP_2seg_dict, seg_event_counter)

def make_cp_dict():
	path = 'D:\\Documents\\python\\screenpy\\ParserOutput_VSD\\'

	genre_folders = [(f, join(path, f)) for f in listdir(path) if not isfile(join(path, f))]

	# regular CP dict
	CP_dict = defaultdict(lambda: {0: [], 1: []})
	# CP dict where we look at potential causal links across segments
	CP_2seg_dict = defaultdict(lambda: {0: [], 1: []})
	event_count = defaultdict(int)
	seg_event_counter = defaultdict(int)

	for genre, genre_path in genre_folders:
		print(genre)
		screenplay_files = [join(genre_path, f) for f in listdir(genre_path) if
		                    isfile(join(genre_path, f)) and f[-5:] == '.json']

		for play in screenplay_files:
			with open(play) as json_file:
				data = json.load(json_file)

			if len(data) == 0:
				continue

			print(play)
			process_screenplay(CP_dict, CP_2seg_dict, event_count, seg_event_counter)

		# print('here')
	pickle.dump(dict(CP_dict), open('CP_dict.pkl', 'wb'))
	pickle.dump(dict(CP_2seg_dict), open('CP_2seg_dict.pkl', 'wb'))
	pickle.dump((event_count, seg_event_counter), open('event_counters.pkl', 'wb'))



def calc_CP_with_triples():
	print('loading CP dict and event Counter')
	# CP_dict = pickle.load(open('CP_dict.pkl', 'rb'))
	# CP_2seg_dict = pickle.load(open('CP_2seg_dict.pkl', 'rb'))
	ecount, segcount = pickle.load(open('event_counters.pkl', 'rb'))

	print('calculating CP for window 1')
	# basic_triple = make_triple_database(CP_dict)
	basic_triple = pickle.load(open('basic_triple.pkl', 'rb'))
	# pickle.dump(basic_triple, open('basic_triple.pkl', 'wb'))
	# print('dump')
	window_1 = calculate_CP(basic_triple, ecount)
	pickle.dump(window_1, open('CP_scores.pkl', 'wb'))

	# twoSeg_triple = make_triple_database(CP_2seg_dict)
	twoSeg_triple = pickle.load(open('twoSeg_triple.pkl', 'rb'))
	# pickle.dump(twoSeg_triple, open('twoSeg_triple.pkl', 'wb'))
	print('dump2')
	window_2 = calculate_CP(twoSeg_triple, segcount)
	pickle.dump(window_2, open('CP_Seg_scores.pkl', 'wb'))


def calc_triples():
	print('loading CP dict and event Counter')
	CP_dict = pickle.load(open('CP_dict.pkl', 'rb'))
	CP_2seg_dict = pickle.load(open('CP_2seg_dict.pkl', 'rb'))

	print('calculating CP for window 1')
	basic_triple = make_triple_database(CP_dict)
	pickle.dump(basic_triple, open('basic_triple.pkl', 'wb'))


	twoSeg_triple = make_triple_database(CP_2seg_dict)
	pickle.dump(twoSeg_triple, open('twoSeg_triple.pkl', 'wb'))


if __name__ == '__main__':

	# make_cp_dict()
	# calc_triples()
	# calc_CP_with_triples()

	cp = pickle.load(open('CP_scores.pkl', 'rb'))
	cp = list(cp.items())
	cp.sort(key=lambda tup: -tup[1])
	print('here')
	# with open('top_2000_causal_pairs.txt', 'w') as file:
	# 	for pair in cp[:2000]:
	# 		file.write(str(pair[0]) + '\t' + str(pair[1]) + '\n')

	cp2 = pickle.load(open('CP_Seg_scores.pkl', 'rb'))
	cp2 = list(cp2.items())
	cp2.sort(key=lambda tup: -tup[1])
	print('here')
	with open('top_2000_2seg_causal_pairs.txt', 'w') as file:
		for pair in cp2[:2000]:
			file.write(str(pair[0]) + '\t' + str(pair[1]) + '\n')


	print('here')