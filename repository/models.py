from django.db import models
from django.core.files.storage import FileSystemStorage
from django.db.models.fields.files import *
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.encoding import smart_str

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        """
        Creates and saves a User with the given email, name and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email, name and password.
        """
        user = self.create_user(email,
                                password=password,
                                )
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('email address', unique=True, db_index=True)
    joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    dateofbirth = models.DateField(null=True, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return smart_str(self.email)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin


def upload_path_handler_digital(instance, filename):
    return "{id_user}/{id_repository}/digital/{filename}".format(id_user=instance.repository.user_id, id_repository=instance.repository.id_repository, filename=filename)

def upload_path_handler_electronic(instance, filename):
    return "{id_user}/{id_repository}/electronics/{filename}".format(id_user=instance.repository.user_id, id_repository=instance.repository.id_repository, filename=filename)

def upload_path_handler_photos(instance, filename):
    return "{id_user}/{id_repository}/photos/{filename}".format(id_user=instance.repository.user_id, id_repository=instance.repository.id_repository, filename=filename)

fileStorage = FileSystemStorage(os.path.join(settings.MEDIA_ROOT, "upload/user/"))


class Repository(models.Model):
    id_repository = models.CharField(max_length=15, primary_key=True, unique=True)
    repository_name = models.CharField(max_length=100, null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    user = models.ForeignKey(User, related_name='repository')
    date = models.DateField(blank=True, null=True)
    info = models.TextField(blank=True)
    class Meta:
        ordering = ('created',)

    def delete(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        # Delete the model before the file
        super(Repository, self).delete(*args, **kwargs)
        # Delete the file after the model

class DigitalEvidence(models.Model):
    repository = models.ForeignKey(Repository, related_name='digital')
    filename = models.CharField(max_length=50, default='',  blank=False, null=False)
    file = models.FileField(storage=fileStorage, upload_to=upload_path_handler_digital)
    info_file = models.TextField(null=True)

    def delete(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        storage = self.file.storage
        path =  self.file.path
        # Delete the model before the file
        super(DigitalEvidence, self).delete(*args, **kwargs)
        # Delete the file after the model
        storage.delete(path)


class ElectronicEvidence(models.Model):
    repository = models.ForeignKey(Repository, related_name='electronic')
    filename = models.CharField(max_length=50, default='', blank=False, null=False)
    file = models.FileField(storage=fileStorage, upload_to=upload_path_handler_electronic)
    info_file = models.TextField(null=True)

    def delete(self, *args, **kwargs):
        # You have to prepare what you need before delete the model
        storage = self.file.storage
        path = self.file.path
        # Delete the model before the file
        super(ElectronicEvidence, self).delete(*args, **kwargs)
        # Delete the file after the model
        storage.delete(path)

