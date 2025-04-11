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



        

    # Rocanville Saskatchewan Special Meeting (Dec. 19th)
    def test_rocanville_saskatchewan_special_meeting_dec_19th(self):
        """Test rocanville_saskatchewan_special_meeting_dec_19th"""
        line = "Rocanville Saskatchewan Special Meeting (Dec. 19th)"
        result = handle_special_meeting(text_fixes(line), self.countries)
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['state'], 'Saskatchewan')
        self.assertEqual(result['location'], 'Rocanville')
        self.assertEqual(result['note'], 'Dec. 19th Special Meeting')
        self.assertEqual(result['month'], 'Dec')
        self.assertEqual(result['start_date'], '12/19')





if __name__ == '__main__':
    unittest.main() 