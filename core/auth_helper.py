import yaml
import requests
from requests_oauthlib import OAuth2Session
import os
import time
import datetime
import pytz
from django.conf import settings as conf_settings
# This is necessary for testing with non-HTTPS localhost
# Remove this if deploying to production
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# This is necessary because Azure does not guarantee
# to return scopes in the same case and order as requested
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'
os.environ['OAUTHLIB_IGNORE_SCOPE_CHANGE'] = '1'

# Load the oauth_settings.yml file
stream = open(os.path.join(conf_settings.BASE_DIR, conf_settings.OAUTH_FILE), 'r')
settings = yaml.load(stream)
authorize_url = '{0}{1}'.format(settings['authority'], settings['authorize_endpoint'])
token_url = '{0}{1}'.format(settings['authority'], settings['token_endpoint'])

def get_sign_in_url():
  aad_auth = OAuth2Session(settings['app_id'],
    scope=settings['scopes'],
    redirect_uri=settings['redirect'])
  sign_in_url, state = aad_auth.authorization_url(authorize_url, prompt='login')
  return sign_in_url, state



# Method to exchange auth code for access token
def get_token_from_code(callback_url, expected_state):
  aad_auth = OAuth2Session(settings['app_id'],
    state=expected_state,
    scope=settings['scopes'],
    redirect_uri=settings['redirect'])
  token = aad_auth.fetch_token(token_url,
    client_secret = settings['app_secret'],
    authorization_response=callback_url)
  return token


def store_token(request, token):
  request.session['oauth_token'] = token



def store_user(request, user):
  request.session['user'] = {
    'is_authenticated': True,
    'name': user['displayName'],
    'email': user['mail'] if (user['mail'] != None) else user['userPrincipalName']
  }



def get_token(request):
  token = request.session['oauth_token']
  print('Insession retrieved token is', token)
  if token != None:
    now = time.time()
    expire_time = token['expires_at'] - 300
    if now >= expire_time:
      aad_auth = OAuth2Session(settings['app_id'],
        token = token,
        scope=settings['scopes'],
        redirect_uri=settings['redirect'])

      refresh_params = {
        'client_id': settings['app_id'],
        'client_secret': settings['app_secret'],
      }
      new_token = aad_auth.refresh_token(token_url, **refresh_params)
      store_token(request, new_token)
      return new_token

    else:
      # Token still valid, just return it
      return token

def get_client_token(client):
  token = client.token
  if token != None:
    now = time.time()
    UTC = pytz.timezone(conf_settings.TIME_ZONE)
    then  = datetime.datetime(1970, 1,1, tzinfo=UTC)
    updated = client.updated - then
    expire_time = updated.total_seconds() - (token['expires_at'] - 300)
    print('now is', now)
    print('expire_time is', expire_time)
    if now >= expire_time:
      aad_auth = OAuth2Session(settings['app_id'],
        token = token,
        scope=settings['scopes'],
        redirect_uri=settings['redirect'])

      refresh_params = {
        'client_id': settings['app_id'],
        'client_secret': settings['app_secret'],
      }
      token = aad_auth.refresh_token(token_url, **refresh_params)
      client.token = token
      client.save()
    return token

def get_app_token():
  token_url = "https://login.microsoftonline.com/{0}/oauth2/v2.0/token".format(settings['tenant'])
  scope="https://graph.microsoft.com/.default"
  header = {
  "Content_Type": "application/x-www-form-urlencoded"
  }
  data = {
  "client_id": settings['app_id'],
  "scope" : scope,
  "client_secret": settings['app_secret'],
  "grant_type": "client_credentials",
  }
  token= requests.post(token_url, data=data, headers=header)
  return token.json()


def remove_user_and_token(request):
  if 'oauth_token' in request.session:
    del request.session['oauth_token']

  if 'user' in request.session:
    del request.session['user']