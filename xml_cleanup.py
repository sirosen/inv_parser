#Author -- Stephen Rosen

from __future__ import print_function
import lxml.etree as etree
import string, re

#cleans up the xpath expression for use in our xml, respecting xpath syntax
def clean_xpath(exp):
    def clean_single_exp(exp):
        #prepend a '_' to each section, and clean it up for our xml
        parts = re.split('(?<!\\\\)/',exp)
        for i in xrange(len(parts)):
            part = parts[i]
            if part == '' \
                or part[0] == '@' or part[0] == '*' or part[0] == '.'\
                or (len(part) >= 6 and part[0:6] == 'node()'):
                    continue
            else:
                parts[i] = make_name_conform(part.strip())
        return "/".join(parts)
    #split into multiple xpath expressions on OR, conform, then merge
    expressions = exp.split('|')
    return ' | '.join([clean_single_exp(x.strip()) for x in expressions])


def make_name_conform(exp):
    #can't use a regex for this because bracket nesting is recursive
    exp=list(exp) #convert to list of chars
    #We used to think we could just explicitly check a set of bad characters, oh, how naive we were...
    goodchars=string.letters+string.digits
    brackets = 0
    #replace bad chars with underscores, unless they are in brackets
    for i in xrange(len(exp)):
        cur = exp[i]
        if cur == '[': brackets+=1
        elif cur == ']':
            brackets-=1
            if brackets < 0: brackets = 0
        elif brackets == 0:
            if cur not in goodchars:
                exp[i]='_'+str(ord(cur))+'_'
                if cur == '\\': exp[i] =''
            elif cur == '/':
                if (i > 0) and exp[i-1] == '\\':
                    exp[i]='_'
                    exp[i-1]=''
    exp=''.join(exp) #convert back into a string
    return '_'+exp

#sadly, the attributes are not always safe in xml
def clean_attribute(attribute):
    attribute=list(attribute)
    for i in xrange(len(attribute)):
        if attribute[i] in '&<"' or attribute[i] not in string.printable:
            attribute[i] = '_'+str(ord(attribute[i]))+'_'
    return ''.join(attribute)
