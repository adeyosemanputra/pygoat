#!/usr/bin/env python
"""
Test script to verify XSS Lab 2 case-insensitive filter fix
"""
import re

def test_xss_lab2_filter():
    """Test the case-insensitive script tag filter"""
    
    test_cases = [
        # (input, expected_output, description)
        ("<script>alert('XSS')</script>", "", "Lowercase script tags"),
        ("<SCRIPT>alert('XSS')</SCRIPT>", "", "Uppercase script tags"),
        ("<ScRiPt>alert('XSS')</ScRiPt>", "", "Mixed case script tags"),
        ("<script src='evil.js'></script>", "", "Script tag with attributes"),
        ("<SCRIPT SRC='evil.js'></SCRIPT>", "", "Uppercase script with attributes"),
        ("<img src=x onerror=alert('XSS')>", "<img src=x onerror=alert('XSS')>", "Other XSS vectors should work"),
        ("Hello <script>bad()</script> World", "Hello  World", "Script in middle of text"),
        # Edge cases suggested by Copilot
        ("<script>alert('XSS')", "<script>alert('XSS')", "Script tags without closing tags"),
        ("<script/>", "<script/>", "Self-closing script tags"),
        ("<script>\nalert('XSS')\n</script>", "", "Script tags with newlines"),
        ("<script>alert(1)</script>text<SCRIPT>alert(2)</SCRIPT>", "text", "Multiple script tags in one input"),
        ("< script >alert('XSS')</ script >", "< script >alert('XSS')</ script >", "Script tags with unusual spacing"),
    ]
    
    print("Testing XSS Lab 2 Filter Fix\n" + "="*50)
    
    all_passed = True
    for input_str, expected, description in test_cases:
        # Apply the same filter logic as in views.py
        username = input_str.strip()
        username = re.sub(r'<script\b[^>]*>.*?</script>', '', username, flags=re.IGNORECASE | re.DOTALL)
        
        passed = username == expected
        all_passed = all_passed and passed
        
        status = "PASS" if passed else "FAIL"
        print(f"\n{status}: {description}")
        print(f"  Input:    {input_str}")
        print(f"  Expected: {expected}")
        print(f"  Got:      {username}")
    
    print("\n" + "="*50)
    if all_passed:
        print("All tests passed!")
        return 0
    else:
        print("Some tests failed!")
        return 1

if __name__ == "__main__":
    exit(test_xss_lab2_filter())
