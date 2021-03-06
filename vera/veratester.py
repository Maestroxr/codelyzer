import subprocess as sub
import os, os.path
import difflib
from timeit import timeit
import sys

def testFiles(fileList, dir, cmdMaker,reportTime = False, files = set()):
    diffList = []
    for file in fileList:
        if files and file not in files:
            continue

        splitFile = os.path.splitext(file)
        nameOnly, extension = splitFile[0], splitFile[1]
        cmd = cmdMaker(nameOnly,extension)
        filePath = dir+"\\"+nameOnly
        if not extension in [".c",".cpp"]:
            continue

        p = sub.Popen(cmd, stdout=sub.PIPE, stderr=sub.PIPE)
        output, errors = p.communicate()
        #print(output.decode('ascii'))
        if errors:
            print("file:"+nameOnly+" errors:"+str(errors.decode('ascii')))
            continue
        else:
            print("file:"+nameOnly+" OK!")
        with open(filePath+".out",'wb') as outputFile:
            outputFile.write(output)

        with open(filePath + ".out", 'r') as outputFile:
            if os.path.isfile(filePath+".cmp"):
                with open(filePath + ".cmp", 'r') as cmpFile:
                    diff = difflib.unified_diff(
                        cmpFile.readlines(),
                        outputFile.readlines())

                    for line in diff:
                        diffList.append((file,line))
        if reportTime:
            repeat = 10
            time = timeit("sub.Popen(list(" + str(cmd) + "), stdout=sub.PIPE, stderr=sub.PIPE).communicate()",
                          setup="import subprocess as sub", number=repeat)
            print("Time "+nameOnly+": " + str(time*1000/repeat))
    for file, differentLine in diffList:
        #if differentLine[:3] in ["---", "+++"] or differentLine[0] in ["@","-"]: continue
        print("In file:"+file+" non-matching line:<"+differentLine+">")
        pass


os.chdir((".."))
dir = os.path.dirname(os.path.realpath(__file__))
testsDir = dir + "\\tests\\"
filesIter = os.walk(testsDir)

path, _, fileList = next(filesIter)


#testFiles(fileList, testsDir,lambda f,e:  ['vera++', '-d', '--root', dir,'-P', 'sanitizer-on=False', testsDir+f+e ])
sanitizerDir = testsDir+"sanitizer"
filesIter = os.walk(sanitizerDir)
path, _, fileList = next(filesIter)
#testFiles(fileList, sanitizerDir, lambda f,e: ['vera++', '-d', '--root', dir,'-P', 'sanitizer-dir='+sanitizerDir,'-P', 'sanitizer-file='+f+".log", sanitizerDir+"\\"+f+e ],False)

testsDir = dir + "\\examples\\"
fileList = ["nginx.c","mergesort.c", "convolutional_layer.c"]
#testFiles(fileList, testsDir,lambda f,e:  ['vera++', '-d', '--root', dir,'-P', 'sanitizer-on=False', testsDir+f+e ],True)

testsDir = dir + "\\tests\\weirdos\\"
filesIter = os.walk(testsDir)
path, _, fileList = next(filesIter)
#testFiles(fileList, testsDir,lambda f,e:  ['vera++', '-d', '--root', dir,'-P', 'sanitizer-on=False', testsDir+f+e ])

testsDir = os.path.abspath(os.path.join(os.path.join(dir, os.pardir),os.pardir)) + "\\temp\\12-02\\"
print(testsDir)
filesIter = os.walk(testsDir)
path, _, fileList = next(filesIter)
testFiles(fileList, testsDir,lambda f,e:  ['vera++', '-d', '--root', dir,'-P', 'sanitizer-dir='+testsDir+"sanitizer", testsDir+f+e ])

