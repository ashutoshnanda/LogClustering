#! /usr/bin/python3

import os
import numpy as np
from scipy.cluster.vq import kmeans, whiten, kmeans2

logFileName = "trimmed-mongodb.log"

logTypeInfo = "Log Types"
logLinesInfo = "Log Lines"

similarity_cutoff = 0.8

csv_log_export_filename = "../log-visualization/data/log.csv"
csv_types_export_filename = "../log-visualization/data/types.csv"

##Analysis methods

def prechecks():
	print("Doing prechecks..")

	print("Log file name: \"%s\"" % logFileName)

	if os.path.isfile(logFileName):
		print("Log file \"%s\" exists" % logFileName)
	else:
		print("Log file \"%s\" not found!")
		print("Exiting..")
		exit()

	if os.path.isfile(csv_log_export_filename):
		print("Found log.csv file at \"%s\".." % csv_log_export_filename)
		print("Removing \"%s\".." % csv_log_export_filename)
		os.remove(csv_log_export_filename)

	if os.path.isfile(csv_types_export_filename):
		print("Found types.csv file at \"%s\".." % csv_types_export_filename)
		print("Removing \"%s\".." % csv_types_export_filename)
		os.remove(csv_types_export_filename)
		
	print("Done doing prechecks..\n")

def readLog():
	print("Reading in log..")

	logFile = open(logFileName, 'r')
	logLines = logFile.readlines()
	print("Stripping lines..")
	logLines = [logLine.strip() for logLine in logLines]

	print("Done reading in log..\n")
	return logLines

def preprocessLog(logLines):
	print("Preprocessing log..")

	print("Removing all lines not containing square brackets..")
	initial = len(logLines)
	logLines = [logLine for logLine in logLines if "[" and "]" in logLine]
	final = len(logLines)
	print("Removed %d lines.." % (initial - final))

	print("Done preprocessing log..\n")
	return logLines

def extract_type(logLines):
	print("Extracting type of log lines..")

	logTypes = [logLine.split("[")[1].split("]")[0] for logLine in logLines]

	print("Done extracting type of log lines..\n")
	return logTypes

def extract_time(logLines):
	print("Extracting timestamps of the log lines..")
	
	logTimes = [logLine.split(" [")[0] for logLine in logLines]

	print("Done extracting timestamps of the log lines..")	
	return logTimes
		
def analyze_type(logTypes):
	print("Analyzing types of log lines..")

	uniqueLogTypes = list(set(logTypes))
	#print("Unique Log Types (%d): %s" % (len(uniqueLogTypes), repr(uniqueLogTypes)))

	countsOfLogType = [logTypes.count(typeOfLog) for typeOfLog in uniqueLogTypes]
	logType2countsOfLogType = dict(zip(uniqueLogTypes, countsOfLogType))
	#print("Counts information..")
	for logType in logType2countsOfLogType:
		#print("%s --> %d (%f%%)" % (logType, logType2countsOfLogType[logType], 100 * logType2countsOfLogType[logType] / len(logTypes)))
		pass		

	print("Combining all \"conn\" types..")
	uniqueLogTypes = [uniqueLogType for uniqueLogType in uniqueLogTypes if "conn" not in uniqueLogType]
	uniqueLogTypes.append("conn")
	print("Unique Log Types [\"conn\" trimmed] (%d): %s" % (len(uniqueLogTypes), repr(uniqueLogTypes)))
	countsOfLogType = [sum([uniqueLogType in logType for logType in logTypes]) for uniqueLogType in uniqueLogTypes]	#True == 1 in Python, so I can sum booleans
	logType2countsOfLogType = dict(zip(uniqueLogTypes, countsOfLogType))
	print("Counts information [\"conn\" trimmed]..")
	for logType in logType2countsOfLogType:
		print("%s --> %d (%f%%)" % (logType, logType2countsOfLogType[logType], 100 * logType2countsOfLogType[logType] / len(logTypes)))
	
	print("Done analyzing types of log lines..\n")

def sanitize_log_contents(logLines):
	#Removes certain characters and isolates log contents
	print("Sanitizing log lines..")
	sanitizedLogContents = [logLine.split("] ")[1].strip().replace("(", "").replace(")", " ").replace(":", " ").replace("[", "").replace("]", "")\
				.replace("{", "").replace("}", "").replace(".", "").replace(",", "").replace("\"", "").replace("_", "") for logLine in logLines]
	print("Done sanitizing log lines..\n")
	return sanitizedLogContents

def build_corpus(logContents):
	print("Making a dictionary of all words occurring in log lines..")
	corpus = []
	for logContent in logContents:
		for word in logContent.split(" "):
			if word not in corpus and noNumbers(word) and len(word) > 0:
				corpus.append(word)
	print("Gathered %d words.." % len(corpus))
	print("Done making a dictionary of all words occurring in log lines..\n")
	return corpus

def analyze_corpus(words, log):
	print("Analyzing the dictionary of all words occurring in log lines..")
	countsOfWords = []
	for word in words:
		counts = 0
		for logLine in log:
			for logWord in logLine.split(" "):
				if word == logWord:
					counts += 1
		countsOfWords.append(counts)
	words2countsOfWords = dict(zip(words, countsOfWords))
	pairedWordsCountsOfWords = list(zip(words, countsOfWords))
	pairedWordsCountsOfWords.sort(key = lambda pair: pair[1], reverse = True)
	
	#print("Printing word counts..")	
	#[print("\"%s\" -- %d" % (pair[0], pair[1])) for pair in pairedWordsCountsOfWords]
	
	print("Done analyzing the dictionary of all words occurring in log lines..\n")

