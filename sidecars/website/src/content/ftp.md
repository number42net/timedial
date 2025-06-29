# FTP / FTPS Access for timedial.org

You can access your `timedial.org` home directory using standard FTP protocols. For security reasons, **FTPS** (FTP with TLS encryption) is strongly recommended.

## Server Information

- **Server:** `timedial.org`
- **Port:** `21` (used for both FTP and FTPS)
- **Username:** Your timedial.org username
- **Password:** Your timedial.org password
- **Encryption:** STARTTLS (explicit FTP over TLS) **strongly recommended**

## Notes

- Unencrypted FTP is supported, but **strongly discouraged** - use it only if FTPS is not possible and you're connected on a network your trust
- Using an unencrypted connection potentially exposes your credentials to 3rd parties
