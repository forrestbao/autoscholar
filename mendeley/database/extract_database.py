from flask import Flask, redirect, render_template, session
from mendeley.session import MendeleySession
from mendeley import Mendeley
import requests
import yaml
import pprint



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


def get_documents_from_library(session: MendeleySession):
    """
    Get all the documents from the library
    """
    data = {"Documents": []}
    for documents in session.documents.iter():
        docDict = {}
        docDict.__setitem__("id", documents.id)
        docDict.__setitem__("title", documents.title)
        docDict.__setitem__("doi", documents.identifiers)
        docDict.__setitem__("type", documents.type)
        docDict.__setitem__("year", documents.year)
        docDict.__setitem__("created", documents.created)
        docDict.__setitem__("source", documents.source)
        docDict.__setitem__("lastModified", documents.last_modified)
        if len(documents.authors) > 0:
            authors = []
            for author in documents.authors:
                authorDict = {}
                authorDict.__setitem__("firstName", author.first_name)
                authorDict.__setitem__("lastName", author.last_name)
                authors.append(authorDict)
            docDict.__setitem__("authors", authors)
        if documents.files is not None:
            fileDict = {}
            fileDict.__setitem__("catalog_id", documents.files.catalog_id)
            fileDict.__setitem__("document_id", documents.files.document_id)
            fileDict.__setitem__("group_id", documents.files.group_id)
            docDict.__setitem__("files", fileDict)
        data["Documents"].append(docDict)
    return data


def get_groups(session: MendeleySession):
    """
    Get Groups Associated with the profile
    """
    groups = {"Groups": []}
    for group in session.groups.iter():
        groupDict = {}
        groupDict.__setitem__("accessLevel", group.access_level)
        groupDict.__setitem__("created", group.created)
        groupDict.__setitem__("id", group.id)
        groupDict.__setitem__("role", group.role)
        groupDict.__setitem__("link", group.link)
        groupDict.__setitem__("name", group.name)
        groupDict.__setitem__("description", group.description)
        groupDict.__setitem__("disciplines", group.disciplines)
        if group.documents is not None:
            groupDoc = []
            for documents in group.documents.iter():
                docDict = {}
                docDict.__setitem__("abstract", documents.abstract)
                docDict.__setitem__("id", documents.id)
                docDict.__setitem__("title", documents.title)
                docDict.__setitem__("doi", documents.identifiers)
                docDict.__setitem__("type", documents.type)
                docDict.__setitem__("year", documents.year)
                docDict.__setitem__("created", documents.created)
                docDict.__setitem__("source", documents.source)
                docDict.__setitem__("lastModified", documents.last_modified)
                docDict.__setitem__("keywords", documents.keywords)
                if len(documents.authors) > 0:
                    authors = []
                    for author in documents.authors:
                        authorDict = {}
                        authorDict.__setitem__("firstName", author.first_name)
                        authorDict.__setitem__("lastName", author.last_name)
                        authors.append(authorDict)
                    docDict.__setitem__("authors", authors)
                if documents.files is not None:
                    fileDict = {}
                    fileDict.__setitem__("catalog_id", documents.files.catalog_id)
                    fileDict.__setitem__("document_id", documents.files.document_id)
                    fileDict.__setitem__("group_id", documents.files.group_id)
                    docDict.__setitem__("files", fileDict)
                groupDoc.append(docDict)
            groupDict.__setitem__("documents", groupDoc)
        groups["Groups"].append(groupDict)
    return groups


if __name__ == '__main__':
    config = getConfig('config.yaml')
    session = connect_to_mendeley_db(config)
    pprint.pprint(get_documents_from_library(session))
    pprint.pprint(get_groups(session))

