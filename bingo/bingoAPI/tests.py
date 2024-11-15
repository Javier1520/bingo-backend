from django.test import TestCase
from bingoAPI.models import BingoCard

class BingoCardTest(TestCase):
    def setUp(self):
        self.card = BingoCard.objects.create(numbers={
            'B': [1, 2, 3, 4, 5],
            'I': [16, 17, 18, 19, 20],
            'N': [31, 32, None, 34, 35],
            'G': [46, 47, 48, 49, 50],
            'O': [61, 62, 63, 64, 65]
        })

    def test_card_generation(self):
        """Test that generated cards are unique and properly structured"""
        card = BingoCard()
        card.generate_unique_card()

        # Verify structure
        self.assertTrue(all(col in card.numbers for col in 'BINGO'))
        self.assertEqual(len(card.numbers['B']), 5)
        self.assertEqual(len(card.numbers['I']), 5)
        self.assertEqual(len(card.numbers['N']), 5)
        self.assertEqual(len(card.numbers['G']), 5)
        self.assertEqual(len(card.numbers['O']), 5)

        # Verify ranges
        self.assertTrue(all(1 <= n <= 15 for n in card.numbers['B'] if n))
        self.assertTrue(all(16 <= n <= 30 for n in card.numbers['I'] if n))
        self.assertTrue(all(31 <= n <= 45 for n in card.numbers['N'] if n))
        self.assertTrue(all(46 <= n <= 60 for n in card.numbers['G'] if n))
        self.assertTrue(all(61 <= n <= 75 for n in card.numbers['O'] if n))

        # Verify free space
        self.assertIsNone(card.numbers['N'][2])

    def test_unique_cards(self):
        """Test that generated cards are unique"""
        cards = set()
        for _ in range(5):  # Generate 5 cards
            card = BingoCard()
            card.generate_unique_card()
            cards.add(str(card.numbers))
        self.assertEqual(len(cards), 5)

    def test_row_win(self):
        """Test winning by completing a row"""
        # Test first row
        drawn_balls = {1, 16, 31, 46, 61}  # First row
        self.assertTrue(self.card.is_winner(drawn_balls))

    def test_third_row_win(self):
        """Test winning by completing a row"""
        # Test third row
        drawn_balls = {3, 18, 48, 63}  # Third row
        self.assertTrue(self.card.is_winner(drawn_balls))

    def test_column_win(self):
        """Test winning by completing a column"""
        # Test first column
        drawn_balls = {1, 2, 3, 4, 5}  # B column
        self.assertTrue(self.card.is_winner(drawn_balls))

    def test_column_n_win(self):
        """Test winning by completing a column"""
        # Test third column
        drawn_balls = {31, 32, 34, 35}  # N column
        self.assertTrue(self.card.is_winner(drawn_balls))

    def test_main_diagonal_win(self):
        """Test winning by completing main diagonal"""
        drawn_balls = {1, 17, 49, 65}  # Don't need 33 due to free space
        self.assertTrue(self.card.is_winner(drawn_balls))

    def test_anti_diagonal_win(self):
        """Test winning by completing anti-diagonal"""
        drawn_balls = {5, 19, 47, 61}  # Don't need 33 due to free space
        self.assertTrue(self.card.is_winner(drawn_balls))

    def test_four_corners_win(self):
        """Test winning by completing four corners"""
        drawn_balls = {1, 5, 61, 65}  # Four corners
        self.assertTrue(self.card.is_winner(drawn_balls))

    def test_full_card_win(self):
        """Test winning by completing full card"""
        drawn_balls = set()
        for col in self.card.numbers.values():
            drawn_balls.update(num for num in col if num is not None)
        self.assertTrue(self.card.is_winner(drawn_balls))

    def test_incomplete_pattern(self):
        """Test that incomplete patterns don't win"""
        # Almost complete row
        drawn_balls = {1, 16, 31, 46}  # Missing 61
        self.assertFalse(self.card.is_winner(drawn_balls))

        # Almost complete column
        drawn_balls = {1, 2, 3, 4}  # Missing 5
        self.assertFalse(self.card.is_winner(drawn_balls))

        # Almost complete diagonal
        drawn_balls = {1, 17, 49}  # Missing 65
        self.assertFalse(self.card.is_winner(drawn_balls))

    def test_free_space(self):
        """Test that free space is correctly handled"""
        # Test row with free space
        drawn_balls = {31, 32, 34, 35}  # Middle row without free space
        self.assertTrue(self.card.is_winner(drawn_balls))

        # Test column with free space
        drawn_balls = {31, 32, 34, 35}  # N column without free space
        self.assertTrue(self.card.is_winner(drawn_balls))

    def test_random_non_winning_numbers(self):
        """Test that random non-winning combinations don't win"""
        drawn_balls = {1, 17, 33, 49, 62}  # Random numbers
        self.assertFalse(self.card.is_winner(drawn_balls))

    def test_empty_drawn_balls(self):
        """Test with no drawn balls"""
        self.assertFalse(self.card.is_winner([]))

    def test_all_numbers_drawn(self):
        """Test with all possible numbers drawn"""
        drawn_balls = set(range(1, 76))
        self.assertTrue(self.card.is_winner(drawn_balls))
