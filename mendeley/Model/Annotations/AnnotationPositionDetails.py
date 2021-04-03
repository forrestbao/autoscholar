class AnnotationPositionDetails:
    """
    Annotation Position Details
    """

    def __init__(self, id: int, locationType: str, x_loc: float, y_loc: float):
        """
        Constructor
        @param id: Id of the Anotation Position Details
        @param locationType: location (top-right, top-bottom, bottom-right, bottom-left)
        @param x_loc: x-coordinates
        @param y_loc: y-coordinates
        """
        self.id = id
        self.location_type = locationType
        self.x_loc = x_loc
        self.y_loc = y_loc