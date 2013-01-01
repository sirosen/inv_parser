#Author -- Stephen Rosen

from __future__ import print_function
from xml_cleanup import make_name_conform, clean_attribute
import lxml.etree as etree

#name_to_exp_map is a map from field names to xpath expressions
#tree is an etree containing a system profiler report
def lookup(name_to_exp_map, tree, log=None):
    ret = {}
    for name in name_to_exp_map:
        exp = name_to_exp_map[name]
        if log: print(name + " : " + exp,file=log)
        ret[name] = tree.xpath(exp)
    return ret

def make_xml(profile):
    return etree.tostring(profile, pretty_print=True)

def from_xml(filename):
    return etree.parse(filename)

def build_profile(filename,machine_name,machine_location):
    def get_indent(line): return len(line) - len(line.lstrip())

    #this value tracks the indentation of the previous non-empty line
    prev_indent = -1

    #etree containing the system profiler report
    profile = etree.Element('profile',name=machine_name,location=machine_location)
    #stack of nodes, in order of nesting
    #we initialize with profile and -1 to reduce the number of edge cases to handle
    locations = [(prev_indent,profile)]

    #insert a key,value pair into the current dictionary, (key => [ ..., (val,{})])
    #push the new dictionary associated with that key, recording the current indent, onto the location stack
    def insert(row,cur_indent):
        node_name = row[0]
        (indent,parent_node) = locations[-1]

        #this check ensures that lines without colons will still be safe
        node_val = ''
        if len(row) > 1:
            node_val = row[1].strip()

        #Create an etree for the new node, and add it to the parent as a child
        new_node=etree.Element(make_name_conform(node_name),
                               val=clean_attribute(node_val),
                               name=clean_attribute(node_name))
        parent_node.append(new_node)
        locations.append((cur_indent,new_node))

    ######
    #Main Function Body
    ######
    with open(filename) as f:
        for line in f:
            #skip empty lines
            if line.strip('\r\n ') == '': continue
            #get the line indent and break it on the first semicolon
            cur_indent = get_indent(line)
            line = line.strip()
            row = line.split(":", 1)

            #going deeper into the structure
            if prev_indent < cur_indent:
                insert(row,cur_indent)
            #coming back out
            elif prev_indent > cur_indent:
                (tmp_indent, _) = locations[-1]
                while cur_indent <= tmp_indent: #find the last time we were as unindented as cur_indent
                    locations.pop()
                    (tmp_indent, cur_node) = locations[-1]
                insert(row,cur_indent)
            #adding values at a fixed depth
            elif prev_indent == cur_indent:
                #pop the other node off the stack, since insertions include a push, and they are at equal depth
                locations.pop()
                insert(row,cur_indent)
            prev_indent = cur_indent

    return profile
