from django.db import models

# Create your models here.


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'uploads/%Y%m%d-{0}'.format(filename)


class FileModel(models.Model):
    title = models.CharField(max_length=50)
    file = models.FileField(upload_to=user_directory_path)
