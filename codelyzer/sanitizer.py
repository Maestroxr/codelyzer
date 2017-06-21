import re
import os
import glob

runtimeErrorList = {}

pattern = r'(?:==[0-9]+==.+Sanitizer: )(detected memory leaks|SEGV on unknown address|attempting double-free|'\
                     r'global-buffer-overflow|use-of-uninitialized-value|heap-use-after-free|stack-use-after-return|'\
                     r'stack-buffer-overflow|heap-buffer-overflow)((?:[\n]|.)+(?:(SUMMARY.*)))'

addressPattern = r'(0x[0-9a-z]+)'
onAddressPattern = r'(on address )'+addressPattern+r'(?:.|\n)*(READ|WRITE)( of size [0-9]+ at)((?:.|\n)*)\2'
freedAllocatedPattern = r'(is located [A-Za-z0-9]+ bytes inside of [0-9a-z-]+ region)(?:(?:.|\n)*)(freed by thread' \
                        r' [A-Z0-9]+ here:)((?:.|\n)*)(previously allocated by thread [A-Z0-9]+ here:)((?:.|\n)*)SUMMARY:'
fileLinePattern = r'([a-zA-Z-_ 0-9]+\.(?:cpp|c)):([0-9]+)'
summaryFilePattern = r'SUMMARY:(?:.|\n)*?'+fileLinePattern
locatedAtStackPattern = r'(is located in stack of thread [A-Za-z0-9]+ at offset [0-9]+ in frame)((?:.|\n)*)(This frame (?:.|\n)*)HINT:(?:.|\n)*?'
def sanitize(sanitizerDir, sanitizerFile):
    """
    This function iterates sanitization log files and parses errors according to regular expressions.
    :param sanitizerDir: The directory which holds the logs.
    :param sanitizerFile: If specified, a single log file to parse.
    :return: A list of the runtime errors gathered by the sanitizer.
    """
    onlyfiles = []
    if sanitizerFile != "None":
        onlyfiles = [sanitizerDir+"\\"+sanitizerFile]
    else:
        try:
            os.chdir(sanitizerDir)
            for logFile in glob.glob("*.log"):
                if os.path.isfile(logFile):
                    onlyfiles.append(logFile)
                else:
                    print("scenario memory log file path is wrong:" + logFile)
        except:
            print("Directory " + sanitizerDir + " doesn't exist.")
            return runtimeErrorList
    for logFile in onlyfiles:
        with open(logFile, 'r') as fin:
            read_file = fin.read()

            for (warning,body,summary) in re.findall(pattern,read_file):
                if warning == "global-buffer-overflow":
                    addRuntimeErrors(logFile,regexGlobalBufferOveflow(body,summary))

                elif warning == "stack-buffer-overflow":
                    addRuntimeErrors(logFile, regexStackBufferOverflow(body,summary))

                elif warning == "heap-buffer-overflow":
                    addRuntimeErrors(logFile, regexHeapBufferOveflow(body,summary))

                elif warning == "heap-use-after-free":
                    addRuntimeErrors(logFile, regexHeapUseAfterFree(body,summary))

                elif warning == "SEGV on unknown address":
                    addRuntimeErrors(logFile, regexSegmentationFault(body,summary))

                elif warning == "detected memory leaks":
                    addRuntimeErrors(logFile, regexMemoryLeaks(body,summary))

                elif warning == "use-of-uninitialized-value":
                    addRuntimeErrors(logFile, regexUninitializedMemoryUse(body, summary))

                elif warning == "attempting double-free":
                    addRuntimeErrors(logFile,regexDoubleFree(body,summary))

                elif warning == "stack-use-after-return":
                    addRuntimeErrors(logFile,regexUseAfterReturn(body,summary))

    return runtimeErrorList

