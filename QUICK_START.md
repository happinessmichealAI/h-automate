# H-Automate Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Backend Dependencies (2 minutes)

```bash
cd C:/Users/USER/Documents/h-automate
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Note:** If WeasyPrint installation fails on Windows, you may need to install GTK3 runtime first:
- Download from: https://github.com/tschoonj/GTK-for-Windows-Runtime-Environment-Installer
- Run installer, then retry `pip install -r requirements.txt`

### Step 2: Install Frontend Dependencies (1 minute)

```bash
cd frontend
npm install
```

### Step 3: Start Backend Server (30 seconds)

Open a terminal:

```bash
cd C:/Users/USER/Documents/h-automate
venv\Scripts\activate
cd backend
uvicorn main:app --reload --port 8000
```

You should see:
```
✅ H-Automate API ready
   Groq API key: ********************XXXX
INFO:     Uvicorn running on http://127.0.0.1:8000
```

**Keep this terminal open!**

### Step 4: Start Frontend Server (30 seconds)

Open a **new** terminal:

```bash
cd C:/Users/USER/Documents/h-automate/frontend
npm run dev
```

You should see:
```
  VITE v5.4.2  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### Step 5: Open the App (10 seconds)

Open your browser and go to:
```
http://localhost:5173
```

---

## ✅ Quick Test

### Test 1: Sample Data Analysis (30 seconds)

1. Click **"Try Sample Business Data"**
2. Select **"Mini-Mart"**
3. Wait 10-15 seconds
4. ✅ You should see:
   - Business Health Snapshot with 4 color-coded metrics
   - AI Diagnosis text
   - 3 charts (Revenue Trend, Top Products, Category Performance)
   - Download PDF button

### Test 2: File Upload (1 minute)

1. Click **"Upload Your File"** in the navigation
2. Select business type: **Mini-Mart**
3. Upload file: `C:/Users/USER/Documents/h-automate/sample_data/minimart_sales.csv`
4. Wait 12-18 seconds
5. ✅ You should see the same results as Test 1

### Test 3: Smart Operations (30 seconds)

1. Click **"Smart Operations"** in the navigation
2. Enter problem: `Customers buy once but rarely return`
3. Select business type: **Mini-Mart**
4. Click **"Analyze Problem"**
5. Wait 8-12 seconds
6. ✅ You should see:
   - Situation Summary
   - Likely Causes (3-5 cards)
   - Recommended Actions with difficulty badges
   - Workflow timeline
   - Expected Outcome

---

## 🎯 What to Test Next

Follow the comprehensive **TESTING_GUIDE.md** for:
- All 5 business types
- Mobile responsiveness (360px width)
- Error states
- PDF generation
- All acceptance criteria

---

## 🐛 Common Issues

### Issue: "GROQ_API_KEY not found"
**Solution:** Your `.env` file is already created with the API key. Make sure you're running the backend from the correct directory.

### Issue: "Module not found" errors
**Solution:** Make sure you activated the virtual environment:
```bash
venv\Scripts\activate
```

### Issue: Frontend can't connect to backend
**Solution:** Make sure backend is running on port 8000. Check the terminal for errors.

### Issue: CORS errors in browser console
**Solution:** This is normal if backend isn't running. Start the backend server first.

### Issue: Charts not displaying
**Solution:** Recharts will be installed when you run `npm install`. If issues persist, run:
```bash
cd frontend
npm install recharts
```

---

## 📊 Expected Results

### Business Health Snapshot
You should see 4 metrics with scores:
- Revenue Stability: XX/100
- Customer Activity: XX/100
- Expense Efficiency: XX/100
- Inventory Health: XX/100

Each metric is color-coded:
- 🟢 Green (75-100): Healthy
- 🟡 Amber (50-74): Moderate
- 🔴 Red (0-49): Needs Attention

### AI Diagnosis
Plain English analysis including:
- Transaction counts and daily averages
- Specific product names
- Weekday vs weekend patterns
- At least one insight the owner likely hasn't noticed
- No jargon (no "KPIs", "synergy", "leverage")

### Charts (Maximum 3)
1. **Revenue Trend** - Line chart showing monthly daily averages
2. **Top Products** - Horizontal bar chart (mobile-friendly)
3. **Category Performance** - Donut chart (max 5 categories + "Other")

### PDF Report
Consultant-style document with:
- Executive Summary
- Business Health Snapshot
- Key Metrics
- AI Diagnosis
- Likely Contributing Factors
- Recommended Actions
- Suggested Automation Workflows
- Important Note

---

## 🎉 Success Criteria

You'll know everything is working when:

✅ Backend starts without errors  
✅ Frontend loads at http://localhost:5173  
✅ Sample data analysis completes in 10-15 seconds  
✅ Health metrics display with color coding  
✅ Charts render correctly  
✅ PDF downloads successfully  
✅ No console errors in browser  
✅ Mobile view works (resize browser to 360px width)  

---

## 📚 Next Steps

1. **Test all 5 business types:**
   - Mini-Mart ✅
   - Pharmacy
   - POS Agent
   - Restaurant
   - Fashion Store

2. **Test mobile responsiveness:**
   - Open browser DevTools (F12)
   - Toggle device toolbar
   - Set width to 360px
   - Test all features

3. **Test error states:**
   - Upload wrong file type (.txt)
   - Upload file with missing columns
   - Stop backend and try analysis

4. **Review full testing guide:**
   - See `TESTING_GUIDE.md` for complete checklist

5. **Deploy to production:**
   - See `README.md` for deployment instructions

---

## 🆘 Need Help?

1. **Check the logs:**
   - Backend: Look at the terminal running uvicorn
   - Frontend: Open browser DevTools (F12) → Console tab

2. **Review documentation:**
   - `README.md` - Full setup guide
   - `TESTING_GUIDE.md` - Complete testing checklist
   - `IMPLEMENTATION_SUMMARY.md` - Technical overview

3. **Common fixes:**
   - Restart both servers
   - Clear browser cache
   - Check .env file exists and has API key
   - Verify you're in the correct directory

---

## ⏱️ Time Estimates

- **First-time setup:** 5-10 minutes
- **Subsequent starts:** 1 minute (just start both servers)
- **Complete testing:** 1-2 hours
- **Production deployment:** 30-60 minutes

---

**Ready to launch!** 🚀

Your H-Automate application is fully implemented and ready for testing.
All files are at: `C:/Users/USER/Documents/h-automate/`