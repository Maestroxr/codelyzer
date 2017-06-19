"""
Underlying is the stack pop module.
It is responsible for popping the stack.
"""
import vera

literals = {"intlit", "stringlit", "charlit"}
operators = { "plus", "plusplus","notequal", "minus", "minusminus", "less", "greater", "greaterequal"}
assignOperators = { "assign" , "percentassign", "minusassign", "plusassign", "andassign", "divideassign",
                    "orassign", "starassign", "shiftleftassign", "shiftrightassign", "xorassign" }
recursiveTokenNames = {"rightbracket" : "leftbracket" , "rightbrace" : "leftbrace", "rightparen" : "leftparen"}
recursiveTokenLiterals = { "rightbracket" : "]", "leftbracket" : "[", "rightbrace" : "}", \
                           "leftbrace" : "{", "rightparen" : ")", "leftparen" : "(" }
libFunctions = { "strlen","fgets","strcmp" }

whitespace = " "

def isBefore(first,second):
    """
    This function makes sure that the first token is prior to the second.
    :param first: First token.
    :param second: Second token.
    :return: True if prior, else False.
    """
    return first.line < second.line or (first.line == second.line and first.column < second.column)


def popRecursiveAux(stack, token, tokenList,fileName):
    """
    This is the auxiliary function of the pop recursive function.
    It is used to recursively pop the tokens out of the stack. In case a recursive token is found,
    it is called recursively.
    :param stack: The stack that is examined.
    :param token: The token that is examined.
    :param tokenList: The token list being examined.
    :param fileName: The file name.
    :return: Returns the correct format so far of the tokens examined.
    """
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
        error = "Spacing for identifier/literal in operator "+endToken.value+token.value+ \
                ", supposed to be '" + correctFormat +"'."
        vera.report(fileName, token.line, error)
    #print(correctFormat)
    #print("FINISH> value:" + endToken.value + " line:" + str(endToken.line) + " column:" + str(endToken.column))
    return correctFormat


def popRecursive(token, fileName, stack, state, flags, infoDict, assignOpPresent, flagsAssignOpPresent):
    """
    This function recursively pops recursive tokens.
    Whenever a '{' or '[' or '(' is met, it is popped recursively.
    The correct format is that which has a space between each recursive token and the next token, unless
    the recursive token is followed by the closing recursive token of the same kind.
    That means that an example in which the recursive token is followed promptly with another token,
    which is not the closure of the same kind, or in which the following token is promptly followed by a closure token,
    will produce an error.
    Furthermore only the '{' or '[' tokens and their closures will require spacing, as dictated by conventions.
    In the case of a char type, the only kind of possible intialization is '{ 0 }'.
    The information surmised regarding malloc will enable comparison of the types being assigned, in case the variable
    type is already loaded in the stack, but notwithstanding the lack of a loaded type, a supplemental check is made
    to infer the type from previously gathered data.
    :param token: The recursive token being popped.
    :param fileName: The file name.
    :param stack: The stack being popped.
    :param state: The state of the stack.
    :param flags: The flags of the stack.
    :param infoDict: The information dictionary.
    :param assignOpPresent: Is an assign operator present in the stack's state.
    :param flagsAssignOpPresent: Is an assign operator present in the stack's flags.
    """
    defineDict, typeDict = infoDict["defineDict"], infoDict["typeDict"]
    tokenList = []
    correctFormat = popRecursiveAux(stack, token, tokenList, fileName)
    #print(correctFormat)

    if not (assignOpPresent and not flagsAssignOpPresent):
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
            if flagsAssignOpPresent:
                for t in tokenList:
                    if t.type == "identifier" and not defineDict.has_key(t.value):
                        vera.report(fileName, t.line,
                                    "Non #define identifier '" + t.value + "' used to initialize array.")

    elif token.type == "rightparen" and "malloc" in flags:
        identifier = state["identifier"] if "vars" not in state else state["vars"][-1]
        if "type" in state:
            type = state["type"][:]
            if "stars" in state and state["stars"]:
                type += state["stars"][-1]
        elif identifier.value in typeDict:
            type = typeDict[identifier.value][:]
        identifierType = ''.join([t.value for t in type])
        mallocType = ''.join([t.value for t in tokenList[1:-1]])
        flags["mallocType"] = mallocType
        if identifierType != mallocType:
            vera.report(fileName, token.line,
                        "Malloc's cast is to incorrect type, pointer '"+identifier.value+"' initialized as '" + \
                        identifierType + "' but cast was to '" + mallocType + "'.")



