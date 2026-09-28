import unittest

from card_crypto import CardCipher, CardError, luhn_valid, mask_pan, normalize_pan


class CardCryptoTests(unittest.TestCase):
    def test_luhn_accepts_test_number(self):
        self.assertTrue(luhn_valid("4242424242424242"))

    def test_luhn_rejects_invalid_number(self):
        self.assertFalse(luhn_valid("4242424242424241"))

    def test_normalize_and_mask(self):
        pan = normalize_pan("4242 4242 4242 4242")
        self.assertEqual(mask_pan(pan), "************4242")

    def test_invalid_pan_raises(self):
        with self.assertRaises(CardError):
            normalize_pan("1234")

    def test_authenticated_round_trip(self):
        cipher = CardCipher(b"x" * 32)
        payload = cipher.encrypt("4242424242424242", "tok_test")
        self.assertEqual(cipher.decrypt(payload, "tok_test"), "4242424242424242")

    def test_random_nonce_changes_ciphertext(self):
        cipher = CardCipher(b"x" * 32)
        first = cipher.encrypt("4242424242424242", "tok_test")
        second = cipher.encrypt("4242424242424242", "tok_test")
        self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()
