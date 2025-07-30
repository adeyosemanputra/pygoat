# Template Injection Lab

This lab demonstrates Server-Side Template Injection (SSTI) vulnerabilities in a Flask application using Jinja2 templates. Users can create blog posts that are rendered using the template engine, making it vulnerable to template injection attacks.

## Getting Started

1. Build and run the lab using Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. Access the lab at `http://localhost:5000`

## Vulnerability Description

The application creates blog posts by directly rendering user input as Jinja2 templates. This allows attackers to inject malicious template expressions that could lead to:
- Information disclosure
- Remote code execution
- Server file system access

### Example Payload

Try creating a blog post with the following content to test the template injection:
```
{{ 7 * 7 }}
```

For more advanced exploitation, try:
```
{{ config }}
{{ self._TemplateReference__context.cycler.__init__.__globals__.os.popen('id').read() }}
```

## Learning Objectives

1. Understand how template injection vulnerabilities occur
2. Learn to identify vulnerable template usage in web applications
3. Practice exploiting template injection vulnerabilities
4. Understand secure template usage and mitigation strategies

## Security Best Practices

To prevent template injection:
1. Never use user input directly in template rendering
2. Use a sandboxed environment for template rendering
3. Apply proper input validation and sanitization
4. Use safe template contexts that limit available functions and objects

## References

- [OWASP Template Injection](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/18-Testing_for_Server_Side_Template_Injection)
- [PayloadsAllTheThings - SSTI](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection)
- [HackTricks - SSTI](https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection)
