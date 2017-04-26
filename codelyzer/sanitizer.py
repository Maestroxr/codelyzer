import re
import os
import glob

runtimeErrorList = {}
onAddressPattern = r'(on address )(0x[0-9a-z]+)(?:.|\n)*(READ|WRITE)( of size [0-9]+ at)((?:.|\n)*)\2'
pattern = r'(?:==[0-9]+==.+Sanitizer: )(detected memory leaks|SEGV on unknown address|'\
                     r'global-buffer-overflow|use-of-uninitialized-value|heap-use-after-free|'\
                     r'stack-buffer-overflow|heap-buffer-overflow)((?:[\n]|.)+)(?:(SUMMARY.*)|ABORTING)'
fileLinePattern = r'([a-zA-Z-_ 0-9]+\.(?:cpp|c)):([0-9]+)'
summaryFilePattern = r'SUMMARY:(?:.|\n)*?'+fileLinePattern
def sanitize(sanitizerDir, sanitizerFile):
    onlyfiles = []
    if sanitizerFile != "None":
        onlyfiles = [sanitizerDir+"\\"+sanitizerFile]
    else:
        try:
            os.chdir(sanitizerDir)
            for file in glob.glob("*.log"):
                if os.path.isfile(file):
                    onlyfiles.append(file)
                else:
                    print("scenario memory log file path is wrong:" + file)
        except:
            print("Directory " + sanitizerDir + " doesn't exist.")
            return runtimeErrorList

    for file in onlyfiles:
        with open(file, 'r') as fin:
            read_file = fin.read()
            for (warning,body,summary) in re.findall(pattern,read_file):
                if warning == "global-buffer-overflow":
                    addRuntimeErrors(file,grepGlobalBufferOveflow(body))

                elif warning == "stack-buffer-overflow":
                    addRuntimeErrors(file, grepStackBufferOverflow(body))

                elif warning == "heap-buffer-overflow":
                    addRuntimeErrors(file, grepHeapBufferOveflow(body))

                elif warning == "heap-use-after-free":
                    addRuntimeErrors(file, grepHeapUseAfterFree(body))

                elif warning == "SEGV on unknown address":
                    addRuntimeErrors(file, grepSegmentationFault(body))

                elif warning == "detected memory leaks":
                    addRuntimeErrors(file, grepMemoryLeaks(body,summary))

                elif warning == "use-of-uninitialized-value":
                    addRuntimeErrors(file, grepUninitializedMemoryUse(body, summary))

    return runtimeErrorList

def addRuntimeErrors(logfile, errorList):
    global runtimeErrorList
    for errorfile, line, error, injectVars  in errorList:
        if not runtimeErrorList.has_key((errorfile, line)):
            runtimeErrorList[(errorfile, line,error)] = (injectVars, {logfile})
        else:
            runtimeErrorList[(errorfile, line)][2].add(logfile)


def grepTrace(text):
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
    atTrace = grepTrace(body)
    overflow = "\n\tWas accessed by " + "read" if readWrite == "READ" else "write"
    overflow += ofSize1 + ":\n" + parseTrace(atTrace)
    return overflow

def grepGlobalBufferOveflow(text):

    globalLocatedAtPattern = re.compile(r'(is located [0-9]+ bytes to the right of global variable \'([0-9a-zA-Z]+)\''
                         r' from \'([a-zA-Z-_ ]+.(?:cpp|c))\') (?:\(0x[0-9a-z]+\)) (of size [0-9]+)(?:.|\n)*'+summaryFilePattern)

    locatedAt, identifier, originFile, ofSize2, accessFile, line = re.findall(globalLocatedAtPattern,text)[0]
    error = "Global variable buffer overflow, '"+identifier +"' from file "+originFile+parseOverflow(text)+ "\n\tAccessed address "+locatedAt + ",\n\t" +ofSize2
    return [(accessFile,line , error, None)]


def grepHeapBufferOveflow(text):
    heapLocatedAtPattern = re.compile(r'(is located [0-9]+ bytes to the right of )((?:[0-9]+).*region)((?:.|\n)*)SUMMARY:(?:.|\n)*?([a-zA-Z-_ ]+.(?:cpp|c)):([0-9]+)')
    locatedAt, ofSize2, body, accessFile, line = re.findall(heapLocatedAtPattern, text)[0]
    allocatedAtTrace = grepTrace(body)
    error = "Heap buffer overflow"
    error2= parseOverflow(text) + "\n\tAccessed address "+locatedAt  +ofSize2
    error2 += ", allocated at:\n" + parseTrace(allocatedAtTrace)
    return [(accessFile, line, error + error2, lambda vars: error + ", suspect variables: " + vars + error2)]

