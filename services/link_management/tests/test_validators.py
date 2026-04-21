import pytest
from src.services.url_validator import URLValidator


class TestURLValidator:
    """Test suite for URL validation"""
    
    def test_valid_http_url(self):
        """Test valid HTTP URL"""
        is_valid, error = URLValidator.validate_url("http://example.com")
        assert is_valid is True
        assert error == ""
    
    def test_valid_https_url(self):
        """Test valid HTTPS URL"""
        is_valid, error = URLValidator.validate_url("https://example.com/path")
        assert is_valid is True
    
    def test_url_with_query_params(self):
        """Test URL with query parameters"""
        is_valid, error = URLValidator.validate_url("https://example.com?param=value")
        assert is_valid is True
    
    def test_invalid_url_too_short(self):
        """Test URL that's too short"""
        is_valid, error = URLValidator.validate_url("http://a")
        assert is_valid is False
        assert "krótki" in error.lower()
    
    def test_invalid_url_too_long(self):
        """Test URL that's too long"""
        long_url = "https://example.com/" + "a" * 3000
        is_valid, error = URLValidator.validate_url(long_url)
        assert is_valid is False
        assert "długi" in error.lower()
    
    def test_invalid_url_format(self):
        """Test malformed URL"""
        is_valid, error = URLValidator.validate_url("not-a-url")
        assert is_valid is False
    
    def test_invalid_scheme(self):
        """Test URL with invalid scheme"""
        is_valid, error = URLValidator.validate_url("ftp://example.com")
        assert is_valid is False
        assert "schemat" in error.lower()
    
    def test_blacklisted_domain(self):
        """Test blacklisted domain"""
        is_valid, error = URLValidator.validate_url("https://malware.com/test")
        assert is_valid is False
        assert "zablokowana" in error.lower()
    
    def test_normalize_url_adds_https(self):
        """Test URL normalization adds HTTPS"""
        normalized = URLValidator.normalize_url("example.com")
        assert normalized.startswith("https://")
    
    def test_normalize_url_strips_whitespace(self):
        """Test URL normalization strips whitespace"""
        normalized = URLValidator.normalize_url("  https://example.com  ")
        assert normalized == "https://example.com"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
