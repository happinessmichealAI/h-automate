# H-Automate Testing & Deployment Guide

## Quick Start Testing

### 1. Install Backend Dependencies

```bash
cd C:/Users/USER/Documents/h-automate
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 3. Start Backend Server

```bash
cd C:/Users/USER/Documents/h-automate
venv\Scripts\activate
cd backend
uvicorn main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

### 4. Start Frontend Development Server

Open a new terminal:

```bash
cd C:/Users/USER/Documents/h-automate/frontend
npm run dev
```

Frontend will be available at: http://localhost:5173

---

## Testing Checklist

### ✅ Backend API Tests

#### Health Check
```bash
curl http://localhost:8000/health
```
Expected: `{"status": "ok", "product": "H-Automate", "version": "1.0.0"}`

#### Sample Data Analysis (Mini-Mart)
```bash
curl -X POST http://localhost:8000/api/analyze \
  -F "business_type=mini-mart" \
  -F "sample_type=mini-mart"
```
Expected: JSON response with diagnosis, metrics, warnings

#### Sample Data Analysis (All 5 Business Types)
Test each:
- `mini-mart`
- `pharmacy`
- `pos-agent`
- `restaurant`
- `fashion-store`

#### File Upload Test
1. Navigate to http://localhost:5173/business-insights
2. Upload `sample_data/minimart_sales.csv`
3. Select business type: Mini-Mart
4. Click "Analyze Business Data"
5. Verify diagnosis appears

#### Smart Operations Test
```bash
curl -X POST http://localhost:8000/api/operations \
  -H "Content-Type: application/json" \
  -d '{
    "problem": "Customers buy once but rarely return",
    "business_type": "mini-mart"
  }'
```

---

### ✅ Frontend UI Tests

#### Landing Page
- [ ] Hero section displays correctly
- [ ] "Try Sample Business Data" button works
- [ ] "Upload Your File" button works
- [ ] Business type modal opens with 5 cards
- [ ] Each business card is clickable
- [ ] Modal closes properly

#### Business Insights Page
- [ ] File upload drag-and-drop works
- [ ] File picker works
- [ ] Business type dropdown shows all 5 types
- [ ] Sample data loads when triggered from Landing
- [ ] Loading state displays with animated steps
- [ ] Results display after analysis
- [ ] HealthSnapshot component renders with color-coded metrics
- [ ] Charts component renders (3 charts max)
- [ ] Download PDF button appears
- [ ] Error states display correctly

#### Smart Operations Page
- [ ] Problem textarea accepts input
- [ ] Character count validation works (min 10 chars)
- [ ] Business type selector works
- [ ] Loading state displays
- [ ] Results display in structured format
- [ ] Difficulty badges show correct colors
- [ ] Workflow timeline renders
- [ ] Download report button works

---

### ✅ Mobile Responsiveness Tests

Test at these viewport widths:
- [ ] 360px (minimum width requirement)
- [ ] 375px (iPhone SE)
- [ ] 414px (iPhone Pro Max)
- [ ] 768px (iPad)
- [ ] 1024px (Desktop)

#### Mobile-Specific Checks
- [ ] Navigation menu is accessible
- [ ] Business type cards stack vertically
- [ ] File upload area is tappable
- [ ] All buttons are at least 44px tall (touch target)
- [ ] Text is readable (minimum 14px)
- [ ] Charts are readable on small screens
- [ ] Horizontal bar chart used for Top Products (not vertical)
- [ ] No horizontal scrolling

---

### ✅ Error Handling Tests

#### Unreadable File
1. Upload a .txt file
2. Verify error: "We couldn't understand this file format"
3. Verify "View Sample File Format" button appears

#### Messy Data
1. Upload a CSV with missing columns
2. Verify error: "Your file may be missing important sales information"
3. Verify "See How to Prepare Your File" button appears

#### Wrong File Type
1. Upload an image file
2. Verify error: "This doesn't look like sales data"

#### AI Unavailable
1. Stop backend server
2. Try to analyze data
3. Verify error: "Analysis is taking longer than expected"
4. Verify "Try Again" button appears

#### Empty State
1. Navigate to Business Insights without uploading
2. Verify empty state message
3. Verify "See Sample Report" button

---

### ✅ Loading State Tests

#### Business Insights Loading
1. Upload file or select sample data
2. Verify loading animation appears
3. Verify 5 steps animate sequentially:
   - Reading your file
   - Understanding sales patterns
   - Identifying business risks
   - Generating recommendations
   - Preparing your report
4. Verify time estimate shows
5. Wait 15+ seconds
6. Verify "Still working..." message appears
7. Verify "Keep Waiting" and "Try Again" buttons

#### Smart Operations Loading
1. Enter problem description
2. Click "Analyze Problem"
3. Verify 3 steps animate:
   - Analyzing your situation
   - Reviewing possible causes
   - Building your action plan

---

### ✅ PDF Generation Tests

#### Business Insights PDF
1. Complete an analysis
2. Click "Download Business Report"
3. Verify PDF downloads
4. Open PDF and verify:
   - [ ] Header with business type and date
   - [ ] Executive Summary section
   - [ ] Business Health Snapshot
   - [ ] Key Metrics with scores
   - [ ] AI Diagnosis text
   - [ ] Likely Contributing Factors
   - [ ] Recommended Actions
   - [ ] Suggested Automation Workflows
   - [ ] Important Note at bottom
   - [ ] Footer with H-Automate branding
   - [ ] Professional consultant-style formatting
   - [ ] No technical jargon