def addRuntimeErrors(logfile, errorList):
    """
    This function adds a list of errors to the runtime errors list.
    :param logfile: The log file the error was parsed from.
    :param errorList: The error list.
    """
    global runtimeErrorList
    for errorfile, line, error, injectVars  in errorList:
        if not runtimeErrorList.has_key((errorfile, line,error)):
            runtimeErrorList[(errorfile, line,error)] = (injectVars, {logfile})
        else:
            runtimeErrorList[(errorfile, line, error)][1].add(logfile)


def regexTrace(text):
    """
    This function parses a stack trace from text.
    :param text: The text which holds the trace.
    :return: Returns a list containing the trace entries.
    """
    traceList = []
    tracePattern = re.compile(r'(#[0-9]+)(?:.)*(?:in ([a-z0-9A-Z]+))(?:.)*?'+fileLinePattern)
    for (number, function,file,line) in re.findall(tracePattern, text):
        traceList.append((number, function,file,line))
    return traceList

def parseTrace(trace):
    """
    This function parses a list containing trace entries into a trace text.
    :param trace: The trace list.
    :return: The parsed trace.
    """
    s = ""
    for number, function,file,line in trace:
        s += '\t\t'+ file +":"+line+" in function '"+function+"'\n"
    return s

def parseOverflow(text):
    """
    This function parses an overflow prefix of a sanitizer log file.
    :param text: The text which holds the overflow data.
    :return: A parsed overflow string.
    """
    _, address, readWrite, ofSize1, body = re.findall(onAddressPattern, text)[0]
    atTrace = regexTrace(body)
    overflow = "\n\tWas accessed by " + ("read" if readWrite == "READ" else "write")
    overflow += ofSize1 + ":\n" + parseTrace(atTrace)
    return overflow, atTrace


def createInjectVarsLambda(accessFile, line, error1, error2):
    """
    This function creates a lambda function which parses an error by injecting the lamda's only variable - a list of
    suspect variables.
    The lambda then parses the error string according to specified structure.
    :param accessFile: The file that was accessed when the error occured.
    :param line: The line of access.
    :param error1: The first part of the error.
    :param error2: The second part of the error.
    :return: A lambda which parses the error string and recieved a list of string representing the variables.
    """
    # str(vars)[1:-1] to ignore brackets [] of suspect variables list
    return lambda vars: error1 + ", suspect variables: " + str(vars) + error2 if (len(vars) > 1) else error1 + \
            ", suspect variable: " + str(vars)[1:-1] + error2


def createSecondError(accessFile,line):
    """
    A function that parses the second error string.
    :param accessFile: The file accessed when the occured.
    :param line: The line of access.
    :return: A parsed second part of an error.
    """
    return ", "+accessFile+ ":" + line


def regexSummary(summary, trace):
    """
    This function parses a summary text.
    :param summary: The summary text to parse.
    :param trace: The trace that the access file and line should be regexed from, incase the summary does not have them.
    :return: returns an accessed file and line tuple.
    """
    regexpedSummary = re.findall(summaryFilePattern, summary)
    if regexpedSummary:
        accessFile, line = regexpedSummary[0]
    elif trace is not None:
        accessFile, line = trace[0][2], trace[0][3]
    else:
        return "Parsing Error - no access file", 1
    return accessFile, line



def regexGlobalBufferOveflow(text, summary):
    """
    This function construct a global buffer overflow error.
    :param text: The text the error should be regexed from.
    :return: The error list parsed.
    """
    globalLocatedAtPattern = re.compile(r'(is located [0-9]+ bytes to the right of global variable \'([0-9a-zA-Z]+)\''
                         r' from \'([a-zA-Z-_ ]+.(?:cpp|c))\') (?:\(0x[0-9a-z]+\)) (of size [0-9]+)(?:.|\n)*SUMMARY:')

    locatedAt, identifier, originFile, ofSize2= re.findall(globalLocatedAtPattern,text)[0]
    accessFile, line = regexSummary(summary, None)
    error = "Global variable buffer overflow, '"+identifier +"' from file "+originFile+ ", accessed at"+\
            createSecondError(accessFile,line)[1:] +parseOverflow(text)[0]+"\tAccessed address "+locatedAt + ", " +ofSize2
    return [(accessFile,line , error, None)]



