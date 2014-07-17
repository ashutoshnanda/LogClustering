#! /cygdrive/c/Python33/python.exe

logFileName = "trimmed-mongodb.log"

logTypeInfo = "Log Types"
logLinesInfo = "Log Lines"

import os

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
		

def head(n, lines, info = ""):
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

if __name__ == '__main__':
	print("Log Clustering Algorithm, v0.1\n")
	prechecks()
	log = readLog()
	log = preprocessLog(log)
	logTypes = extract_type(log)
	head(20, logTypes)
	print("Exiting..")
