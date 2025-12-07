# Example Resume for Testing

This directory contains example resume files for testing InternHunt v6.

## Sample Resume Text

The file `sample_resume.txt` contains a sample resume with various technical skills that can be used for testing the resume parser.

## Creating a PDF Resume for Testing

To test the PDF parsing functionality, you need to convert the text resume to PDF format. Here are several methods:

### Method 1: Using Online Converters

1. Open `sample_resume.txt` in a text editor
2. Copy the content
3. Visit any online text-to-PDF converter:
   - https://www.text2pdf.com/
   - https://www.online-convert.com/
   - https://smallpdf.com/
4. Paste the content and convert to PDF
5. Save as `sample_resume.pdf` in this directory

### Method 2: Using Microsoft Word / Google Docs

1. Open `sample_resume.txt` in a text editor
2. Copy the content
3. Paste into Microsoft Word or Google Docs
4. Format as desired (optional)
5. Export/Save as PDF
6. Save as `sample_resume.pdf` in this directory

### Method 3: Using Python (if you have reportlab installed)

```bash
pip install reportlab
python create_sample_pdf.py
```

### Method 4: Using LibreOffice (Linux/Mac/Windows)

1. Open LibreOffice Writer
2. Open `sample_resume.txt`
3. File → Export as PDF
4. Save as `sample_resume.pdf`

## Testing with the Sample Resume

Once you have created `sample_resume.pdf`, test it with InternHunt:

```bash
# From the project root directory
python internhunt.py examples/sample_resume.pdf
```

Expected behavior:
- The system should extract 20-30 skills from the resume
- Skills should include: Python, Java, JavaScript, Machine Learning, TensorFlow, React, etc.
- These skills will be used to score internship listings

## Skills in Sample Resume

The sample resume includes skills from multiple categories:

**Programming Languages:**
- Python, Java, JavaScript, C++, SQL

**Web Development:**
- React, Node.js, Express.js, Django, Flask, HTML, CSS

**Machine Learning & AI:**
- TensorFlow, PyTorch, Scikit-learn, Pandas, NumPy, Machine Learning, Deep Learning, NLP

**Databases:**
- PostgreSQL, MongoDB, Redis, MySQL

**Cloud & DevOps:**
- AWS, Docker, Kubernetes, Git, Linux

**Tools:**
- VS Code, Jupyter Notebook, Postman, JIRA

This diverse skill set allows for comprehensive testing of the skill matching algorithm.

## Creating Your Own Test Resume

To create your own test resume:

1. Copy `sample_resume.txt` as a template
2. Modify with your own information
3. Ensure you include technical skills from the skill library
4. Convert to PDF using any of the methods above
5. Test with InternHunt

## Notes

- The resume parser works best with text-based PDFs (not scanned images)
- Ensure your PDF is not password-protected or encrypted
- The parser extracts skills using semantic similarity, so exact keyword matches are not required
- Skills are matched against the predefined skill library in `src/skill_library.py`
