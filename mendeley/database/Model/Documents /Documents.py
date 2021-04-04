class Documents:
    """
    Mendeley Documents
    """
    def __init__(self, docid: str , title: str = None,
                 abstract: str = None, type: str = None, year:int = None, page: str = None, volume: str = None,
                 issue: str = None,source: str = None, created: str = None, file_attached: bool = False,
                 read: bool = False,starred: bool = False,authored: bool = False, confirmed: bool = False,
                 hidden: bool = False, private_publication: bool = False,publisher: str = None,
                 citation_key: str = None,last_modified: str = None, group_id: str = None, profile_id: str = None):
        """
        Constructor
        @param docid: Document Id
        @param title: Document Title
        @param abstract: Document Abstract
        @param type: Document Type
        @param year: Document Year
        @param page: Document Page
        @param volume: Document Volume
        @param issue: Document Issue
        @param source: Document Source
        @param created: Document Created
        @param file_attached: Document File Attached
        @param read: Document Read Permission
        @param starred: Document Starred Status
        @param authored: Document Authored Status
        @param confirmed: Document Confirmed Status
        @param hidden: Document Hidden Status
        @param private_publication: Document Private Publication Status
        @param publisher: Document Publisher
        @param citation_key: Document Citation Key
        @param last_modified: Document Last Modified
        @param group_id: Document group id
        @param profile_id: Document Profile id
        """
        self.profile_id = profile_id
        self.group_id = group_id
        self.last_modified = last_modified
        self.citation_key = citation_key
        self.publisher = publisher
        self.private_publication = private_publication
        self.hidden = hidden
        self.confirmed = confirmed
        self.authored = authored
        self.starred = starred
        self.read = read
        self.file_attached = file_attached
        self.created = created
        self.source = source
        self.issue = issue
        self.volume = volume
        self.page = page
        self.docid = docid
        self.title = title
        self.abstract = abstract
        self.type = type
        self.year = year



