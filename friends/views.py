from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiParameter, OpenApiResponse
from rest_framework import viewsets, fields
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from friends.models import FriendsRequests
from user.models import User
from user_profile.views import user_to_user_data


class FriendsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: inline_serializer("FriendsList",
                                   {"id": fields.IntegerField(),
                                    "email": fields.CharField(),
                                    "fullname": fields.CharField(),
                                    "age": fields.IntegerField(),
                                    "city": fields.CharField(),
                                    "university": fields.CharField(),
                                    "logo_url": fields.CharField()}, many=True),
        },
    )
    def list(self, request):
        user = request.user
        data = []
        for friend in user.friends.all():
            data.append(user_to_user_data(friend))
        return Response(data, status=200)

    @extend_schema(
        parameters=[
            OpenApiParameter("user_id", int)
        ],
        responses={
            200: OpenApiResponse(description="User deleted user_{user_id} from friend"),
        },
    )
    def delete(self, request):
        user = request.user
        user_id = request.GET.get('user_id', None)

        if user_id is None:
            raise ValidationError("user_id field does not exist")
        if user_id == user.id:
            raise ValidationError("User can not delete himself from friends")
        if not User.objects.filter(id=user_id).exists():
            raise ValidationError("User with user_id does not exist")
        if not user.friends.filter(id=user_id).exists():
            raise ValidationError("Users are not friends")

        user2 = User.objects.get(id=user_id)
        user.friends.remove(user2)
        user2.friends.remove(user)
        return Response(f"User deleted user_{user_id} from friend", status=200)

    @extend_schema(
        parameters=[
            OpenApiParameter("to_user_id", int)
        ],
        responses={
            200: OpenApiResponse(description="Request was send"),
        },
    )
    def send_request(self, request):
        user = request.user
        to_user_id = request.GET.get('to_user_id', None)

        if to_user_id is None:
            raise ValidationError("to_user_id field does not exist")
        if to_user_id == user.id:
            raise ValidationError("User can not send friend request to himself")
        if not User.objects.filter(id=to_user_id).exists():
            raise ValidationError("User with to_user_id does not exist")
        if user.friends.filter(id=to_user_id).exists():
            raise ValidationError("User already in friends")
        if FriendsRequests.objects.filter(user_from=user, user_to_id=to_user_id, status="PENDING").exists():
            raise ValidationError("Request already exists")

        friends_request = FriendsRequests.objects.create(user_from=user,
                                                         user_to_id=to_user_id,
                                                         status="PENDING")
        return Response("Request was send", status=200)

    @extend_schema(
        description='status = [PENDING, DECLINED, APPROVED]',
        parameters=[
            OpenApiParameter("status", str)
        ],
        responses={
            200: inline_serializer("IncomeRequests",
                                   {"id": fields.IntegerField(),
                                    "user": inline_serializer("RequestUsers",
                                                              {"id": fields.IntegerField(),
                                                               "email": fields.CharField(),
                                                               "fullname": fields.CharField(),
                                                               "age": fields.IntegerField(),
                                                               "city": fields.CharField(),
                                                               "university": fields.CharField(),
                                                               "logo_url": fields.CharField()})},
                                   many=True),
        },
    )
    def income_request(self, request):
        user = request.user
        status = request.GET.get('status', None)

        if status is None:
            raise ValidationError("status field does not exist")
        if status != "PENDING" and status != "APPROVED" and status != "DECLINED":
            raise ValidationError("not valid status")

        friends_requests = FriendsRequests.objects.filter(user_to=user, status=status)

        data = []
        for rq in friends_requests:
            data.append({'id': rq.id, 'user': user_to_user_data(rq.user_from)})
        return Response(data, status=200)

    @extend_schema(
        parameters=[
            OpenApiParameter("request_id", int)
        ],
        responses={
            200: OpenApiResponse(description="Request approved"),
        },
    )
    def approve_request(self, request):
        user = request.user
        request_id = request.GET.get('request_id', None)

        if request_id is None:
            raise ValidationError("request_id field does not exist")
        if not FriendsRequests.objects.filter(id=request_id, user_to=user, status="PENDING").exists():
            raise ValidationError("Request does not exist")

        friends_requests = FriendsRequests.objects.get(id=request_id)
        friends_requests.status = "APPROVED"
        friends_requests.save()

        user_from = friends_requests.user_from
        user.friends.add(user_from)
        user_from.friends.add(user)

        return Response("Request approved", status=200)

    @extend_schema(
        parameters=[
            OpenApiParameter("request_id", int)
        ],
        responses={
            200: OpenApiResponse(description="Request declined"),
        },
    )
    def decline_request(self, request):
        user = request.user
        request_id = request.GET.get('request_id', None)

        if request_id is None:
            raise ValidationError("request_id field does not exist")
        if not FriendsRequests.objects.filter(id=request_id, user_to=user, status="PENDING").exists():
            raise ValidationError("Request does not exist")

        friends_requests = FriendsRequests.objects.get(id=request_id)
        friends_requests.status = "DECLINED"
        friends_requests.save()

        return Response("Request declined", status=200)
