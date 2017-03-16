import re
import os
import glob
def sanitize():
    onlyfiles, sanitizerDir = [], "/task/student/sanitizer"
    try:
        os.chdir(sanitizerDir)
        for file in glob.glob("*.log"):
            if os.path.isfile(file):
                onlyfiles.append(file)
            else:
                print("scenario memory log file path is wrong:" + file)
    except:
        print("Directory " + sanitizerDir + " doesn't exist.")


    runtimeErrorList = {}
    for file in onlyfiles:

        with open(file, 'r') as fin:

            read_file = fin.read()
            pattern = re.compile(r'(?:WARNING|ERROR): [A-Za-z]+Sanitizer: (detected memory leaks|[A-Za-z-]+)((?:[\n]|.)+?(?:SUMMARY|ABORTING).*)')
            generalFilePattern = re.compile(
                r'(SUMMARY:|Direct leak|allocated by thread|Uninitialized value was created by a heap allocation|freed by thread|previously allocated by thread|READ)(?:.|\n)*?\/([a-zA-Z-_ ]+.(?:cpp|c)):([0-9]+)')
            for (warning,body) in re.findall(pattern,read_file):
                identifierPattern, filePattern = None, generalFilePattern
                if warning == "global-buffer-overflow":
                    identifierPattern = re.compile(r'(?:global variable \')([a-zA-Z0-9-_]+)')
                elif warning == "stack-buffer-overflow":
                    identifierPattern = re.compile(r'\'(.+?)\' <==')
                elif warning == "heap-use-after-free":
                    filePattern = re.compile(r'(freed by thread|previously allocated by thread|READ)(?:.|\n)*?\/([a-zA-Z-_ ]+.(?:cpp|c)):([0-9]+)')
                if identifierPattern is not None:
                    identifier = re.search(identifierPattern,body).group(1)
                else:
                    identifier = None

                for (extraInfo,codefile, line) in re.findall(filePattern,body):
                    if not runtimeErrorList.has_key((codefile,line)):
                        runtimeErrorList[(codefile,line)]=(warning+", "+extraInfo,identifier,{file}) \
                            if extraInfo != "SUMMARY:" else (warning,identifier,{file})
                    else:
                        runtimeErrorList[(codefile,line)][2].add(file)
                    #result = re.search(pattern,read_file)
    return runtimeErrorList

