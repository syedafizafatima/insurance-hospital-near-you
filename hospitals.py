from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
import time
import googlemaps
from math import radians, sin, cos, sqrt, atan2
import pandas as pd
import os
from datetime import datetime

class HospitalFinder:

    
    def __init__(self, reference_location, api_key):
        self.reference_location = reference_location
        self.gmaps = googlemaps.Client(key=api_key)
        self.all_hospital_data = []
        
    def setup_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Uncomment for headless mode
        driver = webdriver.Chrome(options=options)
        return driver

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        R = 6371  # Earth's radius in kilometers
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        return R * c

    def get_coordinates(self, location):
        try:
            result = self.gmaps.geocode(location)
            if result:
                location = result[0]['geometry']['location']
                return location['lat'], location['lng']
            return None, None
        except Exception as e:
            print(f"Error geocoding address: {str(e)}")
            return None, None

    def get_all_insurance_companies(self, driver):
        insurance_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_ddinsurance"))
        )
        select = Select(insurance_dropdown)
        return [option.text for option in select.options if option.text != "--Select Insurername--"]

    def process_hospital_data(self, driver, insurance_name):
        try:
            # Select Insurance
            insurance_dropdown = Select(driver.find_element(By.ID, "ContentPlaceHolder1_ddinsurance"))
        
            insurance_dropdown.select_by_visible_text(insurance_name)
            time.sleep(2)
            
            # Select State (Telangana)
            state_dropdown = Select(driver.find_element(By.ID, "ContentPlaceHolder1_ddlState"))
            state_dropdown.select_by_visible_text("Telangana")
            time.sleep(2)
            
            # Select City (Hyderabad)
            city_dropdown = Select(driver.find_element(By.ID, "ContentPlaceHolder1_ddlCity"))
            city_dropdown.select_by_visible_text("Hyderabad")
            time.sleep(2)
            
            # Click Search button
            search_button = driver.find_element(By.ID, "ContentPlaceHolder1_btnGo")
            search_button.click()
            time.sleep(3)
            
            # Process table data
            table = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "ContentPlaceHolder1_grdProviderDetails"))
            )
            
            rows = table.find_elements(By.TAG_NAME, "tr")
            for row in rows[1:]:  # Skip header row
                cols = row.find_elements(By.TAG_NAME, "td")
                if len(cols) >= 4:
                    hospital_data = {
                        'Insurance Company': insurance_name,
                        'Serial No': cols[0].text.strip(),
                        'Hospital Name': cols[1].text.strip(),
                        'Address': cols[2].text.strip(),
                        'Contact': cols[3].text.strip()
                    }
                    
                    # Get coordinates and calculate distance
                    hospital_address = f"{hospital_data['Address']}, Hyderabad, Telangana"
                    hosp_lat, hosp_lon = self.get_coordinates(hospital_address)
                    
                    if hosp_lat and hosp_lon:
                        ref_lat, ref_lon = self.get_coordinates(self.reference_location)
                        if ref_lat and ref_lon:
                            distance = self.calculate_distance(ref_lat, ref_lon, hosp_lat, hosp_lon)
                            hospital_data['Distance_km'] = round(distance, 2)
                            hospital_data['Coordinates'] = f"{hosp_lat}, {hosp_lon}"
                        else:
                            hospital_data['Distance_km'] = float('inf')
                            hospital_data['Coordinates'] = "Not found"
                    else:
                        hospital_data['Distance_km'] = float('inf')
                        hospital_data['Coordinates'] = "Not found"
                    
                    self.all_hospital_data.append(hospital_data)
                    print(f"Processed: {hospital_data['Hospital Name']} - Distance: {hospital_data['Distance_km']} km")
                    
        except Exception as e:
            print(f"Error processing insurance {insurance_name}: {str(e)}")

    def scrape_and_calculate(self):
        driver = self.setup_driver()
        try:
            # Navigate to the page
            driver.get("https://www.fhpl.net/WhatsappNetworkhospitals/")
            
            # # Get list of all insurance companies
            insurance_name = "Magma General Insurance Limited"
            insurance_companies = self.process_hospital_data(driver,insurance_name)
            # print(f"Found {len(insurance_companies)} insurance companies to process")
            
            # Process each insurance company
            for insurance_name in insurance_companies:
                print(f"\nProcessing insurance company: {insurance_name}")
                self.process_hospital_data(driver, insurance_name)
                
        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            driver.quit()
            
        # Convert to DataFrame and sort by distance
        df = pd.DataFrame(self.all_hospital_data)
        df_sorted = df.sort_values('Distance_km')
        
        # Create timestamp for filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'hospitals_by_distance_{timestamp}.csv'
        
        # Save to CSV
        df_sorted.to_csv(filename, index=False)
        print(f"\nData saved to {filename}")
        
        # Print nearest hospitals
        print("\nNearest hospitals to your location:")
        nearest_hospitals = df_sorted[df_sorted['Distance_km'] != float('inf')].head(530)
        for _, hospital in nearest_hospitals.iterrows():
            print(f"\nHospital: {hospital['Hospital Name']}")
            print(f"Distance: {hospital['Distance_km']} km")
            print(f"Address: {hospital['Address']}")
            print(f"Contact: {hospital['Contact']}")
            print(f"Insurance: {hospital['Insurance Company']}")
            
        return df_sorted

def main():
    # Your Plus Code location
    REFERENCE_LOCATION = "8FV5+HPG Hyderabad, Telangana"
    # Your Google Maps API key
    GOOGLE_MAPS_API_KEY = 'Add key'
    
    finder = HospitalFinder(REFERENCE_LOCATION, GOOGLE_MAPS_API_KEY)
    hospitals_df = finder.scrape_and_calculate()
    
    print("\nScript completed successfully!")
    print(f"Total hospitals processed: {len(hospitals_df)}")
    print(f"Hospitals with valid distances: {len(hospitals_df[hospitals_df['Distance_km'] != float('inf')])}")

if __name__ == "__main__":
    main() 