def grepStackBufferOverflow(text):
    stackLocatedAtPattern = re.compile(
        r'(is located in stack of thread [A-Za-z0-9]+ at offset [0-9]+ in frame)((?:.|\n)*)(This frame (?:.|\n)*)HINT:(?:.|\n)*?([a-zA-Z-_ ]+.(?:cpp|c)):([0-9]+)')
    locatedAt, frameTraceBody, frameBody, accessFile, line = re.findall(stackLocatedAtPattern, text)[0]
    frameTrace = grepTrace(frameTraceBody)
    error = "Stack buffer overflow"
    error2 = parseOverflow(text) + "\n\tAccessed address " + locatedAt
    error2 += ":\n" + parseTrace(frameTrace) # + "\n\t" + frameBody
    return [(accessFile, line, error + error2, lambda vars: error + ", suspect variables: " + vars + error2)]

def grepHeapUseAfterFree(text):
    heapUseLocatedAtPattern = re.compile(
        r'(is located [A-Za-z0-9]+ bytes inside of [0-9a-z-]+ region)(?:(?:.|\n)*)(freed by thread [A-Z0-9]+ here:)((?:.|\n)*)(previously allocated by thread [A-Z0-9]+ here:)((?:.|\n)*)SUMMARY:(?:.|\n)*?([a-zA-Z-_ ]+.(?:cpp|c)):([0-9]+)')
    locatedAt, freedByThread, freedByThreadTrace, previouslyAllocated, previouslyAllocatedTrace, accessFile, line = re.findall(heapUseLocatedAtPattern, text)[0]
    error = "Heap use after free"
    error2 = parseOverflow(text) + "\n\tAccessed address " + locatedAt +", "+ freedByThread
    error2 += "\n" + parseTrace(grepTrace(freedByThreadTrace)) + "\n\t" + previouslyAllocated + "\n" + parseTrace(grepTrace(previouslyAllocatedTrace))
    return [(accessFile, line, error + error2, lambda vars: error + ", suspect variables: " + vars + error2)]

def grepSummary(summary, trace):
    greppedSummary = re.findall(summaryFilePattern, summary)
    if greppedSummary:
        accessFile, line = greppedSummary[0]
    else:
        accessFile, line = trace[0][2], trace[0][3]
    return accessFile, line

def grepSegmentationFault(text):
    segTrace = grepTrace(text)
    accessFile, line = grepSummary(text,segTrace)
    error = "Segmentation fault"
    error2 = " at:\n" + parseTrace(segTrace)
    return [(accessFile, line, error + error2, lambda vars: error + ", suspect variables: " + vars + error2)]


def grepMemoryLeaks(text, summary):
    memoryLeakPattern = re.compile(r'(Direct leak of [0-9]+ byte\(s\) in [0-9]+ object\(s\) allocated from:)((?:.|\n)*?)\n\n')
    errorList = []
    for directLeak, leakBody in re.findall(memoryLeakPattern,text):
        error = "Detected memory leaks"
        leakTrace = grepTrace(leakBody)
        error2 = "\n"+parseTrace(leakTrace)
        accessFile, line = leakTrace[0][2], leakTrace[0][3]
        errorList.append((accessFile, line, error + error2, lambda vars: error+ ", suspect variables: " + vars + error2))
    #errorList.append((accessFile,1,summary, None))
    return errorList

def grepUninitializedMemoryUse(text, summary):
    uninitializedMemoryPattern = re.compile(r'((?:.|\n)*?)\n\n(.*)((?:.|\n)*?)\n\n')
    errorList = []
    useBody, uninitValue, allocatedBody = re.findall(uninitializedMemoryPattern,text)[0]
    error = "Use of uninitialized value"
    useTrace, allocatedTrace = grepTrace(useBody), grepTrace(allocatedBody)
    error2 = "\n\tUsed at:\n"+parseTrace(useTrace)
    error2 += "\n\tAllocated at:\n"+parseTrace(allocatedTrace)
    accessFile, line = grepSummary(summary,useTrace)
    errorList.append((accessFile, line, error + error2, lambda vars: error+ ", suspect variables: " + vars + error2))

    return errorList
