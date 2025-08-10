# 🏥 Insurance Hospital Finder  

## 📌 Overview  
Insurance Hospital Finder is a **Python-based automation tool** that scrapes hospital data from the FHPL Network Hospitals portal, retrieves their geographical locations using the **Google Maps API**, and calculates distances from a user’s reference location.  
The script outputs a **sorted list of hospitals** (nearest to farthest) along with their **names, addresses, contact details, insurance company**, and **distance in km**.  

---

## 🚀 Features  
- **Automated data scraping** of hospital details using **Selenium**.  
- Fetches **geolocation coordinates** via Google Maps API.  
- Calculates distance from your reference location using the **Haversine formula**.  
- Sorts hospitals from **nearest to farthest**.  
- Outputs results to a **timestamped CSV file** for record keeping.  
- Includes **insurance company details** for each hospital.  
- Prints nearest hospitals for quick reference.  

---

## 📦 Requirements  

Make sure you have the following installed:  

- **Python 3.8+**  
- **Google Maps API Key** (with Geocoding API enabled)  
- **Google Chrome** browser  
- **ChromeDriver** (matching your Chrome version)  

### Install dependencies:
```bash
pip install selenium googlemaps pandas
``` 
## ⚙️ Setup

1️⃣ **Clone the repository**  
git clone https://github.com/syedafizafatima/insurance-hospital-near-you.git  
cd insurance-hospital-finder  

2️⃣ **Add your Google Maps API Key**  
Open main() in the script and replace:  
GOOGLE_MAPS_API_KEY = 'Add key'  
with your actual API key.  

3️⃣ **Set your reference location**  
Replace REFERENCE_LOCATION in the script with your location or Plus Code:  
REFERENCE_LOCATION = "8FV5+HPG Hyderabad, Telangana"  

---

## ▶️ Usage
Run the script:  
python hospital_finder.py  

The script will:  
- Open the FHPL hospitals portal.  
- Select an insurance provider and location.  
- Scrape hospital names, addresses, and contacts.  
- Fetch coordinates from Google Maps API.  
- Calculate distances from your location.  
- Save results to a CSV file.  

---

## 📂 Output
CSV File → hospitals_by_distance_YYYYMMDD_HHMMSS.csv containing:  
- Insurance Company  
- Hospital Name  
- Address  
- Contact  
- Coordinates  
- Distance (km)  
