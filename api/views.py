#from django.shortcuts import render
from rest_framework.decorators import permission_classes
from rest_framework.response import Response 
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets

from . import tasks

from django.http import Http404
from django.core.cache import cache


from . import models, serializers
import pickle


class RegistrationView(APIView):
    permission_classes = [
                AllowAny,
            ]
    serializer_class = serializers.RegistrationSerializer

    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response(user,status=status.HTTP_201_CREATED)

class LoginView(APIView):
    permission_classes = [
                AllowAny,
            ]
    serializer_class = serializers.LoginSerializer

    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.validated_data
            token = RefreshToken.for_user(user)
            output = {
                        "access":str(token.access_token),
                        "refresh":str(token),
                        "user":user.email
                    }
            return Response(output,status=status.HTTP_200_OK)


class ContentViewSet(viewsets.ModelViewSet):
    permission_classes = [
                IsAuthenticated,
            ]
    queryset = models.Content.objects.all()
    serializer_class = serializers.ContentSerializer

    #def get(self,request,url)

class SubscriptionView(APIView):
    permission_classes = [
                IsAuthenticated,
            ]
    serializer_class = serializers.SubscriptionSerializer

    def get_object(self,request):
        user = models.Users.objects.filter(email=request.user.email).first()
        return user

    def put(self,request):
        user = self.get_object(request)
        serializer = self.serializer_class(data=request.data,instance=user)
        if serializer.is_valid(raise_exception=True):
            output = serializer.save()
            return Response(output,status=status.HTTP_201_CREATED)

class InteractionView(APIView):
    permission_classes = [
                IsAuthenticated,
            ]
    serializer_class = serializers.UserInteractionSerializer

    def get(self,request):
        content_id = request.query_params.get("id",None)
        try:
            content = models.Content.objects.get(id=content_id)
            user = request.user
            if models.UserInteraction.objects.filter(user=user,content=content).exists():
                pass
            else:
                models.UserInteraction.objects.create(
                        user=user,
                        content=content,
                        interaction = "Viewed"
                    )
                tasks.train_predictor.delay()
                cache.delete("Recommendations")
            output = {
                        "title":content.title,
                        "description":content.description,
                    }
            return Response(output,status=status.HTTP_200_OK)
        except:
            raise Http404({"error":"Invalid Content Id"})

    def post(self,request):
        serializer = self.serializer_class(data=request.data,context={"request":request})
        if serializer.is_valid(raise_exception=True):
            output = serializer.save()
            tasks.train_predictor.delay()
            cache.delete("Recommendations")
            return Response(output,status=status.HTTP_201_CREATED)

    def delete(self,request):
        content_id = request.query_params.get("id",None)
        try:
            content = models.Content.objects.get(id=content_id)
            user = request.user
            try:
                interaction =models.UserInteraction.objects.get(user=user,content=content)
                interaction.delete()
                tasks.train_predictor.delay()
                cache.delete("Recommendations")
                return Response(status=status.HTTP_204_NO_CONTENT)
            except:
                return Response({"error":"No related history with content"},status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"error":"Invalid Content Id"},status=status.HTTP_400_BAD_REQUEST)



class PredictionView(APIView):
    permission_classes = [
                IsAuthenticated,
            ]

    def get(self,request):
        user = request.user
        recommendations = cache.get("Recommendations")
        if not recommendations:
            #To ensure updated model is used everytime incase of periodic training
            with open("predictor.pkl","rb") as file:
                predictor = pickle.load(file)
            Unseen_contents = models.UserInteraction.objects.exclude(user=user).values("content")
        
            container = []
            for item in Unseen_contents:
                container.append(item["content"])
            Unseen_contents = set(container)
            predictions = []
            for item in Unseen_contents:
                pred = predictor.predict(user.id,item)
                predictions.append(pred)
            predictions.sort(key=lambda x:x.est,reverse=True)
            if len(predictions) > 5:
                top_5 = predictions[:5]
            else:
                top_5 = predictions
            output = []
            [output.append({"Content":models.Content.objects.filter(id=item.iid).values("title","description","category","tags","ai_score"),"Recommendation Index":item.est}) for item in top_5]
            #store cache for 1 hour
            cache.set("Recommendations",output,timeout=60*60)
            return Response(output,status=status.HTTP_200_OK)
        else:
            return Response(recommendations,status=status.HTTP_200_OK)


class TrainPredictorView(APIView):
    permission_classes = [
                AllowAny,
            ]
    def get(self,request):
        tasks.train_predictor.delay()
        return Response("Training Model",status=status.HTTP_200_OK)

