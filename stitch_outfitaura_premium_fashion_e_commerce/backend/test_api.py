import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
from fastapi.testclient import TestClient

from backend.app.main import app

class TestOutfitAuraAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client_ctx = TestClient(app)
        cls.client = cls.client_ctx.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client_ctx.__exit__(None, None, None)

    def test_01_health_check(self):
        res = self.client.get("/api/health")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["status"], "online")
        self.assertIn("database", data)
        print("✓ Health Check Passed:", data["database"]["mode"])

    def test_02_api_root(self):
        res = self.client.get("/api")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("endpoints", data)
        print("✓ API Overview Passed:", list(data["endpoints"].keys()))

    def test_03_list_products(self):
        res = self.client.get("/api/products")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertGreater(data["total"], 0)
        self.assertGreaterEqual(len(data["products"]), 1)
        print(f"✓ Products List Passed: {data['total']} products found")

    def test_04_get_product_detail(self):
        res = self.client.get("/api/products/silk-slip-dress")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["slug"], "silk-slip-dress")
        self.assertEqual(data["name"], "Silk Slip Dress")
        self.assertGreater(len(data["colors"]), 0)
        self.assertGreater(len(data["sizes"]), 0)
        print("✓ Product Detail by Slug Passed:", data["name"], f"${data['price']}")

    def test_05_featured_and_categories(self):
        res_feat = self.client.get("/api/products/featured")
        self.assertEqual(res_feat.status_code, 200)
        feat_data = res_feat.json()
        self.assertGreaterEqual(len(feat_data), 1)

        res_cat = self.client.get("/api/products/categories")
        self.assertEqual(res_cat.status_code, 200)
        cat_data = res_cat.json()
        self.assertIn("Women", cat_data["categories"])
        print("✓ Featured & Categories Passed:", cat_data["categories"])

    def test_06_auth_flow(self):
        # Register new user
        reg_payload = {
            "email": "test_fashionista@outfitaura.com",
            "password": "securepassword123",
            "full_name": "Test Fashionista"
        }
        res_reg = self.client.post("/api/auth/register", json=reg_payload)
        self.assertIn(res_reg.status_code, [201, 400])
        
        # Login
        login_payload = {
            "email": "test_fashionista@outfitaura.com",
            "password": "securepassword123"
        }
        res_login = self.client.post("/api/auth/login", json=login_payload)
        self.assertEqual(res_login.status_code, 200)
        auth_data = res_login.json()
        self.assertIn("access_token", auth_data)
        token = auth_data["access_token"]
        print("✓ Registration & Login JWT Token Received")

        # Test /api/auth/me
        headers = {"Authorization": f"Bearer {token}"}
        res_me = self.client.get("/api/auth/me", headers=headers)
        self.assertEqual(res_me.status_code, 200)
        self.assertEqual(res_me.json()["email"], "test_fashionista@outfitaura.com")
        print("✓ Auth /me Profile Verified:", res_me.json()["full_name"])

    def test_07_cart_flow(self):
        headers = {"X-Session-ID": "test_session_123"}
        
        # Add item
        add_payload = {
            "product_id": "prod_silk_slip_01",
            "size": "S",
            "color": "Blush Pink",
            "quantity": 2
        }
        res_add = self.client.post("/api/cart/items", json=add_payload, headers=headers)
        self.assertEqual(res_add.status_code, 200)
        cart_data = res_add.json()
        self.assertEqual(cart_data["total_items"], 2)
        self.assertEqual(cart_data["subtotal"], 370.0)
        item_id = cart_data["items"][0]["id"]
        print(f"✓ Cart Add Passed: subtotal=${cart_data['subtotal']}, items={cart_data['total_items']}")

        # Update quantity
        res_upd = self.client.put(f"/api/cart/items/{item_id}", json={"quantity": 1}, headers=headers)
        self.assertEqual(res_upd.status_code, 200)
        self.assertEqual(res_upd.json()["total_items"], 1)
        print("✓ Cart Quantity Update Passed")

        # Remove item
        res_del = self.client.delete(f"/api/cart/items/{item_id}", headers=headers)
        self.assertEqual(res_del.status_code, 200)
        self.assertEqual(res_del.json()["total_items"], 0)
        print("✓ Cart Remove Passed")

    def test_08_newsletter(self):
        res = self.client.post("/api/newsletter/subscribe", json={"email": "client@example.com"})
        self.assertIn(res.status_code, [200, 201])
        data = res.json()
        self.assertIn("discount_code", data)
        print("✓ Newsletter Subscription Passed:", data["discount_code"])


if __name__ == "__main__":
    unittest.main()
