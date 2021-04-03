class Annotation():
    """
    Annotation Class
    """

    def __init__(self, id: str, type: str, color: dict, created: str, last_modified: str, privacy_level: str,
                 filehash: str, document_id: str, ann_profile_id: str):
        """
        Constructor
        @param id: str
        @param type: str
        @param color: str
        @param created: str
        @param last_modified: str
        @param privacy_level: str
        @param filehash: str
        @param document_id: str
        @param ann_profile_id: str
        """
        self.id = id
        self.type = type
        self.color = "%02x%02x%02x" % tuple((color.values()))  # Converts to Hex
        self.last_modified = last_modified
        self.privacy_level = privacy_level
        self.filehash = filehash
        self.document_id = document_id
        self.ann_profile_id = ann_profile_id

