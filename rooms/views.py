from rest_framework.views import APIView
from django.db import transaction
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, NotAuthenticated, ParseError, PermissionDenied
from .models import Amenity, Room
from categories.models import Category
from .serializers import AmenitySerializer, RoomListSerializer, RoomDetailSerializer


class Amenities(APIView):
  def get(self, request):
    all_amenities = Amenity.objects.all()
    serializer = AmenitySerializer(all_amenities, many=True)
    return Response(serializer.data)

  def post(self, request):
    serializer = AmenitySerializer(data=request.data)
    if serializer.is_valid():
      amenity = serializer.save()
      return Response(AmenitySerializer(amenity).data)
    else:
      return Response(serializer.errors)


class AmenityDetail(APIView):

  def get_object(self, pk):
    try:
      return Amenity.objects.get(pk=pk)
    except Amenity.DoesNotExist:
      raise NotFound

  def get(self, request, pk):
    amenity = self.get_object(pk)
    serializer = AmenitySerializer(amenity)
    return Response(serializer.data)

  def put(self, request, pk):
    amenity = self.get_object(pk)
    serializer = AmenitySerializer(
      amenity,
      data=request.data,
      partial=True
    )
    if serializer.is_valid():
      updated_amenity = serializer.save()
      return Response(AmenitySerializer(updated_amenity.data))
    else:
      return Response(serializer.errors)

  def delete(self, request, pk):
    amenity = self.get_object(pk)
    amenity.delete()
    return Response(status=HTTP_204_NO_CONTENT)
  

class Rooms(APIView):
  def get(self, request):
    all_rooms = Room.objects.all()
    serializer = RoomListSerializer(all_rooms, many=True)
    return Response(serializer.data)
  
  def post(self, request):
    if request.user.is_authenticated:
      serializer = RoomDetailSerializer(data=request.data)
      if serializer.is_valid():
        category_pk = request.data.get("category")
        if not category_pk:
          raise ParseError("Category is required.")
        try:
          category = Category.objects.get(pk=category_pk)
          if category.kind == Category.CategoryKindChoices.EXPERIENCES:
            raise ParseError("The category kind should be 'rooms'")
        except Category.DoesNotExist:
          raise ParseError("Category not found")
        try:
          with transaction.atomic():
            room = serializer.save(
              owner=request.user,
              category=category,
            )
            amenities = request.data.get("amenities")
            for amenity_pk in amenities:
              amenity = Amenity.objects.get(pk=amenity_pk)
              room.amenities.add(amenity)
            serializer = RoomDetailSerializer(room)
            return Response(serializer.data)
        except Exception:
          raise ParseError("Amenity not found")
      else:
        return Response(serializer.errors)
    else:
      raise NotAuthenticated
  

class RoomDetail(APIView):
  def get_object(self, pk):
    try:
      return Room.objects.get(pk=pk)
    except Room.DoesNotExist:
      raise NotFound

  def get(self, request, pk):
    room = self.get_object(pk)
    serializer = RoomDetailSerializer(room)
    return Response(serializer.data)
  
  def put(self, request, pk):
    room = self.get_object(pk)
    if not request.user.is_authenticated:
      raise NotAuthenticated
    if room.owner != request.user:
      raise PermissionDenied
    serializer = RoomDetailSerializer(
            room,
            data=request.data,
            partial=True,
    )

    if serializer.is_valid():
      category_pk = request.data.get("category")
      if category_pk:
        try:
          category = Category.objects.get(pk=category_pk)
          if category.kind == Category.CategoryKindChoices.EXPERIENCES:
            raise ParseError("The category kind should be rooms")
        except Category.DoesNotExist:
          raise ParseError(detail="Category not found")

      try:
        with transaction.atomic():
          if category_pk:
            room = serializer.save(category=category)
          else:
            room = serializer.save()

          amenities = request.data.get("amenities")
          if amenities:
            room.amenities.clear()
            for amenity_pk in amenities:
              amenity = Amenity.objects.get(pk=amenity_pk)
              room.amenities.add(amenity)

          return Response(RoomDetailSerializer(room).data)
      except Exception as e:
        print(e)
        raise ParseError("amenity not found")
    else:
      return Response(serializer.errors)

  
  def delete(self, request, pk):
    room = self.get_object(pk)
    if not request.user.is_authenticated:
      raise NotAuthenticated
    if room.owner != request.user:
      raise PermissionDenied
    room.delete()
    return Response(status=HTTP_204_NO_CONTENT)

  


'''
{
  "name": "House created with DRF",
  "country": "S.Korea",
  "city": "Seoul",
  "price": 1000,
  "rooms": 2,
  "toilets": 2,
  "description": "DRF is great!",
  "address": "123",
  "pet_friendly": true,
  "category": 3,
  "amenities": [67777, 2, 3, 4],
  "kind": "private_room"
}
'''