class DownloadError(Exception):
    pass


class IllustInitError(Exception):
    pass


class LoginError(IllustInitError):
    pass


class GetInfoError(IllustInitError):
    pass
