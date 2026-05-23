# H-Automate

**AI-powered business operations assistant for Nigerian SMEs**

H-Automate helps small business owners — mini-marts, pharmacies, POS agents, restaurants, and fashion stores — make better decisions by analyzing their sales data and returning plain-English diagnoses, likely causes, and actionable recommendations.

---

## Features

- **CSV/Excel File Upload** — Analyze your sales data in minutes
- **5 Business Types Supported** — Mini-Mart, Pharmacy, POS Agent, Restaurant, Fashion Store
- **AI-Powered Diagnosis** — Using Groq API (llama-3.3-70b-versatile)
- **Business Health Snapshot** — 4 scored metrics with color-coded status
- **Actionable Recommendations** — Immediate, short-term, and medium-term actions
- **Downloadable PDF Reports** — Consultant-style business reports
- **Mobile-First Design** — Works perfectly on 360px width screens
- **Demo Mode** — Try sample business data without uploading files

---

## Tech Stack

### Backend
- **Python 3.9+**
- **FastAPI** — Modern, fast web framework
- **Pandas** — Data processing and analysis
- **Groq API** — AI-powered business diagnosis
- **WeasyPrint** — PDF report generation
- **SlowAPI** — Rate limiting (5 requests/minute)

### Frontend
- **React 18** — UI framework
- **Vite** — Build tool
- **TailwindCSS** — Styling
- **shadcn/ui** — UI components
- **Recharts** — Data visualization
- **Framer Motion** — Animations

---

