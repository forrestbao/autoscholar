class Disciplines:
    """
    Mendeley Disciplines
    """
    def __init__(self, id, name, profile_id, group_id):
        """
        Constructor
        @param id: Disciplines id
        @param name: Name of the discipline
        @param profile_id: profile_id that  discipline is attached to
        @param group_id: Group_id discipline is attached to
        """
        self.id = id
        self.name = name
        self.profile_id = profile_id
        self.group_id = group_id