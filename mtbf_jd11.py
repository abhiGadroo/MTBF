#Logging included
#optimized cases
#working with dev11

import logging
import getpass
import requests
import json
from requests.auth import HTTPBasicAuth
import datetime
import time
USER_NAME = raw_input("JIRA UserName: ")
PASS = getpass.getpass('Password:')
now = datetime.datetime.now()
logging.basicConfig(filename='logs.log', level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)
#IQL for current day productivity
r= requests.get("https://jd11.labs.greyorange.com/jira/rest/insight/1.0/iql/objects?objectSchemaId=4&iql=ObjectType=Productivity%20AND%20Datetime%20%3E%20startOfDay()",auth=(USER_NAME,PASS))
totalCreatedToday = r.json()['totalFilterCount']
logging.info("Total Reports Recieved Today : -" + str(totalCreatedToday))
x = r.json()
def createIssue():
    try:
        url = "https://jd11.labs.greyorange.com/jira/rest/api/2/issue"
        req4 = requests.post(url,auth=(USER_NAME,PASS),data = json.dumps(dataForIssue),headers= headers)
        logging.info ("Issue Created for mntce"+str(req4.json()['key']))
    except:
        logging.warning( "ERROR CREATING ISSUE")
        logging.warning( req4.status_code)
    try:
        newDate = {'objectAttributeValues': [{'value': str(now)}]}
        logging.info( newDate)
        q= r2['objectEntries'][0]['attributes'][r2attr2]['id']
        req5 = requests.put("https://jd11.labs.greyorange.com/jira/rest/insight/1.0/objectattribute/"+str(q), auth=(USER_NAME,PASS),data= json.dumps(newDate),headers= headers)    
    except :
        logging.warning( "Doesn't exists or didnt posted")
if totalCreatedToday == 0:
    logging.error ("Error Reading Objects from Productivity OR haven't recieved reports yet")
