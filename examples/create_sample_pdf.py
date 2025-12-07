#!/usr/bin/env python3
"""
Script to create a sample PDF resume for testing InternHunt v6.

This script converts the sample_resume.txt file into a PDF format
that can be used to test the resume parsing functionality.

Requirements:
    pip install reportlab

Usage:
    python create_sample_pdf.py
"""

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
except ImportError:
    print("Error: reportlab is not installed.")
    print("Please install it using: pip install reportlab")
    exit(1)

from pathlib import Path


def create_sample_pdf():
    """Create a sample PDF resume from the text file."""
    
    # Read the sample resume text
    text_file = Path(__file__).parent / "sample_resume.txt"
    
    if not text_file.exists():
        print(f"Error: {text_file} not found!")
        return
    
    with open(text_file, 'r', encoding='utf-8') as f:
        resume_text = f.read()
    
    # Output PDF path
    pdf_file = Path(__file__).parent / "sample_resume.pdf"
    
    # Create PDF document
    doc = SimpleDocTemplate(
        str(pdf_file),
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='#2C3E50',
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=14,
        textColor='#34495E',
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#2C3E50',
        spaceAfter=6,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor='#2C3E50',
        spaceAfter=6,
        alignment=TA_LEFT,
        fontName='Helvetica'
    )
    
    # Parse the resume text and create PDF elements
    lines = resume_text.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        
        if not line:
            # Add small spacer for empty lines
            elements.append(Spacer(1, 0.1*inch))
            continue
        
        # Detect section headers (all caps or followed by dashes)
        if i + 1 < len(lines) and lines[i + 1].strip().startswith('---'):
            # This is a section header
            elements.append(Paragraph(line, heading_style))
            continue
        
        if line.startswith('---'):
            # Skip the dash lines
            continue
        
        # First line is the name (title)
        if i == 0:
            elements.append(Paragraph(line, title_style))
            continue
        
        # Second line is the subtitle
        if i == 1:
            elements.append(Paragraph(line, subtitle_style))
            elements.append(Spacer(1, 0.2*inch))
            continue
        
        # Regular body text
        # Escape special characters for reportlab
        line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        elements.append(Paragraph(line, body_style))
    
    # Build PDF
    try:
        doc.build(elements)
        print(f"✓ Successfully created: {pdf_file}")
        print(f"\nYou can now test InternHunt with:")
        print(f"  python internhunt.py {pdf_file}")
    except Exception as e:
        print(f"Error creating PDF: {e}")


if __name__ == "__main__":
    print("Creating sample PDF resume...")
    create_sample_pdf()
