"""
This module is responsible for keeping track of control structures, finding functions and several
other errors reporting.
"""
import vera

START, CONTROL, EXPECTED_BLOCK, BLOCK, EXPECTED_IDENTIFIER, EXPECTED_SEMICOLON = range(6)
ANY, ONE, TWO = range(4, 7)

controlState,  functionState = START, START
functionary, flags = {}, {}
parenCount, braceCount, returnCount, controlParenCount = 0, 0, 0, 0
controlToken, prev, lastReturn, lastSemicolon, identifier, controlIdentifier = None, None, None, None, None, None
types = {"int", "char", "void", "float", "double"}
functionalyzeTokenTypes = {"for", "while", "do", "else", "if", "equal", "notequal", "not", "leftparen", "rightparen",
                           "leftbrace", "rightbrace", "semicolon", "identifier", "return", "struct"} | types
controlTokenTypes = {"for", "if", "while", "do", "else", "leftparen", "rightparen", "leftbrace", "rightbrace",
                     "semicolon","not"}

def handleToken(t, fileName):
    """
    This functions handle the current token.
    It also checks for main function appearing before struct defintion and more than one semicolon per line.
    :param t: The token handled.
    :param fileName: The file name.
    :return:
    """
    global parenCount, braceCount, returnCount, lastReturn, controlParenCount, controlState, controlToken, \
        functionary, flags, lastSemicolon
    if t.type == "leftparen":
        parenCount += 1

    elif t.type == "rightparen":
        parenCount -= 1

    elif t.type == "leftbrace":
        braceCount += 1

    elif t.type == "rightbrace":
        braceCount -= 1
        if braceCount == 0:
            flags.pop("struct", None)
            returnCount, lastReturn = 0, None

    elif t.type == "for" or t.type == "if":
        controlParenCount = 0
        controlState = CONTROL
        controlToken = t

    elif t.type == "do" or t.type == "else":
        controlState = EXPECTED_BLOCK

    elif t.type == "while" and prev != "rightbrace":
        controlParenCount = 0
        controlState = CONTROL
        controlToken = t

    elif t.type == "return":
        returnCount += 1
        if returnCount > 1:
            vera.report(fileName, t.line,
                        "Only one 'return' token should be used in a function. Found another in line:" + str(
                            lastReturn.line))
        lastReturn = t

    elif t.type == "struct" and braceCount == 0:
        if functionary.has_key("main"):
            vera.report(fileName, t.line,
                        "Main function appears before struct defintion. struct is at line " + str(t.line) + \
                        " , main appeared at line " + str(functionary["main"].line) + ".")
        flags["struct"] = t

    elif t.type == "semicolon" and "forState" not in flags:
        if lastSemicolon != None and t.line == lastSemicolon.line:
            vera.report(fileName, t.line,
                        "More than one semicolon cannot appear in the same line unless in an if statement.")
        lastSemicolon = t

def isBefore(first,second):
    """
    Checks if first token is before second.
    :param first: First token.
    :param second: Second token.
    :return: True if before, else False.
    """
    return first.line < second.line or (first.line == second.line and first.column < second.column)



