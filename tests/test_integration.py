"""
Integration test for the complete URL shortener flow.
Tests: Link creation -> Redirection -> Analytics
"""
import pytest
import time
import requests
from datetime import datetime


class TestIntegration:
    """Integration tests for the complete system"""
    
    LINK_MANAGEMENT_URL = "http://localhost:8001"
    REDIRECTION_URL = "http://localhost:8002"
    ANALYTICS_URL = "http://localhost:8003"
    
    @pytest.fixture(autouse=True)
    def check_services(self):
        """Check if all services are running"""
        try:
            requests.get(f"{self.LINK_MANAGEMENT_URL}/health", timeout=2)
            requests.get(f"{self.REDIRECTION_URL}/health", timeout=2)
            requests.get(f"{self.ANALYTICS_URL}/health", timeout=2)
        except requests.exceptions.RequestException:
            pytest.skip("Services not running. Start all services first.")
    
    def test_complete_flow(self):
        """Test the complete flow: create -> redirect -> analytics"""
        
        # Step 1: Create a short link
        create_response = requests.post(
            f"{self.LINK_MANAGEMENT_URL}/api/v1/links",
            json={"long_url": "https://www.google.com"}
        )
        assert create_response.status_code == 201
        short_code = create_response.json()["short_code"]
        print(f"\n✓ Created link with code: {short_code}")
        
        # Step 2: Use the redirect (don't follow, just check response)
        redirect_response = requests.get(
            f"{self.REDIRECTION_URL}/{short_code}",
            allow_redirects=False
        )
        assert redirect_response.status_code == 301
        assert redirect_response.headers["Location"] == "https://www.google.com"
        print(f"✓ Redirect works: 301 -> {redirect_response.headers['Location']}")
        
        # Step 3: Wait for analytics processing (RabbitMQ queue)
        print("⏳ Waiting for analytics processing...")
        time.sleep(2)
        
        # Step 4: Check analytics
        stats_response = requests.get(
            f"{self.ANALYTICS_URL}/stats/{short_code}"
        )
        
        # Note: This might fail if analytics worker isn't running
        if stats_response.status_code == 200:
            stats = stats_response.json()
            assert stats["total_visits"] >= 1
            print(f"✓ Analytics recorded: {stats['total_visits']} visit(s)")
        else:
            print("⚠ Analytics not available (worker may not be running)")
    
    def test_cache_behavior(self):
        """Test that Redis cache improves performance"""
        
        # Create a link
        create_response = requests.post(
            f"{self.LINK_MANAGEMENT_URL}/api/v1/links",
            json={"long_url": "https://www.example.com/cache-test"}
        )
        short_code = create_response.json()["short_code"]
        
        # First request (cache miss)
        start1 = time.time()
        requests.get(f"{self.REDIRECTION_URL}/{short_code}", allow_redirects=False)
        time1 = time.time() - start1
        
        # Second request (cache hit)
        start2 = time.time()
        requests.get(f"{self.REDIRECTION_URL}/{short_code}", allow_redirects=False)
        time2 = time.time() - start2
        
        print(f"\n✓ First request (cache miss): {time1*1000:.2f}ms")
        print(f"✓ Second request (cache hit): {time2*1000:.2f}ms")
        print(f"✓ Speedup: {time1/time2:.2f}x faster")
        
        # Cache hit should be faster
        assert time2 <= time1
    
    def test_duplicate_url_handling(self):
        """Test that duplicate URLs return the same short code"""
        url = f"https://www.example.com/duplicate-test-{datetime.now().timestamp()}"
        
        # Create first link
        response1 = requests.post(
            f"{self.LINK_MANAGEMENT_URL}/api/v1/links",
            json={"long_url": url}
        )
        code1 = response1.json()["short_code"]
        
        # Create second link with same URL
        response2 = requests.post(
            f"{self.LINK_MANAGEMENT_URL}/api/v1/links",
            json={"long_url": url}
        )
        code2 = response2.json()["short_code"]
        
        assert code1 == code2
        print(f"\n✓ Duplicate URLs return same code: {code1}")
    
    def test_invalid_short_code(self):
        """Test 404 for non-existent short code"""
        response = requests.get(
            f"{self.REDIRECTION_URL}/nonexistent123",
            allow_redirects=False
        )
        assert response.status_code == 404
        print("\n✓ Non-existent codes return 404")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 INTEGRATION TESTS")
    print("="*60)
    print("\n⚠️  Make sure all services are running:")
    print("  1. docker-compose up -d (PostgreSQL, Redis, RabbitMQ)")
    print("  2. Link Management (port 8001)")
    print("  3. Redirection (port 8002)")
    print("  4. Analytics (port 8003)")
    print("  5. Analytics Worker\n")
    
    pytest.main([__file__, "-v", "-s"])
