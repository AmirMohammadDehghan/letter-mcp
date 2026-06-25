# آماده‌سازی سرور Ubuntu

## مسیر نصب پروژه

مسیر پیشنهادی:

```bash
sudo mkdir -p /opt/apps
sudo chown -R $USER:$USER /opt/apps
cd /opt/apps
```

کلون پروژه:

```bash
cd /opt/apps
git clone git@github.com:AmirMohammadDehghan/letter-mcp.git
cd letter-mcp
```

اگر از HTTPS استفاده می‌کنی:

```bash
git clone https://github.com/AmirMohammadDehghan/letter-mcp.git
```

## نصب Docker و Docker Compose

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg git unzip nano

sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo $VERSION_CODENAME) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

اضافه کردن کاربر به گروه Docker:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

تست:

```bash
docker --version
docker compose version
```

## ابزارهای کمکی

```bash
sudo apt install -y curl jq awscli postgresql-client
```

اگر از MinIO Client برای RustFS استفاده می‌کنی:

```bash
curl -O https://dl.min.io/client/mc/release/linux-amd64/mc
chmod +x mc
sudo mv mc /usr/local/bin/mc
```

## تنظیم ساعت سرور

```bash
timedatectl
sudo timedatectl set-timezone Asia/Tehran
```

اگر NTP مشکل داشت:

```bash
timedatectl timesync-status
journalctl -u systemd-timesyncd -n 50 --no-pager
```
