import random
import string
from datetime import timedelta
from decimal import Decimal
from decruck.main.models import (
    Order, OrderItemLink, ScorePage, ScoreListingPage, ShoppingCartPage,
    ContactFormPage, Message
)
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone
from os.path import join
from paypal.standard.ipn.tests.test_ipn import MockedPostbackMixin
from six import text_type
from six.moves.urllib.parse import urlencode
from wagtail.core.rich_text import RichText


CHARSET = "windows-1252"


class CompositionModelTest(TestCase):
    def test_test(self):
        pass


class ContactPageTest(TestCase):
    def test_form_submission(self):
        self.assertEqual(0, Message.objects.count())
        self.client.post(
            ContactFormPage.objects.first().url,
            {
                'name': 'Maurice Decruck',
                'email_address': 'maurice@decruck.com',
                'message': 'I like to play the bass.'
            }
        )
        self.assertEqual(1, Message.objects.count())
        self.assertEqual(len(mail.outbox), 1)


class ScorePageTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Sample score page
        parent = ScoreListingPage.objects.first()
        with open(join(settings.BASE_DIR, 'data/pdf_example.pdf'), 'rb') as f:
            pdf_file = InMemoryUploadedFile(
                file=f,
                field_name=None,
                name='pdf_example.pdf',
                size=f.tell,
                content_type='application/pdf',
                charset=None,
                content_type_extra=None
            )
            score = ScorePage(
                title='Example Score',
                cover_image=None,
                description=[
                    ('rich_text', RichText('<p>Description text</p>'))],
                duration='00:05:43',
                price='14.99',
                file=pdf_file,
                preview_score=pdf_file
            )
            parent.add_child(instance=score)
            score.save_revision().publish()
            cls.score = score

    def test_create_preview_score_images(self):
        self.assertEquals(self.score.preview_score_images.count(), 2)

    def test_add_remove_shopping_cart(self):
        """
        Test adding and removing items from the shopping cart
        """
        # Add item
        self.client.post(self.score.get_url())
        self.assertListEqual(
            self.client.session['shopping_cart'],
            [self.score.pk]
        )

        # Remove item
        self.client.post(self.score.get_url())
        self.assertListEqual(
            self.client.session['shopping_cart'],
            []
        )


