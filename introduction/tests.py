from django.test import TestCase, Client
from django.contrib.auth.models import User
import re


class XSSLab2FilterTestCase(TestCase):
    """Test suite for XSS Lab 2 case-insensitive script tag filter"""
    
    def setUp(self):
        """Create test user and client"""
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')
    
    def apply_filter(self, username):
        """Apply the same filter logic as in views.py"""
        username = username.strip()
        username = re.sub(r'<script\b[^>]*>.*?</script>', '', username, flags=re.IGNORECASE | re.DOTALL)
        return username
    
    def test_lowercase_script_tags(self):
        """Test filtering of lowercase script tags"""
        result = self.apply_filter("<script>alert('XSS')</script>")
        self.assertEqual(result, "")
    
    def test_uppercase_script_tags(self):
        """Test filtering of uppercase script tags"""
        result = self.apply_filter("<SCRIPT>alert('XSS')</SCRIPT>")
        self.assertEqual(result, "")
    
    def test_mixed_case_script_tags(self):
        """Test filtering of mixed case script tags"""
        result = self.apply_filter("<ScRiPt>alert('XSS')</ScRiPt>")
        self.assertEqual(result, "")
    
    def test_script_tags_with_attributes(self):
        """Test filtering of script tags with attributes"""
        result = self.apply_filter("<script src='evil.js'></script>")
        self.assertEqual(result, "")
        
        result = self.apply_filter("<SCRIPT SRC='evil.js'></SCRIPT>")
        self.assertEqual(result, "")
    
    def test_script_in_middle_of_text(self):
        """Test filtering script tags embedded in text"""
        result = self.apply_filter("Hello <script>bad()</script> World")
        self.assertEqual(result, "Hello  World")
    
    def test_multiple_script_tags(self):
        """Test filtering multiple script tags in one input"""
        result = self.apply_filter("<script>alert(1)</script>text<SCRIPT>alert(2)</SCRIPT>")
        self.assertEqual(result, "text")
    
    def test_script_tags_with_newlines(self):
        """Test filtering script tags with newlines between opening and closing"""
        result = self.apply_filter("<script>\nalert('XSS')\n</script>")
        self.assertEqual(result, "")
    
    def test_script_tags_without_closing(self):
        """Test incomplete script tags (should not match - requires closing tag)"""
        result = self.apply_filter("<script>alert('XSS')")
        self.assertEqual(result, "<script>alert('XSS')")
    
    def test_self_closing_script_tags(self):
        """Test self-closing script tags (should not match - regex requires closing tag)"""
        result = self.apply_filter("<script/>")
        self.assertEqual(result, "<script/>")
    
    def test_script_with_unusual_spacing(self):
        """Test script tags with spaces in tag name (should not match - valid HTML requires no spaces)"""
        result = self.apply_filter("< script >alert('XSS')</ script >")
        self.assertEqual(result, "< script >alert('XSS')</ script >")
    
    def test_other_xss_vectors_unaffected(self):
        """Test that other XSS vectors are not filtered (intended behavior)"""
        result = self.apply_filter("<img src=x onerror=alert('XSS')>")
        self.assertEqual(result, "<img src=x onerror=alert('XSS')>")
