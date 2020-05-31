from django.test import TestCase


class CompositionModelTest(TestCase):
    # write some code to bootstrap a homepage, composition listing page
    # and a composition
    # Think about factories and a mixin
    def test_test(self):
        pass


class ScorePageTest(TestCase):
    def test_test(self):
        pass
        # test adding and removing items from the shopping cart


class ShoppingCartPageTest(TestCase):
    def test_test(self):
        pass
    # Test removing items from cart
    # Test the confirmation page creates a new Order object in the correct state
    # Test the context of the confirmation page contains the correct items
    # Test the context of the confirmation page contains an order UUID
    # Test that the thank you page clears items from the cart
    # Create an order object, try posting valid values to the PayPal endpoint and check that:
    # - Link objects are created
    # - The email is sent
    # Post an order to the PayPal endpoint with a phony UUID and check that it takes no action
    # Post an order the the PayPal endpoint with a real UUID but incorrect total and check that it takes no action
    # Check that the order status is updated when the links are sent
    # Check that the order retreival page sends email with correct links when given valid email
    # Check that the order retrieval page takes no action when given an email which has no associated orders
    # Check that the retrieval links work within 24 hours of now
    # Check that retrieval links don't work when thier expiration time is set to be more than 24 hours ago

