from django.test import TestCase
from django.test import SimpleTestCase

from django.urls import reverse

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Ticket, Ticket_month_year
# Create your tests here.


class AboutpageTests(SimpleTestCase):
    def test_url_available_by_name(self):
        response = self.client.get(reverse("Pana-about"))
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):
        response = self.client.get(reverse("Pana-about"))
        self.assertTemplateUsed(response, "Home/about.html")

    def test_template_content(self):
        response = self.client.get(reverse("Pana-about"))
        self.assertContains(response, "<h1>About PAge!</h1>")
        self.assertNotContains(response, "Not on the page")

class Testhomeview(TestCase):
    def test_anonymous_cannot_see_page(self):
        response = self.client.get(reverse("Pana-home"))
        self.assertRedirects(response, "/login/?next=/")

    def test_authenticated_user_can_see_home_page(self):
        user = User.objects.create_user("Juliana", "Julianacompany@test.com", "Some_pass321")
        self.client.force_login(user=user)
        response = self.client.get(reverse("Pana-home"))
        self.assertContains(response, "<h1>Panalog HomePage Welcome!</h1>")
        self.assertEqual(response.status_code, 200)

class TestTicketCreation(TestCase):
    def test_ticket_creation(self):
        ticket1 = Ticket.objects.create(ticketNo = "222-222222")
        self.assertEqual(str(ticket1), "222-222222")
        print("Created Ticket 222-2222222 :", isinstance(ticket1,Ticket))
        self.assertTrue(isinstance(ticket1,Ticket))

class SigninTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="Clifford", password="Some_pass453", email="cliffishere@test.com")
        self.user.save()

    def tearDown(self):
        self.user.delete()

    def test_success(self):
        user = authenticate(username="Clifford", password="Some_pass453")
        self.assertTrue((user is not None) and user.is_authenticated)

    def test_wrong_username(self):
        user = authenticate(username="Clearlywrong", password="Some_pass453")
        self.assertFalse(user is not None and user.is_authenticated)

    def test_wrong_password(self):
        user = authenticate(username="Clifford", password="Clearlythisiswrong443")
        self.assertFalse(user is not None and user.is_authenticated)
