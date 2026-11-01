# Information Disclosure lab

This lab deliberately reproduces **Sensitive Information in URL** in the VocabUp development app. It adds a development-only GET login, records full request URLs, and exposes the Nginx access log at `/logs/access.log`. The normal production login remains POST-only.

Use a disposable test account only. The ngrok URL makes the vulnerable app and its log readable to anyone who has the URL. Stop the tunnel and lab as soon as you finish. Do not enter a real email/password or reuse a real password.

## Run the lab

### Terminal 1 — database and VocabUp

From the VocabUp folder:

```powershell
Set-Location D:\CSATTT\VocabUP
docker compose up -d mysql
npm.cmd run dev
```

Leave this terminal running. Wait until the API on port `4000` and Vite on port `5173` have both started.

### Terminal 2 — Nginx

From the same folder, in a second terminal:

```powershell
Set-Location D:\CSATTT\VocabUP
docker compose -f nginx/docker-compose.yml up -d --force-recreate
```

Nginx listens on port `8080`, proxies the app and API, writes its access log to `nginx/logs/access.log` on the host, and intentionally serves that file under `/logs/`.

### Terminal 3 — ngrok

```powershell
ngrok http 8080
```

Open the HTTPS URL printed by ngrok. Register a disposable test account, then log in with it. In the browser Network panel, the login request is `GET /api/auth/login?email=...&password=...`. Open `<ngrok-url>/logs/access.log` to see the same fake credentials in Nginx's access log. The backend also records the request URL in `backend/access.log` and its terminal.

The demo only changes the login method while Vite is in dev mode. The backend GET route and full-URL logger are disabled when `NODE_ENV=production`.

## Run the clickjacking lab

The clickjacking lab is in the same VocabUp folder. Follow [CLICKJACKING_DEMO.md](../CLICKJACKING_DEMO.md). It uses VocabUp on port `5173` and its separate lure page on `4174`; the Information Disclosure demo uses Nginx on `8080`. You can run either lab against this same codebase. Keep the app account disposable.

## Stop

Stop ngrok with `Ctrl+C`, stop the app with `Ctrl+C` in Terminal 1, and stop Nginx with:

```powershell
docker compose -f nginx/docker-compose.yml down
```