def regexHeapBufferOveflow(text, summary):
    """
        This function construct a heap buffer overflow error.
        :param text: The text the error should be regexed from.
        :return: The error list parsed.
        """

    heapLocatedAtPattern = re.compile(r'(is located [0-9]+ bytes to the right of )((?:[0-9]+).*region)((?:.|\n)*)SUMMARY:')
    locatedAt, ofSize2, body = re.findall(heapLocatedAtPattern, text)[0]
    allocatedAtTrace = regexTrace(body)
    overflowText, overflowTrace = parseOverflow(text)
    accessFile, line = regexSummary(summary, overflowTrace)
    error = "Heap buffer overflow"
    error2 = createSecondError(accessFile,line)
    error2 += overflowText + "\tAccessed address "+locatedAt  +ofSize2
    error2 += ", allocated at:\n" + parseTrace(allocatedAtTrace)
    return [(accessFile, line, error + error2, createInjectVarsLambda(accessFile, line, error, error2))]

def regexStackBufferOverflow(text, summary):
    """
        This function construct a stack buffer overflow error.
        :param text: The text the error should be regexed from.
        :return: The error list parsed.
        """
    stackLocatedAtPattern = re.compile(locatedAtStackPattern)
    locatedAt, frameTraceBody, frameBody= re.findall(stackLocatedAtPattern, text)[0]
    frameTrace = regexTrace(frameTraceBody)
    overflowText, overflowTrace = parseOverflow(text)
    accessFile, line = regexSummary(summary, overflowTrace)
    error = "Stack buffer overflow"
    error2 = createSecondError(accessFile, line)
    error2 += overflowText + "\tAccessed address " + locatedAt
    error2 += ":\n" + parseTrace(frameTrace) # + "\n\t" + frameBody
    return [(accessFile, line, error + error2, createInjectVarsLambda(accessFile, line, error, error2))]

def regexHeapUseAfterFree(text, summary):
    """
        This function construct a heap use after free error.
        :param text: The text the error should be regexed from.
        :return: The error list parsed.
        """
    heapUseLocatedAtPattern = re.compile(freedAllocatedPattern)
    locatedAt, freedByThread, freedByThreadTrace, previouslyAllocated, previouslyAllocatedTrace= re.findall(heapUseLocatedAtPattern, text)[0]
    overflowText, overflowTrace = parseOverflow(text)
    accessFile, line = regexSummary(summary, overflowTrace)
    accessFile, line = regexSummary(summary, overflowTrace)
    error = "Heap use after free"
    error2 = createSecondError(accessFile, line)
    error2 += overflowText + "\tAccessed address " + locatedAt +", "+ freedByThread
    error2 += "\n" + parseTrace(regexTrace(freedByThreadTrace)) + "\t" + "P"+previouslyAllocated[1:] + "\n" + parseTrace(regexTrace(previouslyAllocatedTrace))
    return [(accessFile, line, error + error2, createInjectVarsLambda(accessFile, line, error, error2))]


def regexSegmentationFault(text, summary):
    """
        This function construct a segmentation fault error.
        :param text: The text the error should be regexed from.
        :return: The error list parsed.
        """
    segTrace = regexTrace(text)
    accessFile, line = regexSummary(summary,segTrace)
    error = "Segmentation fault"
    error2 = createSecondError(accessFile, line)
    error2 += " at:\n" + parseTrace(segTrace)
    return [(accessFile, line, error + error2, createInjectVarsLambda(accessFile, line, error, error2))]


