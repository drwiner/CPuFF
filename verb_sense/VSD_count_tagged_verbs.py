from os import listdir
from os.path import isfile, join

# from collections import defaultdict

from verb_sense.VSD_withSpacy import count_verbs
import json

# given text, output number of verbs
def tally_verbs(text):
	return count_verbs(text)

def score_stats(screenplay_files):
	frames = 0
	verbs = 0
	num_files = 0
	total_segs = 0
	total_msegs = 0
	for file in screenplay_files:
		with open(file) as json_file:
			data = json.load(json_file)

		if len(data) == 0:
			continue

		print(file)
		num_files += 1
		total_msegs += len(data)
		total_segs += sum(1 for mseg in data for seg in mseg)

		for mseg in data:
			for seg in mseg:
				if 'sense_profile' not in seg.keys():
					pass
				else:
					sps = seg['sense_profile']
					if sps is None or sps == '' or sps == 'none' or sps == []:
						pass
					else:

						num_frames = 0
						for sp in sps:
							if sp is None or sp == '' or sp == 'none' or sp == []:
								pass
							else:
								num_frames += 1
						frames += num_frames

				text = seg['text']
				if text == '' or text is None or text == [] or text == 'none':
					pass
				else:
					verbs += count_verbs(text)

	genre_avg_verbs_per_screenplay = (verbs) / num_files
	genre_avg_verbs_per_seg = (verbs) / total_segs
	genre_avg_verbs_per_mseg = (verbs) / total_msegs
	genre_percent_tagged = (frames) / (verbs)

	return (genre_avg_verbs_per_screenplay, genre_avg_verbs_per_seg, genre_avg_verbs_per_mseg,genre_percent_tagged)


def output_genre_stats(genre_stats, filename):
	with open(filename, 'w') as genre_file:
		for genre, (genre_avg_verbs_per_screenplay,
		            genre_avg_verbs_per_seg,
					genre_avg_verbs_per_mseg,
		            genre_percent_tagged) in genre_stats.items():

			genre_file.write(str(genre) + '\t')
			genre_file.write(str(genre_avg_verbs_per_screenplay) + '\t')
			genre_file.write(str(genre_avg_verbs_per_seg) + '\t')
			genre_file.write(str(genre_avg_verbs_per_mseg) + '\t')
			genre_file.write(str(genre_percent_tagged) + '\n')



if __name__ == '__main__':

	# get this path from arguments in command line
	path = 'D:\\Documents\\python\\screenpy\\ParserOutput_VSD\\'

	genre_folders = [(f, join(path, f)) for f in listdir(path) if not isfile(join(path, f))]
	genre_stats = {}
	for genre, genre_path in genre_folders:
		print(genre)
		screenplay_files = [join(genre_path, f) for f in listdir(genre_path) if
		                    isfile(join(genre_path, f)) and f[-5:] == '.json']

		genre_stats[genre] = score_stats(screenplay_files)

	output_genre_stats(genre_stats, filename='D:\\documents\\python\\screenpy\\VSD_genre//VSD_percent_tagged_verbs_stats2.txt')