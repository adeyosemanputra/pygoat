# XSS Lab 3: Regex pattern removes all alphanumeric characters making lab impossible to solve

## Summary
XSS Lab 3 uses `r'\w'` regex pattern which removes ALL alphanumeric characters (letters, digits, underscores) from user input, making it impossible to execute any meaningful JavaScript code including the intended XSS payload.

## Environment
- OS: Windows 11
- Python version: 3.13.7
- Django version: 4.2
- Branch/Commit: main (latest)
- How you ran PyGoat: Local install (`python manage.py runserver`)

## Steps to Reproduce
1. Navigate to http://127.0.0.1:8000/xss
2. Click on "Access Lab" for the third XSS lab (Lab 3)
3. Go to http://127.0.0.1:8000/xssL3
4. Try to input ANY payload in the "Name" field, for example:
   - `<svg/onload=alert(1)>` 
   - `alert(document.cookie)`
   - `';alert('XSS');//`
5. Submit the form
6. Observe the output in the page source

## Expected Behavior
According to the lab description in `/introduction/templates/Lab/XSS/xss.html` (lines 106-113):

> "The goal of this challenge is to trigger an alert, User input is being Reflected on script Tag, but the real challenge lies in the fact that all alphanumeric characters are **escaped**. Can you find way to pop an alert ?"

The lab should:
1. **Escape** alphanumeric characters (not remove them)
2. Still allow creative XSS payloads to work through alternative character encoding or special characters
3. Be solvable with advanced XSS techniques

## Actual Behavior
The current implementation in `/introduction/views.py` (lines 123-133):

```python
def xss_lab3(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST.get('username')
            print(type(username))
            pattern = r'\w'  # ← PROBLEM: This matches ALL word characters
            result = re.sub(pattern, '', username)  # ← REMOVES them entirely
            context = {'code':result}
            return render(request, 'Lab/XSS/xss_lab_3.html',context)
        else:
            return render(request, 'Lab/XSS/xss_lab_3.html')
    else:        
        return redirect('login')
```

**What actually happens:**
- The regex `r'\w'` matches: letters (a-z, A-Z), digits (0-9), and underscore (_)
- `re.sub(pattern, '', username)` **REMOVES** all these characters completely
- Input: `<svg/onload=alert(1)>` → Output: `</=/()>`
- Input: `alert(document.cookie)` → Output: `(..)`
- This makes it **impossible** to execute ANY JavaScript code

The template then renders this in a script tag (`/introduction/templates/Lab/XSS/xss_lab_3.html`, lines 20-23):

```html
<script>
    // LAB 3 JS CODE
    {{code}}
</script>
```

Even without the `|safe` filter, the stripped code is useless.

## Impact
1. **Lab is broken**: Students cannot complete the lab - there's no valid solution
2. **Misleading documentation**: Description says "escaped" but code actually "removes"
3. **Learning objective lost**: Students can't learn advanced XSS bypass techniques if the lab is impossible

## Possible Cause / Proposed Fix

**Root cause:** 
- Wrong regex pattern: `r'\w'` removes ALL word characters instead of escaping them
- Lab description and implementation don't match

**Proposed solutions:**

### Option 1: Fix the regex to match the description (escape instead of remove)
Replace the character removal with proper escaping:

```python
def xss_lab3(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST.get('username', '')
            # Escape alphanumeric characters using HTML entities or hex encoding
            result = ''
            for char in username:
                if char.isalnum():
                    result += f'&#x{ord(char):x};'  # Convert to hex entity
                else:
                    result += char
            context = {'code': result}
            return render(request, 'Lab/XSS/xss_lab_3.html', context)
        else:
            return render(request, 'Lab/XSS/xss_lab_3.html')
    else:        
        return redirect('login')
```

With this fix, students could still solve it using:
- JSFuck (JavaScript with only 6 characters: `[]()!+`)
- Hex/Unicode encoding in event handlers
- Other creative bypasses

### Option 2: Update lab description to match current code
If the intention is to remove characters, update the description to:
> "The goal of this challenge is to trigger an alert. User input is being reflected in a script tag, but all alphanumeric characters are **removed**. Can you find a way to pop an alert using only special characters?"

Then provide a valid solution (e.g., using JSFuck or similar techniques).

### Option 3: Redesign the lab with a different filter
Create a more realistic bypass scenario, such as:
- Filter only `<script>` tags (case-sensitive)
- Filter specific keywords like `alert`, `eval`, `document`
- Allow bypasses using alternative functions or encoding

## Test Cases
After implementing the fix, verify that:

1. **Lab is solvable**: At least one valid XSS payload works
2. **Description matches implementation**: "escaped" vs "removed" is consistent
3. **Educational value**: Students learn actual XSS bypass techniques
4. **No regressions**: Other XSS labs (Lab 1 & 2) still work correctly

## Additional Context
- XSS Lab 1 works correctly (uses `|safe` in template for reflected XSS)
- XSS Lab 2 has a separate issue #314 (case-sensitive filter)
- This lab (Lab 3) appears to be the most broken of the three

---

**If this issue is valid, I would like to work on a fix and open a PR.**

I can provide:
1. Fixed `views.py` with proper character escaping
2. Updated tests to verify the lab is solvable
3. Updated documentation with a working example solution
4. Verification that the learning objective is achieved