def regexMemoryLeaks(text, summary):
    """
        This function constructs a memory leaks error.
        :param text: The text the error should be regexed from.
        :param summary: THe summary text parts of the error should be regexed from.
        :return: The error list parsed.
        """
    memoryLeakPattern = re.compile(r'(Direct leak of [0-9]+ byte\(s\) in [0-9]+ object\(s\) allocated from:)((?:.|\n)*?)\n\n')
    errorList = []
    for directLeak, leakBody in re.findall(memoryLeakPattern,text):
        error = "Detected memory leaks"
        leakTrace = regexTrace(leakBody)
        accessFile, line = leakTrace[0][2], leakTrace[0][3]
        error2 = createSecondError(accessFile, line)
        error2 += "\n" + parseTrace(leakTrace)
        errorList.append((accessFile, line, error + error2, createInjectVarsLambda(accessFile, line, error, error2)))
    #errorList.append((accessFile,1,summary, None))
    return errorList

def regexUninitializedMemoryUse(text, summary):
    """
    This function constructs an uninitialized memory use error.
    :param text: The text the error should be regexed from.
    :param summary: THe summary text parts of the error should be regexed from.
    :return: The error list parsed.
    """
    uninitializedMemoryPattern = re.compile(r'((?:.|\n)*?)\n\n(.*)((?:.|\n)*?)\n\n')
    useBody, uninitValue, allocatedBody = re.findall(uninitializedMemoryPattern,text)[0]
    error = "Use of uninitialized value"
    useTrace, allocatedTrace = regexTrace(useBody), regexTrace(allocatedBody)

    accessFile, line = regexSummary(summary,useTrace)
    error2 = createSecondError(accessFile, line)
    error2 += "\n\tUsed at:\n" + parseTrace(useTrace)
    error2 += "\tAllocated at:\n" + parseTrace(allocatedTrace)
    return [(accessFile, line, error + error2, createInjectVarsLambda(accessFile, line, error, error2))]


def regexDoubleFree(text, summary):
    """
        This function constructs a double free error.
        :param text: The text the error should be regexed from.
        :return: The error list parsed.
        """
    doubleFreePattern = re.compile(addressPattern+r' (in thread [A-Za-z0-9]+:)((?:.|\n)*)\1 '+freedAllocatedPattern)
    address, doubleFreeInThread, doubleFreeBody, locatedAt, originalFreeByThread, originalFreeBody,\
        previouslyAllocated, previouslyAllocatedBody = re.findall(doubleFreePattern, text)[0]

    doubleFreeTrace, originalFreeTrace, previouslyAllocatedTrace = \
        regexTrace(doubleFreeBody), regexTrace(originalFreeBody), regexTrace(previouslyAllocatedBody)

    accessFile, line = regexSummary(summary, doubleFreeTrace)
    error = "Double free of heap memory"
    error2 = createSecondError(accessFile, line)
    error2 += "\n\tAttempted double free " + doubleFreeInThread + "\n" + parseTrace(doubleFreeTrace)
    error2 += "\tFreed address " + locatedAt +", already " + originalFreeByThread +"\n" + parseTrace(originalFreeTrace)
    error2 += "\t" + "P" + previouslyAllocated[1:] + "\n" + parseTrace(previouslyAllocatedTrace)
    return [(accessFile, line, error + error2, createInjectVarsLambda(accessFile, line, error, error2))]

def regexUseAfterReturn(text, summary):
    """
        This function constructs a use after return error.
        :param text: The text the error should be regexed from.
        :return: The error list parsed.
        """
    stackLocatedAtPattern = re.compile(locatedAtStackPattern)
    locatedAt, frameTraceBody, frameBody = re.findall(stackLocatedAtPattern, text)[0]
    frameTrace = regexTrace(frameTraceBody)

    overflowText, overflowTrace = parseOverflow(text)
    accessFile, line = regexSummary(summary, overflowTrace)
    error = "Stack memory use after function return"
    error2 = createSecondError(accessFile, line)
    error2 += overflowText + "\tAccessed address " + locatedAt +":\n"
    error2 +=  parseTrace(frameTrace)  # + "\n\t" + frameBody
    return [(accessFile, line, error + error2, createInjectVarsLambda(accessFile, line, error, error2))]