import os

import requests
import yaml
from pprint import pprint
from mendeley import Mendeley
from mendeley.session import MendeleySession
from sqlobject import *


def getConfig(filename: str) -> dict:
    """
    Read the config.yaml file
    """
    try:
        with open(file=filename) as configFile:
            config = yaml.load(configFile, Loader=yaml.FullLoader)
            return config
    except FileNotFoundError as fne:
        print('File {} not found!'.format(filename))


def connect_to_mendeley_db(config: dict) -> MendeleySession:
    """
    Connect to the Mendeley Database
    """
    if len(config) == 0:
        raise ValueError('Configuration Error: Check the configuration yaml file!')
    try:
        mendeley = Mendeley(client_id=config.get('clientId'), client_secret=config.get('clientSecret'),
                            redirect_uri=config.get('redirectURI'))
        authorization = mendeley.start_implicit_grant_flow()
        if authorization is not None:
            loginURL = authorization.get_login_url()
            if loginURL != "" or loginURL is not None:
                authHeader = {
                    "username": config.get("username"),
                    "password": config.get("password")
                }
                request = requests.post(loginURL, allow_redirects=False, data=authHeader)
                if request.status_code >= 400:
                    raise ConnectionError(
                        'Error: Cannot connect to Mendeley Database: Status Code: {}'.format(request.status_code))
                session = authorization.authenticate(request.headers['Location'])
                return session
            else:
                raise ValueError('Error: Cannot Retrieve the Login URL')
        else:
            raise ConnectionAbortedError('Error: Unauthorized User!')
    except Exception as exc:
        print('Error: Connecting to the Mendeley Database')


def connect_to_db():
    """
    Connect to the sqlite database
    """
    db_filename = os.path.abspath('mendeley.sqlite')
    connection_url = "sqlite:" + db_filename
    connection = connectionForURI(connection_url)
    sqlhub.processConnection = connection
    return sqlhub.processConnection


def get_all_document_by_group(session: MendeleySession, groupId: str) -> dict:
    """
    Get All the documents by group
    Save the data to database
    """
    if session is None:
        raise ValueError('Mendeley Database: No Session Token Provided!')
    if len(groupId) == 0:
        raise ValueError('Mendeley Database: No Group Id Provided!')
    access_token = session.token['access_token']
    print(access_token)
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    params = {'group_id': groupId}
    response = requests.get(url='https://api.mendeley.com/documents', headers=headers, params=params)
    if response.status_code != 200:
        raise requests.RequestException('Mendeley Database: {} - {}'.format(response.status_code, response))
    else:
        content = response.json()
        return content


def get_users_profile(session: MendeleySession):
    """
    Get Logged-In User Profile
    """
    # TODO: Repeating code: Make a different private method to retrieve the session token, Security Threat!!!!!
    if session is None:
        raise ValueError('Mendeley Database: No Session Token Provided!')
    else:
        access_token = session.token['access_token']
        headers = {'Authorization': 'Bearer {}'.format(access_token)}
        response = requests.get(url='https://api.mendeley.com/profiles/me',
                                headers=headers)
        if response.status_code != 200:
            raise requests.RequestException('Mendeley Database: {} - {}'.format(response.status_code, response))
        else:
            content = response.json()
            return content


def get_annotations_by_docId(session: MendeleySession, docid: str):
    """
    Get Annotation By Document Id
    """
    if session is None:
        raise ValueError('Mendeley Database: No Session Token Provided!')
    if len(docid)== 0:
        raise ValueError('Retrieve Annotation By Id: {} - Invalid Document Id!'.format(docid))
    else:
        access_token = session.token['access_token']
        headers = {'Authorization': 'Bearer {}'.format(access_token)}
        params = {'document_id': docid}
        response = requests.get(url='https://api.mendeley.com/annotations', headers=headers, params=params)
        if response.status_code != 200:
            raise requests.RequestException('Mendeley Database: {} - {}'.format(response.status_code, response))
        else:
            content = response.json()
            return content

if __name__ == '__main__':
    config = getConfig('config.yaml')
    session = connect_to_mendeley_db(config)
    connect_to_db()
    pprint(get_all_document_by_group(session, "a6921378-5d32-3644-961a-c3b6bd1d65f7"))
    # pprint(get_users_profile(session))
    # pprint(get_annotations_by_docId(session, "b477c17a-53b4-307f-8c8e-b91a97a52a51"))
