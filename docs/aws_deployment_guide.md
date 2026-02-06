# AWS EC2 Deployment Guide

This guide outlines the steps to deploy the Antigravity Agent (Stock Trading Bot) to an AWS EC2 instance for 24/7 reliability.

## 1. Launch EC2 Instance
- **Region**: `us-east-1` (Virginia) - closest to most financial data centers (Alpaca servers) + extensive Free Tier support.
- **AMI**: Ubuntu Server 22.04 LTS (HVM)
- **Instance Type**: `t2.micro` or `t3.micro` (Free Tier eligible)
- **Security Group**: 
  - **Inbound Rule 1 (SSH)**: Allow Port 22 from `0.0.0.0/0` (Anywhere).
    - *Why?* Since you use a PEM key file, it is secure enough to open to the world, allowing you to connect from cafes/hotels.
  - **Inbound Rule 2 (Streamlit)**: DO NOT OPEN Port 8501 to the world.
    - *Why?* Streamlit has no default password. We will access it safely via SSH Tunneling.

## 2. Server Setup (SSH)
Connect to your instance (Amazon Linux 2023):
```bash
ssh -i "key.pem" -L 8501:localhost:8501 ec2-user@<IP-ADDRESS>
```

### Update & Install Dependencies
```bash
sudo dnf update -y
sudo dnf install git python3-pip -y
```

## 3. Clone Repository & Setup
```bash
# Clone
git clone <your-repository-url> stock-trading
cd stock-trading

# Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install Requirements
pip install -r requirements.txt
```

### Configure Environment
Create the `.env` file manually.
```bash
nano .env
```
Paste your Alpaca Paper API Keys:
```
ALPACA_API_KEY=PK...
ALPACA_SECRET_KEY=...
ALPACA_BASE_URL=https://paper-api.alpaca.markets
```

## 4. Systemd Service (Auto-Start)
Create a service file.

```bash
sudo nano /etc/systemd/system/antigravity.service
```

Content (Note: User is `ec2-user`):
```ini
[Unit]
Description=Antigravity Trading Agent
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/stock-trading
ExecStart=/home/ec2-user/stock-trading/venv/bin/python main.py
Restart=always
RestartSec=5
StandardOutput=append:/home/ec2-user/stock-trading/agent.log
StandardError=append:/home/ec2-user/stock-trading/agent.error.log

[Install]
WantedBy=multi-user.target
```

### Enable & Start
```bash
sudo systemctl daemon-reload
sudo systemctl enable antigravity
sudo systemctl start antigravity
```

### Monitor Logs
```bash
# Real-time logs
tail -f agent.log
```

## 5. Dashboard (Optional)
To run the Streamlit dashboard:
```bash
# Run in background via nohup
nohup streamlit run src/dashboard/app.py --server.port 8501 &
```
*Note: For better security, consider SSH tunneling instead of opening port 8501.*
`ssh -i key.pem -L 8501:localhost:8501 ubuntu@ip` then browse `localhost:8501`.
