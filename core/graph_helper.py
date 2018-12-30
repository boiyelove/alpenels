from requests_oauthlib import OAuth2Session
import json
import pprint


graph_url = 'https://graph.microsoft.com/v1.0'
graph_beta_url = 'https://graph.microsoft.com/beta'

def get_user(token):
  graph_client = OAuth2Session(token=token)
  user = graph_client.get('{0}/me'.format(graph_url))
  return user.json()
  

def get_calendar_events(token):
  graph_client = OAuth2Session(token=token)

  # Configure query parameters to
  # modify the results
  query_params = {
    '$select': 'subject,organizer,start,end',
    '$orderby': 'createdDateTime DESC'
  }
  events = graph_client.get('{0}/me/events'.format(graph_url), params=query_params)
  return events.json()

def get_contact_list(token):
  graph_client = OAuth2Session(token=token)
  contact_list = graph_client.get('{0}/me/contacts'.format(graph_url))
  return contact_list.json()


class GraphClient:
    def __init__(self, token):
      self.token = token
      self.graph_client = OAuth2Session(token=token)


class MailGraph(GraphClient):

  def get_mails(self):
    mails = self.graph_client.get('{0}/me/messages'.format(graph_url))
    '''
    HTTP/1.1 200 OK
    Content-type: application/json
    Content-length: 317

    {
      "value": [
        {
          "receivedDateTime": "datetime-value",
          "sentDateTime": "datetime-value",
          "hasAttachments": true,
          "subject": "subject-value",
          "body": {
            "contentType": "",
            "content": "content-value"
          },
          "bodyPreview": "bodyPreview-value"
        }
      ]
    }
    '''
    return mails.json()

  def get_inbox(self):
    inbox = self.graph_client.get("{0}/me/mailFolders('Inbox')/messages".format(graph_url))
    return inbox.json()

  def list_mailboxFolders(self):
    mailfolder_list = self.graph_client.get('{0}/me/mailFolders'.format(graph_url))
    '''
    SAMPLE RESPONSE
    HTTP/1.1 200 OK
    Content-type: application/json
    Content-length: 232

    {
      "value": [
        {
          "displayName": "displayName-value",
          "parentFolderId": "parentFolderId-value",
          "childFolderCount": 99,
          "unreadItemCount": 99,
          "totalItemCount": 99,
          "id": "id-value"
        }
      ]
    }
    '''
    return mailfolder_list.json()

  def get_folder_messages(self, id):
    folder_messages = self.graph_client.get('{0}/me/mailFolders/{1}/messages'.format(graph_url, id))
    return folder_messages.json()



  def create_draft_mail(self):
    body = {
    "contentType":"HTML",
    "content": "They were <b> awesome</b>!"
    }
    query_params = {
    'subject': "this is the subject",
    'importance': 'low',
    'body': body,
    "toRecipients":[
    {
    "emailAddress": {
            "address": "daahrmmieboiye+test1@gmail.com"
        }
      }
    ],

    }

  def send_mail(self, to=[], subject=None, body=None, save_to_sent=False, cc=[]):
    rc_list = [{'emailAddress': {'Address':address}} for address in to]
    email_msg = {'Message': {'Subject': subject,
                        'Body': {'ContentType': 'HTML', 'Content': body},
                        'toRecipients': rc_list},
                        'saveToSentItems': True}
    # data = {}
    # data["message"] = {}
    # data["message"] = { 'Subject': 'Meet for lunch?', 
          
    #       'body': {
    #         'ContentType': 'HTML',
    #         'Content': 'They were <b>awesome</b>!',
    #       },
    #       'toRecipients': [
    #         {
    #           'emailAddress': {
    #             'address': 'daahrmmieboiye+test@gmail.com'
    #           }
    #         }
    #       ],
    #     }

    # data['saveToSentItems'] = False
    # pp = pprint.PrettyPrinter(indent=2)
    # pp.pprint(data)
    # pdata = json.dumps(data, indent=2, sort_keys=True)
    # data = json.dumps(data)
    # print(pdata)

    header = {"Content-type": "application/json"}
    new_mail = self.graph_client.post('{0}/me/sendMail'.format(graph_url), data=json.dumps(email_msg), headers=header)
    return new_mail.json()

class SharePointGraph(GraphClient):
  pass


class InvitationGraph(GraphClient):
    def send_invite(self, email, rdrurl, message):
      data = {
      "invitedUserEmailAddress": email,
      "inviteRedirectUrl": rdrurl,
      "customizedMessageBody": message,
      "sendInvitationMessage": True
      }
      invite = self.graph_client.post('{0}/invitations'.format(graph_url))
      return invite.json()



class UserGraph(GraphClient):

    def list_users(self):
      query_params = {
      #'$select': 'displayName,givenName,postalCode'
      '$select': 'id,mail,displayName,userPrincipalName,jobTitle'
      }
      user_list = self.graph_client.get('{0}/users'.format(graph_url))
      return user_list.json()

    def create_user(self):
      data = {
      'accountEnabled':True,
      'displayName':'A New Sombody',
      'userPrincipalName':'doverosey@live.com',
      'password':'dummyP@$$word',
      }
      new_user = self.graph_client.post('{0}/users'.format(graph_url), params=data)
      return new_user.json()

    def update_user(self):
      pass

