import re
import os

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

interfaceFileName = 'IExampleClass.h'
interfaceClassName = interfaceFileName[0:interfaceFileName.rindex('.')]
mockClassName = interfaceClassName[1:] + 'Mock'
headerName = convert(mockClassName) + '_H_'

output = '#ifndef ' + headerName + '\n'
output+= '#define ' + headerName + '\n'
output+= '#include "' + interfaceFileName + '"\n\n\n'
output+= 'class ' + mockClassName + ' : public ' + interfaceClassName + '\n{\n'
output+= 'public:\n'

with open(interfaceFileName) as f:
    fileText = f.read()

expression = r'virtual\ (.*(<.*>))\ (?P<funcName>\S*)\((([^()]+(<.*>)?)*)\)( const)?( \= 0)?;'

m = re.findall(expression, fileText)

for found in m :
    line = 'MOCK_'
    if found[6] == ' const':
        line = line + 'CONST_'

    line = line + 'METHOD'

    arguments = countArgs(found[3])
    line = line + str(arguments)

    line = line + '(' + found[2] + ', ' + found[0] + '(' + found[3] + '));'
    output+= '\t' + line + '\n'

output+= '};\n\n'
output+= '#endif // ' + headerName

mockFileName = mockClassName + '.h'
with open(mockFileName, 'w', encoding='utf-8') as f:
    f.write(output)
