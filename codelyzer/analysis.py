"""
This module is responsible for analyzing c code.
A pushdown automaton is used in order to analyze the code.
Three passes are made on the code:
    First pass - in this pass tokens of code are pushed into the stack of the pushdown automaton, one stack at a time.
    Second pass - in this pass tokens of code are  popped out of the stack of the pushdown automaton, one stack at a time.
    Third pass - in this pass we analyze the code structure in order to determine whether it's a function or a control
        structure such as if, for, while and so on.
After all passes are done the sanitizer runs, using data gathered from the three passes.


Attributes:
    uppercasePattern (_sre.SRE_Pattern): This is a regular expression pattern, which is used to check for variables
        having all characters in uppercase and having an undrscore between words.
    camelCasePattern (_sre.SRE_Pattern): This is a regular expression pattern, which is used to check for camel case
        in variable names.
    fileInfoDict (dict): This dictionary stores all data gathered for each file of code.

Todo:
    * Interleave passes one and three, rendering functionalyze obsolete.
"""

import os
import re
import operator
import vera
from codelyzer.stack_push import pushInitializationStack
from codelyzer.stack_pop import popInitializationStack
from codelyzer.functionalyze import functionalyze
from codelyzer.sanitizer import sanitize

uppercasePattern = re.compile("^[A-Z][A-Z0-9_]*[A-Z0-9]$")
camelCasePattern = re.compile("[^$a-zA-Z0-9]")
fileInfoDict = {}

def veraAnalysis():
    """
    This is the main function of the analysis tool, it runs in a loop on all code files, and for each code file
    iterated it runs the above mentioned three passes sequentially.
    Subsequently, it then continues to check identifier naming conventions such as upper case and camel case,
    concluding with two more convention checks.
    """
    sourceFiles = vera.getSourceFileNames()

    for fileName in sourceFiles:
        stackStateList = pushInitializationStack(fileName)
        stackStateList = stackStateList[::-1]
        #printStack = [(stackState[1],[(t.type,t.value,t.line) for t in stackState[0]]) for stackState in stackStateList]
        #print(printStack)

        infoDict = popInitializationStack(fileName, stackStateList)
        fileInfoDict[fileName] = infoDict
        infoDict["funcDict"].update(functionalyze(fileName, infoDict))

        # defines need to be checked for uppercase
        checkUppercaseUnderscore(fileName, infoDict["defineDict"], "#define")
        # const identifiers need to be checked for uppercase
        checkUppercaseUnderscore(fileName, infoDict["constDict"], "const variable")
        nonConstVarDict = {k: v for k, v in infoDict["varDict"].items() if k not in infoDict["constDict"]}
        # non const variables need to be checked for camelCase
        checkCamelCase(fileName, nonConstVarDict)
        # functions need to be checked for camelCase
        checkCamelCase(fileName, infoDict["funcDict"])

        isPointerMissingNullCheck(fileName, infoDict["mallocDict"])
        isVarBeforeFirstFunction(infoDict["funcDict"], infoDict["varDict"],infoDict["typeDict"], fileName)



def sanitizerAnalysis(sanirizerDir,sanitizerFile):
    """
    This function analyses memory errors produced by the address, leak and memory sanitizers.
    Initially the function calls sanitize from sanitizer.py, recieving the list of errors regexed from the report.
    Later two attempts are made incase the identifier is missing from the report, once to load current knowledge
    of identifiers and in case the identifier doesn't appear in the current knowledge another run is made on the file
    to populate all identifiers.
    :param sanirizerDir: The directory from which to load the sanitizer reports.
    :param sanitizerFile: A sanitizer report file, if "None" then all rports are scanned.
    """
    runtimeErrorList= sanitize(sanirizerDir, sanitizerFile)
    pointerLineDict = {}
    fileNameOnly = { os.path.basename(k):k for k,v in fileInfoDict.items()}
    for (file, line, error), (injectVars, appearsInFiles) in runtimeErrorList.iteritems():
        if file not in fileInfoDict:
            if file not in fileNameOnly:

                return
            file = fileNameOnly[file]
        line, identifiers = int(line), None


        if injectVars is not None:
            populateIdentifierLines(file, pointerLineDict)
            if not (pointerLineDict.has_key(file) and pointerLineDict[file].has_key(line)):
                lookupRecurrentIdentifiers(file, pointerLineDict)
            if pointerLineDict.has_key(file) and pointerLineDict[file].has_key(line):
                identifiers = pointerLineDict[file][line]
                error =  injectVars(identifiers.keys())
        scenariosString = "Memory:"+"["+",".join([os.path.splitext(scen)[0] for scen in sorted(appearsInFiles)])+"] "

        error = scenariosString+error + ":MemoryEnd:"

        vera.report(file, line, error)





