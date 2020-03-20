class MissingMetadataError(KeyError):
    pass


class MissingParameterError(MissingMetadataError):
    pass


class MissingAttributeError(MissingMetadataError):
    pass
