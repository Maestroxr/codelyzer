#!/usr/bin/python
# variable, define, function naming
import re
from codelyzer.sanitizer import sanitize
import operator
import vera


START, CONTROL, EXPECTED_BLOCK, BLOCK, EXPECTED_IDENTIFIER, EXPECTED_SEMICOLON = range(6)
ANY, ONE, TWO = range(4, 7)

literals = {"intlit", "stringlit", "charlit"}
types = {"int", "char", "void", "float", "double"}
functionalyzeTokenTypes = {"for", "while", "do", "else", "if", "equal", "notequal", "not", "leftparen", "rightparen",
                           "leftbrace", "rightbrace", "semicolon", "identifier", "return", "struct"} | types
controlTokenTypes = {"for", "if", "while", "do", "else", "leftparen", "rightparen", "leftbrace", "rightbrace",
                     "semicolon","not"}

operators = { "plus", "plusplus","notequal", "minus", "minusminus", "less", "greater", "greaterequal"}
assignOperators = { "assign" , "percentassign", "minusassign", "plusassign" }
stackContinueTokens = {"star", "identifier", "leftbracket", "rightbracket", "malloc", "leftbrace","comma",
                  "rightbrace", "int", "char", "leftparen", "rightparen", "identifier","arrow","dot", "not",
                       "const"}  | literals | types | operators | assignOperators
stackConsiderTokens = { "leftbracket", "rightbracket", "identifier", "assign", "intlit", "charlit", "stringlit", "comma",
                       "semicolon", "leftbrace", "rightbrace", "leftparen", "rightparen", "star", "arrow", "dot", "not",
                       "for", "if","while", "switch", "struct", "const", "pp_define", "newline"} | types | operators
fileInfoDict = {}
libFunctions = { "strlen","fgets","strcmp" }
recursiveTokenNames = {"rightbracket" : "leftbracket" , "rightbrace" : "leftbrace", "rightparen" : "leftparen"}
recursiveTokenLiterals = { "rightbracket" : "]", "leftbracket" : "[", "rightbrace" : "}", \
                           "leftbrace" : "{", "rightparen" : ")", "leftparen" : "(" }
uppercasePattern = re.compile("^[A-Z][A-Z0-9_]*[A-Z0-9]$")
camelCasePattern = re.compile("[^$a-zA-Z0-9]")

"""
----Functionalyze global area:-----------------------------------------------------------
"""
controlState,  functionState = START, START
functionary, flags = {}, {}
parenCount, braceCount, returnCount, controlParenCount = 0, 0, 0, 0
controlToken, prev, lastReturn, lastSemicolon, identifier, controlIdentifier = None, None, None, None, None, None
"""
-----------------------------------------------------------------------------------------
"""


def pushFirstToken(stack, state, t):
    if t.type in types:
        state["type"] = [t]
        stack.append(t)

    elif t.type == "leftparen":
        stack.append(t)

    elif t.type == "identifier":
        if t.value in types:
            state["type"] = [t]

        else:
            state["identifier"] = t
        stack.append(t)

    elif t.type in ["for", "if", "while", "switch"]:
        state["control"] = t
        state["leftParen"] = 0

    elif t.type == "struct":
        state["struct"] = t

    elif t.type == "const":
        state["const"] = t

    elif t.type == "pp_define":
        state["define"] = t


def pushSemicolon(stack, stackList, state, t):
    if "struct" in state:
        state["type"] = [state["struct"]] + state["type"]
    stack.append(t)
    stackList.append((stack, state))
    if "control" not in state:
        state, stack = {}, []

    else:
        stack = []
    return stack, state


