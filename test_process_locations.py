import unittest
from process_locations import handle_started_work, handle_workers_meeting, handle_special_meeting, handle_photo, get_state_country
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
        self.assertEqual(result['line'], 'Salt Lake Workers Meeting')

    def test_simple_quebec_atlantic_canada(self):
        """Test quebec_atlantic_canada"""
        line = "Quebec/Atlantic Canada Workers List"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'Quebec/Atlantic')  # Should match the state
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['line'], 'Workers List')

    def test_simple_quebec_atlantic(self):
        """Test quebec_atlantic"""
        line = "Quebec/Atlantic Staff"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'Quebec/Atlantic')  # Should match the state
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['line'], 'Staff')

    def test_complex_paupa_new_guinea2(self):
        """Test paupa_new_guinea2"""
        line = "Australia/Papua New Guinea Workers List (Tasmania)"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'Tasmania')  # Should match the state
        self.assertEqual(result['country'], 'Australia/Papua New Guinea')
        self.assertEqual(result['line'], 'Workers List')

    # Kootenays, Brisco BC Canada Special Meeting
    def test_kootenays_brisco_bc_canada_special_meeting(self):
        """Test kootenays_brisco_bc_canada_special_meeting"""
        line = "Kootenays, Brisco BC Canada Special Meeting"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'British Columbia')  # Should match the state
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['line'], 'Kootenays, Brisco Special Meeting')

    # Edgewood New Mexico Convention
    def test_edgewood_new_mexico_convention(self):
        """Test edgewood_new_mexico_convention"""
        line = "Edgewood New Mexico Convention"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'New Mexico')  # Should match the state
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['line'], 'Edgewood Convention')

    # Wisconsin Dells Wisconsin Convention (Pennsylvania)
    def test_wisconsin_dells_wisconsin_convention(self):
        """Test wisconsin_dells_wisconsin_convention"""
        line = "Wisconsin Dells Wisconsin Convention (Pennsylvania)"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'Wisconsin')  # Should match the state
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['line'], 'Dells Convention (Pennsylvania)')

    # Prince George Canada Convention
    def test_prince_george_canada_convention(self):
        """Test prince_george_canada_convention"""
        line = "Prince George Canada Convention"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'British Columbia')  # Should match the state
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], 'Prince George')
        self.assertEqual(result['line'], 'Convention')

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
        self.assertEqual(result['location'], 'Knoxville')

    # British Columbia Staff Photo
    def test_british_columbia_staff_photo(self):
        """Test british_columbia_staff_photo"""
        line = "British Columbia Staff Photo"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'British Columbia')  # Should match the state
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['line'], 'Staff Photo')

    def test_newfoundland_irishtown_state_country(self):
        """Test basic state and country extraction"""
        line = 'Newfoundland Irishtown Special Meeting'
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'Newfoundland and Labrador')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], 'Irishtown')
        self.assertEqual(result['line'], 'Special Meeting')

    def test_glen_valley_state_country(self):
        """Test Glen Valley British Columbia Staff Photo"""
        line = "Glen Valley British Columbia Staff Photo"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'British Columbia')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], 'Glen Valley')
        self.assertEqual(result['line'], 'Staff Photo')

    def test_glen_valley_2_state_country(self):
        """Test Glen Valley 2 British Columbia Staff Photo"""
        line = "Glen Valley 2 British Columbia Staff Photo"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'British Columbia')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], 'Glen Valley 2')
        self.assertEqual(result['line'], 'Staff Photo')

    # San Rafael Special Meeting Argentina
    def test_san_rafel_state_country(self):
        """Test test_san_rafel_state_country"""
        line = "San Rafael Special Meeting Argentina"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], '')  # Should match the state
        self.assertEqual(result['country'], 'Argentina')
        self.assertEqual(result['location'], 'San Rafael')
        self.assertEqual(result['line'], 'Special Meeting')



    # New Brunswick (Started in the work)
    def test_new_brunswick_started_in_the_work(self):
        """Test new_brunswick_started_in_the_work"""
        line = "New Brunswick (Started in the work)"
        result = handle_started_work(line, self.countries)
        self.assertEqual(result['state'], 'New Brunswick')  # Should match the state
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], '')
        self.assertEqual(result['note'], 'Started in the work')

    # Oct Started in the work
    def test_oct_started_in_the_work(self):
        """Test oct_started_in_the_work"""
        line = "Oct Started in the work"
        result = handle_started_work(line, self.countries)
        self.assertEqual(result['state'], '')  # Should match the state
        self.assertEqual(result['country'], '')
        self.assertEqual(result['location'], '')
        self.assertEqual(result['note'], 'Started in the work')

    #New York *Started in the work*
    def test_new_york_started_in_the_work(self):
        """Test new_york_started_in_the_work"""
        line = "New York *Started in the work*"
        result = handle_started_work(line, self.countries)
        self.assertEqual(result['state'], 'New York')  # Should match the state
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], '')
        self.assertEqual(result['note'], 'Started in the work')

    # July 6, Started in the work
    def test_july_6_started_in_the_work(self):
        """Test july_6_started_in_the_work"""
        line = "July 6, Started in the work"
        result = handle_started_work(line, self.countries)
        self.assertEqual(result['state'], '')  # Should match the state
        self.assertEqual(result['country'], '')
        self.assertEqual(result['location'], '')
        self.assertEqual(result['note'], 'Started in the work')

    # Knoxsville Tennessee Workers Meeting
    def test_knoxsville_tennessee_workers_meeting(self):
        """Test knoxsville_tennessee_workers_meeting"""
        line = "Knoxsville Tennessee Workers Meeting"
        result = handle_workers_meeting(line, self.countries)
        self.assertEqual(result['state'], 'Tennessee')  # Should match the state
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Knoxsville Workers Meeting')

    # Portage Canada Workers Meeting
    def test_portage_canada_workers_meeting(self):
        """Test portage_canada_workers_meeting"""
        line = "Portage Canada Workers Meeting"
        result = handle_workers_meeting(line, self.countries)
        self.assertEqual(result['state'], 'Manitoba')  # Should match the state
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], 'Portage')
        self.assertEqual(result['note'], 'Workers Meeting')

    # Nashville Tennessee Workers Meeting (Colorado)
    def test_nashville_tennessee_workers_meeting(self):
        """Test nashville_tennessee_workers_meeting"""
        line = "Nashville Tennessee Workers Meeting (Colorado)"
        result = handle_workers_meeting(line, self.countries)
        self.assertEqual(result['state'], 'Tennessee')  # Should match the state
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Nashville Workers Meeting Visiting from Colorado')

    # Minnesota Workers Meeting (MO)
    def test_minnesota_workers_meeting(self):
        """Test minnesota_workers_meeting"""
        line = "Minnesota Workers Meeting (MO)"
        result = handle_workers_meeting(line, self.countries)
        self.assertEqual(result['state'], 'Minnesota')  # Should match the state
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Workers Meeting Visiting from Missouri')

    # Kenai Alaska Special Meeting
    def test_kenai_alaska_special_meeting(self):
        """Test kenai_alaska_special_meeting"""
        line = "Kenai Alaska Special Meeting"
        result = handle_special_meeting(line, self.countries)
        self.assertEqual(result['state'], 'Alaska')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], None) 
        self.assertEqual(result['note'], 'Kenai Special Meeting')

    # South Dakota Special Meeting (Winter)
    def test_south_dakota_special_meeting_winter(self):
        """Test south_dakota_special_meeting_winter"""
        line = "South Dakota Special Meeting (Winter)"
        result = handle_special_meeting(line, self.countries)
        self.assertEqual(result['state'], 'South Dakota')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], None) 
        self.assertEqual(result['note'], 'Winter Special Meeting')

    # Quebec/Atlantic Canada Special Meetings (Pennsylvania)
    def test_quebec_atlantic_canada_special_meetings(self):
        """Test quebec_atlantic_canada_special_meetings"""
        line = "Quebec/Atlantic Canada Special Meetings (Pennsylvania)"
        result = handle_special_meeting(line, self.countries)
        self.assertEqual(result['state'], 'Quebec/Atlantic')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], None) 
        self.assertEqual(result['note'], 'Special Meetings Visiting from Pennsylvania')

    # San Rafael Special Meeting Argentina (July 14)
    def test_san_rafael_special_meeting_argentina(self):
        """Test san_rafael_special_meeting_argentina"""
        line = "San Rafael Special Meeting Argentina (July 14)"
        result = handle_special_meeting(line, self.countries)
        self.assertEqual(result['state'], None)
        self.assertEqual(result['country'], 'Argentina')
        self.assertEqual(result['location'], 'San Rafael')
        self.assertEqual(result['note'], 'July 14 Special Meeting')

    # Fermanagh Ireland Summer Special Meetings
    def test_fermanagh_ireland_summer_special_meetings(self):
        """Test fermanagh_ireland_summer_special_meetings"""
        line = "Fermanagh Ireland Summer Special Meetings"
        result = handle_special_meeting(line, self.countries)
        self.assertEqual(result['state'], None)
        self.assertEqual(result['country'], 'Ireland')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Fermanagh Summer Special Meetings') 

    # Philippines Special Meeting Rounds
    def test_philippines_special_meeting_rounds(self):
        """Test philippines_special_meeting_rounds"""
        line = "Philippines Special Meeting Rounds"
        result = handle_special_meeting(line, self.countries)
        self.assertEqual(result['state'], None)
        self.assertEqual(result['country'], 'Philippines')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Special Meeting Rounds')

    # Special Meeting Gilbert Arizona
    def test_special_meeting_gilbert_arizona(self):
        """Test special_meeting_gilbert_arizona"""
        line = "Special Meeting Gilbert Arizona"
        result = handle_special_meeting(line, self.countries)
        self.assertEqual(result['state'], 'Arizona')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], 'Gilbert')
        self.assertEqual(result['note'], 'Special Meeting')
        
    # QC/Atlantic Canada Special Meeting
    def test_qc_atlantic_canada_special_meeting(self):
        """Test qc_atlantic_canada_special_meeting"""
        line = "QC/Atlantic Canada Special Meeting"
        result = handle_special_meeting(line, self.countries)
        self.assertEqual(result['state'], 'Quebec/Atlantic')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Special Meeting')

    # Oregon/ S. Idaho Special Meetings
    def test_oregon_s_idaho_special_meetings(self):
        """Test oregon_s_idaho_special_meetings"""
        line = "Oregon/ S. Idaho Special Meetings"
        result = handle_special_meeting(line, self.countries)
        self.assertEqual(result['state'], 'Oregon/Southern Idaho')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Special Meetings')

    # Anchorage Alaska Special Meeting
    def test_anchorage_alaska_special_meeting(self):
        """Test anchorage_alaska_special_meeting"""
        line = "Anchorage Alaska Special Meeting"
        result = handle_special_meeting(line, self.countries)
        self.assertEqual(result['state'], 'Alaska')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], 'Anchorage')
        self.assertEqual(result['note'], 'Special Meeting')

    # Clover Special Meeting
    def test_clover_special_meeting(self):
        """Test clover_special_meeting"""
        line = "Clover Special Meeting"
        result = handle_special_meeting(line, self.countries)
        self.assertEqual(result['state'], 'South Carolina')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], 'Clover')
        self.assertEqual(result['note'], 'Special Meeting')

    # Newfoundland (Irishtown) Special Meeting
    def test_newfoundland_irishtown_special_meeting(self):
        """Test newfoundland_irishtown_special_meeting"""
        line = "Newfoundland (Irishtown) Special Meeting"
        result = handle_special_meeting(line, self.countries)
        self.assertEqual(result['state'], 'Newfoundland and Labrador')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], 'Irishtown')
        self.assertEqual(result['note'], 'Special Meeting')

    # Doak’s Special Meeting Shed United Kingdom
    def test_doaks_special_meeting_shed_united_kingdom(self):
        """Test Doak’s Special Meeting Shed United Kingdom"""
        line = "Doak’s Special Meeting Shed United Kingdom"
        result = handle_special_meeting(line, self.countries)
        self.assertEqual(result['state'], None)
        self.assertEqual(result['country'], 'United Kingdom')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], "Doak's Special Meeting Shed")





    # Manitoba/NW Ontario Staff Photo
    def test_manitoba_nw_ontario_staff_photo(self):
        """Test Manitoba/NW Ontario Staff Photo"""
        line = "Manitoba/NW Ontario Staff Photo"
        result = handle_photo(line, self.countries)
        self.assertEqual(result['state'], 'Manitoba/Northwest Ontario')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['note'], 'Staff Photo')

    # Alma Michigan Workers Picture
    def test_alma_michigan_workers_picture(self):
        """Test Alma Michigan Workers Picture"""
        line = "Alma Michigan Workers Picture"
        result = handle_photo(line, self.countries)
        self.assertEqual(result['state'], 'Michigan')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], 'Alma')
        self.assertEqual(result['note'], 'Workers Picture')

    # California Workers Picture
    def test_california_workers_picture(self):
        """Test California Workers Picture"""
        line = "California Workers Picture"
        result = handle_photo(line, self.countries)
        self.assertEqual(result['state'], 'California')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['note'], 'Workers Picture')

    # Glen Valley 2 British Columbia Canada Staff Photo
    def test_glen_valley_2_british_columbia_canada_staff_photo(self):
        """Test Glen Valley 2 British Columbia Canada Staff Photo"""
        line = "Glen Valley 2 British Columbia Canada Staff Photo"
        result = handle_photo(line, self.countries)
        self.assertEqual(result['state'], 'British Columbia')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], 'Glen Valley 2')
        self.assertEqual(result['note'], 'Staff Photo')

    # Glen Valley British Columbia Staff Photo
    def test_glen_valley_british_columbia_staff_photo(self):
        """Test Glen Valley British Columbia Staff Photo"""
        line = "Glen Valley British Columbia Staff Photo"
        result = handle_photo(line, self.countries)
        self.assertEqual(result['state'], 'British Columbia')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], 'Glen Valley')
        self.assertEqual(result['note'], 'Staff Photo')

if __name__ == '__main__':
    unittest.main() 