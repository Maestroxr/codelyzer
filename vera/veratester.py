import subprocess as sub
import os
dir = os.path.dirname(os.path.realpath(__file__))
testsDir = dir + "\\tests"
filesIter = os.walk(testsDir)

path, _, fileList = next(filesIter)
relative = "C:\\Work\\AutoAssessment\\Analysis Tools\\lint"
print(fileList)
for file in fileList:
    splitFile = file.split('.')[-1]
    nameOnly, extension = ''.join(splitFile[:-1]), splitFile[-1]
    filePath = testsDir+"\\"+nameOnly
    if not extension in ["c","cpp"]:
        continue
    print(extension)
    p = sub.Popen(['vera++', '-d', '-R', 'M007', '--root', dir, testsDir+"\\"+file], stdout=sub.PIPE, stderr=sub.PIPE)
    output, errors = p.communicate()
    print(output)
    #print(errors)
    with open(filePath+".out",'w') as f:
        f.write(str(output))
    if os.path.isfile(filePath+".cmp"):