def checkUppercaseUnderscore(file, dic,errorPrefix):
    """
    Checks if the given dictionary(String,Token) contains identifiers
    that need to conform to UPPERCASE_WITH_UNDERSCORE.
    :param file: File to check.
    :param dic: Dictionary with identifiers that need to conform.
    :param errorPrefix: Add this to the beginning of error.
    """

    for k, v in dic.iteritems():
        result = re.search(uppercasePattern,k)
        if result == None:
            vera.report(file,v.line,errorPrefix+" "+k+" name isn't UPPERCASE_WITH_UNDERSCORE.")


def checkCamelCase(fileName,dic):
    """
    Checks if the given dictionary(String,Token) contains identifiers that need to conforom
    to lowerCamelCase, meaning they need to start with either a lowercase letter, or two or more
    uppercase letters.
    :param file: File to check.
    :param dic: Dictionary with identifiers that need to conform.
    """
    for k, v in dic.iteritems():
        result = re.findall(camelCasePattern, k)
        if result is None:
            vera.report(fileName, v.line,"Bad char(s) " + str(result) + " used for identifier " + k + ".")
        result = re.search("^([A-Z]{2,}|[a-z])",k)

        if result is None:
            vera.report(fileName, v.line,
                        "Identifier name does not conform to camelCase ,"
                        " can't start with digit or one capital letter in identifier " + v.value + ".")

        #if len(k) == 1 and k not in ["x", "y", "z", "m", "n", "k", "i", "j", "r","c","p"]:
          #  vera.report(fileName, v.line, "A non-approved single char used for identifier  " + k + ".")


def isPointerMissingNullCheck(fileName, mallocDict):
    """
    We make a pass on the malloc dictionary to check if the malloc count is larger than zero, meaning
    not every malloc allocation we encountered, has a corresponding malloc null check.
    :param fileName: File to check.
    :param mallocDict: Dictionary with mallocs that need to conform.
    """
    for k, v in mallocDict.iteritems():
        for malloc in v:
            vera.report(fileName, malloc.line,
                        "Pointer's '" + k + "' malloc is missing null pointer check.")


def isVarBeforeFirstFunction(funcs, vars, types, fileName):
    """
    This function adheres to variables not appearing before the first function.
    :param funcs: The functions dictionary.
    :param vars: The vaiablles dictionary.
    :param types: The types dictionnay.
    :param fileName: The file that is being checked.
    :return:
    """
    globalVars = [token for identifier, token in vars.items() if types[identifier][0].column == 0]
    if not globalVars or not funcs:
        return
    firstFunc = min([f for f in funcs.values()],key = operator.attrgetter('line'))
    firstVar = min(globalVars, key= operator.attrgetter('line'))
    if firstVar.line > firstFunc.line:
        vera.report(fileName, firstVar.line, "Global variable '" + firstVar.value +
                "' appears after the first function "+firstFunc.value+".")




def addDictionaryIdentifiers(dict,file, pointerLineDict):
    """
    This function adds identifiers to the pointer line dictionary, thus populating the dictionary, hence
    making available the information gathered.
    :param dict: The dictionary the tokens are taken from.
    :param file: The file that is being acted upon.
    :param pointerLineDict: The pointer line dictionary.
    """
    for identifierK, identifierV in dict.iteritems():
        if identifierV.line not in pointerLineDict[file]:
            pointerLineDict[file][identifierV.line] = {}
        pointerLineDict[file][identifierV.line][identifierV.value] = identifierV


def populateIdentifierLines(file, pointerLineDict):
    """
    This function populates the identifiers' lines, by utilizing the data comprehended upon the three-pass run.
    :param file: The file acted upon.
    :param pointerLineDict: The pointer line dictionary.
    """
    if pointerLineDict.has_key(file) or file not in fileInfoDict:
        return
    pointerLineDict[file] = {}
    infoDict = fileInfoDict[file]
    constDict, varDict, mallocDict = infoDict["constDict"], infoDict["varDict"], infoDict["mallocDict"]
    mallocDict = {identifier:varDict[identifier] for identifier,mallocList in mallocDict.iteritems()}
    addDictionaryIdentifiers(mallocDict,file,pointerLineDict)
    addDictionaryIdentifiers(varDict,file,pointerLineDict)
    addDictionaryIdentifiers(constDict,file,pointerLineDict)


def lookupRecurrentIdentifiers(file, pointerLineDict):
    """
    Upon data deficiency in the sanitation run a supplemental attempt is made to gather lines information,
    in which the former line data held by the dictionary is added upon by the supplemental run which will add to it.
    :param file: The file acted upon.
    :param pointerLineDict: The pointer line dictionary.
    """
    if file not in fileInfoDict: return
    infoDict = fileInfoDict[file]
    constDict, varDict, mallocDict = infoDict["constDict"], infoDict["varDict"], infoDict["mallocDict"]
    identifierMap = dict(mallocDict)
    identifierMap.update(varDict)
    identifierMap.update(constDict)
    for t in vera.getTokens(file,1, 0, -1, -1,["identifier"]):
        if t.value in identifierMap.keys():
            if not pointerLineDict[file].has_key(t.line):
                pointerLineDict[file][t.line] = {}
            pointerLineDict[file][t.line][t.value] = t

