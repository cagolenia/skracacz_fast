"""
Test Data Loader for URL Shortener
Creates sample links for testing and demonstration
"""
import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict

# Service URLs
LINK_MANAGEMENT_URL = "http://localhost:8001"

# Sample URLs to shorten
SAMPLE_URLS = [
    "https://www.github.com",
    "https://www.stackoverflow.com",
    "https://www.python.org",
    "https://www.fastapi.tiangolo.com",
    "https://www.docker.com",
    "https://www.postgresql.org",
    "https://www.redis.io",
    "https://www.rabbitmq.com",
    "https://www.youtube.com",
    "https://www.wikipedia.org",
    "https://www.google.com/search?q=python+fastapi",
    "https://www.linkedin.com",
    "https://www.twitter.com",
    "https://www.medium.com",
    "https://www.dev.to",
]

# Custom aliases for some links
CUSTOM_LINKS = [
    {"long_url": "https://www.github.com/explore", "custom_alias": "gh-explore"},
    {"long_url": "https://docs.python.org/3/", "custom_alias": "py-docs"},
    {"long_url": "https://fastapi.tiangolo.com/tutorial/", "custom_alias": "fastapi-tut"},
]

# Links with expiration
EXPIRING_LINKS = [
    {
        "long_url": "https://www.example.com/promo",
        "custom_alias": "promo-7days",
        "expires_at": (datetime.now() + timedelta(days=7)).isoformat()
    },
    {
        "long_url": "https://www.example.com/event",
        "custom_alias": "event-30days",
        "expires_at": (datetime.now() + timedelta(days=30)).isoformat()
    },
]


def check_service():
    """Check if link management service is available"""
    try:
        response = requests.get(f"{LINK_MANAGEMENT_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Link Management Service is running")
            return True
        else:
            print("✗ Service returned non-200 status")
            return False
    except requests.exceptions.RequestException as e:
        print(f"✗ Cannot connect to service: {e}")
        print("\n⚠️  Please start the Link Management service:")
        print("   cd services/link_management")
        print("   uvicorn src.main:app --reload --port 8001")
        return False


def create_link(link_data: Dict) -> Dict:
    """Create a short link"""
    try:
        response = requests.post(
            f"{LINK_MANAGEMENT_URL}/api/v1/links",
            json=link_data,
            timeout=5
        )
        
        if response.status_code == 201:
            data = response.json()
            return {
                "success": True,
                "short_code": data["short_code"],
                "long_url": data["long_url"],
                "short_url": data.get("short_url", "")
            }
        else:
            return {
                "success": False,
                "error": response.json().get("detail", "Unknown error")
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


def load_test_data():
    """Load all test data"""
    
    print("\n" + "="*60)
    print("🔗 URL SHORTENER - TEST DATA LOADER")
    print("="*60 + "\n")
    
    # Check service
    if not check_service():
        return
    
    print("\n📝 Loading test data...\n")
    
    results = {
        "created": 0,
        "failed": 0,
        "links": []
    }
    
    # Load regular URLs
    print("1️⃣  Creating regular short links...")
    for i, url in enumerate(SAMPLE_URLS, 1):
        result = create_link({"long_url": url})
        if result["success"]:
            results["created"] += 1
            results["links"].append(result)
            print(f"   [{i}/{len(SAMPLE_URLS)}] ✓ {result['short_code']} -> {url[:50]}...")
        else:
            results["failed"] += 1
            print(f"   [{i}/{len(SAMPLE_URLS)}] ✗ Failed: {result['error']}")
    
    # Load custom alias links
    print(f"\n2️⃣  Creating links with custom aliases...")
    for i, link_data in enumerate(CUSTOM_LINKS, 1):
        result = create_link(link_data)
        if result["success"]:
            results["created"] += 1
            results["links"].append(result)
            print(f"   [{i}/{len(CUSTOM_LINKS)}] ✓ {result['short_code']} (custom)")
        else:
            results["failed"] += 1
            print(f"   [{i}/{len(CUSTOM_LINKS)}] ✗ Failed: {result['error']}")
    
    # Load expiring links
    print(f"\n3️⃣  Creating links with expiration dates...")
    for i, link_data in enumerate(EXPIRING_LINKS, 1):
        result = create_link(link_data)
        if result["success"]:
            results["created"] += 1
            results["links"].append(result)
            print(f"   [{i}/{len(EXPIRING_LINKS)}] ✓ {result['short_code']} (expires)")
        else:
            results["failed"] += 1
            print(f"   [{i}/{len(EXPIRING_LINKS)}] ✗ Failed: {result['error']}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 SUMMARY")
    print("="*60)
    print(f"✓ Successfully created: {results['created']} links")
    print(f"✗ Failed: {results['failed']} links")
    print(f"📈 Total: {results['created'] + results['failed']} attempts")
    
    # Display some examples
    if results["links"]:
        print(f"\n🔗 Example Short Links:")
        for link in results["links"][:5]:
            print(f"   • {link['short_url']}")
        
        if len(results["links"]) > 5:
            print(f"   ... and {len(results['links']) - 5} more")
    
    # Save to file
    output_file = "test_data_links.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Results saved to: {output_file}")
    
    # Testing instructions
    print("\n" + "="*60)
    print("🧪 NEXT STEPS")
    print("="*60)
    print("\n1. Test redirection:")
    print(f"   curl -L http://localhost:8002/<short_code>")
    print("\n2. View all links:")
    print(f"   curl http://localhost:8001/api/v1/links")
    print("\n3. Check analytics (after visiting links):")
    print(f"   curl http://localhost:8003/stats/<short_code>")
    print("\n4. View interactive docs:")
    print(f"   http://localhost:8001/docs (Link Management)")
    print(f"   http://localhost:8003/docs (Analytics)")
    print()


if __name__ == "__main__":
    load_test_data()
