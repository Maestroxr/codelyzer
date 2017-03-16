#!/usr/bin/python
# Curly brackets from the same pair should be either in the same line or in the same column
import re
import vera

emptyLinePattern = re.compile("^\s*$")
indentation, stateIndex, index, end = 0, 0, 0, 0
file, parens, state, allLines, stateTokens, commentLineDic = None, None, None, None, None, None


def acceptPairs ():
    """
        A recursive function that collects the current level's bracer couples, and for each one found
        activates itself recursively, so each bracer couple will look for it's own lower-level bracer couples.
        Each '{}' curly bracket will be checked sperately for indentation on the same level and the expected tab amount.
    """
    global file, parens, index, end, indentation, allLines, stateTokens, stateIndex, state
    thisLevelsParens = []
    while index != end:
        nextToken = parens[index]
        tokenValue = nextToken.value
        if tokenValue == "{":
            leftParenLine,  leftParenColumn= nextToken.line, nextToken.column
            thisLevelsParens.append(index)
            startingIndex = index
            index+=1

            if (stateIndex < len(stateTokens)):
                if (stateTokens[stateIndex].line < leftParenLine-1):
                    vera.report(file, leftParenLine, "Control structure of type:"+stateTokens[stateIndex].type+ \
                                " is missing matching parenthesis")

                elif stateTokens[stateIndex].line == leftParenLine-1:
                    state = stateTokens[stateIndex].type
                    stateIndex += 1

            indentation+=1
            lowerLevelsParens = acceptPairs()
            checkFragmentedIndentation(parens[startingIndex].line,parens[index].line,lowerLevelsParens)

            if index == end:
                vera.report(file,leftParenLine,"Opening curly bracket is not closed.")
                return
            nextToken = parens[index]
            thisLevelsParens.append(index)
            index+=1
            rightParenLine = nextToken.line
            rightParenColumn = nextToken.column
            if (leftParenLine != rightParenLine):
                if (leftParenColumn != rightParenColumn):
                    # make an exception for line continuation
                    leftLine = allLines[leftParenLine-1]
                    rightLine = allLines[rightParenLine-1]
                    if (leftLine[-1] != "\\") and (rightLine[-1] != "\\"):
                        vera.report(file,rightParenLine,"Closing curly bracket not in the same line or column,"
                        " or brackets are not both indented with tabs.")
                if leftParenColumn != indentation:
                    vera.report(file, leftParenLine, "Curly bracket tab indentation incorrect, found " + str(
                        leftParenColumn) + " characters but expected " + str(indentation)+" tabs.")

        else:
            indentation-=1
            return thisLevelsParens
    #print("returing parenthesis list:")
    #print(thisLevelsParens)
    return thisLevelsParens

def checkFragmentedIndentation(startingLine,endingLine,bracerCouples):
    """
       This function checks for the right indentation from startingLine to
       endingLine and between the bracer couples list recieved.
    """
    if (len(bracerCouples) > 1):
        checkLineRangeIndentation(startingLine, parens[bracerCouples[0]].line)
        checkLineRangeIndentation(parens[bracerCouples[-1]].line, endingLine)
        for i in range(1, (len(bracerCouples) / 2 - 1)):
            checkLineRangeIndentation(parens[bracerCouples[i * 2]].line, parens[bracerCouples[i * 2 + 1]].line)
    else:
        checkLineRangeIndentation(parens[index - 1].line, parens[index].line)


def checkLineRangeIndentation (startingLine, endingLine):
    """
        This function runs through the lines and checks for tab amount at the
        start of each line equal to indentation global variable.
    """
    global allLines, indentation, file, stateTokens, stateIndex, state, commentLineDic
    #print("checking line, starting:"+str(startingLine)+ " ending:" + str(endingLine)+" indentation:"+str(indentation))

    i = startingLine+1
    while i < endingLine:

        if i in commentLineDic:
            newLines = len(re.findall("\n",commentLineDic[i].value))
            i += newLines + 1
            continue

        line = allLines[i-1]
        result = re.search(emptyLinePattern, line)
        if (result != None):
            i += 1
            continue
        indentationOffset = 1
        if stateIndex < len(stateTokens) and state != None:
            if  state == "switch":
                stateToken = stateTokens[stateIndex]
                #print(str(stateToken.line)+","+str(i)+": "+state + " " + str(stateIndex) + " " + stateToken.type)
                if stateToken.line == i:
                    stateIndex+=1
                    if stateToken.type == "break":
                        state = "switch"
                if stateToken.type == "break":
                    indentationOffset +=1
                #print(stateToken.type + " " + str(indentation)+" "+str(indentationOffset)+"\n"+line)

        overallIndentation = indentation+indentationOffset
        result = re.search("^\t{"+str(overallIndentation)+"}(?! ).*$",line)
        if (result == None):
            vera.report(file,i,"Bad line indentation, expected to start with "+str(overallIndentation)+" tab(s).")
        i += 1



def indentationAnalysis():
    """
        For every file we will use the recursive function acceptPairs, which in this case will
        return the top-level bracer couples list, and we'll check for zero indentation between those.
    """
    global state, stateIndex, index, end, parens, commentLineDic, stateTokens, allLines, indentation, file
    for file in vera.getSourceFileNames():
        parens = vera.getTokens(file, 1, 0, -1, -1, ["leftbrace","rightbrace"])
        stateTokens = vera.getTokens(file, 1, 0, -1, -1, ["switch","break","case","default"])
        commentTokens = vera.getTokens(file, 1, 0, -1, -1, ["ccomment","cppcomment"])
        commentLineDic = {}
        for comment in commentTokens:
            commentLineDic[comment.line] = comment

        allLines = vera.getAllLines(file)
        state, stateIndex, index = None, 0, 0
        end = len(parens)
        indentation = 0
        topLevelBracers = acceptPairs()
        if (index != end):
            vera.report(file,parens[index].line, "Excessive closing bracket?")
        indentation = -1
        checkFragmentedIndentation(1,len(allLines)-1,topLevelBracers)

