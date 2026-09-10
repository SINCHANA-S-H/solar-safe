# Solar Safe — AI-Powered Solar PV Fault Detection Platform

Solar Safe is an intelligent solar photovoltaic (PV) inspection dashboard designed for rapid fault detection, electroluminescence/thermal anomaly screening, and automated maintenance compliance reporting.

---

## Technology Stack

- **Framework**: React 19 + Vite 8
- **Routing**: React Router DOM 7
- **Styling**: Tailwind CSS v4 (`@tailwindcss/vite`)
- **HTTP Client**: Axios with custom interceptors
- **Icons**: Lucide React

---

## Directory Structure

```text
frontend/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── chatbot/
│   │   │   └── ChatBot.jsx             # Floating solar safety rule-based assistant
│   │   ├── dashboard/
│   │   │   └── DashboardCards.jsx      # Metrics calculated strictly from scan history
│   │   ├── layout/
│   │   │   ├── Navbar.jsx              # Status heartbeat, breadcrumbs, user profile
│   │   │   ├── ProtectedRoute.jsx      # Route guard wrapping authenticated layout
│   │   │   └── Sidebar.jsx             # Desktop and mobile responsive navigation
│   │   └── upload/
│   │       ├── AIAnalysis.jsx          # Derived technical risk assessment & recommendations
│   │       ├── GradCAMViewer.jsx       # MobileNetV2 explainability architecture
│   │       ├── PredictionCard.jsx      # Result badge, confidence bar, class probabilities
│   │       └── UploadCard.jsx          # Drag-and-drop file target & JPG/PNG validation
│   ├── context/
│   │   ├── AuthContext.jsx             # Session provider with localStorage persistence
│   │   ├── authContextInstance.js      # Isolated Context instance
│   │   └── useAuth.js                  # Custom auth hook
│   ├── pages/
│   │   ├── Dashboard.jsx               # Inspection stats, recent scans, quick scan CTA
│   │   ├── History.jsx                 # Filterable & searchable scan history table
│   │   ├── Login.jsx                   # Production auth portal calling /login
│   │   ├── Register.jsx                # New inspector registration calling /signup
│   │   ├── Reports.jsx                 # On-demand PDF audit report downloads
│   │   ├── Settings.jsx                # Inspector credentials & API configuration status
│   │   ├── SolarMap.jsx                # GIS simulation & solar potential architecture
│   │   └── Upload.jsx                  # Solar PV image classification workspace
│   ├── services/
│   │   ├── api.js                      # Centralized Axios client with token injection
│   │   ├── authService.js              # /signup and /login API bindings
│   │   ├── chatService.js              # /chat assistant endpoint
│   │   ├── historyService.js           # /history query endpoint
│   │   ├── predictionService.js        # /predict multipart/form-data upload
│   │   └── reportService.js            # /report binary PDF stream & download trigger
│   ├── App.css
│   ├── App.jsx                         # Root application router
│   ├── index.css                       # Design tokens, fonts, and custom scrollbars
│   └── main.jsx
├── .env.example
├── package.json
└── vite.config.js
```

---

## Getting Started

### 1. Environment Configuration

Copy `.env.example` to create your local `.env`:

```powershell
cp .env.example .env
```

Ensure `VITE_API_BASE_URL` points to your active FastAPI backend instance:
```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 2. Install Dependencies

```powershell
npm install
```

### 3. Run Development Server

```powershell
npm run dev
```

The application will be accessible at: `http://localhost:5173/`

### 4. Build for Production

```powershell
npm run build
```

### 5. Lint Codebase

```powershell
npm run lint
```

---

## FastAPI Backend Integration Contract

- **`POST /signup`**: Query params `username`, `email`, `password`
- **`POST /login`**: Query params `email`, `password`
- **`POST /predict`**: Form-data `email` (string), `image` (JPG/PNG file)
  - Returns prediction, confidence, probabilities (`Cell_Crack`, `Hotspot`, `Normal`), and `image_name`.
- **`GET /history`**: Query param `email`
- **`POST /report`**: Query params `email`, `prediction`, `confidence`
  - Returns binary `application/pdf`
- **`POST /chat`**: Query param `message`
