class Groups:
    """ Mendeley Groups"""

    def __init__(self, group_id:str, link: str = None, owning_profile_id: str = None, access_level: str = None,
                 created: str = None, name: str = None, description:str = None, webpage: str = None):
        """
        Constructor
        @param group_id: Group id
        @param link: Group link
        @param owning_profile_id: Profile that owns the group
        @param access_level: Access level for the group
        @param created: Creation time
        @param name: Group name
        @param description:  Group description
        @param webpage:  Group Webpage 
        """
        self.group_id = group_id
        self.link = link
        self.owning_profile_id = owning_profile_id
        self.access_level = access_level
        self.created = created
        self.name = name
        self.description = description
        self.webpage = webpage

