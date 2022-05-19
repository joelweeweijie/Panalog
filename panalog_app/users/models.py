from django.db import models
from django.contrib.auth.models import User
from PIL import Image
# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #if user deleted > profile deleted, profile deleted > user will not delete
    team = models.CharField(null=True, blank=True, max_length=10) # BASIS
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    fullname = models.CharField(null=True, blank=True, max_length=50)

    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
