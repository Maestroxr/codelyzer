import re
import os
import glob

runtimeErrorList = {}

pattern = r'(?:==[0-9]+==.+Sanitizer: )(detected memory leaks|SEGV on unknown address|attempting double-free|'\
                     r'global-buffer-overflow|use-of-uninitialized-value|heap-use-after-free|stack-use-after-return|'\
                     r'stack-buffer-overflow|heap-buffer-overflow)((?:[\n]|.)+)(?:(SUMMARY.*)|ABORTING)'

addressPattern = r'(0x[0-9a-z]+)'
onAddressPattern = r'(on address )'+addressPattern+r'(?:.|\n)*(READ|WRITE)( of size [0-9]+ at)((?:.|\n)*)\2'
freedAllocatedPattern = r'(is located [A-Za-z0-9]+ bytes inside of [0-9a-z-]+ region)(?:(?:.|\n)*)(freed by thread' \
                        r' [A-Z0-9]+ here:)((?:.|\n)*)(previously allocated by thread [A-Z0-9]+ here:)((?:.|\n)*)'
fileLinePattern = r'([a-zA-Z-_ 0-9]+\.(?:cpp|c)):([0-9]+)'
summaryFilePattern = r'SUMMARY:(?:.|\n)*?'+fileLinePattern
locatedAtStackPattern = r'(is located in stack of thread [A-Za-z0-9]+ at offset [0-9]+ in frame)((?:.|\n)*)(This frame (?:.|\n)*)HINT:(?:.|\n)*?'+fileLinePattern
def sanitize(sanitizerDir, sanitizerFile):
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
                    addRuntimeErrors(logFile,regexGlobalBufferOveflow(body))

                elif warning == "stack-buffer-overflow":
                    addRuntimeErrors(logFile, regexStackBufferOverflow(body))

                elif warning == "heap-buffer-overflow":
                    addRuntimeErrors(logFile, regexHeapBufferOveflow(body))

                elif warning == "heap-use-after-free":
                    addRuntimeErrors(logFile, regexHeapUseAfterFree(body))

                elif warning == "SEGV on unknown address":
                    addRuntimeErrors(logFile, regexSegmentationFault(body))

                elif warning == "detected memory leaks":
                    addRuntimeErrors(logFile, regexMemoryLeaks(body,summary))

                elif warning == "use-of-uninitialized-value":
                    addRuntimeErrors(logFile, regexUninitializedMemoryUse(body, summary))

                elif warning == "attempting double-free":
                    addRuntimeErrors(logFile,regexDoubleFree(body))

                elif warning == "stack-use-after-return":
                    addRuntimeErrors(logFile,regexUseAfterReturn(body))

    return runtimeErrorList

def addRuntimeErrors(logfile, errorList):
    global runtimeErrorList
    for errorfile, line, error, injectVars  in errorList:
        if not runtimeErrorList.has_key((errorfile, line)):
            runtimeErrorList[(errorfile, line,error)] = (injectVars, {logfile})
        else:
            runtimeErrorList[(errorfile, line)][2].add(logfile)


def regexTrace(text):
    traceList = []
    tracePattern = re.compile(r'(#[0-9]+)(?:.)*(?:in ([a-z0-9A-Z]+))(?:.)*?'+fileLinePattern)
    for (number, function,file,line) in re.findall(tracePattern, text):
        traceList.append((number, function,file,line))
    return traceList

def parseTrace(trace):
    s = ""
    for number, function,file,line in trace:
        s += '\t\t'+ file +":"+line+" in function '"+function+"'\n"
    return s

def parseOverflow(text):
    _, address, readWrite, ofSize1, body = re.findall(onAddressPattern, text)[0]
    atTrace = regexTrace(body)
    overflow = "\n\tWas accessed by " + ("read" if readWrite == "READ" else "write")
    overflow += ofSize1 + ":\n" + parseTrace(atTrace)
    return overflow


def createInjectVarsLambda(accessFile, line, error1, error2):
    # str(vars)[1:-1] to ignore brackets [] of suspect variables list
    return lambda vars: error1 + ", suspect variables: " + str(vars) + error2 if (len(vars) > 1) else error1 + \
            ", suspect variable: " + str(vars)[1:-1] + error2


def createSecondError(accessFile,line):
    return ", "+accessFile+ ":" + line

def regexGlobalBufferOveflow(text):

    globalLocatedAtPattern = re.compile(r'(is located [0-9]+ bytes to the right of global variable \'([0-9a-zA-Z]+)\''
                         r' from \'([a-zA-Z-_ ]+.(?:cpp|c))\') (?:\(0x[0-9a-z]+\)) (of size [0-9]+)(?:.|\n)*'+summaryFilePattern)

    locatedAt, identifier, originFile, ofSize2, accessFile, line = re.findall(globalLocatedAtPattern,text)[0]
    error = "Global variable buffer overflow, '"+identifier +"' from file "+originFile+ ", accessed at"+\
            createSecondError(accessFile,line)[1:] +parseOverflow(text)+"\tAccessed address "+locatedAt + ", " +ofSize2
    return [(accessFile,line , error, None)]



