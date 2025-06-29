# Email on TimeDial.org

You can access your **timedial.org** email account using standard IMAP and SMTP clients, like Thunderbird, Apple Mail, etc. This guide outlines the required settings and recommendations for securely connecting your mail client.

## Important Notes

- Email can only be sent and received within the `timedial.org` domain. 
- You **cannot** send or receive mail to/from external domains (e.g., `gmail.com`, `yahoo.com`).
- SSL is strongly recommended for IMAP (port 993) and required for SMTP. When you connect without SSL you risk exposing your credentials to others.

## IMAP (Incoming Mail)

- **Server:** `timedial.org`
- **Port (SSL/TLS):** `993` (recommended)
- **Port:** `143` (not recommended)
- **Encryption:** SSL/TLS strongly recommended
- **Username:** Your timedial.org username
- **Password:** Your timedial.org password

## SMTP (Outgoing Mail)

- **Server:** `timedial.org`
- **Port:** `587`
- **Encryption:** STARTTLS **(required)**
- **Username:** Your timedial.org username
- **Password:** Your timedial.org password