## Quick Start

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- Groq API key ([Get one here](https://console.groq.com))

### Backend Setup

1. **Navigate to project directory**
   ```bash
   cd C:/Users/USER/Documents/h-automate
   ```

2. **Create Python virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create .env file**
   ```bash
   # Copy the example file
   copy .env.example .env
   
   # Edit .env and add your Groq API key
   # GROQ_API_KEY=your_actual_groq_api_key_here
   ```

6. **Run the backend server**
   ```bash
   cd backend
   uvicorn main:app --reload --port 8000
   ```

   The API will be available at:
   - **API Base:** http://localhost:8000/api
   - **API Docs:** http://localhost:8000/docs
   - **Health Check:** http://localhost:8000/health

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run development server**
   ```bash
   npm run dev
   ```

   The app will be available at: http://localhost:5173

---

## Project Structure

```
h-automate/
├── .env                          # API keys (NEVER commit)
├── .env.example                  # Safe template
├── .gitignore                    # Git exclusions
├── README.md                     # This file
├── requirements.txt              # Python dependencies
│
├── backend/
│   ├── main.py                   # FastAPI entry point
│   ├── groq_client.py            # AI diagnosis engine
│   ├── routes/
│   │   ├── analyst.py            # /api/analyze endpoint
│   │   └── operations.py         # /api/operations endpoint
│   ├── utils/
│   │   ├── data_cleaner.py       # Pandas preprocessing
│   │   └── pdf_generator.py     # PDF report generation
│   └── templates/
│       └── report_template.html  # PDF template
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Landing.jsx
│   │   │   ├── BusinessInsights.jsx
│   │   │   └── SmartOperations.jsx
│   │   ├── components/
│   │   │   ├── HealthSnapshot.jsx
│   │   │   ├── Charts.jsx
│   │   │   ├── LoadingState.jsx
│   │   │   └── ErrorState.jsx
│   │   └── App.jsx
│   └── public/
│
├── sample_data/
│   ├── minimart_sales.csv
│   ├── pharmacy_sales.csv
│   ├── pos_agent.csv
│   ├── restaurant_sales.csv
│   └── fashion_sales.csv
│
└── diagnosis_targets/
    ├── diagnosis_minimart.md
    ├── diagnosis_pharmacy.md
    └── diagnosis_pos.md
```

---

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Required
GROQ_API_KEY=your_groq_api_key_here

# Optional
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

**⚠️ IMPORTANT:** Never commit the `.env` file to version control. It's already listed in `.gitignore`.

---

## API Endpoints

### Business Insights

**POST /api/analyze**

Analyze sales data and return business diagnosis.

**Request (File Upload):**
```json
{
  "file": "base64_encoded_csv_or_excel",
  "business_type": "mini-mart",
  "filename": "sales.csv"
}
```

**Request (Sample Data):**
```json
{
  "sample_type": "mini-mart"
}
```

**Response:**
```json
{
  "status": "success",
  "diagnosis": "full structured diagnosis text",
  "metrics": {
    "total_transactions": {...},
    "monthly_averages": {...},
    "top_products": {...}
  },
  "missing_fields": [],
  "warnings": []
}
```

### Smart Operations

**POST /api/operations**

Get operational recommendations for a business problem.

**Request:**
```json
{
  "problem_description": "Customers buy once but rarely return",
  "business_type": "mini-mart"
}
```

**Response:**
```json
{
  "status": "success",
  "situation_summary": "...",
  "likely_causes": [...],
  "recommended_actions": [...],
  "workflow": [...],
  "expected_outcome": "..."
}
```

### Download Report

**POST /api/download-report**

Generate and download PDF business report.

---

## Sample Data

Sample CSV files for all 5 business types are available in the `sample_data/` directory:

- `minimart_sales.csv` — Mini-mart stock and sales data
- `pharmacy_sales.csv` — Pharmacy sales with expiry tracking
- `pos_agent.csv` — POS agent transaction data
- `restaurant_sales.csv` — Restaurant revenue and costs
- `fashion_sales.csv` — Fashion store customer patterns

Use these files to test the application without uploading your own data.

---

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Python linting
flake8 backend/

# JavaScript linting
cd frontend
npm run lint
```

### Building for Production

**Backend:**
```bash
# Backend runs with uvicorn in production
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run build
```

---

## Deployment

### Backend (Railway)

1. Create a new project on [Railway](https://railway.app)
2. Connect your GitHub repository
3. Set environment variables:
   - `GROQ_API_KEY`
   - `ENVIRONMENT=production`
   - `ALLOWED_ORIGINS=https://your-frontend-domain.vercel.app`
4. Deploy

### Frontend (Vercel)

1. Create a new project on [Vercel](https://vercel.com)
2. Connect your GitHub repository
3. Set environment variable:
   - `VITE_API_URL=https://your-backend.railway.app`
4. Deploy

---

## Usage Guide

### For Business Owners

1. **Try Sample Data First**
   - Click "Try Sample Business Data"
   - Select your business type
   - Review the AI-generated diagnosis

2. **Upload Your Own File**
   - Prepare your sales data in CSV or Excel format
   - Required columns: Date, Product, Revenue
   - Optional columns: Quantity, Cost, Payment Method
   - Click "Upload Your File"
   - Select your business type
   - Wait 10-15 seconds for analysis

3. **Review Your Diagnosis**
   - Business Health Snapshot (4 scored metrics)
   - Key Insights (specific patterns found)
   - Likely Causes (why these patterns exist)
   - Recommended Actions (what to do next)
   - Charts (visual trends)

4. **Download Report**
   - Click "Download Business Report"
   - Save the PDF for your records
   - Share with partners or advisors

### File Format Requirements

**CSV/Excel files must include:**
- **Date column** — Transaction date (any format)
- **Product column** — Product/item name
- **Revenue column** — Sale amount (with or without ₦ symbol)

**Optional columns:**
- Quantity — Units sold
- Cost — Cost price
- Payment Method — Cash, POS, Transfer
- Category — Product category

**Example CSV:**
```csv
Date,Product,Revenue,Quantity,Payment Method
2026-01-05,Rice,5000,2,Cash
2026-01-05,Indomie,800,5,POS
2026-01-06,Vegetable Oil,3500,1,Transfer
```

---

## Troubleshooting

### Backend Issues

**Error: "GROQ_API_KEY not found"**
- Ensure `.env` file exists in project root
- Verify `GROQ_API_KEY` is set correctly
- Restart the backend server

**Error: "Import errors" or "Module not found"**
- Activate virtual environment: `venv\Scripts\activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**Error: "Rate limit exceeded"**
- Wait 1 minute before trying again
- Rate limit is 5 requests per minute per IP

### Frontend Issues

**Error: "Failed to fetch"**
- Ensure backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Verify `VITE_API_URL` environment variable

**Error: "Cannot read properties of undefined"**
- Clear browser cache
- Restart development server: `npm run dev`

### File Upload Issues

**Error: "We couldn't understand this file format"**
- Ensure file is CSV or Excel (.xlsx)
- Check that file has required columns (Date, Product, Revenue)
- Remove merged cells from Excel files

**Error: "Your file may be missing important sales information"**
- Verify Date column has valid dates
- Ensure Revenue column has numeric values
- Check for empty rows or columns

---

## Security

- **API Key Protection:** Never commit `.env` file or hardcode API keys
- **Rate Limiting:** 5 requests/minute per IP to prevent abuse
- **CORS:** Only explicitly allowed origins can access the API
- **File Validation:** Only CSV and Excel files accepted, max 5MB
- **No Data Storage:** Uploaded files are processed in memory and not saved

---

## Contributing

This is a private project for Nigerian SME business analysis. Contributions are welcome from authorized developers only.

### Development Guidelines

1. Follow the existing code structure
2. Never modify `groq_client.py` prompts without approval
3. Test all changes on mobile (360px width minimum)
4. Use plain English in all user-facing text (no jargon)
5. Ensure all error states are user-friendly

---

## License

Proprietary — All rights reserved

---

## Support

For technical support or business inquiries:
- **Email:** support@h-automate.com
- **Documentation:** See `h-automate-implementation-plan.md`

---

## Acknowledgments

- **Groq** — AI inference platform
- **FastAPI** — Modern Python web framework
- **React** — UI framework
- **TailwindCSS** — Utility-first CSS framework
- **shadcn/ui** — Beautiful UI components

---

**Built for Nigerian SMEs with ❤️**