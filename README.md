# Admin Web Panel

A simple admin dashboard for the Telegram shop bot.

## Features
- View all orders with status
- Update order status
- Update product stock quantity
- Basic admin login protection

## Run locally

```bash
cd AdminWEB
python -m venv .venv
. .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

## Environment variables

Create `.env` in the project root or set these in your environment:

```env
BOT_TOKEN=your_bot_token
DB_HOST=localhost
DB_PORT=5432
DB_NAME=telegram_shop
DB_USER=postgres
DB_PASSWORD=password
ADMIN_WEB_USERNAME=admin
ADMIN_WEB_PASSWORD=admin123
ADMIN_WEB_SECRET=replace_with_random_secret
ADMIN_WEB_ALLOWED_IPS=127.0.0.1,203.0.113.10
```

The site uses the same PostgreSQL database as the Telegram bot.

## Whitelist setup

The whitelist works by IP address. If the request comes from an allowed IP, the admin panel opens without entering a password.

How to add a device:

1. Find the current IP address of the device you use.
   - On Windows: `ipconfig`
   - On Mac/Linux: `ifconfig` or `ip addr`
2. Add it to `ADMIN_WEB_ALLOWED_IPS` in `.env` as a comma-separated list.
3. Restart the Flask app.

Example:

```env
ADMIN_WEB_ALLOWED_IPS=127.0.0.1,192.168.1.50,95.163.255.14
```

If the device has a dynamic IP, it may change later and stop being allowed. In that case, use a VPN or static IP, or keep the password fallback enabled.

If no IP is in the whitelist, the normal username/password login will still work.

## Deployment

This app is ready for deployment on free hosting such as Render.

### Option 1: Render (free)

1. Push the `AdminWEB` folder to GitHub.
2. Create a new Web Service on Render.
3. Connect the repository.
4. Set the build command:

```bash
pip install -r requirements.txt
```

5. Set the start command:

```bash
gunicorn app:app --bind 0.0.0.0:$PORT
```

6. Add environment variables:

```env
DB_HOST=your_db_host
DB_PORT=5432
DB_NAME=telegram_shop
DB_USER=postgres
DB_PASSWORD=your_db_password
ADMIN_WEB_USERNAME=admin
ADMIN_WEB_PASSWORD=strong_password_here
ADMIN_WEB_SECRET=random_secret_here
ADMIN_WEB_ALLOWED_IPS=127.0.0.1
PORT=10000
FLASK_DEBUG=0
```

7. Deploy.

Render will give you a public URL like:

```text
https://your-app-name.onrender.com
```

### Important:

- Free hosting is good for testing and simple admin access.
- For production, it is safer to use a real database host, not a local PC database.
- The app can be opened from any phone/browser in the world through the public URL.

### Disable local debug mode on deployed app

Keep:

```env
FLASK_DEBUG=0
```

Do not use `debug=True` on public hosting.
