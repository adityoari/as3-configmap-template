# Simple Python3 script to generate AS3 ConfigMap YAML file using Jinja2 template 

import sys
from jinja2 import Environment as Envi, FileSystemLoader as FSload
from pprint import pprint as pp

# Constant global variables
CONST_monitors_env = 7
CONST_monitors_noenv = 20

# Parse command-line arguments: <template-directory>/<template-file>
# return names of template directory and template file
def parseArgs():
    print('sys argv len = {}'.format(len(sys.argv)))
    for i in sys.argv:
            print('i : {}'.format(i))
    if len(sys.argv)>=3:
            templDir,templFile = sys.argv[1].split('/')
            dataFile = sys.argv[2]
    else:
            print('Usage : ' + sys.argv[0] + ' <template-directory>/<template-file> <data-csv>')
            exit(1)
    return templDir,templFile,dataFile

# Load .j2 file containing AS3 ConfigMap template from the directory
# return jinja2 Environment handler and FSLoader handler
def loadTemplate(templDir, templFile):
    envi = Envi(loader=FSload(templDir))
    templ = envi.get_template(templFile)
    return envi,templ

# Load .csv file containing lines of key,value[,value2,...]
# return List of data lines
def loadData(dataFile):
    with open(dataFile, 'r') as f:
        dataLines = f.readlines()
    return dataLines

# Parse List containing CSV data file lines
# return Dict of DataKey,DataValue(s)
def parseDataLines(dataLines):
    retDict = {}
    lineDict = {}
    for lin in dataLines:
        lineList = lin.strip().split(',')
        k = lineList[0]
        if k:
            if len(lineList)>2:
                v = lineList[1:]
            elif len(lineList)==2:
                v = lineList[1]
            try:
                if v:
                    retDict[k] = v
            except:
                continue
    return retDict

# Post-process data Dict to add template-compatible properties
# return processed Dict
def processDataDict(dataDict):
    
    # Add lowercase Site & Env
    dataDict['DATA_site_lower'] = dataDict['APP_site'].lower()
    if 'APP_env' in dataDict.keys():
        dataDict['DATA_env_lower'] = dataDict['APP_env'].lower()
    else:
        dataDict['DATA_env_lower'] = ''
        
    # Add Monitor list
    if 'APP_env' in dataDict.keys():
        dataDict['DATA_monitors'] = list(range(1,CONST_monitors_env+1))
    else:
        dataDict['DATA_monitors'] = list(range(1,CONST_monitors_noenv+1))

    # Add indices parameter based on instances
    if int(dataDict['APP_instances'])>1:
        dataDict['DATA_indices'] = [str(x) for x in list(range(1,1+int(dataDict['APP_instances'])))]
    else:
        dataDict['DATA_indices'] = [str(1)]
    
    # build instance-keyed VIP dict
    vipDict = {}
    vipFirst = dataDict['APP_vip1']
    for instanc in dataDict['DATA_indices']:
        vipDict[instanc] = {}
        vipDict[instanc]['ip'] = ipPlus(vipFirst, int(instanc)-1)
        vipDict[instanc]['name'] = vipDict[instanc]['ip'].replace('.', '_')
    dataDict['DATA_vipdict'] = vipDict
    
    # build TCP port Dict
    tcpDict = {}
    increm = ''
    if len(dataDict['APP_ports_tcp'])==3:
        tcpFront,tcpBack1,increm = dataDict['APP_ports_tcp']
    if len(dataDict['APP_ports_tcp'])==2:
        tcpFront,tcpBack1 = dataDict['APP_ports_tcp']
    for instanc in dataDict['DATA_indices']:
        if increm.startswith('inc'):
            tcpDict[instanc] = str(int(tcpBack1) + int(instanc) - 1)
        else:
            tcpDict[instanc] = str(int(tcpBack1))
    dataDict['DATA_tcpfront'] = tcpFront
    dataDict['DATA_tcpbacks'] = tcpDict

    # build UDP port Dict
    udpDict = {}
    increm = ''
    if len(dataDict['APP_ports_udp'])==3:
        udpFront,udpBack1,increm = dataDict['APP_ports_udp']
    elif len(dataDict['APP_ports_udp'])==2:
        udpFront,udpBack1 = dataDict['APP_ports_udp']
    for instanc in dataDict['DATA_indices']:
        if increm.startswith('inc'):
            udpDict[instanc] = str(int(udpBack1) + int(instanc) - 1)
        else:
            udpDict[instanc] = str(int(udpBack1))
    dataDict['DATA_udpfront'] = udpFront
    dataDict['DATA_udpbacks'] = udpDict

    # Add prefix based on instance,client,site,env,port
    if 'APP_env' in dataDict.keys() and dataDict['APP_env']:
        dataDict['DATA_prefixtcp'] = dataDict['APP_client'] + '-' + dataDict['DATA_site_lower'] + '-' + dataDict['DATA_env_lower'] + '-' + dataDict['DATA_tcpfront']
        dataDict['DATA_prefixudp'] = dataDict['APP_client'] + '-' + dataDict['DATA_site_lower'] + '-' + dataDict['DATA_env_lower'] + '-' + dataDict['DATA_udpfront']
    else:
        dataDict['DATA_prefixtcp'] = dataDict['APP_client'] + '-' + dataDict['DATA_site_lower'] + '-' + dataDict['DATA_tcpfront']
        dataDict['DATA_prefixudp'] = dataDict['APP_client'] + '-' + dataDict['DATA_site_lower'] + '-' + dataDict['DATA_udpfront']


    return dataDict

# increase last octet of an IPv4 address
def ipPlus(baseIP, increm):
    ipList = baseIP.split('.')
    oct4 = int(ipList[3]) + increm
    return '.'.join(ipList[0:3] + [ str(oct4) ])

def main():
    templDir,templFile,dataFile = parseArgs()
    envi,templ = loadTemplate(templDir, templFile)

    dataList = loadData(dataFile)
    dataDict = parseDataLines(dataList)
    dataDict = processDataDict(dataDict)
    pp(dataDict)

    as3 = templ.render(data=dataDict)
    
    outFile = dataFile.replace('.csv', '.out.yaml')
    with open(outFile, 'w') as f:
        print('{}'.format(as3), file=f)

if __name__ == '__main__':
    main()