def convert_log_lines(words, log):
	print("Converting log lines into vectors..")
	vectorLines = [[1 if sum([word == logWord for logWord in logLine.split(" ")]) > 0 else 0 for word in words] for logLine in log]
	print("Done converting log lines into vectors..\n")
	return vectorLines

def clustering(vecs):
	print("Clustering the logs..")
	print("Number of lines: %d" % len(vecs))
	print("Number of features: %d" % len(vecs[0]))
	
	uniqueVecs = [item for (n, item) in enumerate(vecs) if item not in vecs[:n]] 
	print("Number of Unique Vectors = %d.." % len(uniqueVecs))
	counts = [sum([uniqueVec == vec for vec in vecs]) for uniqueVec in uniqueVecs]
	for (i, uniqueVec) in enumerate(uniqueVecs):
		print("Counts: %d; Max Value: %d" % (counts[i], max(uniqueVec)))
	
	before = len(uniqueVecs)
	uniqueVecs = list(filter(lambda x: sum(x) != 0, uniqueVecs))
	after = len(uniqueVecs)
	print("Removed %d zero vecs.." % (before - after)) if before - after != 0 else None

	similarities = [[dot(other, uniqueVec) / (dot(uniqueVec) * dot(other)) ** 0.5 if other != uniqueVec else 0 for other in uniqueVecs] for uniqueVec in uniqueVecs]
	head(similarities, len(similarities))
	nonzerosimilarities = []
	for i in range(len(similarities)):
		for j in range(len(similarities[i])):
			if similarities[i][j] > 0 and similarities[i][j] not in [item[0] for item in nonzerosimilarities]:
				nonzerosimilarities.append((similarities[i][j], i, j))
	nonzerosimilarities.sort(key = lambda x: x[0], reverse = True)
	print(nonzerosimilarities)

	mapping = list(range(len(uniqueVecs)))
	for item in nonzerosimilarities:
		if item[0] > similarity_cutoff:
			count = 0
			first_id = min(item[1:])
			second_id = max(item[1:])
			mapping[first_id] = second_id
			print("Mapped %d to %d (count = %d).." % (first_id, second_id, counts[first_id]))
			counts[second_id] += counts[first_id]
			counts[first_id] = 0
	print(counts)

	#matrix = np.asarray(vecs) #Each row represents a different line from the log file; each column represents a different feature
	#whitematrix = whiten(matrix)
	#centroids = [1, 4, 10, 20]
	#for centroid in centroids:
	#	code, dist = kmeans(whitematrix, centroid)
	#	print("%d --> %f" % (centroid, dist))

	return (uniqueVecs, mapping)
	
	print("Done clustering the logs..\n")

def classify(log, logVectors, templates, mapping):
	print("Classifying the log lines..")
	
	print(mapping)

	for i, logline in enumerate(log):
		index = templates.index(logVectors[i]) if logVectors[i] in templates else -1
		print("%d: %s" % (mapping[index], logline))
	

	print("Done classifying the log lines..\n")

def csv_export(log, sanitizedlog, logvectors, vectortypes, vectortimes, templates, mapping, dictionary):
	print("Exporting data to .csv format..")
	
	csv_export = open(csv_log_export_filename, 'w')

	csv_export.write("Timestamp;Log Type;Unique Vector ID;Matched ID;Raw Log;Sanitized Log\n")

	for i in range(len(log)):
		uniqueID = templates.index(logvectors[i])
		csv_export.write("%s;%s;%d;%d;\"%s\";\"%s\"\n" % (vectortimes[i], vectortypes[i], uniqueID, mapping[uniqueID], log[i], sanitizedlog[i]))

	csv_export.close()

	csv_export = open(csv_types_export_filename, 'w')

	csv_export.write("Type;Words\n")

	for i, template in enumerate(templates):
		csv_export.write("%d;\"" % i)
		nonzero = [j for (j, value) in enumerate(template) if value != 0]
		for j in range(len(nonzero)):
			csv_export.write(dictionary[nonzero[j]])
			if j != len(nonzero) - 1:
				csv_export.write(" ")
		csv_export.write("\"\n")

	csv_export.close()

	print("Done exporting data to .csv format..")
	
##Utilities

def noNumbers(string):
	return string == "".join(filter(lambda char: not char.isdigit(), string))

def head(lines, n, info = ""):
	#Prints first n values of lines

	intro = "Printing first %d lines" % n
	if info != "":
		intro += " of %s" % info
	print("%s.." % intro)

	for i in range(n):
		print(lines[i])

	outro = "Done printing first %d lines" % n
	if info != "":
		outro += " of %s" % info
	print("%s.." % outro)

def dot(u, v = None):
	if not v:
		v = u
	assert(len(u) == len(v))
	return sum([u[i] * v[i] for i in range(len(u))])

## Analysis Modes

def mainAnalysis():
	print("Log Clustering Algorithm, v0.1\n")
	prechecks()
	log = readLog()
	log = preprocessLog(log)
	logTypes = extract_type(log)
	analyze_type(logTypes)
	logTimes = extract_time(log)
	sanitizedLog = sanitize_log_contents(log)
	corpus = build_corpus(sanitizedLog)
	analyze_corpus(corpus, sanitizedLog)
	vectorLines = convert_log_lines(corpus, sanitizedLog)
	(uniqueVectors, mapping) = clustering(vectorLines)
	classify(log, vectorLines, uniqueVectors, mapping)
	csv_export(log, sanitizedLog, vectorLines, logTypes, logTimes, uniqueVectors, mapping, corpus)
	print("Exiting..", end = "")

## Main

if __name__ == '__main__':
	mainAnalysis()
