from django.db import models

from user.models import User


class FriendsRequests(models.Model):
    id = models.AutoField(primary_key=True)
    user_from = models.ForeignKey(User, related_name="user_from", on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, related_name="user_to", on_delete=models.CASCADE)
    status = models.CharField(choices=[('P', 'PENDING'),
                                       ('A', 'APPROVED'),
                                       ('D', 'DECLINED')], max_length=256)

    class Meta:
        db_table = 'friends_request'


