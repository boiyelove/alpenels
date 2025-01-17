from requests_oauthlib import OAuth2Session
import json
import pprint
import requests
from urllib.parse import quote
from .auth_helper import get_app_token


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



def send_invite_mail(display_name=None, email=None, body=None, invite_rdr_url=None):
    token = get_app_token()
    message = {"customizedMessageBody": body}
    data = {
    "invitedUserDisplayName": display_name,
    "invitedUserEmailAddress": email,
    "inviteRedirectUrl": invite_rdr_url,
    "sendInvitationMessage": True,
    "invitedUserMessageInfo": message,
    }
    header = {
    'Authorization': 'Bearer {0}'.format(token['access_token']),
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    }

    invitation = requests.post("{0}/invitations".format(graph_url),
      data=json.dumps(data),
      headers=header)
    return invitation.json()


def list_invitations():
    token = get_app_token()
    header = {
    'Authorization': 'Bearer {0}'.format(token['access_token']),
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    }

    invitations = requests.get("https://graph.microsoft.com/beta/users?filter=externalUserState".format(graph_url),
      headers=header)
    # https://graph.microsoft.com/beta/users?filter=externalUserState
    return invitations.json()

class MailGraph(GraphClient):
  def get_mail(self, message_id):
    message_id = quote(message_id)
    mail = self.graph_client.get("%s/me/messages/%s" % (graph_url, message_id))
    return mail.json()

  def get_mails(self):
    mails = self.graph_client.get('{0}/me/messages?$top50'.format(graph_url))
    return mails.json()

  def get_inbox(self):
    inbox = self.graph_client.get("{0}/me/mailFolders('Inbox')/messages?$top50".format(graph_url))
    return inbox.json()

  def get_sentitems(self):
    inbox = self.graph_client.get("{0}/me/mailFolders('SentItems')/messages?$top50".format(graph_url))
    return inbox.json()

  def get_drafts(self):
    inbox = self.graph_client.get("{0}/me/mailFolders('Drafts')/messages?$top50".format(graph_url))
    return inbox.json()

  def get_deleteditems(self):
    inbox = self.graph_client.get("{0}/me/mailFolders('DeletedItems')/messages?$top50".format(graph_url))
    return inbox.json()

  def get_mailFolders(self):
    mailfolder_list = self.graph_client.get('{0}/me/mailFolders'.format(graph_url))
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
                        'saveToSentItems': save_to_sent}

    header = {"Content-type": "application/json"}
    new_mail = self.graph_client.post('{0}/me/sendMail'.format(graph_url), data=json.dumps(email_msg), headers=header)
    return new_mail


class SharePointGraph(GraphClient):
  pass





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

