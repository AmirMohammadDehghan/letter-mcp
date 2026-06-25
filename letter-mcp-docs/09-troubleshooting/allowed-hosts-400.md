# خطای 400 Bad Request و ALLOWED_HOSTS

## نشانه

```text
HTTP/1.1 400 Bad Request
```

در Django production، علت رایج `DisallowedHost` است.

## تست‌ها

```bash
curl -I http://127.0.0.1:8002/admin/
curl -I http://SERVER_IP:8002/admin/
curl -I http://SERVER_IP:8002/admin/ -H "Host: lettermcp.24u.ir"
```

اگر با Host دامنه `302` ولی با IP `400` بود، یعنی IP داخل `ALLOWED_HOSTS` نیست.

## تنظیم .env

```env
ALLOWED_HOSTS=lettermcp.24u.ir,SERVER_IP,127.0.0.1,localhost
CSRF_TRUSTED_ORIGINS=https://lettermcp.24u.ir,http://SERVER_IP:8002
```

بعد:

```bash
docker compose restart web
```

## دیدن لاگ دقیق

```bash
docker compose logs --tail=120 web | grep -i "Invalid HTTP_HOST" -A2 -B2
```

هر host که Django در لاگ می‌گوید را به `ALLOWED_HOSTS` اضافه کن.

## دامنه اشتباه

در طول deploy یک اشتباه تایپی بین این دو دامنه رخ داد:

```text
lettermcp.24u.ir
lettermpc.24u.ir
```

حتماً دامنه نهایی را یکدست کن.