def handleControl(t, fileName, infoDict):
    """
    This function handles a control token.
    It also checks for legal lhs = rhs operations, for loops having all three loop arguments
    and control structures having full blocks.
    :param t: The control token.
    :param fileName: The file name.
    :param infoDict: The information dictionary.
    """
    global controlState, controlParenCount, controlToken, flags, prev, controlIdentifier
    constDict, mallocDict, varDict, defineDict, typeDict = infoDict["constDict"], infoDict["mallocDict"], infoDict["varDict"], \
                                                 infoDict["defineDict"], infoDict["typeDict"]
    if controlState == CONTROL:
        if t.type == "leftparen":
            controlParenCount += 1

        elif t.type == "rightparen":
            controlParenCount -= 1
            if controlParenCount == 0:
                controlState = EXPECTED_BLOCK
                if controlToken.type == "for" and flags["forIdentifiers"] < 3:
                    vera.report(fileName, controlToken.line,
                                "For loops must have all three loop arguments present.")
                controlIdentifier, controlToken, flags = None, None, {}
        if controlToken != None:
            if controlToken.type == "if":
                if t.type == "equal" or t.type == "notequal":
                    flags["equal"] = t

                elif t.type == "identifier":

                    if prev == "not" and t.value in mallocDict and mallocDict[t.value]:
                        malloc = mallocDict[t.value][0]
                        if isBefore(malloc, t):
                            mallocDict[t.value].pop(0)

                    elif "equal" in flags and controlIdentifier != None:
                        rhs = None
                        if constDict.has_key(t.value):
                            rhs = constDict[t.value]
                        if rhs == None and defineDict.has_key(t.value):
                            rhs = defineDict[t.value]
                        if varDict.has_key(controlIdentifier.value) and typeDict[controlIdentifier.value][0].type != "const" and rhs != None:
                            vera.report(fileName, t.line,
                                        "Equality checking '" + controlIdentifier.value + " == " + rhs.value + "' with "
                                             "left-hand side argument as variable and right-hand side as const or #define.")
                        if t.value == "NULL" and controlIdentifier.value in mallocDict and mallocDict[controlIdentifier.value]:
                            malloc = mallocDict[controlIdentifier.value][0]
                            if isBefore(malloc, controlIdentifier):
                                mallocDict[controlIdentifier.value].pop(0)
                        elif controlIdentifier.value == "NULL" and t.value in mallocDict and mallocDict[t.value]:
                            malloc = mallocDict[t.value][0]
                            if isBefore(malloc, t):
                                mallocDict[t.value].pop(0)
                        controlIdentifier = None
                        del flags["equal"]

                    elif controlIdentifier is None:
                        controlIdentifier = t

            elif controlToken.type == "for":
                if "forState" not in flags:
                    flags["forState"] = EXPECTED_IDENTIFIER
                    flags["forParenthesis"] = controlParenCount + 1
                    flags["forIdentifiers"], flags["forSemicolons"] = 0, 0
                if t.type == "identifier" and flags["forState"] == EXPECTED_IDENTIFIER:
                    flags["forState"] = EXPECTED_SEMICOLON
                    flags["forIdentifiers"] += 1

                elif t.type == "semicolon":
                    controlIdentifier = None
                    if flags["forState"] == EXPECTED_IDENTIFIER:
                        vera.report(fileName, t.line, "For loops must have all three loop arguments present.")

                    elif flags["forState"] == EXPECTED_SEMICOLON:
                        flags["forSemicolons"] += 1
                        flags["forState"] = EXPECTED_IDENTIFIER

    elif controlState == EXPECTED_BLOCK and t.type in controlTokenTypes:
        if prev == "else" and t.type == "if":
            pass

        elif t.type != "leftbrace" and t.type != "else":
            vera.report(fileName, t.line, "Full block {} expected in the control structure.")
        controlState = BLOCK
    prev = t.type if t.type in controlTokenTypes | {"identifier"} else prev


def handleFunction(t, constDict):
    """
    This function handles the identification of function statements, and keeps track of all functions.
    :param t: The current token.
    :param constDict: The constant variables dictionary.
    """
    global functionState, identifier, functionary
    if functionState == START and t.type in types and not constDict.has_key(t.value):
        functionState, type = ANY, t

    elif functionState == ANY and t.type == "identifier":
        identifier, functionState = t, ONE

    elif functionState == ONE and t.type == "leftparen":
        functionState = TWO

    elif functionState == TWO and t.type in {"leftbrace", "rightparen", "identifier", "star"} | types:
        if t.type == "leftbrace" and parenCount == 0:
            functionary[identifier.value], functionState = identifier, START

    else:
        functionState, identifier = START, None


def functionalyze(fileName, infoDict):
    """
    This function embodies the third pass, keeping track of functions, control structures and special token
     patterns.
    :param fileName: The file name.
    :param infoDict: The information dictionary.
    """
    constDict, mallocDict, varDict, defineDict = infoDict["constDict"], infoDict["mallocDict"],\
                                                            infoDict["varDict"], infoDict["defineDict"]
    global parenCount, braceCount, returnCount, lastReturn, controlParenCount, controlState, controlToken, \
        functionary, flags, lastSemicolon, identifier
    controlState,  functionState = START, START
    functionary, flags = {}, {}
    parenCount, braceCount, returnCount, controlParenCount = 0, 0, 0, 0
    controlToken, prev, lastReturn, lastSemicolon, identifier = None, None, None, None, None

    for t in vera.getTokens(fileName, 1, 0, -1, -1, list(functionalyzeTokenTypes)):
        handleToken(t, fileName)
        handleControl(t, fileName, infoDict)
        handleFunction(t, constDict)
    return functionary

