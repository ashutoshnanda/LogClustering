#! /cygdrive/c/Python33/python.exe

logFileName = "trimmed-mongodb.log"

logTypeInfo = "Log Types"
logLinesInfo = "Log Lines"

import os

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
	sanitizedLogContents = [logLine.split("] ")[1].strip().replace("(", "").replace(")", "").replace(":", "").replace("[", "").replace("]", "")\
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
	vectorLines = [[sum([word == logWord for logWord in logLine.split(" ")]) for word in words] for logLine in log]
	print("Done converting log lines into vectors..\n")
	return vectorLines

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
	print("%s..\n" % outro)

## Analysis Modes

def mainAnalysis():
	print("Log Clustering Algorithm, v0.1\n")
	prechecks()
	log = readLog()
	log = preprocessLog(log)
	logTypes = extract_type(log)
	analyze_type(logTypes)
	sanitizedLog = sanitize_log_contents(log)
	corpus = build_corpus(sanitizedLog)
	analyze_corpus(corpus, sanitizedLog)
	vectorLines = convert_log_lines(corpus, sanitizedLog)
	print("Exiting..")

## Main

if __name__ == '__main__':
	mainAnalysis()