#### Smart Operations PDF
1. Complete an operations analysis
2. Click "Download Action Report"
3. Verify PDF downloads with action plan

---

### ✅ Data Quality Tests

Test with real-world messy data:

#### Test Case 1: Inconsistent Product Names
Create CSV with:
```
Date,Product,Amount
2026-01-01,Coke 50cl,500
2026-01-02,coca cola small,500
2026-01-03,COKE,500
```
Verify: Products are normalized to "Coca Cola"

#### Test Case 2: Missing Dates
Create CSV with some blank date cells
Verify: Warning appears about unreadable dates

#### Test Case 3: Merged Cells (Excel)
Create Excel with merged cells
Verify: Data cleaner handles gracefully

#### Test Case 4: Zero Values
Create CSV with ₦0 entries
Verify: Zero entries are excluded from analysis

---

### ✅ Acceptance Criteria Verification

From the implementation brief:

#### Core Functionality
- [ ] User can run complete sample analysis for all 5 business types
- [ ] CSV upload works on mobile (360px width)
- [ ] Excel (.xlsx) upload works
- [ ] Business type selection works for all 5 types
- [ ] `get_diagnosis()` called correctly from backend
- [ ] `data_cleaner.py` computes all fields before calling AI
- [ ] Diagnosis output follows correct structure

#### Output Quality
- [ ] Business Health Snapshot renders with 4 scored metrics
- [ ] Output follows Insight → Interpretation → Action structure
- [ ] Maximum 3 charts rendered
- [ ] Donut chart shows max 5 categories + "Other"
- [ ] All language is plain English (no jargon)
- [ ] Safe AI language used ("Likely..." not "Your sales dropped because...")
- [ ] If data incomplete, clear note appears

#### Security
- [ ] GROQ_API_KEY loaded from .env (never hardcoded)
- [ ] .env listed in .gitignore
- [ ] .env.example committed with placeholder only

#### Report
- [ ] Downloadable PDF generates correctly
- [ ] PDF includes all 7 sections in order
- [ ] PDF looks consultant-style, not technical

#### States
- [ ] All 5 error states render correctly
- [ ] Business Insights loading state animates
- [ ] Smart Operations loading state animates
- [ ] Slow network delay state triggers after 15 seconds
- [ ] No empty screens anywhere

#### Mobile
- [ ] Full app works at 360px width
- [ ] All buttons tappable on mobile
- [ ] Charts readable on small screens
- [ ] Horizontal bar chart for Top Products

#### Smart Operations
- [ ] Text input accepts problem description
- [ ] Output renders all 5 sections
- [ ] Workflow renders as visual timeline
- [ ] No fake precision in Expected Outcome

---

## Performance Tests

### Backend Response Times
- [ ] Health check: < 100ms
- [ ] Sample data analysis: 10-15 seconds
- [ ] File upload analysis: 12-18 seconds
- [ ] Smart operations: 8-12 seconds

### Frontend Load Times
- [ ] Initial page load: < 2 seconds
- [ ] Navigation between pages: < 500ms
- [ ] Chart rendering: < 1 second

### Rate Limiting
- [ ] 6th request within 1 minute returns 429 error
- [ ] Error message is user-friendly

---

## Browser Compatibility

Test on:
- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

---

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] No console errors in browser
- [ ] No Python errors in backend logs
- [ ] .env file configured with production API key
- [ ] CORS origins updated for production domain
- [ ] Rate limiting configured appropriately

### Backend Deployment (Render/Railway/Heroku)
- [ ] Environment variables set
- [ ] Python version specified (3.11+)
- [ ] requirements.txt up to date
- [ ] Health check endpoint working
- [ ] Static files served correctly

### Frontend Deployment (Vercel/Netlify)
- [ ] Environment variables set (VITE_API_URL)
- [ ] Build command: `npm run build`
- [ ] Output directory: `dist`
- [ ] Redirects configured for SPA routing

### Post-Deployment
- [ ] Production URL accessible
- [ ] Sample data analysis works
- [ ] File upload works
- [ ] PDF download works
- [ ] Mobile experience tested on real devices
- [ ] SSL certificate active (HTTPS)

---

## Common Issues & Solutions

### Issue: "Import weasyprint could not be resolved"
**Solution:** WeasyPrint requires system dependencies. On Windows:
```bash
# Install GTK3 runtime
# Download from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
pip install weasyprint
```

### Issue: "GROQ_API_KEY not found"
**Solution:** Create .env file in project root:
```
GROQ_API_KEY=your_actual_key_here
```

### Issue: CORS errors in browser
**Solution:** Check backend CORS configuration in `main.py`:
```python
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://your-production-domain.com"
]
```

### Issue: Charts not rendering
**Solution:** Verify Recharts is installed:
```bash
cd frontend
npm install recharts
```

### Issue: PDF generation fails
**Solution:** Check WeasyPrint installation and system dependencies

### Issue: Rate limit errors
**Solution:** Adjust rate limit in `main.py` or wait 1 minute between requests

---

## Next Steps After Testing

1. **Fix any failing tests** before deployment
2. **Document any discovered issues** in GitHub Issues
3. **Update README** with any new setup requirements
4. **Create user documentation** for business owners
5. **Set up monitoring** (error tracking, analytics)
6. **Plan V2 features** based on user feedback

---

## Support

For issues or questions:
- Check README.md for setup instructions
- Review this testing guide
- Check backend logs: `backend/logs/`
- Check browser console for frontend errors
- Verify .env file is configured correctly

---

**Last Updated:** May 22, 2026  
**Version:** 1.0.0