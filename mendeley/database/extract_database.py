import os
import sqlite3

import requests
import yaml
from mendeley import Mendeley
from mendeley.session import MendeleySession
import enum


####################
#   ENUM
####################
class TABLE(enum.Enum):
    CREATE_DOCUMENT_TABLE = "document"
    CREATE_DOCUMENT_WEBSITE_TABLE = "document_website"
    CREATE_DOCUMENT_IDENTIFIERS = "identifiers"
    CREATE_DOCUMENT_AUTHORS = "authors"
    CREATE_KEYWORDS = "keywords"
    CREATE_ANNOTATION_TABLE = "annotation"
    CREATE_ANNOTATION_POSITION_TABLE = "annotation_position"


####################
#   Database Queries
####################
CREATE_DOCUMENT_TABLE = """CREATE TABLE IF NOT EXISTS document ( 
                                id TEXT PRIMARY KEY,
                                title TEXT,
                                abstract TEXT,
                                type TEXT, 
                                year Integer,
                                pages TEXT,
                                volume TEXT,
                                issue TEXT,
                                source TEXT,
                                created TEXT,
                                file_attached TEXT DEFAULT 'false',
                                read TEXT DEFAULT 'false',
                                starred TEXT DEFAULT 'false',
                                authored TEXT DEFAULT 'false',
                                confirmed TEXT DEFAULT 'false',
                                hidden TEXT DEFAULT 'false',
                                private_publication TEXT DEFAULT 'false',  
                                publisher TEXT, 
                                citation_key TEXT,
                                last_modified TEXT,
                                group_id TEXT, 
                                profile_id TEXT);          
                        """
CREATE_DOCUMENT_WEBSITE_TABLE = """CREATE TABLE IF NOT EXISTS document_website (
                                        id Integer PRIMARY KEY AUTOINCREMENT, 
                                        url TEXT,
                                        docid TEXT NOT NULL ,
                                        FOREIGN KEY (docid) REFERENCES document(id));
                                """

CREATE_DOCUMENT_IDENTIFIERS = """CREATE TABLE IF NOT EXISTS identifiers (
                                    id Integer PRIMARY KEY AUTOINCREMENT, 
                                    issn TEXT, 
                                    isbn TEXT, 
                                    pmid TEXT, 
                                    arxiv TEXT, 
                                    doi TEXT, 
                                    scopus TEXT, 
                                    docid TEXT NOT NULL, 
                                    FOREIGN KEY (docid) REFERENCES document(id)); 
                              """

CREATE_DOCUMENT_AUTHORS = """CREATE TABLE IF NOT EXISTS authors (
                                id Integer PRIMARY KEY AUTOINCREMENT, 
                                first_name TEXT,
                                last_name TEXT, 
                                docid TEXT NOT NULL, 
                                FOREIGN KEY (docid) REFERENCES document(id));
                          """

CREATE_KEYWORDS = """CREATE TABLE IF NOT EXISTS keywords (
                        id Integer PRIMARY KEY AUTOINCREMENT,
                        value TEXT, 
                        docid TEXT NOT NULL, 
                        FOREIGN KEY (docid) REFERENCES document(id)); 
                  """

CREATE_ANNOTATION_TABLE = """
                            CREATE TABLE IF NOT EXISTS annotation (
                                id Text PRIMARY KEY,
                                type Text,
                                text Text,
                                color Text,
                                created Text, 
                                last_modified Text, 
                                filehash Text, 
                                document_id Text, 
                                profile_id Text,
                                privacy_level Text, 
                                FOREIGN KEY (document_id) REFERENCES document(id)); 
                          """

CREATE_ANNOTATION_POSITION_TABLE = """
                                    CREATE TABLE IF NOT EXISTS annotation_position (
                                        id Integer PRIMARY KEY AUTOINCREMENT, 
                                        page TEXT NOT NULL, 
                                        location_type TEXT NOT NULL, 
                                        xvalue TEXT NOT NULL, 
                                        yvalue TEXT NOT NULL, 
                                        annotationid TEXT NOT NULL, 
                                        FOREIGN KEY (annotationid) REFERENCES annotation(id));
                                    """


####################
#   Configuration
#       - Mendeley
#       - Database
####################

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
    try:
        db_filename = os.path.abspath('mendeley.sqlite')
        connection = sqlite3.connect(db_filename)
        if connection is not None:
            create_sqlite_table(connection, CREATE_DOCUMENT_TABLE)
            create_sqlite_table(connection, CREATE_DOCUMENT_WEBSITE_TABLE)
            create_sqlite_table(connection, CREATE_KEYWORDS)
            create_sqlite_table(connection, CREATE_DOCUMENT_AUTHORS)
            create_sqlite_table(connection, CREATE_DOCUMENT_IDENTIFIERS)
            create_sqlite_table(connection, CREATE_ANNOTATION_TABLE)
            create_sqlite_table(connection, CREATE_ANNOTATION_POSITION_TABLE)
            return connection
        else:
            raise Exception("Cannot Connect to Database!")
    except sqlite3.Error as error:
        print(error)


