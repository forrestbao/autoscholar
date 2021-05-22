import os
import json

import requests
import yaml
from mendeley import Mendeley
from mendeley.session import MendeleySession


def getConfig(filename: str) -> dict:
    """
    Read the config.yaml file
    """
    try:
        with open(file=filename) as configFile:
            config = yaml.load(configFile, Loader=yaml.FullLoader)
            return config
    except FileNotFoundError as fne:
        print('Mendeley cloud config file {} not found!'.format(filename))

def establish_mendeley_session(config: dict) -> MendeleySession:
    """
    Connect to Mendeley's RESTful server
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


def get_docs_by_group_name(session: MendeleySession, groupName:str, verbose=False):
    for group in session.groups.iter(page_size=200): 
    # There is a limitation here that we can get up to 200 papers per group. 
    # But it is enough for our case. If you want more, use the RESTful API
        if group.name == groupName:
            # print (group.name, group.id, group.documents)
            print ("Group {0} has {1} papers.".format(group.name, len(group.documents.list(page_size=200).items)), end=" ")
            if verbose: 
                print ("The first 5 are:")
                for i in range(5):
                    doc = group.documents.list().items[i]
                    print ("  {0}: {1}".format(i+1, doc.title))
            break
    return group.documents


def get_annots_by_group_name(session: MendeleySession, groupName:str):
    """Extract all annotations in a group by group name
    Usage example: 
        annots = get_annots_by_group_name(session, 'NSF project')
    """
    annots_list_of_dicts = []
    docs = get_docs_by_group_name(session, groupName)
    for doc in docs.iter(page_size=200):
        annots_per_doc = get_annotations_by_docId(session, doc.id)
        
        doc_info = {'doc_id':doc.id, 
            'doc_title':doc.title, 
            'year':doc.year, 
            'source':doc.source,
            'url': doc.files.list().items[0].download_url
        }
        annots_distilled_per_doc = \
        [ {key:annot[key] for key in ['id','type','profile_id', 'positions']}            
                      for annot in annots_per_doc  if annot['type']!='note'  ]

        # print (json.dumps(annots_distilled_per_doc, indent=4))
        doc_info.update({'annots':annots_distilled_per_doc})
        annots_list_of_dicts.append(doc_info)

    # print (annots_list_of_dicts[0])
    print ("Annotation extraction done")
    return annots_list_of_dicts

def get_docs_by_group_id(session: MendeleySession, groupId: str) -> list:
    """
    Get All the documents by group id
    Save the data to database
    """
    if session is None:
        raise ValueError('Mendeley Database: No Session Token Provided!')
    if len(groupId) == 0:
        raise ValueError('Mendeley Database: No Group Id Provided!')
    access_token = session.token['access_token']
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    params = {'group_id': groupId, 'view': 'all'}
    response = requests.get(url='https://api.mendeley.com/documents', headers=headers, params=params)
    if response.status_code != 200:
        raise requests.RequestException('Mendeley Database: {} - {}'.format(response.status_code, response))
    else:
        content = response.json()
        return content


def get_users_profile(session: MendeleySession):
    """
    Get Logged-In User Profile
    NOT IN USE
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
    if len(docid) == 0:
        raise ValueError('Retrieve Annotation By Id: {} - Invalid Document Id!'.format(docid))
    else:
        access_token = session.token['access_token']
        headers = {'Authorization': 'Bearer {}'.format(access_token)}
        params = {'document_id': docid, 'limit':'200'}
        response = requests.get(url='https://api.mendeley.com/annotations', headers=headers, params=params)
        if response.status_code != 200:
            raise requests.RequestException('Mendeley Database: {} - {}'.format(response.status_code, response))
        else:
            content = response.json()
            return content



if __name__ == '__main__':
    groupName = 'BioNLP'
    config = getConfig('config.yaml')
    session = establish_mendeley_session(config)
    annots = get_annots_by_group_name(session, groupName)
    list(map(len, [annot['annots'] for annot in annots]))
    with open("annot.json", 'w') as f:
        json.dump(annots, f, indent=2)



## Documentation 

# doc structure

{'title': 'Improving product yields on D-glucose in Escherichia coli via knockout of pgi and zwf and feeding of supplemental carbon sources',
  'type': 'journal',
  'authors': [{'first_name': 'Eric', 'last_name': 'Shiue'},
   {'first_name': 'Irene M.', 'last_name': 'Brockman'},
   {'first_name': 'Kristala L J', 'last_name': 'Prather'}],
  'year': 2015,
  'source': 'Biotechnology and Bioengineering',
  'identifiers': {'arxiv': '15334406',
   'isbn': '1097-0290',
   'issn': '10970290',
   'doi': '10.1002/bit.25470',
   'pmid': '25258165'},
  'keywords': ['Biomass',
   'D-glucaric acid',
   'Product yield',
   'Strain engineering'],
  'id': 'fbd7fd4e-e24c-33e6-b39a-95bfa2e55749',
  'created': '2017-06-10T15:02:06.069Z',
  'profile_id': 'b635eeeb-d712-3316-9ebc-40b70e7d8d60',
  'group_id': 'a6921378-5d32-3644-961a-c3b6bd1d65f7',
  'last_modified': '2021-03-05T04:09:58.155Z',
  'abstract': 'The use of lignocellulosic biomass as a feedstock for microbial fermentation processes presents an opportunity for increasing the yield of bioproducts derived directly from glucose. Lignocellulosic biomass consists of several fermentable sugars, including glucose, xylose, and arabinose. In this study, we investigate the ability of an E. coli Δpgi Δzwf mutant to consume alternative carbon sources (xylose, arabinose, and glycerol) for growth while reserving glucose for product formation. Deletion of pgi and zwf was found to eliminate catabolite repression as well as the ability of E. coli to consume glucose for biomass formation. In addition, the yield from glucose of the bioproduct D-glucaric acid was significantly increased in a Δpgi Δzwf strain. Biotechnol. Bioeng. 2015;112: 579–587. © 2014 Wiley Periodicals, Inc.'}

  # docs structure 


{'name': 'NSF project',
  'description': 'Chemical engineering papers with manual annotations for training the computer to learn generating selective summarization',
  'disciplines': ['Computer and Information Science'],
  'tags': [],
  'photo': {'standard': 'https://photos.mendeley.com/awaiting.png',
   'square': 'https://photos.mendeley.com/disciplines/small/computer-and-information-science.png'},
  'webpage': '',
  'id': 'a6921378-5d32-3644-961a-c3b6bd1d65f7',
  'created': '2017-05-22T02:20:31.000Z',
  'owning_profile_id': 'b236d416-82d6-3405-9244-a107fc735576',
  'link': 'http://www.mendeley.com/groups/10952371/nsf-project/',
  'role': 'owner',
  'access_level': 'private',
  'used_space': 0,
  'pending_invitation_count': 0}

  # Annot structure 

{'id': '6a997af5-d63e-4190-bb7f-51a4b57a543b',
'type': 'highlight',
'color': {'r': 255, 'g': 245, 'b': 173},
'profile_id': 'b236d416-82d6-3405-9244-a107fc735576',
'positions': [{'top_left': {'x': 408.2417957509999, 'y': 461.866796923},
    'bottom_right': {'x': 435.897395751, 'y': 476.40019692299995},
    'page': 11}],
'created': '2021-03-31T06:01:14.853Z',
'last_modified': '2021-03-31T06:01:14.853Z',
'privacy_level': 'group',
'filehash': '32c050c7c8f20a88e638b9d715ccd27bedc2a8d0',
'document_id': '174cde18-ea54-3775-b41d-8d54edca857c'}