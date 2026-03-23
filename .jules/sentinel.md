
## 2024-05-20 - Missing Security Headers
**Vulnerability:** The FastAPI application lacked essential HTTP security headers (like X-Frame-Options, X-Content-Type-Options, Strict-Transport-Security), leaving the frontend susceptible to Clickjacking, MIME-sniffing, XSS execution, and downgrade attacks.
**Learning:** FastAPI does not include security headers by default. It relies heavily on deployment assumptions (like Nginx/HAProxy handling them), which is not always the case in modern standalone or containerized deployments.
**Prevention:** Always implement a dedicated security middleware or use a library to enforce baseline HTTP security headers at the application level to ensure defense in depth.
