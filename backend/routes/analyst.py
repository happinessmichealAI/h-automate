"""
H-Automate — analyst.py
Business Insights API route — handles file upload and analysis.

Endpoint: POST /api/analyze
"""

import os
import base64
import pandas as pd
from io import BytesIO
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel
from typing import Optional

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from groq_client import get_diagnosis
from utils.data_cleaner import clean_and_summarize


router = APIRouter()


# ─────────────────────────────────────────────
# REQUEST/RESPONSE MODELS
# ─────────────────────────────────────────────
class AnalyzeRequest(BaseModel):
    """Request model for file analysis"""
    file_content: Optional[str] = None  # base64 encoded file
    filename: Optional[str] = None
    business_type: str
    sample_type: Optional[str] = None  # For demo mode


class AnalyzeResponse(BaseModel):
    """Response model for analysis results"""
    status: str
    diagnosis: str
    metrics: dict
    missing_fields: list
    warnings: list


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────
def load_sample_data(business_type: str) -> pd.DataFrame:
    """Load sample CSV data for demo mode"""
    sample_files = {
        "mini-mart": "minimart_sales.csv",
        "pharmacy": "pharmacy_sales.csv",
        "pos-agent": "pos_agent.csv",
        "restaurant": "restaurant_sales.csv",
        "fashion-store": "fashion_sales.csv",
    }
    
    if business_type not in sample_files:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid business type: {business_type}"
        )
    
    sample_file = sample_files[business_type]
    sample_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "sample_data",
        sample_file
    )
    
    if not os.path.exists(sample_path):
        raise HTTPException(
            status_code=404,
            detail=f"Sample data file not found: {sample_file}"
        )
    
    try:
        return pd.read_csv(sample_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading sample data: {str(e)}"
        )


def parse_uploaded_file(file_content: str, filename: str) -> pd.DataFrame:
    """Parse base64 encoded CSV or Excel file"""
    try:
        # Decode base64
        file_bytes = base64.b64decode(file_content)
        file_buffer = BytesIO(file_bytes)
        
        # Determine file type and parse
        if filename.endswith('.csv'):
            df = pd.read_csv(file_buffer)
        elif filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_buffer, engine='openpyxl')
        else:
            raise HTTPException(
                status_code=400,
                detail="We couldn't understand this file format. Try CSV or Excel (.xlsx)."
            )
        
        return df
    
    except base64.binascii.Error:
        raise HTTPException(
            status_code=400,
            detail="Invalid file encoding. Please upload a valid file."
        )
    except pd.errors.EmptyDataError:
        raise HTTPException(
            status_code=400,
            detail="This file appears to be empty. Please upload a file with data."
        )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error reading file: {str(e)}"
        )


def validate_business_type(business_type: str) -> str:
    """Validate and normalize business type"""
    valid_types = ["mini-mart", "pharmacy", "pos-agent", "restaurant", "fashion-store"]
    
    business_type = business_type.lower().strip()
    
    if business_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid business type. Must be one of: {', '.join(valid_types)}"
        )
    
    return business_type


