# 🐧 Linux Commands Cheat Sheet (Stock Trading Bot)

## 1. 🔑 접속 및 보안 (Connection)
```bash
# SSH 접속 (터널링 포함: 대시보드 8501 포트 연결)
ssh -i "stock-market.pem" -L 8501:localhost:8501 ec2-user@15.164.48.103

# 파일 권한 변경 (로그 권한 문제 해결)
sudo chown ec2-user:ec2-user agent.log
sudo chmod 664 agent.log
```

## 2. 🔄 코드 업데이트 (Update)
```bash
# 주식 봇 폴더로 이동
cd ~/stock-trading

# 최신 코드 받기 (GitHub -> Server)
git pull
```

## 3. 🤖 봇 서비스 관리 (Systemd)
> `main.py` (매매 알고리즘)는 백그라운드 서비스(`antigravity`)로 돌아갑니다.

```bash
# 봇 상태 확인 (살아있는지 체크)
sudo systemctl status antigravity

# 봇 끄기
sudo systemctl stop antigravity

# 봇 켜기
sudo systemctl start antigravity

# 봇 재시작 (코드 업데이트 후 필수!)
sudo systemctl restart antigravity
```

## 4. 📊 대시보드 관리 (Streamlit)
> 대시보드는 별도로 실행해줘야 합니다.

```bash
# 대시보드 강제 종료
pkill -f streamlit

# 대시보드 백그라운드 실행 (비밀번호 설정 후)
nohup ./run.sh > streamlit.log 2>&1 &
```

## 5. 📝 로그 확인 (Monitoring)
```bash
# 봇 에러 로그 확인 (마지막 20줄)
tail -n 20 agent.error.log

# 봇 실시간 로그 보기 (계속 출력됨, 끄려면 Ctrl+C)
tail -f agent.log
```
