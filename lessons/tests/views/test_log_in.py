from django.test import TestCase
from django.urls import reverse
from lessons.models import User, Student, SchoolAdmin
from lessons.tests.helpers import LogInTester
from lessons.forms import LogInForm
from django.contrib import messages

# Create your tests here.
class LogInTest(TestCase, LogInTester):
    def setUp(self):
        self.url = reverse("log_in")
        user = User.objects.create_user(
            email="student@example.org",
            first_name="Real",
            last_name="Person",
            password="password",
        )
        user.save()
        self.student = Student.objects.create(
            user=user, school_name="Queen's Trade School Waitangi"
        )
        self.schooladmin = SchoolAdmin.objects.create(
            user=user, school_name = "King's", is_director=True, can_edit_admins= False, can_create_admins = False, can_delete_admins= False,
        )

    def test_url(self):
        self.assertEqual(self.url, "/log_in/")

    #check if ther form is being displayed correctly
    def test_get_log_in(self):
        response = self.client.get(self.url) #use that to make requests and simulate responses programatically
        #status code should be 200 from responses
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        messages_list = list(response.context['messages'])#retrieve list of messages
        self.assertEqual(len(messages_list), 0) #don't get messages when loggin in

    def test_failed_login_pass(self):
        invalid_pass = ("student@example.org", "passwor")
        self.assertFalse(
            self.client.login(email=invalid_pass[0], password=invalid_pass[1])
        )
        self.assertFalse(self.is_logged_in())

    def test_failed_login_email(self):
        invalid_pass = ("notAnEmail", "password")
        self.assertFalse(
            self.client.login(email=invalid_pass[0], password=invalid_pass[1])
        )
        self.assertFalse(self.is_logged_in())

    def test_unsuccessful_student_log_in(self):
        form_input = {'email':self.student.user.email, 'password': 'WrongPassword123'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])#retrieve list of messages
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_unsuccessful_director_log_in(self):
        form_input = {'email':self.schooladmin.user.email, 'password': 'WrongPassword123'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])#retrieve list of messages
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_valid_log_in_by_inactive_student(self):
        self.student.user.is_active=False
        self.student.user.save()
        form_input = {'email': self.student.user.email, 'password': self.student.user.password}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self.student._is_logged_in())
        messages_list = list(response.context['messages'])#retrieve list of messages
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_valid_log_in_by_inactive_director(self):
        self.schooladmin.user.is_active=False
        self.schooladmin.user.save()
        form_input = {'email': self.schooladmin.user.email, 'password': self.scholadmin.user.password}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertTrue(form.is_bound)
        self.assertFalse(self.schooladmin._is_logged_in())
        messages_list = list(response.context['messages'])#retrieve list of messages
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_valid_log_in_by_student(self):
        form_input = {'username': self.student.user.email, 'password': self.student.user.password}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self.student._is_logged_in())
        #responseurl - url we are getting redirected to
        response_url = reverse('account')
        #target_status_code - code of eventual redirect
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'account_student.html')
        messages_list = list(response.context['messages'])#retrieve list of messages
        self.assertEqual(len(messages_list), 0)#don't get any messages when successfully logging in

    def test_valid_log_in_by_director(self):
        form_input = {'username': self.schooladmin.user.email, 'password': self.schooladmin.user.password}
        response = self.client.post(self.url, form_input, follow=True)
        self.assertTrue(self.schooladmin._is_logged_in())
        #responseurl - url we are getting redirected to
        response_url = reverse('account')
        #target_status_code - code of eventual redirect
        self.assertRedirects(response, response_url, status_code=302, target_status_code=200)
        self.assertTemplateUsed(response, 'account_admin.html')
        messages_list = list(response.context['messages'])#retrieve list of messages
        self.assertEqual(len(messages_list), 0)#don't get any messages when successfully logging in

    def test_log_in_with_blank_username(self):
        form_input = {'email':'', 'password': 'Password123'}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])#retrieve list of messages
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)

    def test_log_in_with_blank_password(self):
        form_input = {'email': 'example.email@fox.org', 'password' : ''}
        response = self.client.post(self.url, form_input)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'log_in.html')
        form = response.context['form']
        self.assertTrue(isinstance(form, LogInForm))
        self.assertFalse(form.is_bound)
        self.assertFalse(self._is_logged_in())
        messages_list = list(response.context['messages'])#retrieve list of messages
        self.assertEqual(len(messages_list), 1)
        self.assertEqual(messages_list[0].level, messages.ERROR)
