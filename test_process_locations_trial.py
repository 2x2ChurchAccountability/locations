import unittest
import process_locations
# Set validate_mode to True in the process_locations module
process_locations.validate_mode = True
from process_locations import handle_started_work, handle_workers_meeting, handle_special_meeting, handle_photo, handle_workers_list, handle_location_only, handle_convention, text_fixes, get_state_country
from countries_data import countries

class TestGetStateCountry(unittest.TestCase):
    def setUp(self):
        # Use the imported countries data
        self.countries = countries



        


        







    # July 6, Started in the work
    def test_july_6_started_in_the_work(self):
        """Test july_6_started_in_the_work"""
        line = "July 6, Started in the work"
        result = handle_location_only(text_fixes(line), self.countries)
        self.assertEqual(result['state'], '--United States--')
        self.assertEqual(result['country'], '--United States--')
        self.assertEqual(result['location'], '--United States--')
        self.assertEqual(result['note'], 'July 6, Started in the work')
        self.assertEqual(result['month'], 'July')
        self.assertEqual(result['start_date'], '07/06')







if __name__ == '__main__':
    unittest.main() 