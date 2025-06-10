"""
Enhanced Integration test with detailed logging
"""

import asyncio
import httpx
import json
from datetime import datetime

class VocabularyAppTester:
    def __init__(self, base_url="http://localhost:5000", auth_token=None ):
        self.base_url = base_url
        self.auth_token = auth_token
        self.headers = {"Authorization": f"Bearer {auth_token}"} if auth_token else {}
        
        print(f"🔧 Tester initialized:")
        print(f"   Base URL: {self.base_url}")
        print(f"   Auth token: {'***' + auth_token[-10:] if auth_token and len(auth_token) > 10 else 'None'}")
        print(f"   Headers: {self.headers}")
    
    async def test_complete_flow(self):
        """Test the complete vocabulary learning flow with detailed logging"""
        
        print("🧪 Starting Integration Test - Complete Learning Flow")
        print("=" * 60)
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            
            # Step 0: Test authentication first
            print("\n🔐 Step 0: Testing authentication...")
            
            try:
                auth_test_response = await client.get(
                    f"{self.base_url}/api/auth/user",
                    headers=self.headers
                )
                
                print(f"   Auth test status: {auth_test_response.status_code}")
                print(f"   Auth test headers sent: {self.headers}")
                
                if auth_test_response.status_code == 200:
                    user_data = auth_test_response.json()
                    print(f"✅ Authentication successful!")
                    print(f"   User ID: {user_data.get('id', 'Unknown')}")
                    print(f"   Email: {user_data.get('email', 'Unknown')}")
                else:
                    print(f"❌ Authentication failed!")
                    print(f"   Response: {auth_test_response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ Auth test exception: {str(e)}")
                return False
            
            # Step 1: Add a test word
            print("\n📝 Step 1: Adding a test word...")
            
            word_data = {
                "word": "integration",
                "user_notes": "A pleasant surprise - integration test word",
                "source": "integration_test"
            }
            
            print(f"   Request URL: {self.base_url}/api/words/")
            print(f"   Request headers: {self.headers}")
            print(f"   Request data: {json.dumps(word_data, indent=2)}")
            
            try:
                add_response = await client.post(
                    f"{self.base_url}/api/words/",
                    json=word_data,
                    headers=self.headers
                )
                
                print(f"   Response status: {add_response.status_code}")
                print(f"   Response headers: {dict(add_response.headers)}")
                
                if add_response.status_code == 200:
                    word_result = add_response.json()
                    print(f"   Response body: {json.dumps(word_result, indent=2)}")
                    
                    if word_result.get("success") and word_result.get("data"):
                        word_id = word_result["data"]["id"]
                        print(f"✅ Word added successfully: {word_result['data']['word']}")
                        print(f"   Word ID: {word_id}")
                        print(f"   Definitions: {len(word_result['data']['definitions'])}")
                    else:
                        print(f"❌ Word addition failed - unexpected response structure")
                        print(f"   Expected 'success' and 'data' fields")
                        return False
                else:
                    print(f"❌ Failed to add word: {add_response.status_code}")
                    print(f"   Response body: {add_response.text}")
                    
                    # Try to parse error details
                    try:
                        error_data = add_response.json()
                        print(f"   Error details: {json.dumps(error_data, indent=2)}")
                    except:
                        print(f"   Raw error text: {add_response.text}")
                    
                    return False
                    
            except httpx.TimeoutException:
                print(f"❌ Request timed out" )
                return False
            except httpx.ConnectError:
                print(f"❌ Connection error - is your server running?" )
                return False
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
                print(f"   Error type: {type(e).__name__}")
                return False
            
            # Step 2: Test server connectivity
            print("\n🌐 Step 2: Testing server connectivity...")
            
            try:
                health_response = await client.get(f"{self.base_url}/")
                print(f"   Server health status: {health_response.status_code}")
                print(f"   Server response: {health_response.text}")
            except Exception as e:
                print(f"   Server connectivity issue: {str(e)}")
            
            # Step 3: List available endpoints
            print("\n📋 Step 3: Testing available endpoints...")
            
            try:
                # Test if words endpoint exists
                words_test = await client.get(
                    f"{self.base_url}/api/words/",
                    headers=self.headers
                )
                print(f"   GET /api/words status: {words_test.status_code}")
                
                if words_test.status_code == 200:
                    words_data = words_test.json()
                    print(f"   Current words count: {len(words_data.get('words', []))}")
                else:
                    print(f"   GET words error: {words_test.text}")
                    
            except Exception as e:
                print(f"   Endpoint test error: {str(e)}")
            
            print("\n" + "=" * 60)
            print("🔍 Detailed debugging complete!")
            return True

# Enhanced runner with more debugging
async def run_integration_test():
    """Run the integration test with enhanced debugging"""
    
    print("🚀 Starting Enhanced Integration Test")
    print("=" * 60)
    
    # Check if server is running
    print("🔍 Pre-flight checks:")
    
    try:
        async with httpx.AsyncClient(timeout=5.0 ) as client:
            server_response = await client.get("http://localhost:5000/" )
            print(f"✅ Server is running (status: {server_response.status_code})")
    except Exception as e:
        print(f"❌ Server not reachable: {str(e)}")
        print("   Make sure your FastAPI server is running:")
        print("   uvicorn src.main:app --reload --port 5000")
        return
    
    # Get auth token
    auth_token = input("\n🔑 Enter your auth token (from login): ").strip()
    
    if not auth_token or auth_token == "YOUR_AUTH_TOKEN_HERE":
        print("\n❌ No auth token provided!")
        print("   To get a token:")
        print("   1. Use Postman or curl to login:")
        print("      POST http://localhost:5000/api/auth/login" )
        print("      Body: {\"email\":\"your-email\",\"password\":\"your-password\"}")
        print("   2. Copy the 'access_token' from the response")
        print("   3. Paste it when prompted")
        return
    
    print(f"✅ Auth token provided (length: {len(auth_token)})")
    
    tester = VocabularyAppTester(auth_token=auth_token)
    success = await tester.test_complete_flow()
    
    if success:
        print("\n🚀 Integration test completed!")
    else:
        print("\n⚠️ Integration test failed - check logs above")

if __name__ == "__main__":
    asyncio.run(run_integration_test())
