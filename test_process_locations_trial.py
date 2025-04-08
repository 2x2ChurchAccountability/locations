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



        


        






    # Bonao, Republica Dominicana Convention
    def test_bonao_republica_dominicana_convention(self):
        """Test bonao_republica_dominicana_convention"""
        line = "Bonao, Republica Dominicana Convention"
        result = handle_convention(text_fixes(line), self.countries)
        self.assertEqual(result['state'], 'Dominican Republic')
        self.assertEqual(result['country'], 'Dominican Republic')
        self.assertEqual(result['location'], 'Bonao')
        self.assertEqual(result['note'], 'Republica Dominicana Convention')
        self.assertEqual(result['month'], None)







if __name__ == '__main__':
    unittest.main() 