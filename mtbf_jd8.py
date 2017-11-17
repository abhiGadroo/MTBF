USER_NAME = raw_input("Enter JIRA UserName: ")
PASS = raw_input("Enter JIRA Password: ")
import requests
import json
from requests.auth import HTTPBasicAuth
#IQL for current day productivity
r= requests.get("https://jd8.labs.greyorange.com/jira/rest/insight/1.0/iql/objects?objectSchemaId=3&iql=ObjectType=Productivity%20AND%20Datetime%20%3E%20startOfDay()",auth=(USER_NAME,PASS))
totalCreatedToday = r.json()['totalFilterCount']
print "Total Reports Recieved Today : -" + str(totalCreatedToday)
x = r.json()
if totalCreatedToday == 0:
    print "Error Reading Objects from Productivity OR haven't recieved reports yet"
else:
    attr = 6
    r2attr = 4
    for y in range(totalCreatedToday):
        print "<____________>"
        attr = 6
        r2attr = 4
        headers = {'content-type': 'application/json'}
        for pop in range (attr,16):

            sysAr = x['objectEntries'][y]['attributes'][4]['objectAttributeValues'][0]['referencedObject']['name']
            req2  =  requests.get("https://jd8.labs.greyorange.com/jira/rest/insight/1.0/iql/objects?objectSchemaId=3&iql=ObjectType=System%20AND%20%22Name%22%20IN%20(%22"+sysAr+"%22)", auth=(USER_NAME,PASS))
            r2 = req2.json()
            dataForIssue = {
  "fields": {
    "project": {
      "id": "10121"
    },
      "summary": "Warning - Maintenance Required"+sysAr,
      "issuetype": {
      "id": "10100"
    },
    "reporter": {
      "name": "abhimanyu.g"
    },
    "description": "Arm"+str(attr-5)+" Maintenance Required. Please update Arm No. "+str(attr-5)+ "value "+str(r2['objectEntries'][0]['attributes'][r2attr]['objectAttributeValues'][0]['value'])+"to 0, of object "+str(r2['objectEntries'][0]['attributes'][r2attr]['objectId'])+" when repairing is done." 
  }
}
            print sysAr
            print "<-- Arm" +str(attr-5)+"(Today's Data/Old System ID Data) -->"
            try:
                print "Old - "+ str(x['objectEntries'][y]['attributes'][attr]['objectAttributeValues'][0]['value'])
            except IndexError:
                continue
            try:
                print "New - "+ str(r2['objectEntries'][0]['attributes'][r2attr]['objectAttributeValues'][0]['value'])
            except IndexError:
                print "None"
            try:
                totalSum = int(x['objectEntries'][y]['attributes'][attr]['objectAttributeValues'][0]['value'])+int(r2['objectEntries'][0]['attributes'][r2attr]['objectAttributeValues'][0]['value'])
                print "Total: "+str(totalSum) 
                if totalSum > 10:
                    try:
                        url = "https://jd8.labs.greyorange.com/jira/rest/api/2/issue"
                        req4 = requests.post(url,auth=(USER_NAME,PASS),data = json.dumps(dataForIssue),headers= headers)
                        print "Issue Created for mntce"+str(req4.json()['key'])
                    except:
                        print "ERROR CREATING ISSUE"
                        print req4.status_code
            except IndexError:
                print "None"
            try:
                p =  r2['objectEntries'][0]['attributes'][r2attr]['id']
                print "Sending totalSum to SystemID"+str(p)  
            except IndexError:
                print "None"
            try:
                data = {'objectAttributeValues': [{'value': +totalSum}]}
            except IndexError:
                print "None"
            try:
                req3 = requests.put("https://jd8.labs.greyorange.com/jira/rest/insight/1.0/objectattribute/"+str(p), auth=(USER_NAME,PASS),data= json.dumps(data),headers= headers)
            except IndexError:
                print "None"
            if (req3.status_code == 200):
                print "Sent"
            else:
                print "Error Sending Data"
            attr = int(attr)+1
            r2attr = int(r2attr)+1
    #print "SKIPPING - "+str(sysAr)
print " _______________"
