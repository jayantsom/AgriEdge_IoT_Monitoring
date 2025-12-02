# services/plant_api_service.py
import requests
import json
import time
from config import TREFLE_API_KEY, PLANTBOOK_API_KEY, PLANTBOOK_CLIENT_ID, PLANTBOOK_CLIENT_SECRET, TREFLE_BASE_URL, PLANTBOOK_BASE_URL

class PlantAPIService:
    def __init__(self):
        self.trefle_token = TREFLE_API_KEY
        self.plantbook_token = None
        self.authenticate_plantbook()
    
    def authenticate_plantbook(self):
        """Authenticate with PlantBook API and get access token"""
        try:
            auth_url = f"{PLANTBOOK_BASE_URL}/token/"
            payload = {
                'grant_type': 'client_credentials',
                'client_id': PLANTBOOK_CLIENT_ID,
                'client_secret': PLANTBOOK_CLIENT_SECRET
            }
            
            response = requests.post(auth_url, data=payload)
            if response.status_code == 200:
                data = response.json()
                self.plantbook_token = data.get('access_token')
                return True
            else:
                print(f"PlantBook auth failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"PlantBook auth error: {str(e)}")
            return False
    
    def search_trefle_by_common_name(self, common_name):
        """Search Trefle API by common plant name"""
        try:
            url = f"{TREFLE_BASE_URL}/plants/search"
            headers = {"Authorization": f"Bearer {self.trefle_token}"}
            params = {"q": common_name.lower(), "limit": 1}
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                plants = data.get('data', [])
                if plants:
                    return plants[0]
            return None
        except Exception as e:
            print(f"Trefle search error: {str(e)}")
            return None
    
    def get_trefle_plant_details(self, plant_id):
        """Get detailed information about a specific plant from Trefle"""
        try:
            url = f"{TREFLE_BASE_URL}/plants/{plant_id}"
            headers = {"Authorization": f"Bearer {self.trefle_token}"}
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                return data.get('data', {})
            return {}
        except Exception as e:
            print(f"Trefle details error: {str(e)}")
            return {}
    
    def get_plantbook_details_by_scientific_name(self, scientific_name):
        """Get plant details from PlantBook using scientific name"""
        if not self.plantbook_token:
            if not self.authenticate_plantbook():
                return {}
        
        try:
            # First search to get PID
            search_url = f"{PLANTBOOK_BASE_URL}/plant/search"
            headers = {
                "Authorization": f"Bearer {self.plantbook_token}",
                "Content-Type": "application/json"
            }
            
            # Use first word of scientific name for search
            first_word = scientific_name.lower().split()[0] if scientific_name else ""
            params = {"alias": first_word, "limit": 1}
            
            response = requests.get(search_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    pid = data['results'][0].get('pid')
                    
                    # Get detailed information
                    detail_url = f"{PLANTBOOK_BASE_URL}/plant/detail/{pid}"
                    detail_response = requests.get(detail_url, headers=headers)
                    
                    if detail_response.status_code == 200:
                        return detail_response.json()
            return {}
        except Exception as e:
            print(f"PlantBook details error: {str(e)}")
            return {}
    
    def get_plant_information(self, common_name):
        """Get comprehensive plant information from both APIs"""
        # Step 1: Get Trefle information
        trefle_plant = self.search_trefle_by_common_name(common_name)
        
        trefle_details = {}
        plantbook_details = {}
        
        if trefle_plant:
            plant_id = trefle_plant.get('id')
            scientific_name = trefle_plant.get('scientific_name')
            
            # Get detailed Trefle info
            trefle_details = self.get_trefle_plant_details(plant_id)
            
            # Get PlantBook info using scientific name
            if scientific_name:
                plantbook_details = self.get_plantbook_details_by_scientific_name(scientific_name)
        
        return {
            'common_name': common_name,
            'trefle': trefle_details,
            'plantbook': plantbook_details
        }
    
    def extract_plant_info_for_display(self, common_name):
        """Extract and format plant information for display"""
        plant_data = self.get_plant_information(common_name)
        
        trefle_data = plant_data.get('trefle', {})
        plantbook_data = plant_data.get('plantbook', {})
        
        # Extract main species data from Trefle
        main_species = trefle_data.get('main_species', {}) if isinstance(trefle_data.get('main_species'), dict) else {}
        
        # Get PlantBook PID
        plantbook_pid = plantbook_data.get('pid', '')
        
        # Prepare display data
        display_data = {
            'common_name': common_name,
            'scientific_name': trefle_data.get('scientific_name', 'Unknown'),
            'trefle_id': trefle_data.get('id', ''),
            'trefle_url': f"https://trefle.io/plants/{trefle_data.get('id', '')}" if trefle_data.get('id') else None,
            'plantbook_pid': plantbook_pid,
            # FIX: Correct PlantBook URL format
            'plantbook_url': f"https://open.plantbook.io/plant/{plantbook_pid.replace(' ', '%20')}" if plantbook_pid else None,
            
            # Basic information
            'family': trefle_data.get('family', {}).get('common_name', ''),
            'genus': trefle_data.get('genus', {}).get('name', ''),
            'observations': trefle_data.get('observations', ''),
            
            # PlantBook environmental data
            'light_mmol': {
                'min': plantbook_data.get('min_light_mmol'),
                'max': plantbook_data.get('max_light_mmol')
            },
            'light_lux': {
                'min': plantbook_data.get('min_light_lux'),
                'max': plantbook_data.get('max_light_lux')
            },
            'temperature': {
                'min': plantbook_data.get('min_temp'),
                'max': plantbook_data.get('max_temp')
            },
            'humidity': {
                'min': plantbook_data.get('min_env_humid'),
                'max': plantbook_data.get('max_env_humid')
            },
            'soil_moisture': {
                'min': plantbook_data.get('min_soil_moist'),
                'max': plantbook_data.get('max_soil_moist')
            },
            'soil_ec': {
                'min': plantbook_data.get('min_soil_ec'),
                'max': plantbook_data.get('max_soil_ec')
            },
            
            # Additional Trefle data
            'vegetable': trefle_data.get('vegetable', False),
            'year': trefle_data.get('year', ''),
            'author': trefle_data.get('author', ''),
            'image_url': trefle_data.get('image_url', ''),
            
            # Main species data
            'duration': main_species.get('duration'),
            'edible': main_species.get('edible'),
            'edible_part': main_species.get('edible_part'),
            'flower': main_species.get('flower', {}),
            'foliage': main_species.get('foliage', {}),
            'growth': main_species.get('growth', {}),
            'specifications': main_species.get('specifications', {})
        }
        
        return display_data


# Singleton instance
plant_api_service = PlantAPIService()