from django.db import models
from common.models import CommonModel

class Experience(CommonModel):

  """Experience Model Definition"""

  country = models.CharField(
    max_length=50,
    default="S.Korea",
  )
  city = models.CharField(
    max_length=80,
    default="Seoul",
  )
  name = models.CharField(
    max_length=250,
  )
  host = models.ForeignKey(
    "users.User",
    on_delete=models.CASCADE,
  )
  price = models.PositiveIntegerField()
  address = models.CharField(
    max_length=250,
  )
  start = models.TimeField()
  end = models.TimeField()
  description = models.TextField()
  perks = models.ManyToManyField(
    "experiences.Perk",
  )


class Perk(CommonModel):

  """What is included on an Experience"""

  name = models.CharField(
    max_length=100,
  )
  details = models.CharField(
    max_length=250,
  )
  explanation = models.TextField()