def pushContinueToken(functionOrControl, stack, state, t):
    maybeTypeToken = "assign" not in state and "dereference" not in state and "type" not in state and not functionOrControl
    if t.type == "assign":
        state["assign"] = t

    elif t.value in types and maybeTypeToken:
        state["type"] = [t]

    elif t.type == "identifier":
        if t.value == "malloc":
            state["malloc"] = t

        elif "identifier" not in state:
            if "const" in state and maybeTypeToken:
                state["type"] = t

            else:
                state["identifier"] = t

        elif maybeTypeToken:
            state["type"] = [state["identifier"]]
            state["identifier"] = t

    elif t.type == "star" and "type" in state:
        if not "identifier" in state:
            state.setdefault("typeStars", [[]])
            state["typeStars"][-1] += [t]

        elif "comma" in state:
            state.setdefault("commaStars", [[]])
            state["commaStars"][-1] += [t]

    elif t.type in ["arrow", "dot"] and "assign" not in state:
        state["dereference"] = t

    elif t.type == "comma":
        if "comma" not in state:
            state.setdefault("comma", t)
        if "commaStars" in state and state["commaStars"] and state["commaStars"][-1]:
            state["commaStars"].append([])
    stack.append(t)


def pushControlToken(stack, stackList, state, t):
    forLoop = "control" in state and state["control"].value == "for"
    if t.type == "leftparen":
        if not forLoop or state["leftParen"] != 0:
            stack.append(t)
        state["leftParen"] += 1

    elif t.type == "rightparen":
        state["leftParen"] -= 1
        if not forLoop or state["leftParen"] != 0:
            stack.append(t)

    else:
        stack.append(t)

    if state["leftParen"] == 0:
        stackList.append((stack, state))
        state, stack = {}, []

    return stack, state


def pushInitializationStack(fileName):
    """
        This phase uses a pushdown automaton in order to keep track of the current state
        that is now being loaded into the stack.
    """
    state, stack, stackList = {}, [], []
    checkBreakLine = set(["leftparen", "leftbrace","rightparen"])
    prev = None
    for t in vera.getTokens(fileName, 1, 0, -1, -1, list(stackConsiderTokens)):
        #print("state:" + str(state) + " value:" + t.value + " type:" + t.type + " line:" + str(t.line))
        # print("stack:"+str([(token.type, token.value, token.line) for token in stack]))
        if not state:
            pushFirstToken(stack, state, t)

        elif "define" in state:
            stack.append(t)
            if t.type == "identifier" and "identifier" not in state:
                state["identifier"] = t

            elif t.type == "newline":
                stackList.append((stack, state))
                state, stack = {}, []

        elif t.type == "newline":
            continue

        else:
            if t.type in ["leftbracket","leftparen", "leftbrace"]:
                if "recursive" not in state and "assign" not in state:
                    state["recursive"] = t
                    if t.type == "leftparen" and "control" not in state:
                        state["function"] = state.pop("identifier")
                        state["leftParen"] = 0
            #This variable signifies the fact that the first control token encountered out of [,(,{ is not '('
            # because that would mean it is either if/for/while/function
            functionOrControl = "recursive" in state and state["recursive"].type == "leftparen"
            isArray = "recursive" in state and state["recursive"].type == "leftbracket"
            if t.type in checkBreakLine and not isArray and not functionOrControl and not [op for op in assignOperators if op in state]:
                stack, state = [], {}

            elif prev.type == "comma" and t.type == "identifier" and "type" in state and not functionOrControl:
                state.setdefault("commaVars", [])
                state["commaVars"].append(t)
                stack.append(t)

            elif t.type == "assign" and "commaVars" in state:
                state.setdefault("commaAssigns", [])
                state["commaAssigns"].append(t)
                stack.append( t)

            elif t.type in stackContinueTokens:
                if "control" in state or "function" in state:
                    stack, state = pushControlToken(stack, stackList, state, t)
                else:
                    pushContinueToken(functionOrControl, stack, state, t)

            elif t.type == "semicolon":
                stack, state = pushSemicolon(stack, stackList, state, t)

            else:
                stack, state = [], {}
        if t.type != "star":
            prev = t
    return stackList


