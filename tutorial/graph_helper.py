from requests_oauthlib import OAuth2Session


graph_url = 'https://graph.microsoft.com/v1.0'
graph_beta_url = 'https://graph.microsoft.com/beta'

def get_user(token):
  graph_client = OAuth2Session(token=token)

  # Send GET to /me
  user = graph_client.get('{0}/me'.format(graph_url))
  print('User is ', user)
  # Return the JSON result
  return user.json()

def get_calendar_events(token):
  graph_client = OAuth2Session(token=token)

  # Configure query parameters to
  # modify the results
  query_params = {
    '$select': 'subject,organizer,start,end',
    '$orderby': 'createdDateTime DESC'
  }

  # Send GET to /me/events
  events = graph_client.get('{0}/me/events'.format(graph_url), params=query_params)
  # Return the JSON result
  return events.json()

def get_contact_list(token):
  graph_client = OAuth2Session(token=token)

  # Send GET to /me/events
  contact_list = graph_client.get('{0}/me/contacts'.format(graph_url))
  # Return the JSON result
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

  def list_mailboxFolders(self):
    mailfolder_list = self.graph_client.get('/me/mailFolders')
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

  def send_mail(self):
    data = {
    "message" :{
    "subject": "Meet for lunch",
    "body":{
    "contentType":"Text",
    "content": "the new cafeteria is open."
    },
    "toRecipients":[
    {
    "emailAddress": {
            "address": "daahrmmieboiye+test1@gmail.com"
        }
      }
    ],
    "ccRecipients": [
    {
    "emailAddress": {
    "address": "daahrmmieboiye+test2@gmail.com"
          }
        }
      ]
    },
    "saveToSentItems": "false"
    }
    new_mail = graph_client.post(url='/me/sendMail', params=data)
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

