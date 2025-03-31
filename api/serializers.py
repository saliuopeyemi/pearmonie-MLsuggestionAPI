#from django.utils.timezone import make_aware

from rest_framework import serializers
from . import models

from datetime import datetime, timedelta
import uuid


subscription_plans = {
        "Basic":{"duration":30,"price":1000},
        "Silver":{"duration":90, "price":2500},
        "Gold":{"duration":183,"price":6000},
        "Platinum":{"duration":365,"price":10000}
        }

subscription_options = (
            ("Basic","Basic"),
            ("Silver","Silver"),
            ("Gold","Gold"),
            ("Platinum","Platinum")
        )


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=100,required=True)
    c_password = serializers.CharField(max_length=100,required=True)

    def validate(self,data):
        if data["password"] != data["c_password"]:
            raise serializers.ValidationError({"error":"Mismatched Passwords"})
        else:
            return data

    def create(self,validated_data):
        validated_data.pop("c_password")
        validated_data["sub_date"] = datetime.now()
        validated_data["exp_date"] = validated_data["sub_date"] + timedelta(days=7)
        validated_data["username"] = uuid.uuid4()
        user = models.Users.objects.create_user(**validated_data)
        output = {
                    "email":user.email,
                    "subscription_expiry":user.exp_date.strftime("%Y-%m-%d")
                }
        return output

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=100)

    def validate(self,data):
        if models.Users.objects.filter(email=data["email"]).exists():
            user = models.Users.objects.get(email=data["email"])
            if user.check_password(data["password"]):
                return user
            else:
                raise serializers.ValidationError({"error":"Incorrect credentials"})
        else:
            raise serializers.ValidationError({"error":"Incorrect credentials"})


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Content
        fields = ["id","title","description","category","tags","ai_score"]
        read_only_fields = ["id"]

class SubscriptionSerializer(serializers.Serializer):
    plan = serializers.ChoiceField(choices=subscription_options)
    auto_renew = serializers.BooleanField(default=False,required=False)
    #Collect card details and implement price transaction for subscription APIs.

    def update(self,instance,validated_data):
        previous_expiry = instance.exp_date
        plan_duration = subscription_plans[validated_data["plan"]]["duration"]
        current_expiry = previous_expiry + timedelta(days=plan_duration)
        instance.exp_date = current_expiry
        instance.auto_renewal = validated_data.get("auto_renew",instance.auto_renewal)
        instance.save()
        output = {
                    "email":instance.email,
                    "exp_date":instance.exp_date
                }
        return output

#Assumption is a Like interaction must be preceded by a view
class UserInteractionSerializer(serializers.Serializer):
    content_id = serializers.IntegerField(required=True)

    def validate(self,data):
        if models.Content.objects.filter(id=data["content_id"]).exists():
            request = self.context["request"]
            data["user"] = request.user
            data["content"] = models.Content.objects.get(id=data["content_id"])
            return data
        else:
            raise serializers.ValidationError({"error":"Invalid Content Id"})

    def create(self,validated_data):
        content = validated_data.get("content")
        user = validated_data.get("user")
        try:
            interaction_instance = models.UserInteraction.objects.get(user=user,content=content)
            interaction_instance.interaction = "Liked"
            interaction_instance.save()
        except:
            models.UserInteraction.objects.create(
                        user=user,
                        content=content,
                        interaction = "Liked"
                    )
        output = {
                        "content_title":content.title,
                        "interaction":"Liked"
                    }
        return output