def popRecursiveAux(stack, token, tokenList,fileName):
    spaceTokens = token.value  in ["}","]"]
    correctFormat = (" " + token.value) if spaceTokens else token.value
    startToken = stack.pop()
    nextToken = startToken
    tokenList.insert(0, token)
    #print("START> value:" + nextToken.value + " line:" + str(nextToken.line) + " column:" + str(nextToken.column))

    while nextToken.type != recursiveTokenNames[token.type]:
        if nextToken.type in recursiveTokenNames:
            #print("NEXT RECURSIVE> value:" + nextToken.value + " line:" + str(nextToken.line) + " column:" + str(nextToken.column))
            innerCorrectFormat = popRecursiveAux(stack, nextToken,tokenList,fileName)
            correctFormat = innerCorrectFormat + correctFormat

        else:
            #print("NEXT> value:" + nextToken.value + " line:" + str(nextToken.line) + " column:" + str(nextToken.column))
            tokenList.insert(0, nextToken)
            correctFormat = nextToken.value + correctFormat
        nextToken = stack.pop()

    endToken = nextToken
    tokenList.insert(0,endToken)
    spaceTokens = spaceTokens and endToken is not startToken
    correctFormat = (endToken.value + " " + correctFormat) if spaceTokens else (endToken.value + correctFormat)
    literalEndColumn = startToken.column + len(startToken.value) - 1
    if spaceTokens and (token.column - 2 < literalEndColumn or tokenList[-2].column - 2 < endToken.column):
        error = "Spacing for identifier/literal in  operator "+endToken.value+token.value+ \
                " ,supposed to be '" + correctFormat +"'."
        vera.report(fileName, token.line, error)
    #print(correctFormat)
    #print("FINISH> value:" + endToken.value + " line:" + str(endToken.line) + " column:" + str(endToken.column))
    return correctFormat


def popRecursive(token, fileName, stack, state, flags, defineDict, typeDict):
    tokenList = []
    # print([(t.value,t.line) for t in tokenList])
    correctFormat = popRecursiveAux(stack, token, tokenList, fileName)
    #print(correctFormat)
    if not ("assign" in state and "assign" not in flags):
        if "tokenList" in flags:
            flags["tokenList"] = tokenList + flags["tokenList"]
            flags["correctFormat"] = correctFormat + flags["correctFormat"]

        else:
            flags["tokenList"] = tokenList
            flags["correctFormat"] = correctFormat

    elif token.type == "rightbrace" and state["type"][0].value == "char":
        if correctFormat != "{ 0 }":
            vera.report(fileName, token.line, "Char array needs to be initialized with '{ 0 }'")
    if stack and stack[-1].type == "identifier":
        identifier = stack[-1]
        if token.type == "rightbracket" and "identifier" in state \
                and identifier.value == state["identifier"].value:
            identifierColumn, leftBracketToken = identifier.column + len(identifier.value) - 1, tokenList[0]
            if leftBracketToken.column - 1 != identifierColumn:
                error = "Spacing for identifier before operator" + tokenList[0].value + token.value + \
                        " supposed to be '" + identifier.value + flags["correctFormat"] + "'."
                vera.report(fileName, token.line, error)
            tokenList = flags["tokenList"] if "tokenList" in flags else tokenList
            if "assign" in flags:
                for t in tokenList:
                    if t.type == "identifier" and not defineDict.has_key(t.value):
                        vera.report(fileName, t.line,
                                    "Non #define identifier '" + t.value + "' used to initialize array.")

    elif token.type == "rightparen" and "malloc" in flags and "assign" not in flags:
        if "type" in state:
            type = state["type"]

        elif state["identifier"].value in typeDict:
            type = typeDict[state["identifier"].value]
        identifierType = ''.join([t.value for t in type])
        mallocType = ''.join([t.value for t in tokenList[1:-1]])
        flags["mallocType"] = mallocType
        if identifierType != mallocType:
            vera.report(fileName, token.line,
                        "Malloc's cast is to incorrect type, pointer initialized as '" + \
                        identifierType + "' but cast was to '" + mallocType + "'.")



