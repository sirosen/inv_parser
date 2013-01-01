#Author -- Stephen Rosen
from __future__ import print_function
import shlex
import profiler, xml_cleanup

def config_parse(filename,log=None):
    xpath_map = {}
    db_inserts = {}
    if log: print('\n\n----------\nConfig file parsing.\n----------',file=log)
    with open(filename) as f:
        for line in f:
            line = line.strip().expandtabs()
            # (Not a comment or empty line)
            if line=="" or line[0] == "#": continue
            lineparts = shlex.split(line,comments=True,posix=False)
            lineparts = (lineparts[0],' '.join(lineparts[1:]))
            identifier = lineparts[0]
            if identifier == 'db-insert':
                key_value = [x.strip() for x in lineparts[1].strip().split(' ', 1)] #key_value[0] is the key, key_value[1] is the value
                if len(key_value) < 2:
                    if log: print(line + " <----- Is not a proper db insertion! Insufficient tokens.",file=log)
                    continue
                if log: print('db insertion: ' + str((key_value[0],key_value[1])) + '.',file=log)
                db_inserts[key_value[0]]=key_value[1]
            else:
                path = lineparts[1].strip()
                if log: print(identifier + ' is mapped to the "xpath" expression: ' + path,file=log)
                path = xml_cleanup.clean_xpath(path)
                if log: print('cleaned xpath expression: ' + path,file=log)
                xpath_map[identifier] = path
    return (xpath_map,db_inserts)

def xpath_lookup(profile,lookup_map,log=None):
    if log: print('\n\n----------\nEvaluating xpath expressions.\n----------',file=log)
    name_to_val=profiler.lookup(lookup_map,profile,log=log)
    if log:
        print('\n\n----------\nValues from xml lookups.\n----------',file=log)
        for colname in name_to_val:
            print(colname + ": " + str(name_to_val[colname]),file=log)
    return name_to_val

def make_profile(report,name,log=None,xmldump=None):
    def get_locs_string(name): ''
    if log: print('\n\n----------\nBuilding Profile Now.\n----------',file=log)
    profile=profiler.build_profile(report,name,get_locs_string(name))
    if xmldump:
        xmlstr = profiler.make_xml(profile)
        print(xmlstr,file=xmldump)
    return profile

def get_insertions(profile,config,log=None):
    def eval_expr(exp,valmap):
        exps=shlex.split(exp,posix=False) #set posix mode to false in order to preserve quotes
        for i in xrange(len(exps)):
            cur = exps[i]
            if cur == '': continue
            elif cur[0] == '"': exps[i]=exps[i][1:-1] #trim quotes
            else:
                exps[i]=';'.join(valmap[cur])
                if exps[i] == '': exps[i] = '?'
        return ''.join(exps)


    def eval_insertions(insertions,name_to_val,log=None):
        if log: print('\n\n----------\nEvaluating insertion expressions.\n----------',file=log)
        for colname in insertions:
            insertions[colname] = eval_expr(insertions[colname],name_to_val)

        if log:
            print('\n\n----------\nEvaluated db insertions.\n----------',file=log)
            for colname in insertions:
                print(colname + ': ' + insertions[colname],file=log)

        return insertions

    #parse config file into two types of expressions
    (lookup_map,insertions)=config_parse(config,log=log)
    #build a mapping from names to xpath lookup results
    name_to_val=xpath_lookup(profile,lookup_map,log)
    #build a mapping from insertion expressions to resultant strings
    insertions=eval_insertions(insertions,name_to_val,log)
    return insertions

def db_insert(insertions,profile,log=None):
    import MySQLdb

    def get_serial(profile):
        xpath_expr=xml_cleanup.clean_xpath('//Hardware/Hardware Overview/Serial Number (system)/@val')
        name_to_val=xpath_lookup(profile,{'serial':xpath_expr})
        return name_to_val['serial']

    serial=get_serial(profile)
    if log: print('\n\n----------\nExecuting db insertions.\n----------',file=log)
    db_conn = MySQLdb.connect('server','db','password','user')
    cursor = db_conn.cursor()
    for colname in insertions:
        val = insertions[colname]
        try:
            if log: print(colname + ' : ' + val,file=log)
            #Use cursor.execute to insert values into the DB
        except MySQLdb.Error, e:
            if log: print('Hit MySQL error: %s' %e,file=log)


def main(config,name,report,suppress_insert=True,log=None,xmldump=None):
    profile=make_profile(report,name,log,xmldump)
    if xmldump: xmldump.close()
    insertions=get_insertions(profile,config,log)
    insertions['location'] = get_locs_string(name)
    if not suppress_insert: db_insert(insertions,profile,log)
    if log: log.close()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Parses the textual output of system_profiler into a recursive dictionary, constructs xml from that dictionary, and performs database insertions from based on the expressions in the config file.')
    parser.add_argument('-r','--report',required=True,help='Output from system_profiler.')
    parser.add_argument('-n','--name',required=True,help='Name of the machine for which this system_profiler report was generated.')
    parser.add_argument('-c','--config',required=True,help='Config file.')
    parser.add_argument('-l','--logfile',type=argparse.FileType('w'),help='Names the file to which all debugging output will be logged.')
    parser.add_argument('-x','--xmldump',type=argparse.FileType('w'),help='Names the file to which the generated xml will be dumped.')
    parser.add_argument('-s','--suppress',action='store_true',default=False,help='Suppresses database insertions when true.')

    args = parser.parse_args(sys.argv[1:])
    report = args.report
    name = args.name
    config = args.config
    log = args.logfile
    xmldump = args.xmldump
    suppress = args.suppress

    main(config,name,report,suppress_insert=suppress,log=log,xmldump=xmldump)
