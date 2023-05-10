from django.db import models

from user.models import User


class Posts(models.Model):
    id = models.AutoField(primary_key=True)
    body = models.CharField(max_length=1024, null=True, blank=True)
    image_url = models.CharField(max_length=256, null=True, blank=True)
    author = models.ForeignKey(User, related_name="post_author", on_delete=models.CASCADE)
    likes = models.ManyToManyField(User, related_name="user_liked", db_table="posts_likes")

    class Meta:
        db_table = 'posts'