def popIdentifier(identifier, fileName, stack, flags, state, constDict, varDict, typeDict):
    # if this identifier isn't in the constDict it must be a regular variable
    # let's check for intialization
    if "type" not in state or "function" in state  or identifier.value in libFunctions:
        return
    assigned = "assign" in state and ("comma" not in state or \
            (state["assign"].line < state["comma"].line or \
             (state["assign"].line == state["comma"].line and state["assign"].column < state["comma"].column)))
    if "commaVars" in state and state["commaVars"][-1].value == identifier.value:
        del state["commaVars"][-1]
        if not state["commaVars"]:
            del state["commaVars"]
        assigned = False
        if "commaAssigns" in state:
            assign = state["commaAssigns"][-1]
            assigned = assign.line > identifier.line or (assign.line == identifier.line and assign.column > identifier.column)
            if assigned:
                del state["commaAssigns"][-1]
                if not state["commaAssigns"]:
                    del state["commaAssigns"]

    elif identifier.value != state["identifier"].value:
        return
    varDict[identifier.value] = identifier
    type = state["type"][:]
    if "const" in state:
        type = [state["const"]] + type
        constDict[identifier.value] = identifier
    if "commaStars" in state and state["commaStars"]:
        type += state["commaStars"][-1]

    elif "typeStars" in state and state["typeStars"]:
        type +=   state["typeStars"][-1]
    typeDict[identifier.value] = type
    if state["type"][0].type == "struct":
        identifierType = state["type"][0].value+" "+''.join([t.value for t in type])

    else:
        identifierType = ''.join([t.value for t in type])

    if not assigned:
        return identifier, "Uninitialized identifier '" + identifier.value + "' of type " + identifierType + "."

    else:
        return None


def popAssign(token, fileName, stack, flags, currentState, mallocDict):
    # we encountered '=', so we are now ready for the variable identifier
    flags["assign"] = token
    if "malloc" in flags:
        if "mallocType" not in flags:
            vera.report(fileName, token.line, "Malloc lacks a pointer cast.")
        pointerIdentifier = currentState["identifier"]
        if mallocDict.has_key(pointerIdentifier.value):
            mallocDict[pointerIdentifier.value] = (
                pointerIdentifier, mallocDict[pointerIdentifier.value][1] + 1)

        else:
            mallocDict[pointerIdentifier.value] = (pointerIdentifier, 1)


def popStar(token, fileName, stack, flags, state): #Justin Bieber
    # the star '*' was encountered, let's check it isn't the cast* star and if it isn't
    # then it's the pointer definition's * star so let's check it's next to the type
    # with a space from the variable
    if "type" not in state or "identifier" not in state:
        return
    dictKey = "commaStars" if "comma" in state and "commaStars" else "typeStars"
    if dictKey not in state or not state[dictKey]: return
    flags.setdefault(dictKey,state[dictKey])
    pointerType, pointerList = state[dictKey][len(state[dictKey])-1], state[dictKey][-1]
    type, star = state["type"] + pointerType, pointerList[-1]

    if token.column != star.column or token.line != star.line: return
    index = len(state["type"]) + len(pointerList) - 1
    identifier = state["identifier"]
    differenceToVar, differenceToNextInType = identifier.column - star.column, 1
    starCloseToIdentifier = index == len(type) - 1 and differenceToVar != 2
    state[dictKey][-1].pop()
    if not state[dictKey][-1]: state[dictKey].pop()

    startType, endType = ''.join([tt.value for tt in type[:index]]), ''.join([tt.value for tt in type[index:]])
    nextColumn = star.column + len(star.value) - 1
    differenceToNextInType = star.column - nextColumn

    if starCloseToIdentifier:
         vera.report(fileName, star.line, "Pointer's '*' does not have a single whitespace before identifier, '"
                     + startType + endType + " " + identifier.value + "' instead of '"
                     + startType + " " * (differenceToNextInType - 1) + endType + " " * (
                    differenceToVar - 1) + identifier.value + "'.")

    elif differenceToNextInType != 1:
        vera.report(fileName, star.line, "Pointer's '*' not next to the pointer's type '"
                    + startType + endType + " " + identifier.value + "' instead of '"
                    + startType + " " * (differenceToNextInType-1) + endType + " " * (differenceToVar-1) + identifier.value + "'.")





