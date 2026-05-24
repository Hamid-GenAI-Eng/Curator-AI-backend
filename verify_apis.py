import httpx
import uuid
import sys
import time

BASE_URL = "http://127.0.0.1:8000"

from PIL import Image
import io

# Generate a small valid 200x200 JPEG image dynamically to satisfy OpenCV processing
img = Image.new('RGB', (200, 200), color=(240, 240, 240))
img_byte_arr = io.BytesIO()
img.save(img_byte_arr, format='JPEG')
DUMMY_PNG = img_byte_arr.getvalue()

def log_test(step_name, success, info=""):
    status = "PASS" if success else "FAIL"
    print(f"[{status}] {step_name}")
    if info:
        print(f"   Info: {info}")
    print("-" * 50)

async def run_verification():
    print("=" * 60)
    print("      AI NOTE ASSISTANT - API VERIFICATION SUITE")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: Verify Root Endpoint
        try:
            r = await client.get(f"{BASE_URL}/")
            if r.status_code == 200:
                log_test("GET / (Root API Availability)", True, r.json().get("message"))
            else:
                log_test("GET / (Root API Availability)", False, f"HTTP {r.status_code}")
        except Exception as e:
            log_test("GET / (Root API Availability)", False, str(e))
            print("ERROR: Cannot connect to backend server. Make sure it is running on http://127.0.0.1:8000")
            sys.exit(1)

        # Generate unique credentials for signup
        unique_id = str(uuid.uuid4())[:8]
        test_email = f"testuser_{unique_id}@example.com"
        test_password = "SuperSecretPassword123!"
        test_name = f"Test User {unique_id}"

        # Step 2: Signup Endpoint
        user_id = None
        try:
            signup_data = {
                "email": test_email,
                "password": test_password,
                "full_name": test_name
            }
            r = await client.post(f"{BASE_URL}/auth/signup", json=signup_data)
            if r.status_code == 201:
                res_data = r.json()
                user_id = res_data.get("id")
                log_test("POST /auth/signup (User Registration)", True, f"Registered: {test_email} (ID: {user_id})")
            else:
                log_test("POST /auth/signup (User Registration)", False, f"HTTP {r.status_code}: {r.text}")
                sys.exit(1)
        except Exception as e:
            log_test("POST /auth/signup (User Registration)", False, str(e))
            sys.exit(1)

        # Step 3: Login Endpoint
        token = None
        try:
            login_data = {
                "email": test_email,
                "password": test_password
            }
            r = await client.post(f"{BASE_URL}/auth/login", json=login_data) # uses json payload
            if r.status_code == 200:
                res_data = r.json()
                token = res_data.get("access_token")
                log_test("POST /auth/login (User Authentication)", True, f"Token received successfully")
            else:
                log_test("POST /auth/login (User Authentication)", False, f"HTTP {r.status_code}: {r.text}")
                sys.exit(1)
        except Exception as e:
            log_test("POST /auth/login (User Authentication)", False, str(e))
            sys.exit(1)

        # Setup authorized headers
        headers = {"Authorization": f"Bearer {token}"}

        # Step 4: Note Processing Upload Endpoint
        note_id = None
        batch_id = None
        try:
            print(">>> Uploading dummy note image for processing (OCR + LLM)...")
            files = {"file": ("test.png", DUMMY_PNG, "image/png")}
            r = await client.post(f"{BASE_URL}/notes/process", files=files, headers=headers)
            if r.status_code == 201:
                note = r.json()
                note_id = note.get("id")
                batch_id = note.get("batch_id")
                log_test("POST /notes/process (Upload & AI Process)", True, f"Created Note ID: {note_id} linked to Batch ID: {batch_id}")
            else:
                log_test("POST /notes/process (Upload & AI Process)", False, f"HTTP {r.status_code}: {r.text}")
        except Exception as e:
            log_test("POST /notes/process (Upload & AI Process)", False, str(e))

        # Step 5: List Batches Endpoint
        try:
            r = await client.get(f"{BASE_URL}/notes/batches", headers=headers)
            if r.status_code == 200:
                batches = r.json()
                log_test("GET /notes/batches (List Project Batches)", True, f"Retrieved {len(batches)} batches successfully")
            else:
                log_test("GET /notes/batches (List Project Batches)", False, f"HTTP {r.status_code}: {r.text}")
        except Exception as e:
            log_test("GET /notes/batches (List Project Batches)", False, str(e))

        # Step 6: Get Batch Detail Endpoint
        if batch_id:
            try:
                r = await client.get(f"{BASE_URL}/notes/batches/{batch_id}", headers=headers)
                if r.status_code == 200:
                    batch_detail = r.json()
                    log_test(f"GET /notes/batches/{{id}} (Hydrated Batch Detail)", True, f"Batch Name: {batch_detail.get('name')} | Notes count: {len(batch_detail.get('notes', []))}")
                else:
                    log_test(f"GET /notes/batches/{{id}} (Hydrated Batch Detail)", False, f"HTTP {r.status_code}: {r.text}")
            except Exception as e:
                log_test(f"GET /notes/batches/{{id}} (Hydrated Batch Detail)", False, str(e))

        # Step 7: Get Note History Endpoint
        try:
            r = await client.get(f"{BASE_URL}/notes/", headers=headers)
            if r.status_code == 200:
                notes_history = r.json()
                log_test("GET /notes/ (Notes History)", True, f"Retrieved {len(notes_history)} note entries successfully")
            else:
                log_test("GET /notes/ (Notes History)", False, f"HTTP {r.status_code}: {r.text}")
        except Exception as e:
            log_test("GET /notes/ (Notes History)", False, str(e))

        # Step 8: Update Note Endpoint
        if note_id:
            try:
                update_data = {"title": "Updated Batch Entry Title"}
                r = await client.patch(f"{BASE_URL}/notes/{note_id}", json=update_data, headers=headers)
                if r.status_code == 200:
                    updated_note = r.json()
                    log_test("PATCH /notes/{id} (Update Note Metadata)", True, f"New Title: {updated_note.get('title')}")
                else:
                    log_test("PATCH /notes/{id} (Update Note Metadata)", False, f"HTTP {r.status_code}: {r.text}")
            except Exception as e:
                log_test("PATCH /notes/{id} (Update Note Metadata)", False, str(e))

    print("=" * 60)
    print("            ALL TESTS EXECUTION COMPLETED")
    print("=" * 60)

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_verification())
