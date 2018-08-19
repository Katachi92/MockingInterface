import re
import os
import sys

def countArgs(insideBrackets) :
    insideBrackets = insideBrackets.strip()

    if (not insideBrackets) or (insideBrackets == 'void'):
        return 0

    bracketsDepth = 0
    words = 1

    for char in insideBrackets :
        if char in '({<' :
            bracketsDepth = bracketsDepth + 1
        elif char in ')}>' :
            bracketsDepth = bracketsDepth - 1
        elif char == ',' :
            words = words + 1

    return words

def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).upper()

class NecessaryNames:
    interfaceFile = ''
    interfaceClass = ''
    mockClass = ''
    header = ''
    mockFile = ''
    fileDir = ''

    def __init__(self, interfaceFilePath):
        interfaceFileName = os.path.basename(interfaceFilePath)
        self.isFileNameCorrect(interfaceFileName)
        fileDir = os.path.dirname(interfaceFilePath)
        print(fileDir)
        self.interfaceFile = interfaceFileName
        self.interfaceClass = self.interfaceFile[0:self.interfaceFile.rindex('.')]
        self.mockClass = self.interfaceClass[1:] + 'Mock'
        self.header = convert(self.mockClass) + '_H_'
        self.mockFile = self.mockClass + '.h'

    def isFileNameCorrect(self, fileName):
        if(None == re.match('^I.*\.h$', fileName)):
            raise Exception('File has incorrect name')
        return True

    def getInputFileDir(self):
        return os.path.join(self.fileDir, self.interfaceFile)

    def getOutputFileDir(self):
        return os.path.join(self.fileDir, self.mockFile)

def main(argv):
    interfaceFilePath = os.path.abspath(argv[0])
    names = NecessaryNames(interfaceFilePath)

    output = '#ifndef ' + names.header + '\n'
    output+= '#define ' + names.header + '\n'
    output+= '#include <gmock/gmock.h>\n\n'
    output+= '#include "' + names.interfaceFile + '"\n\n'
    output+= 'class ' + names.mockClass + ' : public ' + names.interfaceClass + '\n{\n'
    output+= 'public:\n'

    with open(names.getInputFileDir()) as f:
        fileText = f.read()

    virtualFunctionRegex = r'virtual\ (.*(<.*>))\ (?P<funcName>\S*)\((([^()]+(<.*>)?)*)\)( const)?( \= 0)?;'

    matches = re.findall(virtualFunctionRegex, fileText)

    for match in matches :
        line = 'MOCK_'
        if match[6] == ' const':
            line = line + 'CONST_'

        line = line + 'METHOD'

        arguments = countArgs(match[3])
        line = line + str(arguments)

        line = line + '(' + match[2] + ', ' + match[0] + '(' + match[3] + '));'
        output+= '\t' + line + '\n'

    output+= '};\n\n'
    output+= '#endif // ' + names.header

    with open(names.getOutputFileDir(), 'w', encoding='utf-8') as f:
        f.write(output)

if __name__ == '__main__' :
    main(sys.argv[1:])