# ─────────────────────────────────────────────
# MAIN ANALYSIS ENDPOINT
# ─────────────────────────────────────────────
@router.post("/analyze")
async def analyze_business_data(
    file: Optional[UploadFile] = File(None),
    business_type: str = Form(...),
    sample_type: Optional[str] = Form(None)
):
    """
    Analyze business sales data and return AI-powered diagnosis.
    
    Two modes:
    1. File Upload: Upload CSV/Excel file with sales data
    2. Demo Mode: Use sample data by providing sample_type
    
    Parameters:
        file: Uploaded CSV or Excel file (optional if using demo mode)
        business_type: One of: mini-mart, pharmacy, pos-agent, restaurant, fashion-store
        sample_type: Business type for demo mode (optional)
    
    Returns:
        JSON with diagnosis, metrics, and warnings
    """
    
    # Validate business type
    business_type = validate_business_type(business_type)
    
    # Determine mode: sample data or file upload
    if sample_type:
        # Demo mode — load sample data
        sample_type = validate_business_type(sample_type)
        try:
            df = load_sample_data(sample_type)
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "status": "error",
                    "error_type": "sample_data_not_found",
                    "message": e.detail
                }
            )
    
    elif file:
        # File upload mode
        try:
            # Read file content
            file_content = await file.read()
            
            # Check file size (max 5MB)
            if len(file_content) > 5 * 1024 * 1024:
                raise HTTPException(
                    status_code=400,
                    detail="File too large. Maximum size is 5MB."
                )
            
            # Parse file
            file_buffer = BytesIO(file_content)
            
            if file.filename.endswith('.csv'):
                df = pd.read_csv(file_buffer)
            elif file.filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_buffer, engine='openpyxl')
            else:
                return JSONResponse(
                    status_code=400,
                    content={
                        "status": "error",
                        "error_type": "wrong_type",
                        "message": "This doesn't look like sales data. Upload a CSV or Excel sales file."
                    }
                )
        
        except pd.errors.EmptyDataError:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "error_type": "unreadable_file",
                    "message": "This file appears to be empty. Please upload a file with data."
                }
            )
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "error_type": "unreadable_file",
                    "message": "We couldn't understand this file format. Try CSV or Excel (.xlsx)."
                }
            )
    
    else:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Either provide a file or specify sample_type for demo mode."
            }
        )
    
    # Step 1: Clean and summarize data
    try:
        result = clean_and_summarize(df, business_type)
        summary_text = result["summary_text"]
        metrics = result["metrics"]
        missing_fields = result["missing_fields"]
        warnings = result["warnings"]
    
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "error_type": "messy_data",
                "message": "Your file may be missing important sales information. We found inconsistent columns or missing values.",
                "details": str(e)
            }
        )
    
    # Step 2: Get AI diagnosis
    try:
        diagnosis = get_diagnosis(business_type, summary_text)
        
        # Check if diagnosis failed
        if diagnosis.startswith("DIAGNOSIS_ERROR"):
            return JSONResponse(
                status_code=503,
                content={
                    "status": "error",
                    "error_type": "ai_unavailable",
                    "message": "Analysis is taking longer than expected. Please try again shortly.",
                    "details": diagnosis
                }
            )
    
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "error",
                "error_type": "ai_unavailable",
                "message": "Analysis is taking longer than expected. Please try again shortly.",
                "details": str(e)
            }
        )
    
    # Step 3: Return successful response
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "diagnosis": diagnosis,
            "metrics": metrics,
            "missing_fields": missing_fields,
            "warnings": warnings,
            "business_type": business_type
        }
    )


# ─────────────────────────────────────────────
# HEALTH CHECK FOR ANALYSIS ROUTE
# ─────────────────────────────────────────────
@router.get("/analyze/health")
def analyze_health():
    """Check if analysis endpoint is ready"""
    return {
        "status": "ok",
        "endpoint": "/api/analyze",
        "methods": ["POST"],
        "sample_data_available": True
    }




# ─────────────────────────────────────────────
# TEXT REPORT DOWNLOAD ENDPOINT
# Temporary solution until WeasyPrint is installed
# ─────────────────────────────────────────────
@router.post("/download-report")
async def download_report(
    diagnosis: str = Form(...),
    metrics: str = Form(...),
    business_type: str = Form(...),
    missing_fields: str = Form("[]"),
    warnings: str = Form("[]")
):
    """
    Generate and download text report from analysis results.
    Temporary solution until WeasyPrint is installed.
    
    Parameters:
        diagnosis: Full diagnosis text from AI
        metrics: JSON string of metrics dict
        business_type: Business type analyzed
        missing_fields: JSON string of missing fields list
        warnings: JSON string of warnings list
    
    Returns:
        Text file as download
    """
    import json
    
    try:
        # Parse JSON strings
        metrics_dict = json.loads(metrics)
        missing_list = json.loads(missing_fields)
        warnings_list = json.loads(warnings)
        
        # Build text report
        date_str = datetime.now().strftime("%B %d, %Y")
        business_name = business_type.replace('-', ' ').title()
        
        report_text = f"""
═══════════════════════════════════════════════════════════
H-AUTOMATE BUSINESS ANALYSIS REPORT
═══════════════════════════════════════════════════════════

Business Type: {business_name}
Report Date: {date_str}
Generated by: H-Automate AI

───────────────────────────────────────────────────────────
DIAGNOSIS
───────────────────────────────────────────────────────────

{diagnosis}

───────────────────────────────────────────────────────────
KEY METRICS
───────────────────────────────────────────────────────────

{json.dumps(metrics_dict, indent=2)}

"""
        
        if warnings_list:
            report_text += "\n───────────────────────────────────────────────────────────\n"
            report_text += "DATA QUALITY NOTES\n"
            report_text += "───────────────────────────────────────────────────────────\n\n"
            for warning in warnings_list:
                report_text += f"• {warning}\n"
        
        report_text += "\n═══════════════════════════════════════════════════════════\n"
        report_text += "© 2026 H-Automate - AI Business Assistant for Nigerian SMEs\n"
        report_text += "═══════════════════════════════════════════════════════════\n"
        
        # Return text file as download
        filename = f"h-automate-report-{business_type}-{datetime.now().strftime('%Y%m%d')}.txt"
        
        return Response(
            content=report_text.encode('utf-8'),
            media_type="text/plain",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    
    except json.JSONDecodeError as e:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": f"Invalid JSON data: {str(e)}"
            }
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": f"Error generating report: {str(e)}"
            }
        )
