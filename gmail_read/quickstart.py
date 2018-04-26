"""
Shows basic usage of the Gmail API.
Lists the user's Gmail labels.
"""
from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from gmail_api_wrapper.crud.read import GmailAPIReadWrapper


# Setup the Gmail API
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('gmail', 'v1', http=creds.authorize(Http()))

# Call the Gmail API
results = service.users().labels().list(userId='me').execute()
#print(results)
labels = results.get('labels', [])

#watch_mail = service.users().history().list(userId='me', labelId='Label_11').execute()
watch_mail =  service.users().watch(userId='me', body='ACTION REQUIRED: pekrone.ddns.net is Expiring Soon').execute()
mail_topicName =watch_mail.get('topicName',[])

#watch_mail = service.users().watch()
print(mail_topicName)


## Wrapper api
#labels_1 = []
#gmail_api = GmailAPIReadWrapper()

gmail_api.check_new_mail()

#print(gmail_api.get_labels()) 
"""
labels_1 = gmail_api.get_labels()
for i in labels_1 :
 print(labels_a[i]) 
"""
if not labels:
    print('No labels found.')
else:
    print('Labels:')
    for label in labels:
        print(label['name'],'  ' ,label['id'])
    
        
     
#if label['name'] == "NO-IP"        