def popInitializationStack(fileName, stackList):
    """
        In this stage the loaded stack is popped iteratively, and state transitions occur
        according to the current pushdown state and token, along with flags.
    """

    varDict, typeDict, mallocDict, constDict, defineDict, funcDict = {}, {}, {}, {}, {}, {}
    defineStacks = {}
    flags, errors = {}, []
    infoDict = {"varDict": varDict, "typeDict": typeDict, "mallocDict": mallocDict, "constDict": constDict,
                "defineDict": defineDict,
                "funcDict": funcDict, "errorList": errors}


    while len(stackList) > 0:
        stack, state = stackList.pop()
        if "define" in state:
            defineDict[state["identifier"].value] = state["identifier"]
            defineStacks[state["identifier"].value] = stack
            continue

        elif "function" in state:
            funcDict[state["function"].value] = state["function"]
        #print([(t.type,t.value,t.line) for t in stack])
        while len(stack) > 0:
            token = stack.pop()
            #print("type:"+token.type+" value:"+token.value+" line:"+str(token.line)+ " column:"+str(token.column))
            if token.type == "semicolon":
                # we're beginning a new command
                flags = {}

            elif token.type == "identifier" and token.value == "malloc":
                # we encountered malloc so we're turning on malloc flag
                flags["malloc"] = token

            elif token.type in recursiveTokenNames:
                popRecursive(token, fileName, stack, state, flags, defineDict, typeDict)

            elif token.type in literals:
                # we encountered a literal, we can now check the literal flag, because a value is being assigned
                flags["literal"] = token

            elif token.type == "assign":
                popAssign(token, fileName, stack, flags, state, mallocDict)

            elif token.type == "identifier":
                result = popIdentifier(token, fileName, stack, flags, state, constDict, varDict, typeDict)
                if result is not None:
                    errors.append(result)

            elif token.type == "star" and ("assign" in flags or "assign" not in state):
                popStar(token, fileName, stack, flags, state)
    return infoDict





def handleToken(t, fileName):
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


def handleControl(t, fileName, constDict, mallocDict, defineDict, varDict):
    global controlState, controlParenCount, controlToken, flags, prev, controlIdentifier

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

                    if prev == "not" and t.value in mallocDict:
                        mallocDict[t.value] = mallocDict[t.value][0], mallocDict[t.value][1] - 1

                    elif "equal" in flags and controlIdentifier != None:
                        rhs = None
                        if constDict.has_key(t.value):
                            rhs = constDict[t.value]
                        if rhs == None and defineDict.has_key(t.value):
                            rhs = defineDict[t.value]
                        if varDict.has_key(controlIdentifier.value) and rhs != None:
                            vera.report(fileName, t.line,
                                        "Equality checking '" + controlIdentifier.value + " == " + rhs.value + "' with "
                                             "left-hand-side argument as variable and rhs as const or #define.")
                        if t.value == "NULL" and controlIdentifier.value in mallocDict:
                            mallocDict[controlIdentifier.value] = mallocDict[controlIdentifier.value][0], mallocDict[controlIdentifier.value][1] - 1

                        elif controlIdentifier.value == "NULL" and t.value in mallocDict:
                            mallocDict[t.value] = mallocDict[t.value][0], mallocDict[t.value][1] - 1

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
    prev = t.type if t.type in controlTokenTypes else prev


def handleFunction(t, constDict):
    global functionState, identifier, functionary
    # print("state:" + str(functionState) + " value:" + t.value + " type:" + t.type + " line:" + str(t.line))
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


def functionalyze(fileName, infoDict, errorList):
    constDict, mallocDict, varDict, defineDict = infoDict["constDict"], infoDict["mallocDict"], infoDict["varDict"], \
                                                 infoDict["defineDict"]
    global parenCount, braceCount, returnCount, lastReturn, controlParenCount, controlState, controlToken, \
        functionary, flags, lastSemicolon, identifier
    controlState,  functionState = START, START
    functionary, flags = {}, {}
    parenCount, braceCount, returnCount, controlParenCount = 0, 0, 0, 0
    controlToken, prev, lastReturn, lastSemicolon, identifier = None, None, None, None, None
    errorIter = iter(errorList)
    nextError = next(errorIter, None)

    for t in vera.getTokens(fileName, 1, 0, -1, -1, list(functionalyzeTokenTypes)):
        handleToken(t, fileName)
        handleControl(t, fileName, constDict, mallocDict, defineDict, varDict)
        handleFunction(t, constDict)

        while nextError is not None and t.line >= nextError[0].line:
            errorToken, error = nextError
            #print("errorToken line:" + str(errorToken.line) + "t line:" + str(t.line))
            if "struct" not in flags:
                vera.report(fileName,errorToken.line,error)
            nextError = next(errorIter, None)
    return functionary


