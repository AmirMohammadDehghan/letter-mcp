# فایروال، پورت و دامنه

## پورت‌های موردنیاز

در معماری فعلی، Arvan مستقیم به پورت `8002` سرور وصل می‌شود:

```text
Arvan CDN -> http://SERVER_IP:8002 -> Docker web container:8000
```

پس باید پورت 8002 باز باشد:

```bash
sudo ufw allow 8002/tcp
sudo ufw status
```

اگر SSH روی پورت خاصی است، قبل از فعال کردن UFW آن را باز کن:

```bash
sudo ufw allow YOUR_SSH_PORT/tcp
sudo ufw enable
```

## تنظیم Docker port

در `docker-compose.yml` سرویس web باید چنین mapping داشته باشد:

```yaml
ports:
  - "8002:8000"
```

اگر بنویسی:

```yaml
ports:
  - "127.0.0.1:8002:8000"
```

فقط خود سرور می‌تواند دسترسی داشته باشد و Arvan نمی‌تواند به origin وصل شود.

## تنظیم Arvan CDN

رکورد DNS:

```text
Type: A
Name: lettermcp
Value: SERVER_IP
Cloud: ON
```

تنظیم origin:

```text
Protocol: HTTP
Origin IP: SERVER_IP
Origin Port: 8002
```

## تست‌ها

از روی سرور:

```bash
curl -I http://127.0.0.1:8002/admin/
curl -I http://SERVER_IP:8002/admin/ -H "Host: lettermcp.24u.ir"
curl -I https://lettermcp.24u.ir/admin/
```

خروجی سالم برای `/admin/` معمولاً:

```text
HTTP/1.1 302 Found
Location: /admin/login/?next=/admin/
```

## نکته درباره ALLOWED_HOSTS

اگر مستقیم با IP تست می‌کنی، IP هم باید داخل `ALLOWED_HOSTS` باشد:

```env
ALLOWED_HOSTS=lettermcp.24u.ir,SERVER_IP,127.0.0.1,localhost
```
