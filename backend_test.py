import requests
import os
import sys
from PIL import Image
import io
import base64
from datetime import datetime

class SightMateAPITester:
    def __init__(self, base_url="https://351bf4ae-45c1-45a7-b799-de9e18a7126b.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_images = {
            'objects': '/app/tests/test_objects.jpg',
            'text': '/app/tests/test_text.jpg',
            'currency': '/app/tests/test_currency.jpg',
            'colors': '/app/tests/test_colors.jpg'
        }
        
        # Create test images if they don't exist
        self.ensure_test_images()

    def ensure_test_images(self):
        """Create test images directory and sample images if they don't exist"""
        os.makedirs('/app/tests', exist_ok=True)
        
        # Create a simple test image with text if it doesn't exist
        if not os.path.exists(self.test_images['text']):
            img = Image.new('RGB', (400, 200), color=(73, 109, 137))
            from PIL import ImageDraw, ImageFont
            d = ImageDraw.Draw(img)
            d.text((10,10), "Hello World\nSightMate Test", fill=(255,255,0))
            img.save(self.test_images['text'])
            
            # Use the same image for other tests for simplicity
            for key in self.test_images:
                if key != 'text' and not os.path.exists(self.test_images[key]):
                    img.save(self.test_images[key])
    
    def run_test(self, name, endpoint, image_path, expected_status=200):
        """Run a single API test with image upload"""
        url = f"{self.base_url}{endpoint}"
        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        
        try:
            with open(image_path, 'rb') as img_file:
                files = {'file': ('image.jpg', img_file, 'image/jpeg')}
                response = requests.post(url, files=files)
            
            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                print(f"Response: {response.json()}")
                return True, response.json()
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_api_root(self):
        """Test the API root endpoint"""
        url = f"{self.base_url}/api"
        self.tests_run += 1
        print(f"\n🔍 Testing API Root...")
        
        try:
            response = requests.get(url)
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                return True
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False

    def test_object_detection(self):
        """Test object detection endpoint"""
        return self.run_test(
            "Object Detection",
            "/api/vision/objects",
            self.test_images['objects']
        )

    def test_text_reading(self):
        """Test text reading endpoint"""
        return self.run_test(
            "Text Reading",
            "/api/vision/text",
            self.test_images['text']
        )

    def test_currency_detection(self):
        """Test currency detection endpoint"""
        return self.run_test(
            "Currency Detection",
            "/api/vision/currency",
            self.test_images['currency']
        )

    def test_color_detection(self):
        """Test color detection endpoint"""
        return self.run_test(
            "Color Detection",
            "/api/vision/colors",
            self.test_images['colors']
        )

    def test_history_endpoint(self):
        """Test history endpoint"""
        url = f"{self.base_url}/api/history"
        self.tests_run += 1
        print(f"\n🔍 Testing History Endpoint...")
        
        try:
            response = requests.get(url)
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                print(f"Response: {response.json()}")
                return True, response.json()
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_emergency_sos(self):
        """Test emergency SOS endpoint"""
        url = f"{self.base_url}/api/emergency/sos"
        self.tests_run += 1
        print(f"\n🔍 Testing Emergency SOS Endpoint...")
        
        try:
            data = {
                "name": "Test User",
                "location": "Test Location",
                "message": "This is a test emergency message"
            }
            response = requests.post(url, json=data)
            success = response.status_code == 200
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                print(f"Response: {response.json()}")
                return True, response.json()
            else:
                print(f"❌ Failed - Expected 200, got {response.status_code}")
                return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

def main():
    # Setup
    tester = SightMateAPITester()
    
    # Run tests
    tester.test_api_root()
    tester.test_object_detection()
    tester.test_text_reading()
    tester.test_currency_detection()
    tester.test_color_detection()
    tester.test_history_endpoint()
    tester.test_emergency_sos()

    # Print results
    print(f"\n📊 Tests passed: {tester.tests_passed}/{tester.tests_run}")
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())