def popIdentifier(identifier, fileName, stack, flags, state, infoDict, assignOpPresent):
    """
    This function is responsible for popping an identifier.
    If the identifier wasn't assigned, an error is produced.
    :param identifier: The identifier popped.
    :param fileName: The file name.
    :param stack: The stack being popped.
    :param flags: The flags of the stack.
    :param state: The state of the stack.
    :param infoDict: The information dictionary.
    :param assignOpPresent: Is an assign operator present in the state.
    """
    constDict, varDict, typeDict = infoDict["constDict"], infoDict["varDict"], infoDict["typeDict"]
    # if this identifier isn't in the constDict it must be a regular variable
    # let's check for intialization
    if [flag for flag in ["function","structDefinition","dereference"] if flag in state] or "type" not in state or identifier.value in libFunctions:
        return
    assigned = assignOpPresent and state["assignments"] and isBefore(identifier,state["assignments"][-1])

    if "vars" in state:
        if state["vars"][-1].value != identifier.value:
            return
    elif identifier.value != state["identifier"].value:
        return
    varDict[identifier.value] = identifier

    type = state["type"][:]
    if "const" in state:
        type = [state["const"]] + type
        constDict[identifier.value] = identifier
    if "stars" in state and state["stars"]:
        type += state["stars"][-1]
        flags["stars"] = state["stars"][-1][:]
    typeDict[identifier.value] = type
    if state["type"][0].type == "struct":
        identifierType = state["type"][0].value+" "+''.join([t.value for t in type])

    else:
        identifierType = ''.join([t.value for t in type])

    if not assigned:
        vera.report(fileName,identifier.line, "Uninitialized identifier '" + identifier.value + "' of type " + identifierType + ".")




def popAssign(token, fileName, stack, flags, state, mallocDict):
    """
    This function is responsible for popping an assign operator.
    Encountering a malloc afore the assign will bring about a type comparison.
    :param token: The token popped.
    :param fileName: The file name.
    :param stack: The stack being popped.
    :param flags: The flags of the stack.
    :param state: The state of the stack.
    :param infoDict: The information dictionary.
    """
    # we encountered '=', so we are now ready for the variable identifier
    if "assignments" not in state or not (state["assignments"][-1].line == token.line and state["assignments"][-1].column == token.column):
        return
    flags["assign"] = token

    if "malloc" in flags:
        if "mallocType" not in flags:
            vera.report(fileName, token.line, "Malloc lacks a pointer cast.")

        else:
            del flags["mallocType"]
        pointerIdentifier = state["identifier"] if "vars" not in state else state["vars"][-1]
        mallocDict.setdefault(pointerIdentifier.value,[])
        mallocDict[pointerIdentifier.value].append(flags["malloc"])
        del flags["malloc"]


