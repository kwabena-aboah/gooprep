from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """Production storage for collected CSS, JS, fonts, and images."""

    location = 'static'
    default_acl = None
    file_overwrite = True


class MediaStorage(S3Boto3Storage):
    """Production storage for user-uploaded media files."""

    location = 'media'
    default_acl = None
    file_overwrite = False