def regexHeapBufferOveflow(text):
    heapLocatedAtPattern = re.compile(r'(is located [0-9]+ bytes to the right of )((?:[0-9]+).*region)((?:.|\n)*)'+summaryFilePattern)
    locatedAt, ofSize2, body, accessFile, line = re.findall(heapLocatedAtPattern, text)[0]
    allocatedAtTrace = regexTrace(body)
    error = "Heap buffer overflow"
    error2 = createSecondError(accessFile,line)
    error2 += parseOverflow(text) + "\tAccessed address "+locatedAt  +ofSize2
    error2 += ", allocated at:\n" + parseTrace(allocatedAtTrace)
    return [(accessFile, line, error + error2, createInjectVarsLambda(accessFile, line, error, error2))]

def regexStackBufferOverflow(text):
    stackLocatedAtPattern = re.compile(locatedAtStackPattern)
    locatedAt, frameTraceBody, frameBody, accessFile, line = re.findall(stackLocatedAtPattern, text)[0]
    frameTrace = regexTrace(frameTraceBody)
    error = "Stack buffer overflow"
    error2 = createSecondError(accessFile, line)
    error2 += parseOverflow(text) + "\tAccessed address " + locatedAt
    error2 += ":\n" + parseTrace(frameTrace) # + "\n\t" + frameBody
    return [(accessFile, line, error + error2, createInjectVarsLambda(accessFile, line, error, error2))]

def regexHeapUseAfterFree(text):
    heapUseLocatedAtPattern = re.compile(freedAllocatedPattern+summaryFilePattern)
    locatedAt, freedByThread, freedByThreadTrace, previouslyAllocated, previouslyAllocatedTrace, accessFile, line =\
        re.findall(heapUseLocatedAtPattern, text)[0]
    error = "Heap use after free"
    error2 = createSecondError(accessFile, line)
    error2 += parseOverflow(text) + "\tAccessed address " + locatedAt +", "+ freedByThread
    error2 += "\n" + parseTrace(regexTrace(freedByThreadTrace)) + "\t" + "P"+previouslyAllocated[1:] + "\n" + parseTrace(regexTrace(previouslyAllocatedTrace))
    return [(accessFile, line, error + error2, createInjectVarsLambda(accessFile, line, error, error2))]

def regexSummary(summary, trace):
    regexpedSummary = re.findall(summaryFilePattern, summary)
    if regexpedSummary:
        accessFile, line = regexpedSummary[0]
    else:
        accessFile, line = trace[0][2], trace[0][3]
    return accessFile, line

def regexSegmentationFault(text):
    segTrace = regexTrace(text)
    accessFile, line = regexSummary(text,segTrace)
    error = "Segmentation fault"
    error2 = createSecondError(accessFile, line)
    error2 += " at:\n" + parseTrace(segTrace)
    return [(accessFile, line, error + error2, createInjectVarsLambda(accessFile, line, error, error2))]


def regexMemoryLeaks(text, summary):
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
    uninitializedMemoryPattern = re.compile(r'((?:.|\n)*?)\n\n(.*)((?:.|\n)*?)\n\n')
    useBody, uninitValue, allocatedBody = re.findall(uninitializedMemoryPattern,text)[0]
    error = "Use of uninitialized value"
    useTrace, allocatedTrace = regexTrace(useBody), regexTrace(allocatedBody)

    accessFile, line = regexSummary(summary,useTrace)
    error2 = createSecondError(accessFile, line)
    error2 += "\n\tUsed at:\n" + parseTrace(useTrace)
    error2 += "\tAllocated at:\n" + parseTrace(allocatedTrace)
    return [(accessFile, line, error + error2, createInjectVarsLambda(accessFile, line, error, error2))]


def regexDoubleFree(text):
    doubleFreePattern = re.compile(addressPattern+r' (in thread [A-Za-z0-9]+:)((?:.|\n)*)\1 '+freedAllocatedPattern+r'SUMMARY:')
    address, doubleFreeInThread, doubleFreeBody, locatedAt, originalFreeByThread, originalFreeBody,\
        previouslyAllocated, previouslyAllocatedBody = re.findall(doubleFreePattern, text)[0]

    doubleFreeTrace, originalFreeTrace, previouslyAllocatedTrace = \
        regexTrace(doubleFreeBody), regexTrace(originalFreeBody), regexTrace(previouslyAllocatedBody)

    accessFile, line = doubleFreeTrace[0][2], doubleFreeTrace[0][3]
    error = "Double free of memory"
    error2 = createSecondError(accessFile, line)
    error2 += "\n\tAttempted double free " + doubleFreeInThread + "\n" + parseTrace(doubleFreeTrace)
    error2 += "\tFreed address " + locatedAt +", already " + originalFreeByThread +"\n" + parseTrace(originalFreeTrace)
    error2 += "\t" + "P" + previouslyAllocated[1:] + "\n" + parseTrace(previouslyAllocatedTrace)
    return [(accessFile, line, error + error2, createInjectVarsLambda(accessFile, line, error, error2))]

def regexUseAfterReturn(text):
    stackLocatedAtPattern = re.compile(locatedAtStackPattern)
    locatedAt, frameTraceBody, frameBody, accessFile, line = re.findall(stackLocatedAtPattern, text)[0]
    frameTrace = regexTrace(frameTraceBody)
    error = "Memory use after function return"
    error2 = createSecondError(accessFile, line)
    error2 += parseOverflow(text) + "\tAccessed address " + locatedAt +":\n"
    error2 +=  parseTrace(frameTrace)  # + "\n\t" + frameBody
    return [(accessFile, line, error + error2, createInjectVarsLambda(accessFile, line, error, error2))]