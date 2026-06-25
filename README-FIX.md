# letter-mcp deploy fix

This kit fixes the Gunicorn WSGI target for this project.

Correct WSGI target:

```bash
gunicorn core.wsgi:application
```

Wrong target that caused the crash:

```bash
gunicorn mcp.wsgi:application
```

Copy files into the project root, commit, push, then pull on the server and rebuild.
