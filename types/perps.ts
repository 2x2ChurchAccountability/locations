export interface Country {
    name: string;
    recid: string;
  }
  
  export interface Location {
    name: string;
    recid: string;
    country_recid: string;
    country: Country;
  }
  
  export interface PerpLocation {
    recid: string;
    end_date: string | null;
    perp_recid: string;
    start_date: string;
    location_recid: string;
    created_by: string;
    created_date: string;
    changed_by: string;
    changed_date: string;
    location: Location;
  }
  
  export interface Allegation {
    recid: string;
    description: string;
    perp_recid: string;
    created_by: string;
    created_date: string;
    changed_by: string;
    changed_date: string;
  }
  
  export interface PerpNote {
    note: string;
    recid: string;
    perp_recid: string;
    created_by: string;
    created_date: string;
    changed_by: string;
    changed_date: string;
  }
  
  export interface PublicReference {
    description_full: string;
    recid: string;
    perp_recid: string;
    created_by: string;
    created_date: string;
    changed_by: string;
    changed_date: string;
  }
  
  export interface Perp {
    recid: string;
    name: string;
    sex: string;
    birth_date: string;
    death_date: string | null;
    deceased: string;
    position: string;
    created_by: string;
    created_date: string;
    changed_by: string;
    changed_date: string;
    image_link: string;
    perp_location: PerpLocation[];
    allegation: Allegation[];
    perp_note: PerpNote[];
    public_reference: PublicReference[];
  }
  
  export type LocationType = {
    recid: string;
    name: string;
    country: {
      name: string;
    };
  }; 