else:
    attr = 6
    r2attr = 4
    attr2 = 6
    for y in range(totalCreatedToday):
        logging.info ("<____________>")
        attr = 6
        attr2 = 6
        r2attr = 4
        r2attr2 = 5
        r2attr3 = 6
        headers = {'content-type': 'application/json'}
        for pop in range (attr,16):

            sysAr = x['objectEntries'][y]['attributes'][2]['objectAttributeValues'][0]['referencedObject']['name']
            req2  =  requests.get("https://jd11.labs.greyorange.com/jira/rest/insight/1.0/iql/objects?objectSchemaId=4&iql=ObjectType=System%20AND%20%22Name%22%20IN%20(%22"+sysAr+"%22)", auth=(USER_NAME,PASS))
            r2 = req2.json()
            try:
                
                dataForIssue = {
  "fields": {
    "project": {
      "id": "10149"
    },
      "summary": "Warning - Maintenance Required"+sysAr,
      "issuetype": {
      "id": "10119"
    },
    "reporter": {
      "name": "abhimanyu.g"
    },
    "description": "Arm"+str(attr-5)+" Maintenance Required. Please update Arm No. "+str(attr-5)+ "value "+str(r2['objectEntries'][0]['attributes'][r2attr]['objectAttributeValues'][0]['value'])+"to 0, of object "+str(r2['objectEntries'][0]['attributes'][r2attr]['objectId'])+" when repairing is done." 
  }
}
            except IndexError:
                continue
            logging.info (sysAr)
            logging.info ("<-- Arm" +str(attr-5)+"(Today's Data/Old System ID Data) -->")
            try:
                totalSum = int(x['objectEntries'][y]['attributes'][attr2]['objectAttributeValues'][0]['value'])+int(r2['objectEntries'][0]['attributes'][r2attr]['objectAttributeValues'][0]['value'])
                logging.info( "Total Packets" +str(totalSum))
            except IndexError:
                pass
            try:
                rx= requests.get("https://jd11.labs.greyorange.com/jira/rest/insight/1.0/object/8707",auth=("abhimanyu.g","Vodka92@"))
                threshold = rx.json()['attributes'][4]['objectAttributeValues'][0]['value']
                uptime_threshold = rx.json()['attributes'][5]['objectAttributeValues'][0]['value']
                lastUpdated = str(r2['objectEntries'][0]['attributes'][r2attr2]['objectAttributeValues'][0]['value'])
                logging.info ("Last Updated On "+lastUpdated)
                lasUpdated_Epoch = time.mktime(datetime.datetime.strptime(lastUpdated, "%Y-%m-%d %H:%M:%S.%f").timetuple())
                latest_Epoch = (now-datetime.datetime(1970,1,1)).total_seconds()
                time_diff = latest_Epoch - lasUpdated_Epoch
            except: 
                logging.warning( "last updated date not found")
                time_diff = 0
            try:
                totalUptime = int(x['objectEntries'][y]['attributes'][attr2+1]['objectAttributeValues'][0]['value'])+int(r2['objectEntries'][0]['attributes'][r2attr3]['objectAttributeValues'][0]['value'])
                logging.info ("Total Uptime " + str(totalUptime))
                if totalSum > int(threshold):
                    if time_diff > 347006:
                        logging.info( "Time Difference " +str(time_diff))
                        createIssue()
                    elif time_diff < 347006:
                        logging.info( "Time Difference " +str(time_diff)+" is less than threshold. Ticket recently created.")
                elif totalUptime > int(uptime_threshold):
                    if time_diff > 347006:
                        logging.info( "Time Difference " +str(time_diff))
                        createIssue()
                    elif time_diff < 347006:
                        logging.info( "Time Difference " +str(time_diff)+" is less than threshold. Ticket recently created.")
                elif totalSum < int(threshold) and totalUptime < int(uptime_threshold):
                    logging.info("Total Sum"+str(totalSum)+"Total Uptime"+str(totalUptime)+"Time diff"+str(time_diff))
                    logging.info("Total Sum/Arm uptime status/Time difference seems to be less than 10/347006/100")
                elif totalSum > int(threshold) and time_diff == 0 and totalUptime <int(uptime_threshold):
                    logging.info("Last ticket never created")
                    createIssue()
                elif totalSum > int(threshold) and time_diff == 0 and totalUptime >int(uptime_threshold):
                    logging.info("Last ticket never created")
                    createIssue()
                elif totalSum < int(threshold) and time_diff == 0 and totalUptime > int(uptime_threshold):
                    logging.info("Last ticket never created")
                    createIssue()
                else:
                    logging.info("Total Sum"+str(totalSum)+"Total Uptime"+str(totalUptime)+"Time diff"+str(time_diff))
                    logging.info("Ticket Already Exists!")

            except IndexError:
                if totalSum > int(threshold) or totalUptime > uptime_threshold:
                    logging.info("Last Status Change not found! Arm crossed Threshold!! Creating issue.")
                    createIssue()
            try:
                p =  r2['objectEntries'][0]['attributes'][r2attr]['id']
                logging.info("Sending totalSum to SystemID"+str(p))  
            except :
                logging.info("None")
            try:
                data = {'objectAttributeValues': [{'value': +totalSum}]}
                uptimedata = {'objectAttributeValues': [{'value': +totalUptime}]}
            except IndexError:
                logging.info("None")
            try:
                req3 = requests.put("https://jd11.labs.greyorange.com/jira/rest/insight/1.0/objectattribute/"+str(p), auth=(USER_NAME,PASS),data= json.dumps(data),headers= headers)
            except IndexError:
                logging.warning("Failed to Post Arm data in insight!")
            if (req3.status_code == 200):
                logging.info("Sent Arm Data")
            else:
                logging.info(req3.status_code)
            try:
                q= r2['objectEntries'][0]['attributes'][r2attr3]['id']
                req4 = requests.put("https://jd11.labs.greyorange.com/jira/rest/insight/1.0/objectattribute/"+str(q), auth=(USER_NAME,PASS),data= json.dumps(uptimedata),headers= headers)
            except :
                logging.warning("Failed to Post Uptime data in insight!")
            if (req4.status_code == 200):
                logging.info("Sent Uptime data")
            else:
                logging.info(req4.status_code)
            attr = int(attr)+1
            attr2 = int(attr2)+2
            r2attr = int(r2attr)+3
            r2attr2 = int(r2attr2)+3
            r2attr3 = int(r2attr3)+3
    logging.info("SKIPPING - "+str(sysAr))
logging.info(" _______________")
print "done"
