import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.core.database import Base, get_db
from src.models.link import Link

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


class TestLinkManagement:
    """Test suite for Link Management Service"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_root_endpoint(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Link Management Service" in response.json()["message"]
    
    def test_create_link(self, client):
        """Test creating a new short link"""
        response = client.post(
            "/api/v1/links",
            json={"long_url": "https://www.example.com/test"}
        )
        assert response.status_code == 201
        data = response.json()
        assert "short_code" in data
        assert data["long_url"] == "https://www.example.com/test"
        assert data["is_active"] is True
        assert data["clicks"] == 0
    
    def test_create_link_with_custom_alias(self, client):
        """Test creating a link with custom alias"""
        response = client.post(
            "/api/v1/links",
            json={
                "long_url": "https://www.example.com/custom",
                "custom_alias": "my-custom-link"
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["short_code"] == "my-custom-link"
    
    def test_create_link_duplicate_alias(self, client):
        """Test that duplicate aliases are rejected"""
        # Create first link
        client.post(
            "/api/v1/links",
            json={
                "long_url": "https://www.example.com/first",
                "custom_alias": "duplicate"
            }
        )
        
        # Try to create second link with same alias
        response = client.post(
            "/api/v1/links",
            json={
                "long_url": "https://www.example.com/second",
                "custom_alias": "duplicate"
            }
        )
        assert response.status_code == 400
        assert "zajęty" in response.json()["detail"]
    
    def test_create_link_duplicate_url(self, client):
        """Test that duplicate URLs return the same link"""
        url = "https://www.example.com/same-url"
        
        # Create first link
        response1 = client.post("/api/v1/links", json={"long_url": url})
        data1 = response1.json()
        
        # Create second link with same URL
        response2 = client.post("/api/v1/links", json={"long_url": url})
        data2 = response2.json()
        
        # Should return the same short_code
        assert data1["short_code"] == data2["short_code"]
    
    def test_create_link_invalid_url(self, client):
        """Test that invalid URLs are rejected"""
        response = client.post(
            "/api/v1/links",
            json={"long_url": "not-a-valid-url"}
        )
        assert response.status_code == 400
    
    def test_get_link_by_code(self, client):
        """Test retrieving a link by short code"""
        # Create a link
        create_response = client.post(
            "/api/v1/links",
            json={"long_url": "https://www.example.com/get-test"}
        )
        short_code = create_response.json()["short_code"]
        
        # Retrieve it
        response = client.get(f"/api/v1/links/{short_code}")
        assert response.status_code == 200
        data = response.json()
        assert data["short_code"] == short_code
        assert data["long_url"] == "https://www.example.com/get-test"
    
    def test_get_link_not_found(self, client):
        """Test retrieving a non-existent link"""
        response = client.get("/api/v1/links/nonexistent")
        assert response.status_code == 404
    
    def test_list_links(self, client):
        """Test listing all links with pagination"""
        # Create multiple links
        for i in range(5):
            client.post(
                "/api/v1/links",
                json={"long_url": f"https://www.example.com/link{i}"}
            )
        
        # List links
        response = client.get("/api/v1/links?skip=0&limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 5
    
    def test_update_link(self, client):
        """Test updating a link"""
        # Create a link
        create_response = client.post(
            "/api/v1/links",
            json={"long_url": "https://www.example.com/original"}
        )
        link_id = create_response.json()["id"]
        
        # Update it
        response = client.put(
            f"/api/v1/links/{link_id}",
            json={"long_url": "https://www.example.com/updated"}
        )
        assert response.status_code == 200
        assert response.json()["long_url"] == "https://www.example.com/updated"
    
    def test_delete_link(self, client):
        """Test soft deleting a link"""
        # Create a link
        create_response = client.post(
            "/api/v1/links",
            json={"long_url": "https://www.example.com/delete-test"}
        )
        link_id = create_response.json()["id"]
        
        # Delete it
        response = client.delete(f"/api/v1/links/{link_id}")
        assert response.status_code == 200
        
        # Verify it's inactive
        get_response = client.get(f"/api/v1/links/{link_id}")
        assert get_response.json()["is_active"] is False
    
    def test_url_normalization(self, client):
        """Test that URLs are normalized"""
        response = client.post(
            "/api/v1/links",
            json={"long_url": "  https://www.example.com/test  "}
        )
        assert response.status_code == 201
        assert response.json()["long_url"].strip() == response.json()["long_url"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