def popStar(token, fileName, flags, state): #Justin Bieber
    """
    The star '*' was encountered, let's check it isn't the cast* star and if it isn't,
    then it's the pointer definition's * star so let's check it's next to the type
    with a space from the variable.
    :param fileName: The file name.
    :param stack: The stack being popped.
    :param flags: The flags of the stack.
    :param state: The state of the stack.
    """
    if "type" not in state or "identifier" not in state or "stars" not in state or not state["stars"] or not state["stars"][-1]:
        return

    type, star = state["type"] + flags["stars"], state["stars"][-1].pop()
    starList = state["stars"][-1]

    if token.column != star.column or token.line != star.line:
        return

    index, typeLength = len(starList), len(state["type"]) -1
    identifier = state["identifier"]
    startTypeList = [tt.value for tt in type[:typeLength + index+1]]
    endTypeList = [tt.value for tt in type[typeLength + index+1:]]
    nextToken = starList[-1] if starList else state["type"][-1]

    if "commas" in state:
        comma = state["commas"][-1]
        identifier = state["vars"][-1]
        if not starList:
            nextToken = comma
        startTypeList = [tt.value for tt in state["type"]] + [" ",comma.value] + [tt.value for tt in starList]
        endTypeList = [tt.value for tt in flags["stars"][index:]]

    startType = ''.join(startTypeList)
    endType = ''.join(endTypeList)
    differenceToNextInType = star.column - nextToken.column - len(nextToken.value)
    differenceToVar = identifier.column - star.column - 1
    starCloseToIdentifier = index != len(flags["stars"]) - 1 or differenceToVar == 1
    starCloseToNextInType = differenceToNextInType == 0

    if not starCloseToIdentifier:
        vera.report(fileName, star.line, "Pointer's '*' does not have a single whitespace before identifier, '"
                     + startType + endType + " " + identifier.value + "' instead of '"
                     + startType +" "*differenceToNextInType+ endType + " " * (differenceToVar) + identifier.value + "'.")

    if not starCloseToNextInType:
        betweenTypeAndIdentifier = " " if starCloseToIdentifier else " " * differenceToVar

        vera.report(fileName, star.line, "Pointer's '*' not next to the pointer's type '"
                    + startType + endType + " " + identifier.value + "' instead of '"
                    + startType + " " * (differenceToNextInType) + endType + betweenTypeAndIdentifier + identifier.value + "'.")





def popInitializationStack(fileName, stackList):
    """
    In this stage the loaded stack is popped iteratively, and state transitions occur
    according to the current pushdown state and token, along with flags.
    :param fileName: The file name.
    :param stackList: The stack list.
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
        #printTokens(stack,"Between while stack:")
        #print("Between while state:"+str(state))
        assignOpPresent = bool([op for op in assignOperators if op in state])

        while len(stack) > 0:
            token = stack.pop()
            flagsAssignOpPresent = bool([op for op in assignOperators if op in flags])
            #print("type:"+token.type+" value:"+token.value+" line:"+str(token.line)+ " column:"+str(token.column))
            if token.type == "semicolon":
                # we're beginning a new command
                flags = {}

            elif token.type == "identifier" and token.value == "malloc":
                # we encountered malloc so we're turning on malloc flag
                flags["malloc"] = token

            elif token.type in recursiveTokenNames:
                popRecursive(token, fileName, stack, state, flags, infoDict,assignOpPresent, flagsAssignOpPresent)

            elif token.type in literals:
                # we encountered a literal, we can now check the literal flag, because a value is being assigned
                flags["literal"] = token

            elif token.type in assignOperators:
                popAssign(token, fileName, stack, flags, state, mallocDict)

            elif token.type == "identifier":
                result = popIdentifier(token, fileName, stack, flags, state, infoDict, assignOpPresent)
                if result is not None:
                    errors.append(result)

            elif token.type == "star" and (flagsAssignOpPresent or not assignOpPresent):
                popStar(token, fileName, flags, state)
            elif token.type == "comma" and "commas" in state and state["commas"][-1].line == token.line  \
                    and state["commas"][-1].column == token.column:
                state["commas"].pop()
                if not state["commas"]:
                    del state["commas"]
                if "vars" in state:
                    state["vars"].pop()
                    if not state["vars"]:
                        del state["vars"]
                if "stars" in state and state["stars"]:
                    state["stars"].pop()
                if "assignments" in state and state["assignments"] and isBefore(token,state["assignments"][-1]):
                    state["assignments"].pop()

    return infoDict

