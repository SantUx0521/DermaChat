import pytest
from django.test import TestCase
from rest_framework.test import APIClient,APITestCase
from django.db.utils import IntegrityError
from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework import status