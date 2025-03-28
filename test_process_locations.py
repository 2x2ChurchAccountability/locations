import unittest
import process_locations

process_locations.validate_mode = True

from process_locations import handle_started_work, handle_workers_meeting, handle_special_meeting, handle_photo, handle_workers_list, handle_location_only, handle_convention, get_state_country
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
        self.assertEqual(result['location'], 'Edgewood')
        self.assertEqual(result['line'], 'Convention')

    # Wisconsin Dells Wisconsin Convention (Pennsylvania)
    def test_wisconsin_dells_wisconsin_convention(self):
        """Test wisconsin_dells_wisconsin_convention"""
        line = "Wisconsin Dells Wisconsin Convention (Pennsylvania)"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], 'Wisconsin')  # Should match the state
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], 'Dells')
        self.assertEqual(result['line'], 'Convention (Pennsylvania)')

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
        self.assertEqual(result['location'], 'Duncan')
        self.assertEqual(result['line'], 'Convention Preps')

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

    # Bangalore Convention
    def test_bangalore_convention(self):
        """Test bangalore_convention"""
        line = "Bangalore Convention"
        result = get_state_country(line, self.countries)
        self.assertEqual(result['state'], '')
        self.assertEqual(result['country'], 'India')
        self.assertEqual(result['location'], 'Bangalore')
        self.assertEqual(result['line'], 'Convention')




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

    #New York *Started in the work*
    def test_new_york_started_in_the_work2(self):
        """Test new_york_started_in_the_work2"""
        line = "New York *Started in the work* York"
        result = handle_started_work(line, self.countries)
        self.assertEqual(result['state'], 'New York')  # Should match the state
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], '')
        self.assertEqual(result['note'], 'Started in the work: York')

    #New York *Started in the work*
    def test_new_york_started_in_the_work3(self):
        """Test new_york_started_in_the_work3"""
        line = "New York *Started in the work* Mountain Ranch 1"
        result = handle_started_work(line, self.countries)
        self.assertEqual(result['state'], 'New York')  # Should match the state
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], '')
        self.assertEqual(result['note'], 'Started in the work: Mountain Ranch 1')

    #New York *Started in the work*
    def test_new_york_started_in_the_work4(self):
        """Test new_york_started_in_the_work4"""
        line = "New York *Started in the work* Freedom"
        result = handle_started_work(line, self.countries)
        self.assertEqual(result['state'], 'New York')  # Should match the state
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], 'Freedom')
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
        self.assertEqual(result['location'], 'Fermanagh')
        self.assertEqual(result['note'], 'Summer Special Meetings') 

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





    # Jul-Dec Alberta Workers List (West Africa)
    def test_jul_dec_alberta_workers_list_west_africa(self):
        """Test jul_dec_alberta_workers_list_west_africa"""
        line = "Jul-Dec Alberta Workers List (West Africa)"
        result = handle_workers_list(line, self.countries)
        self.assertEqual(result['state'], 'Alberta')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Workers List: Jul-Dec List, West Africa')

    # Nova Scotia Workers List
    def test_nova_scotia_workers_list(self):
        # Test case 1: Check if the workers list is valid
        line = 'Nova Scotia Workers List'
        result = handle_workers_list(line, self.countries)
        self.assertEqual(result['state'], 'Nova Scotia')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Workers List')

    # July Alberta Canada Workers List (West Africa)
    def test_july_alberta_canada_workers_list_west_africa(self):
        """Test july_alberta_canada_workers_list_west_africa"""
        line = "July Alberta Canada Workers List (West Africa)"
        result = handle_workers_list(line, self.countries)
        self.assertEqual(result['state'], 'Alberta')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Workers List: July List, West Africa')

    # British Columbia Canada Workers List (Chilliwack)
    def test_british_columbia_canada_workers_list_chilliwack(self):
        """Test british_columbia_canada_workers_list_chilliwack"""
        line = "British Columbia Canada Workers List (Chilliwack)"
        result = handle_workers_list(line, self.countries)
        self.assertEqual(result['state'], 'British Columbia')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Workers List: Chilliwack')

    # British Columbia Canada Workers List (Kelowna) *Autumn*
    def test_british_columbia_canada_workers_list_kelowna(self):
        """Test british_columbia_canada_workers_list_kelowna"""
        line = "British Columbia Canada Workers List (Kelowna) *Autumn*"
        result = handle_workers_list(line, self.countries)
        self.assertEqual(result['state'], 'British Columbia')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Workers List: Kelowna, Autumn')

    # Saskatchewan/Manitoba/NW Ontario Canada Workers List (Winnipeg East, Interlake MB) *Jul-Dec*
    def test_saskatchewan_manitoba_nw_ontario_canada_workers_list_winnipeg_east_interlake_mb(self):
        """Test saskatchewan_manitoba_nw_ontario_canada_workers_list_winnipeg_east_interlake_mb"""
        line = "Saskatchewan/Manitoba/NW Ontario Canada Workers List (Winnipeg East, Interlake MB) *Jul-Dec*"
        result = handle_workers_list(line, self.countries)
        self.assertEqual(result['state'], 'Saskatchewan/Manitoba/Northwest Ontario')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Workers List: Winnipeg East, Interlake MB, Jul-Dec')

    # British Columbia Canada Workers List (N. Okanagan and Chase) *Winter/Spring*
    def test_british_columbia_canada_workers_list_n_okanagan_and_chase(self):
        """Test british_columbia_canada_workers_list_n_okanagan_and_chase"""
        line = "British Columbia Canada Workers List (N. Okanagan and Chase) *Winter/Spring*"
        result = handle_workers_list(line, self.countries)
        self.assertEqual(result['state'], 'British Columbia')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Workers List: N. Okanagan and Chase, Winter/Spring')

    # Colorado/Utah Workers List (Southwest) overseer
    def test_colorado_utah_workers_list_southwest_overseer(self):
        """Test colorado_utah_workers_list_southwest_overseer"""
        line = "Colorado/Utah Workers List (Southwest) overseer"
        result = handle_workers_list(line, self.countries)
        self.assertEqual(result['state'], 'Colorado/Utah')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Workers List: Southwest, overseer')

    # Jan-Jul SK Workers List (Yorkton/Fort Qu’Appelle) with Merlin Affleck
    def test_jan_jul_sk_workers_list_yorkton_fort_quappelle_with_merlin_affleck(self):
        """Test jan_jul_sk_workers_list_yorkton_fort_quappelle_with_merlin_affleck"""
        line = "Jan-Jul SK Workers List (Yorkton/Fort Qu’Appelle) with Merlin Affleck"
        result = handle_workers_list(line, self.countries)
        self.assertEqual(result['state'], 'Saskatchewan')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Workers List: Jan-Jul List, Yorkton/Fort Qu’Appelle, With Merlin Affleck')

    # Jul-Dec Alberta Workers List (Camrose/Stettler) w/Jack Reddekopp *First year in the work*
    def test_jul_dec_alberta_workers_list_camrose_stettler_with_jack_reddekopp_first_year_in_the_work(self):
        """Test jul_dec_alberta_workers_list_camrose_stettler_with_jack_reddekopp_first_year_in_the_work"""
        line = "Jul-Dec Alberta Workers List (Camrose/Stettler) w/Jack Reddekopp *First year in the work*"
        result = handle_workers_list(line, self.countries)
        self.assertEqual(result['state'], 'Alberta')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Workers List: Jul-Dec List, Camrose/Stettler, With Jack Reddekopp, First year in the work')







    # Jan Changing Fields
    def test_jan_changing_fields(self):
        """Test jan_changing_fields"""
        line = "Jan Changing Fields"
        result = handle_location_only(line, self.countries)
        self.assertEqual(result['state'], None)
        self.assertEqual(result['country'], None)
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Jan Changing Fields')

    # Olmos Peru Preps
    def test_olmos_peru_preps(self):
        """Test olmos_peru_preps"""
        line = "Olmos Peru Preps"
        result = handle_location_only(line, self.countries)
        self.assertEqual(result['state'], 'Lambayeque')
        self.assertEqual(result['country'], 'Peru')
        self.assertEqual(result['location'], 'Olmos')
        self.assertEqual(result['note'], 'Preps')

    # Autumn (Alberta Pro Tem)
    def test_autumn_alberta_pro_tem(self):
        """Test autumn_alberta_pro_tem"""
        line = "Autumn (Alberta Pro Tem)"
        result = handle_location_only(line, self.countries)
        self.assertEqual(result['state'], 'Alberta')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Autumn (Pro Tem)')

    # Ontario/Quebec (Guelph)
    def test_ontario_quebec_guelph(self):
        """Test ontario_quebec_guelph"""
        line = "Ontario/Quebec (Guelph)"
        result = handle_location_only(line, self.countries)
        self.assertEqual(result['state'], 'Ontario/Quebec')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], '(Guelph)')

    # Glen Valley 2 British Columbia Staff Photo (Absent)
    def test_glen_valley_2_british_columbia_staff_photo(self):
        """Test glen_valley_2_british_columbia_staff_photo"""
        line = "Glen Valley 2 British Columbia Staff Photo (Absent)"
        result = handle_location_only(line, self.countries)
        self.assertEqual(result['state'], 'British Columbia')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], 'Glen Valley 2')
        self.assertEqual(result['note'], 'Staff Photo (Absent)')

    # December to 2022 New Year Vacation in Smyrna Beach Florida
    def test_december_to_2022_new_year_vacation_in_smyrna_beach_florida(self):
        """Test december_to_2022_new_year_vacation_in_smyrna_beach_florida"""
        line = "December to 2022 New Year Vacation in Smyrna Beach Florida"
        result = handle_location_only(line, self.countries)
        self.assertEqual(result['state'], 'Florida')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'December to 2022 New Year Vacation in Smyrna Beach')

    # Pennsylvania (Erie/Falls Creek/Pittsburgh/Altoona)
    def test_pennsylvania_erie_falls_creek_pittsburgh_altoona(self):
        """Test pennsylvania_erie_falls_creek_pittsburgh_altoona"""
        line = "Pennsylvania (Erie/Falls Creek/Pittsburgh/Altoona)"
        result = handle_location_only(line, self.countries)
        self.assertEqual(result['state'], 'Pennsylvania')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], '(Erie/Falls Creek/Pittsburgh/Altoona)')

    # Visited South Africa
    def test_visited_south_africa(self):
        """Test visited_south_africa"""
        line = "Visited South Africa"
        result = handle_location_only(line, self.countries)
        self.assertEqual(result['state'], None)
        self.assertEqual(result['country'], 'South Africa')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], "Visited")

    # Quebec/Atlantic (Halifax NS) w/Albert Clark
    def test_quebec_atlantic_halifax_ns_w_albert_clark(self):
        """Test quebec_atlantic_halifax_ns_w_albert_clark"""
        line = "Quebec/Atlantic (Halifax NS) w/Albert Clark"
        result = handle_location_only(line, self.countries)
        self.assertEqual(result['state'], 'Quebec/Atlantic')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], '(Halifax NS) With Albert Clark')

    # La Paz, Ecuador
    def test_la_paz_ecuador(self):
        """Test la_paz_ecuador"""
        line = "La Paz, Ecuador"
        result = handle_location_only(line, self.countries)
        self.assertEqual(result['state'], 'La Paz')
        self.assertEqual(result['country'], 'Bolivia')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Ecuador')

    #was in New Zealand and walked the Routeburn Track (January)
    def test_was_in_new_zealand_and_walked_the_routeburn_track_january(self):
        """Test was_in_new_zealand_and_walked_the_routeburn_track_january"""
        line = "was in New Zealand and walked the Routeburn Track (January)"
        result = handle_location_only(line, self.countries)
        self.assertEqual(result['state'], None)
        self.assertEqual(result['country'], 'New Zealand')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'was in and walked the Routeburn Track (January)')








    # Apopka Florida Convention (West Africa)
    def test_apopka_florida_convention_west_africa(self):
        """Test apopka_florida_convention_west_africa"""
        line = "Apopka Florida Convention (West Africa)"
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], 'Florida')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], 'Apopka')
        self.assertEqual(result['note'], 'Convention. Visiting from West Africa')

    # Olympia 2 Washington Convention (Aug 14-17) (Europe)
    def test_olympia_2_washington_convention_aug_14_17_europe(self):
        """Test olympia_2_washington_convention_aug_14_17_europe"""
        line = "Olympia 2 Washington Convention (Aug 14-17) (Europe)"
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], 'Washington')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], 'Olympia 2')
        self.assertEqual(result['note'], 'Convention - Aug 14-17. Visiting from Europe')

    # Bangalore India Convention
    def test_bangalore_india_convention(self):
        """Test bangalore_india_convention"""
        line = "Bangalore India Convention"
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], None)
        self.assertEqual(result['country'], 'India')
        self.assertEqual(result['location'], 'Bangalore')
        self.assertEqual(result['note'], 'Convention')

    # Prince George Canada Convention Preps
    def test_prince_george_canada_convention_preps(self):
        """Test prince_george_canada_convention_preps"""
        line = "Prince George Canada Convention Preps"
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], 'British Columbia')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], 'Prince George')
        self.assertEqual(result['note'], 'Convention Preps')

    # Ales, France Convention (Aug 12)
    def test_ales_france_convention_aug_12(self):
        """Test ales_france_convention_aug_12"""
        line = "Ales, France Convention (Aug 12)"
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], None)
        self.assertEqual(result['country'], 'France')
        self.assertEqual(result['location'], None)
        self.assertEqual(result['note'], 'Ales Convention - Aug 12')

    # Salmon Arm Convention (Sk- Ukraine)
    def test_salmon_arm_convention_sk_ukraine(self):
        """Test salmon_arm_convention_sk_ukraine"""
        line = "Salmon Arm Convention (Sk- Ukraine)"
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], 'Saskatchewan')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], 'Salmon Arm')
        self.assertEqual(result['note'], 'Convention. Visiting from Ukraine')

    # Juneau Alaska Convention May 28-31
    def test_juneau_alaska_convention_may_28_31(self):
        """Test juneau_alaska_convention_may_28_31"""
        line = "Juneau Alaska Convention May 28-31"
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], 'Alaska')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], 'Juneau')
        self.assertEqual(result['note'], 'Convention May 28-31')

    # Tokyo Japan Convention
    def test_tokyo_japan_convention(self):
        """Test tokyo_japan_convention"""
        line = "Tokyo Japan Convention"
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], None)
        self.assertEqual(result['country'], 'Japan')
        self.assertEqual(result['location'], 'Tokyo')
        self.assertEqual(result['note'], 'Convention')

    # Manhattan 2 Montana Convention June 29-July2
    def test_manhattan_2_montana_convention_june_29_july_2(self):
        """Test manhattan_2_montana_convention_june_29_july_2"""
        line = "Manhattan 2 Montana Convention June 29-July2"
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], 'Montana')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], 'Manhattan 2')
        self.assertEqual(result['note'], 'Convention June 29-July2')

    # Didsbury #2 Canada Convention (Montana Visiting Worker)
    def test_didsbury_2_canada_convention_montana_visiting_worker(self):
        """Test didsbury_2_canada_convention_montana_visiting_worker"""
        line = "Didsbury #2 Canada Convention (Montana Visiting Worker)"
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], 'Alberta')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], 'Didsbury #2')
        self.assertEqual(result['note'], 'Convention. Visiting from Montana')

    # Alma Michigan Convention (CO)
    def test_alma_michigan_convention_co(self):
        """Test alma_michigan_convention_co"""
        line = "Alma Michigan Convention (CO)"
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], 'Michigan')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], 'Alma')
        self.assertEqual(result['note'], 'Convention. Visiting from Colorado')

    # Theodore Canada Convention (TX)
    def test_theodore_canada_convention_tx(self):
        """Test theodore_canada_convention_tx"""
        line = "Theodore Canada Convention (TX)"
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], 'Saskatchewan')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], 'Theodore')
        self.assertEqual(result['note'], 'Convention. Visiting from Texas')

    # Newry Pennsylvania Convention (NY/VT/NH)
    def test_newry_pennsylvania_convention_ny_vt_nh(self):
        """Test newry_pennsylvania_convention_ny_vt_nh"""
        line = "Newry Pennsylvania Convention (NY/VT/NH)"
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], 'Pennsylvania')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], 'Newry')
        self.assertEqual(result['note'], 'Convention. Visiting from NY/VT/NH')

    # Portage Convention (Manitoba Canada)
    def test_portage_convention_manitoba_canada(self):
        """Test portage_convention_manitoba_canada"""
        line = "Portage Convention (Manitoba Canada)"
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], 'Manitoba')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], 'Portage')
        self.assertEqual(result['note'], 'Convention. Visiting from Manitoba Canada')

    # Mountain Ranch 1 California Convention (sent back to S. Africa from this convention)
    def test_mountain_ranch_1_california_convention_sent_back_to_s_africa(self):
        """Test mountain_ranch_1_california_convention_sent_back_to_s_africa"""
        line = "Mountain Ranch 1 California Convention (sent back to S. Africa from this convention)"
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], 'California')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], 'Mountain Ranch 1')
        self.assertEqual(result['note'], 'Convention. Visiting from South Africa. Sent back to S. Africa from this convention')

    def test_prince_george_canada_convention_preps(self):
        """Test prince_george_canada_convention_preps"""
        line = "Prince George Canada Convention Preps"
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], 'British Columbia')
        self.assertEqual(result['country'], 'Canada')
        self.assertEqual(result['location'], 'Prince George')
        self.assertEqual(result['note'], 'Convention Preps')

    # Post Falls, Idaho Convention Jun 9-12
    def test_post_falls_idaho_convention_jun_9_12(self):
        """Test post_falls_idaho_convention_jun_9_12"""
        line = "Post Falls, Idaho Convention Jun 9-12"
        line = process_locations.text_fixes(line)
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], 'Idaho')
        self.assertEqual(result['country'], 'United States')
        self.assertEqual(result['location'], 'Post Falls')
        self.assertEqual(result['note'], 'Convention Jun 9-12')

    # Insurgents Convention
    def test_insurgents_mexico_convention(self):
        """Test insurgents_mexico_convention"""
        line = "Insurgents Mexico Convention"
        line = process_locations.text_fixes(line)
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], None)
        self.assertEqual(result['country'], 'Mexico')
        self.assertEqual(result['location'], 'Insurgentes')
        self.assertEqual(result['note'], 'Convention')

    # Ilocos Convention
    def test_ilocos_convention(self):
        """Test ilocos_convention"""
        line = "Ilocos Convention"
        line = process_locations.text_fixes(line)
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], None)
        self.assertEqual(result['country'], 'Philippines')
        self.assertEqual(result['location'], 'Ilocos')
        self.assertEqual(result['note'], 'Convention')

    # Dunbarton 1 UK Convention
    def test_dunbarton_1_uk_convention(self):
        """Test dunbarton_1_uk_convention"""
        line = "Dunbarton 1 UK Convention"
        line = process_locations.text_fixes(line)
        result = handle_convention(line, self.countries)
        self.assertEqual(result['state'], None)
        self.assertEqual(result['country'], 'United Kingdom')
        self.assertEqual(result['location'], 'Dunbarton 1')
        self.assertEqual(result['note'], 'Convention')







if __name__ == '__main__':
    unittest.main() 