def checkUppercaseUnderscore(file, dic,errorPrefix):
    """
        Checks if the given dictionary(String,Token) contains identifiers
        that need to conform to UPPERCASE_WITH_UNDERSCORE.
    """
    for k, v in dic.iteritems():
        result = re.search(uppercasePattern,k)
        if result == None:
            vera.report(file,v.line,errorPrefix+" '("+k+"' : "+v.value+")' name isn't UPPERCASE_WITH_UNDERSCORE.")


def checkCamelCase(fileName,dic):
    """
        Checks if the given dictionary(String,Token) contains identifiers that need to conforom
        to lowerCamelCase, meaning they need to start with either a lowercase letter, or two or more
        uppercase letters.
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
    """
    for k, v in mallocDict.iteritems():
        if v[1] > 0:
            vera.report(fileName, v[0].line,
                        "Pointer's '" + k + "' Malloc(s) missing '" + str(v[1]) + "' null pointer check(s).")


def isVarBeforeFirstFunction(funcs, vars, types, fileName):
    globalVars = [token for identifier, token in vars.items() if types[identifier][0].column == 0]
    if not globalVars or not funcs:
        return
    firstFunc = min([f for f in funcs.values()],key = operator.attrgetter('line'))
    firstVar = min(globalVars, key= operator.attrgetter('line'))
    if firstVar.line > firstFunc.line:
        vera.report(fileName, firstVar.line, "'Global variable '" + firstVar.value +
                "' appears after the first function "+firstFunc.value+".")




def veraAnalysis():
    for fileName in vera.getSourceFileNames():
        stackStateList = pushInitializationStack(fileName)
        stackStateList = stackStateList[::-1]
        #printStack = [(stackState[1],[(t.type,t.value,t.line) for t in stackState[0]]) for stackState in stackStateList]
        #print(printStack)

        infoDict = popInitializationStack(fileName, stackStateList)
        fileInfoDict[fileName] = infoDict
        infoDict["funcDict"].update(functionalyze(fileName, fileInfoDict[fileName],infoDict["errorList"]))

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


def addDictionaryIdentifiers(dict,file, pointerLineDict):
    for identifierK, identifierV in dict.iteritems():
        if not pointerLineDict[file].has_key(identifierV.line):
            pointerLineDict[file][identifierV.line] = {}
        pointerLineDict[file][identifierV.line][identifierV.value] = identifierV


def populateIdentifierLines(file, pointerLineDict):
    if not pointerLineDict.has_key(file):
        pointerLineDict[file] = {}

    else:
        return
    infoDict = fileInfoDict[file]
    constDict, varDict, mallocDict = infoDict["constDict"], infoDict["varDict"], infoDict["mallocDict"]
    mallocDict = {k:v[0] for k,v in mallocDict.iteritems()}
    addDictionaryIdentifiers(mallocDict,file,pointerLineDict)
    addDictionaryIdentifiers(varDict,file,pointerLineDict)
    #addDictionaryIdentifiers(constDict,file)


def lookupRecurrentIdentifiers(file, pointerLineDict):
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


def sanitizerAnalysis():
    runtimeErrorList= sanitize()
    pointerLineDict = {}

    for (file, line), (warning, identifier,appearsInFiles) in runtimeErrorList.iteritems():
        line, identifiers = int(line), None
        if identifier is not None:
            identifiers = {identifier : None}
            error = warning + ", variable identifier: "+", ".join([i for i in identifiers.keys()])+"."

        else:
            populateIdentifierLines(file, pointerLineDict)
            if not (pointerLineDict.has_key(file) and pointerLineDict[file].has_key(line)):
                lookupRecurrentIdentifiers(file, pointerLineDict)
            if pointerLineDict.has_key(file) and pointerLineDict[file].has_key(line):
                identifiers = pointerLineDict[file][line]
                error =  warning + ", suspect variable identifiers: " + ", ".join(
                       [i for i in identifiers.keys()]) + "."

            else:
                error = warning + "."
        scenariosString = "Memory:"+"["+",".join([scen[:-5] for scen in sorted(appearsInFiles)])+"]: "
        error = scenariosString+error
        vera.report(file, line, error)


#veraAnalysis()
#sanitizerAnalysis()