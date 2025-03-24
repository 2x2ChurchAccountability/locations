import unittest
from process_locations import process_text_patterns, handle_workers_list, handle_convention, handle_special_meeting, handle_travel, handle_location, handle_started_work, handle_photo, handle_workers_meeting, handle_removed_from, handle_guestbook, handle_location_only, handle_other, get_state_country
from countries_data import countries

class TestGetStateCountry(unittest.TestCase):
    def setUp(self):
        # Use the imported countries data
        self.countries = countries

    def test_simple_state_country(self):
        """Test basic state and country extraction"""
        result = get_state_country("California United States", self.countries)
        self.assertEqual(result['state'], 'California')
        self.assertEqual(result['country'], 'United States')

    def test_state_variation(self):
        """Test state variation (abbreviation) extraction"""
        result = get_state_country("CA United States", self.countries)
        self.assertEqual(result['state'], 'California')
        self.assertEqual(result['country'], 'United States')

    def test_combined_state(self):
        """Test combined state extraction (e.g., Oregon/South Idaho)"""
        result = get_state_country("Oregon/South Idaho United States", self.countries)
        self.assertEqual(result['state'], 'Oregon/South Idaho')
        self.assertEqual(result['country'], 'United States')

    def test_state_with_remaining_text(self):
        """Test when there's additional text after state and country"""
        result = get_state_country("California United States Some additional text", self.countries)
        self.assertEqual(result['state'], 'California')
        self.assertEqual(result['country'], 'United States')

    def test_canadian_province(self):
        """Test Canadian province extraction"""
        result = get_state_country("British Columbia Canada", self.countries)
        self.assertEqual(result['state'], 'British Columbia')
        self.assertEqual(result['country'], 'Canada')

    def test_canadian_province_variation(self):
        """Test Canadian province variation (abbreviation) extraction"""
        result = get_state_country("BC Canada", self.countries)
        self.assertEqual(result['state'], 'British Columbia')
        self.assertEqual(result['country'], 'Canada')

    def test_combined_canadian_province(self):
        """Test combined Canadian province extraction"""
        result = get_state_country("Quebec/Atlantic Canada", self.countries)
        self.assertEqual(result['state'], 'Quebec/Atlantic')
        self.assertEqual(result['country'], 'Canada')

    def test_no_match(self):
        """Test when no state or country is found"""
        result = get_state_country("Some random text", self.countries)
        self.assertIsNone(result['state'])
        self.assertIsNone(result['country'])

    def test_state_only(self):
        """Test when only state is found"""
        result = get_state_country("California", self.countries)
        self.assertEqual(result['state'], 'California')
        self.assertEqual(result['country'], 'United States')  # Defaults to US when only state found

    def test_country_only(self):
        """Test when only country is found"""
        result = get_state_country("United States", self.countries)
        self.assertIsNone(result['state'])
        self.assertEqual(result['country'], 'United States')

    def test_complex_combined_state(self):
        """Test complex combined state with multiple parts"""
        result = get_state_country("Tasmania Australia", self.countries)
        self.assertEqual(result['state'], 'Tasmania')  # Should match the state
        self.assertEqual(result['country'], 'Australia')

    def test_complex_paupa_new_guinea(self):
        """Test paupa_new_guinea"""
        line = "This is a test line for Australia/Papua New Guinea and (Tasmania)"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'Tasmania')  # Should match the state
        self.assertEqual(result['country'], 'Australia/Papua New Guinea')

    def test_simple_utah(self):
        """Test Utah"""
        line = "Salt Lake Utah Workers Meeting"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'Utah')  # Should match the state
        self.assertEqual(result['country'], 'United States')

    def test_simple_quebec_atlantic_canada(self):
        """Test quebec_atlantic_canada"""
        line = "Quebec/Atlantic Canada Workers List"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'Quebec/Atlantic')  # Should match the state
        self.assertEqual(result['country'], 'Canada')

    def test_simple_quebec_atlantic(self):
        """Test quebec_atlantic"""
        line = "Quebec/Atlantic Staff"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'Quebec/Atlantic')  # Should match the state
        self.assertEqual(result['country'], 'Canada')
        
    def test_complex_paupa_new_guinea2(self):
        """Test paupa_new_guinea2"""
        line = "Australia/Papua New Guinea Workers List (Tasmania)"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'Tasmania')  # Should match the state
        self.assertEqual(result['country'], 'Australia/Papua New Guinea')

    # Kootenays, Brisco BC Canada Special Meeting
    def test_kootenays_brisco_bc_canada_special_meeting(self):
        """Test kootenays_brisco_bc_canada_special_meeting"""
        line = "Kootenays, Brisco BC Canada Special Meeting"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'British Columbia')  # Should match the state
        self.assertEqual(result['country'], 'Canada')

    # Edgewood New Mexico Convention
    def test_edgewood_new_mexico_convention(self):
        """Test edgewood_new_mexico_convention"""
        line = "Edgewood New Mexico Convention"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'New Mexico')  # Should match the state
        self.assertEqual(result['country'], 'United States')

    # Wisconsin Dells Wisconsin Convention (Pennsylvania)
    def test_wisconsin_dells_wisconsin_convention(self):
        """Test wisconsin_dells_wisconsin_convention"""
        line = "Wisconsin Dells Wisconsin Convention (Pennsylvania)"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'Wisconsin')  # Should match the state
        self.assertEqual(result['country'], 'United States')

    # Prince George Canada Convention
    def test_prince_george_canada_convention(self):
        """Test prince_george_canada_convention"""
        line = "Prince George Canada Convention"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], None)  # Should match the state
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['line'], 'Prince George Convention')

    # Duncan BC Canada Convention Preps
    def test_duncan_bc_canada_convention_preps(self):
        """Test duncan_bc_canada_convention_preps"""
        line = "Duncan BC Canada Convention Preps"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'British Columbia')  # Should match the state
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['line'], 'Duncan Convention Preps')

    # Knoxville Tennessee
    def test_knoxville_tennessee(self):
        """Test knoxville_tennessee"""
        line = "Knoxville Tennessee"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'Tennessee')  # Should match the state
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['line'], 'Knoxville')

    # British Columbia Staff Photo
    def test_british_columbia_staff_photo(self):
        """Test british_columbia_staff_photo"""
        line = "British Columbia Staff Photo"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'British Columbia')  # Should match the state
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['line'], 'Staff Photo')

if __name__ == '__main__':
    unittest.main() 