# 自動化行程規劃系統

依天數、預算、偏好，用 AI 自動生成國內外旅遊行程，整合**每日天氣預報**與皮克敏情報，並具備完整會員系統（含信箱驗證）與歷史行程儲存。

- **後端**：FastAPI + SQLAlchemy + Alembic
- **前端**：React + Vite + Tailwind CSS
- **資料庫**：PostgreSQL（雲端建議 [Neon](https://neon.tech) 永久免費）
- **AI 引擎**：主力 Groq `llama-3.3-70b-versatile`（免費、極快、雲端穩定）；次要 NVIDIA `nemotron-3-ultra-550b-a55b`
- **天氣**：[Open-Meteo](https://open-meteo.com) 預報 + [OpenStreetMap Nominatim](https://nominatim.org) 地理編碼（皆免費免金鑰）
- **部署**：Render（後端 Web Service + 前端 Static Site）+ Neon（資料庫）

---

## 專案結構

```
backend/    FastAPI 後端（auth / itineraries / AI 服務 / migrations）
frontend/   React 前端
docker-compose.yml   本機一鍵開發
render.yaml          Render 一鍵部署藍圖
```

---

## 一、本機開發

### 方式 A：Docker（最簡單，一鍵全起）

```bash
# （選填）先把真正的 NVIDIA 金鑰放進環境變數
# Windows PowerShell:  $env:NVIDIA_API_KEY="你的金鑰"
docker compose up --build
```

- 前端：http://localhost:5173
- 後端 API 文件（Swagger）：http://localhost:8000/docs

> 未設定 SMTP 時，驗證信／重設密碼信不會真的寄出，而是**把連結印到後端 log**。
> 在 `docker compose` 的終端機輸出找 `[EMAIL DEV FALLBACK]` 即可看到驗證連結。

### 方式 B：手動分開跑

**後端**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
copy .env.example .env          # 編輯 .env 填入設定
alembic upgrade head            # 建表（需先有可連線的 PostgreSQL）
uvicorn app.main:app --reload
```

**前端**
```bash
cd frontend
npm install
copy .env.example .env          # 設定 VITE_API_BASE_URL=http://localhost:8000
npm run dev
```

### 跑測試
```bash
cd backend
.venv\Scripts\python -m pytest        # JSON 解析與認證邏輯單元測試
```

---

## 二、需要你提供的設定（環境變數）

| 變數 | 用途 | 備註 |
|------|------|------|
| `GROQ_API_KEY` | **主力** AI 行程生成金鑰 | 免費申請：<https://console.groq.com> 。未填則改用 NVIDIA |
| `NVIDIA_API_KEY` | 次要 AI 金鑰 | 選填，可留空 |
| `JWT_SECRET` | 登入簽章密鑰 | 產生：`python -c "import secrets; print(secrets.token_urlsafe(48))"`（Render 可自動產生） |
| `DATABASE_URL` | 資料庫連線 | 本機由 docker-compose 提供；雲端貼上 Neon 連線字串 |
| `SMTP_HOST/PORT/USER/PASSWORD/EMAIL_FROM` | 寄信服務 | 選填。未填則寄信退回 log fallback |
| `FRONTEND_URL` | 信件連結與 CORS 來源 | 本機 `http://localhost:5173`；部署填前端網址 |

> 天氣預報用 Open-Meteo + OpenStreetMap，**免金鑰、免設定**，部署後即可使用。

---

## 三、部署到 Render + Neon（免費上線）

> 全程免費。資料庫用 **Neon 永久免費 PostgreSQL**（不會像 Render 免費 DB 約 30 天後被刪除），
> 後端／前端用 **Render 免費方案**。我已備好 `render.yaml`、`backend/Dockerfile`，
> 後端啟動時會自動跑 `alembic upgrade head` 建表。

**步驟 0：建立 Neon 免費資料庫（約 2 分鐘）**
1. 到 <https://neon.tech> 用 GitHub 註冊（免費）。
2. New Project → 建立後在 **Connection string** 複製連線字串（形如
   `postgresql://user:password@ep-xxx-pooler.region.aws.neon.tech/neondb?sslmode=require`）。
   待會貼到 Render 的 `DATABASE_URL`。

**步驟 1：把整個專案推上 GitHub**
```bash
git add . && git commit -m "deploy"
git push
```

**步驟 2：Render → New → Blueprint**，選擇此 repo。Render 會讀 `render.yaml`，自動建立：
   - `travel-backend`（後端 Docker）
   - `travel-frontend`（前端 Static Site）

**步驟 3：填入標記為 `sync: false` 的環境變數**（Render 不會自動帶）：
   - `travel-backend` →
     - `DATABASE_URL`（步驟 0 的 Neon 連線字串）
     - `GROQ_API_KEY`（你的 Groq 金鑰，<https://console.groq.com> 免費申請）
     - `FRONTEND_URL`（填 `travel-frontend` 的網址，例如 `https://travel-frontend.onrender.com`）
     - （選填）`NVIDIA_API_KEY`、SMTP 相關
   - `travel-frontend` → `VITE_API_BASE_URL`（填 `travel-backend` 的網址）

**步驟 4：** 因前後端網址互相依賴，**第一次部署完成後，回填上述網址再各 Redeploy 一次**即可。

**步驟 5：** 開 `travel-frontend` 網址，完整測試：註冊 → 收驗證信（或看後端 log 的連結）→ 驗證 → 登入 → 產生行程（含天氣預報）→ 查看歷史。

> 注意：Render 免費方案的服務閒置 15 分鐘會休眠，首次請求需數十秒喚醒（前端會顯示載入中）。
> 要避免休眠可用免費的 [UptimeRobot](https://uptimerobot.com) 每 10 分鐘 ping 後端 `/health`。

---

## 四、API 一覽

| Method | Path | 說明 |
|--------|------|------|
| POST | `/auth/register` | 註冊（寄驗證信） |
| GET | `/auth/verify-email?token=` | 信箱驗證 |
| POST | `/auth/login` | 登入（回 JWT） |
| POST | `/auth/forgot-password` | 申請重設密碼 |
| POST | `/auth/reset-password` | 用 token 設定新密碼 |
| GET | `/users/me` | 取得目前使用者 |
| POST | `/itineraries/generate` | 生成並儲存行程 |
| GET | `/itineraries` | 歷史行程清單 |
| GET | `/itineraries/{id}` | 行程詳情 |
| DELETE | `/itineraries/{id}` | 刪除行程 |
| GET | `/weather?location=&start_date=&days=` | 目的地每日天氣預報（Open-Meteo，免金鑰） |
| GET | `/pikmin/advice?location=` | 皮克敏情報（依地點，每日快取） |

## 五、皮克敏探索（Pikmin Bloom 玩家專用）

針對目的地提供「特別 / 地區限定皮克敏」、各地點類型可獲得的裝飾皮克敏、近期活動與蒐集建議。

- 入口：導覽列「🌸 皮克敏」獨立查詢頁，**並融入**行程產生結果頁與行程詳情頁。
- 資料來源：Pikmin Bloom **無官方公開 API**，故採 AI 知識生成；活動資訊反映模型知識，非當下官方最新公告（UI 已標示）。
- 「每日更新」：後端依 `(地點, 日期)` 快取於 `pikmin_cache`，同地點同一天回快取、隔天自動重新生成，兼顧時效與 API 用量。