def create_sqlite_table(connection, query: str):
    cursor = connection.cursor()
    try:
        cursor.execute(query)
    except sqlite3.Error as error:
        cursor.rollback()
        print(error)
    finally:
        cursor.close()


def insert_data(connection, data, table: str):
    cursor = connection.cursor()
    try:
        keys = tuple(data.keys())
        values = tuple(data.values())
        insert_query = "INSERT INTO {}{} VALUES {};".format(table, keys, values)
        cursor.execute(insert_query)
    except sqlite3.Error as error:
        print(error)
    finally:
        cursor.close()


####################
#   Retrieving Data
####################

def get_all_document_by_group(session: MendeleySession, groupId: str) -> list:
    """
    Get All the documents by group
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
        params = {'document_id': docid}
        response = requests.get(url='https://api.mendeley.com/annotations', headers=headers, params=params)
        if response.status_code != 200:
            raise requests.RequestException('Mendeley Database: {} - {}'.format(response.status_code, response))
        else:
            content = response.json()
            return content


####################
#   Cleaning Data
####################
def clean_document_data(connection, response: list):
    """
    Clean Document Detail
    Insert it into Database
    @param connection:
    @param response:
    @return:
    """
    if len(response) == 0:
        raise ValueError("No Data Retrieved!")
    else:
        documents_list = []
        for data in response:
            if data is not None:
                doc = {key: str(value) for (key, value) in data.items() if
                       (key != "authors") and (key != "identifiers") and
                       (key != "keywords") and (key != "websites")}
                insert_data(connection, doc, TABLE.CREATE_DOCUMENT_TABLE.value)
                # Get the authors of the document
                doc_id = data.get("id")
                for author in data.get("authors"):
                    authorDetails = {}
                    authorDetails.__setitem__("docid", doc_id)
                    authorDetails.__setitem__("first_name", author.get("first_name"))
                    authorDetails.__setitem__("last_name", author.get("last_name"))
                    insert_data(connection, authorDetails, TABLE.CREATE_DOCUMENT_AUTHORS.value)

                # Get the Document Website
                if data.get("websites") is not None:
                    for website in data.get("websites"):
                        website_dict = {}
                        website_dict.__setitem__("url", website)
                        website_dict.__setitem__("docid", doc_id)
                        insert_data(connection, website_dict, TABLE.CREATE_DOCUMENT_WEBSITE_TABLE.value)
                else:
                    print("No Website URL Found For DocumentID - {}".format(doc_id))

                # Get the Identifiers
                identifiers = {key: value for (key, value) in data.get("identifiers").items()}
                identifiers.__setitem__("docid", doc_id)
                insert_data(connection, identifiers, TABLE.CREATE_DOCUMENT_IDENTIFIERS.value)

                if data.get("keywords") is not None:
                    # Get the Keywords
                    for keyword in data.get("keywords"):
                        keyWord = {}
                        keyWord.__setitem__("value", keyword)
                        keyWord.__setitem__("docid", doc_id)
                        insert_data(connection, keyWord, TABLE.CREATE_KEYWORDS.value)


def clean_annotation_data(connection, response):
    """
    Clean Annotation Details
    @param connection:
    @param data:
    @return:
    """
    if len(response) == 0:
        raise ValueError("No Data Retrieved!")
    else:
        for data in response:
            annotation = {key: str(value) for (key, value) in data.items() if
                          (key != "positions") and (key != "color")}
            annotation.__setitem__("color", "#%02x%02x%02x" % tuple(data.get("color").values()))
            insert_data(connection, annotation, TABLE.CREATE_ANNOTATION_TABLE.value)
            for ap in data.get("positions"):
                annotationPosition = {key: str(value) for (key, value) in ap.items() if key == "page"}
                annotationPosition.__setitem__("annotationid", data.get("id"))
                for key, value in ap.items():
                    if key == "top_left" or key == "bottom_right" or key == "top_right" or key == "bottom_left":
                        annotationPosition.__setitem__("location_type", key)
                        for xKey, yValue in ap.get(key).items():
                            if xKey == "x":
                                annotationPosition.__setitem__("xvalue", str(yValue))
                            else:
                                annotationPosition.__setitem__("yvalue", str(yValue))
                    insert_data(connection, annotationPosition, TABLE.CREATE_ANNOTATION_POSITION_TABLE.value)


if __name__ == '__main__':
    if os.path.exists("mendeley.sqlite"):
        os.remove("mendeley.sqlite")
    config = getConfig('config.yaml')
    session = connect_to_mendeley_db(config)
    connection = connect_to_db()
    document = get_all_document_by_group(session, "a6921378-5d32-3644-961a-c3b6bd1d65f7")
    connection.commit()
    clean_document_data(connection, document)
    for eachDoc in document:
        annotation = get_annotations_by_docId(session, eachDoc.get("id"))
        clean_annotation_data(connection, annotation)
        connection.commit()
