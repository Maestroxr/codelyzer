"""
This is the stack push module.
It is responsible for pushing the stack of the pushdown automaton.
"""
import vera
literals = {"intlit", "stringlit", "charlit"}

types = {"int", "char", "void", "float", "double"}

operators = { "plus", "plusplus","notequal", "minus", "minusminus", "less", "greater", "greaterequal"}
assignOperators = { "assign" , "percentassign", "minusassign", "plusassign", "andassign", "divideassign",
                    "orassign", "starassign", "shiftleftassign", "shiftrightassign", "xorassign" }
stackContinueTokens = {"star", "identifier", "leftbracket", "rightbracket", "malloc", "leftbrace","comma",
                  "rightbrace", "int", "char", "leftparen", "rightparen", "identifier","arrow","dot", "not",
                       "const"}  | literals | types | operators | assignOperators
stackConsiderTokens = { "leftbracket", "rightbracket", "identifier", "intlit", "charlit", "stringlit", "comma",
                       "semicolon", "leftbrace", "rightbrace", "leftparen", "rightparen", "star", "arrow", "dot", "not",
                       "for", "if","while", "switch", "struct", "const", "pp_define", "newline"} | types | operators | assignOperators
def pushFirstToken(stack, globalState, state, t):
    """
    This function pushes the first token into the stack.
    :param stack: The stack being pushed into.
    :param globalState: The global state dictionary.
    :param state: The state dictionary.
    :param t: The token being pushed.
    """
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
        if globalState["braceCount"] == 0:
            globalState["structDefinition"] = t

    elif t.type == "const":
        state["const"] = t

    elif t.type == "pp_define":
        state["define"] = t

    elif t.type == "star":
        state["dereference"] = t


def pushSemicolon(stack, stackList, state, t):
    """
    This function pushes a semicolon into the stack.
    :param stack: The stack being pushed into.
    :param stackList: The stack list.
    :param state: The state of the stack.
    :param t: The semicolon token.
    """
    if "struct" in state:
        state["type"] = [state["struct"]] + state["type"]
    stack.append(t)
    stackList.append((stack, state))
    if "control" not in state:
        state, stack = {}, []

    else:
        stack = []
    return stack, state


def pushContinueToken(stack, state, t, functionOrControl, assignOpPresent):
    """
    This function pushes a token that apears in the stack continue tokens set.
    :param stack: The stack being pushed.
    :param state: The state of the stack.
    :param t: The semicolon token.
    :param functionOrControl: Is this a function or control structure.
    :param assignOpPresent: Is assing operator present in stack.
    """
    maybeTypeToken = not assignOpPresent and "dereference" not in state and "type" not in state and not functionOrControl
    if t.type in assignOperators:
        state.setdefault("assign", t)
        state.setdefault("assignments", [])
        state["assignments"].append(t)

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

    elif t.type == "star" and "type" in state and not functionOrControl:
        commas, vars = len(state["commas"]) if "commas" in state else 0, len(state["vars"]) if "vars" in state else 0
        if (commas >= 1 and commas == vars + 1) or (commas == 0 and "identifier" not in state):
            state.setdefault("stars",[[]])
            state["stars"][-1] += [t]

    elif t.type in ["arrow", "dot"] and not assignOpPresent:
        state["dereference"] = t

    elif t.type == "comma":
        state.setdefault("comma", t)
        state.setdefault("commas", [])
        state["commas"].append(t)
        state.setdefault("stars", [[]])

        state["stars"].append([])
    stack.append(t)


def pushControlToken(stack, stackList, state, t):
    """
    This function a token while inside a control structure.
    :param stack: The stack being pushed into.
    :param stackList: The stack list.
    :param state: The state of the stack.
    :param t: The semicolon token.
    """
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

def printTokens(list, prefix = ""):
    """
    This function prints a token list.
    :param list: The token list.
    :param prefix: The print prefix.
    :return:
    """
    print(prefix + str([(token.type, token.value, token.line, token.column) for token in list]))

def resetBraceState(globalState):
    """
    This function resets the brace state of the global state.
    :param globalState: The global state dictionary.
    """
    if "structDefinition" in globalState:
        del globalState["structDefinition"]



def transitionGlobalState(globalState,t):
    """
    This function transitions the global state according to the current token.
    :param globalState: The global state dictionary.
    :param t: The token that transitions.
    """
    if t.type == "leftbrace":
        globalState["braceCount"] += 1
    elif t.type == "rightbrace":
        globalState["braceCount"] -= 1
        if globalState["braceCount"] == 0:
            resetBraceState(globalState)


def pushInitializationStack(fileName):
    """
    This function pushes the initialization stack.
    It does so using several functions.
    :param fileName: The file name.
    :return: A list of stacks.
    """
    """
        This phase uses a pushdown automaton in order to keep track of the current state
        that is now being loaded into the stack.
    """
    globalState, state, stack, stackList = {"braceCount":0}, {}, [], []
    checkBreakLine = set(["leftparen", "leftbrace","rightparen"])
    prev = None
    for t in vera.getTokens(fileName, 1, 0, -1, -1, list(stackConsiderTokens)):
        #print("state:" + str(state) + " value:" + t.value + " type:" + t.type + " line:" + str(t.line) + " column:" + str(t.column))
        #print("globalState:" + str(globalState))
        #print("stack:"+str([(token.type, token.value, token.line) for token in stack]))

        transitionGlobalState(globalState, t)

        if not state:
            pushFirstToken(stack, globalState, state, t)

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
            assignOpPresent = bool([op for op in assignOperators if op in state])
            if "structDefinition" in globalState:
                state["structDefinition"] = globalState["structDefinition"]
            if t.type in ["leftbracket","leftparen", "leftbrace"]:
                if "recursive" not in state and not assignOpPresent:
                    state["recursive"] = t
                    if t.type == "leftparen" and "control" not in state and "dereference" not in state:
                        state["function"] = state.pop("identifier")
                        state["leftParen"] = 0
            #This variable signifies the fact that the first control token encountered out of [,(,{ is not '('
            # because that would mean it is either if/for/while/function
            functionOrControl = "recursive" in state and state["recursive"].type == "leftparen"
            isArray = "recursive" in state and state["recursive"].type == "leftbracket"

            if t.type in checkBreakLine and not isArray and not functionOrControl and not assignOpPresent:
                stack, state = [], {}

            elif t.type == "identifier" and "type" in state and not functionOrControl and prev.type == "comma":
                state.setdefault("vars", [])
                state["vars"].append(t)
                stack.append(t)


            elif t.type in stackContinueTokens:
                if "control" in state or "function" in state:
                    stack, state = pushControlToken(stack, stackList, state, t)
                else:
                    pushContinueToken(stack, state, t, functionOrControl, assignOpPresent)

            elif t.type == "semicolon":
                stack, state = pushSemicolon(stack, stackList, state, t)

            else:
                stack, state = [], {}
        if t.type != "star":
            prev = t
    return stackList