@override_settings(PAYPAL_ACCT_EMAIL='email-facilitator@gmail.com')
class ShoppingCartPageTest(MockedPostbackMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        # Cart page
        cls.cart = ShoppingCartPage.objects.first()

        # Sample score page
        parent = ScoreListingPage.objects.first()
        with open(join(settings.BASE_DIR, 'data/pdf_example.pdf'), 'rb') as f:
            pdf_file_one = InMemoryUploadedFile(
                file=f,
                field_name=None,
                name='pdf_example.pdf',
                size=f.tell,
                content_type='application/pdf',
                charset=None,
                content_type_extra=None
            )
            s1 = ScorePage(
                title='Example Score One',
                cover_image=None,
                description=[
                    ('rich_text', RichText('<p>Description text</p>'))],
                duration='00:05:43',
                price='14.99',
                file=pdf_file_one,
                preview_score=pdf_file_one
            )
            parent.add_child(instance=s1)
            s1.save_revision().publish()

        with open(join(settings.BASE_DIR, 'data/pdf_example.pdf'), 'rb') as f:
            pdf_file_two = InMemoryUploadedFile(
                file=f,
                field_name=None,
                name='pdf_example.pdf',
                size=f.tell,
                content_type='application/pdf',
                charset=None,
                content_type_extra=None
            )
            s2 = ScorePage(
                title='Example Score Two',
                cover_image=None,
                description=[
                    ('rich_text', RichText('<p>Description text</p>'))],
                duration='00:05:43',
                price='14.99',
                file=pdf_file_two,
                preview_score=pdf_file_two
            )
            parent.add_child(instance=s2)
            s2.save_revision().publish()

        cls.scores = [s1, s2]

    def setUp(self):
        super().setUp()
        """Add test scores to cart before eact test case"""
        for score in self.scores:
            if score.pk not in self.client.session:
                self.client.post(score.get_url())

    def paypal_post(self, params):
        """
        Does an HTTP POST the way that PayPal does, using the params given.
        """
        # Taken from paypal.standard.ipn.tests.test_ipn, POST path modified
        # We build params into a bytestring ourselves, to avoid some encoding
        # processing that is done by the test client.
        def cond_encode(param):
            return param.encode(CHARSET) \
                if isinstance(param, text_type) else param

        byte_params = {
            cond_encode(k): cond_encode(v) for k, v in params.items()}
        post_data = urlencode(byte_params)
        return self.client.post(
            "/paypal/",
            post_data,
            content_type='application/x-www-form-urlencoded'
        )

    @staticmethod
    def generate_params(amount, uuid):
        """
        Creates a dict of test params for test requests
        """
        amt = str(amount).encode(encoding='UTF-8')
        item_num = str(uuid).encode(encoding='UTF-8')

        # Transactions with the same ID won't be processed
        txn_id = ''.join(
            [random.choice(string.ascii_uppercase + string.digits) for i
             in range(17)]).encode(encoding='UTF-8')

        return {
            'btn_id1': b"3453595",
            'business': b"email-facilitator@gmail.com",
            'charset': b"windows-1252",
            "first_name": b"Maurice",
            'last_name': b"Decruck",
            'ipn_track_id': b"a48170aadb705",
            'item_name': b"Scores by Fernande Decruck",
            'item_number': item_num,
            'mc_currency': b"USD",
            'mc_fee': b"0.35",
            'mc_gross': amt,
            'mc_gross_1': amt,
            'mc_handling': b"0.00",
            'mc_handling1': b"0.00",
            'mc_shipping': b"0.00",
            'mc_shipping1': b"0.00",
            'notify_version': b"3.8",
            'num_cart_items': b"1",
            'payer_email': b"email@gmail.com",
            'payer_id': b"6EQ6SKDFMPU36",
            'payer_status': b"verified",
            'payment_date': b"03:06:57 Jun 27, 2014 PDT",
            'payment_fee': b"",
            'payment_gross': b"",
            'payment_status': b"Completed",
            'payment_type': b"instant",
            'protection_eligibility': b"Ineligible",
            'quantity1': b"3",
            'receiver_email': b"email-facilitator@gmail.com",
            'receiver_id': b"UCWM6R2TARF36",
            'residence_country': b"US",
            'tax': b"0.00",
            'tax1': b"0.00",
            'test_ipn': b"0",
            'transaction_subject': b"blahblah",
            'txn_id': txn_id,
            'txn_type': b"web_accept",
            'verify_sign': b"A_SECRET_CODE"}

    def test_items_in_cart(self):
        # Check that the items are in the cart context
        response = self.client.get(self.cart.get_url())
        self.assertEquals(len(response.context['items']), 2)

        # Check the total in the cart context
        self.assertEquals(response.context['total'], Decimal('29.98'))

    def test_remove_item_from_cart(self):
        """Test removing items from cart"""
        score = self.scores[0]
        r1 = self.client.post(
            '{}remove/{}/'.format(self.cart.get_url(), score.pk))
        self.assertRedirects(r1, self.cart.get_url())

        # Check that removed item is no longer in the context
        r2 = self.client.get(self.cart.get_url())
        self.assertEquals(len(r2.context['items']), 1)

        self.assertEquals(r2.context['total'], Decimal('14.99'))

    def test_order_creation(self):
        """
        Test the confirmation page creates a
        new Order object in the correct state
        """
        self.assertEquals(len(Order.objects.all()), 0)
        self.client.get(self.cart.get_url() + 'confirmation/')

        self.assertEquals(Order.objects.count(), 1)
        self.assertEquals(Order.objects.first().items.count(), 2)
        self.assertEquals(Order.objects.first().status, 'INITIATED')

    def test_confirmation_page_context(self):
        # Test the context of the confirmation page contains the correct items
        # Test the context of the confirmation page contains an order UUID
        r = self.client.get(self.cart.get_url() + 'confirmation/')
        order = Order.objects.first()

        self.assertEquals(len(r.context['items']), 2)
        self.assertEquals(r.context['total'], Decimal('29.98'))
        self.assertContains(r, order.uuid)

    def test_thank_you_page(self):
        """Test that the thank you page clears items from the cart"""
        self.client.get(self.cart.get_url() + 'thank-you/')
        self.assertTrue('shopping_cart' not in self.client.session)

    def test_order_processing_valid(self):
        """Simulate a valid order"""
        # Create an order object, try posting valid values to the PayPal endpoint and check that:
        # - Link objects are created
        # - The email is sent
        # - The order status is updated when the links are sent
        # - The links are accessible

        # Check that no links already exist, validates creation below
        self.assertEqual(OrderItemLink.objects.all().count(), 0)

        # Simulate an order
        self.client.get(self.cart.get_url() + 'confirmation/')
        order = Order.objects.first()

        # check the initial state of the order
        self.assertEqual(order.status, Order.INITIATED)

        params = self.generate_params(order.total, str(order.uuid))
        response = self.paypal_post(params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(
            'Thank you for your order / Merci pour votre commande',
            mail.outbox[0].subject
        )

        # Check that the status is updated
        order.refresh_from_db()
        self.assertEqual(order.status, Order.PAYMENT_RECEIVED)

        # Check that links are created
        links = OrderItemLink.objects.all()
        self.assertEqual(links.count(), 2)

        # Check that links work
        for link in links:
            res = self.client.get(link.relative_url)
            self.assertEqual(res.status_code, 200)

    def test_order_processing_invalid_uuid(self):
        """Simulate an order with an invalid UUID"""
        # Post an order to the PayPal endpoint with a phony UUID and check that it takes no action

        # Check that no links already exist, validates creation below
        self.assertEqual(OrderItemLink.objects.all().count(), 0)

        # Simulate an order
        self.client.get(self.cart.get_url() + 'confirmation/')
        order = Order.objects.first()

        # check the initial state of the order
        self.assertEqual(order.status, Order.INITIATED)

        params = self.generate_params(order.total, 'space-lizard')
        response = self.paypal_post(params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

        # Check that the status is updated
        order.refresh_from_db()
        self.assertEqual(order.status, Order.INITIATED)

        # Check that links are created
        links = OrderItemLink.objects.all()
        self.assertEqual(links.count(), 0)

    def test_order_processing_invalid_total(self):
        """Simulate an order with an invalid total"""
        # Post an order the the PayPal endpoint with a real UUID but incorrect total and check that it takes no action
        # Check that no links already exist, validates creation below
        self.assertEqual(OrderItemLink.objects.all().count(), 0)

        # Simulate an order
        self.client.get(self.cart.get_url() + 'confirmation/')
        order = Order.objects.first()

        # check the initial state of the order
        self.assertEqual(order.status, Order.INITIATED)

        params = self.generate_params(Decimal('1.99'), str(order.uuid))
        response = self.paypal_post(params)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

        # Check that the status is updated
        order.refresh_from_db()
        self.assertEqual(order.status, Order.INITIATED)

        # Check that links are created
        links = OrderItemLink.objects.all()
        self.assertEqual(links.count(), 0)

    def test_order_retrieval_valid_email(self):
        """
        Check that the order retreival page sends email with
        correct links when given valid email
        """
        # Simulate an order
        self.client.get(self.cart.get_url() + 'confirmation/')
        order = Order.objects.first()
        params = self.generate_params(order.total, str(order.uuid))
        self.paypal_post(params)

        response = self.client.post(
            self.cart.get_url() + 'retrieve-order/',
            {'email_address': 'email@gmail.com'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 2)

    def test_order_retrieval_invalid_email(self):
        """
        Test that no email is sent when an invalid email is given
        """
        response = self.client.post(
            self.cart.get_url() + 'retrieve-order/',
            {'email_address': 'foo@bar.com'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_retrieval_links(self):
        """
        Check that the retrieval links work within 24 hours of now
        Check that retrieval links don't work when thier expiration time is set
        to be more than 24 hours ago
        """
        # Simulate an order
        self.client.get(self.cart.get_url() + 'confirmation/')
        order = Order.objects.first()
        params = self.generate_params(order.total, str(order.uuid))
        self.paypal_post(params)

        links = OrderItemLink.objects.all()
        for link in links:
            r = self.client.get(link.relative_url)
            self.assertEqual(r.status_code, 200)

        # test expired links
        for link in links:
            link.expires = timezone.now() - timedelta(days=2)
            link.save()

        # links = OrderItemLink.objects.all()
        for link in links:
            r = self.client.get(link.relative_url)
            self.assertEqual(r.status_code, 404)

# TODO
# Add test to check that an order with an empty cart can not be created
# Inspect the links in the emails
