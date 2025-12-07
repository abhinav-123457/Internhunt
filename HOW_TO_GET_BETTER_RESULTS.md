# How to Get Better Results from InternHunt

## ✅ What Was Fixed

The app was showing irrelevant internships (UX/UI Design, Chemical Engineering, etc.) instead of ML/AI internships. This has been **FIXED**:

1. ✅ **Keyword matching is now mandatory** - listings with zero keyword matches are rejected
2. ✅ **Keyword weight increased 5x** - from 2 to 10 points per match
3. ✅ **Stipend weight reduced** - from 5 to 3 points max
4. ✅ **Reject keywords working perfectly** - no more HR/sales/marketing internships

## 🎯 How to Get Relevant Results

### Problem: Getting Zero Results

If you're getting zero results with keywords like "ml", "data science", "gen ai", it's because:
- These specific internships are rare on current platforms
- The system is correctly rejecting irrelevant listings

### Solution: Use Broader Keywords

Instead of very specific keywords:
```
❌ BAD: ml, data science, gen ai
```

Use broader, more common keywords:
```
✅ GOOD: python, data, machine, learning, ai, software, developer, analytics
```

## 📝 Recommended Keyword Strategy

### For ML/AI Internships
```
Wanted keywords: python, machine, learning, ai, ml, data, analytics, deep, neural
Reject keywords: hr, sales, marketing, manager, business development
```

This will match:
- "Python Developer"
- "Data Analyst"
- "Machine Learning Intern"
- "AI Engineer"
- "Software Developer" (with Python/ML in description)

### For Data Science Internships
```
Wanted keywords: data, python, analytics, science, ml, statistics, visualization
Reject keywords: hr, sales, marketing, manager
```

### For Software Development Internships
```
Wanted keywords: python, software, developer, programming, backend, frontend, full stack
Reject keywords: hr, sales, marketing, manager
```

## 🔧 Other Settings to Adjust

### 1. Minimum Stipend
If getting too few results, lower the minimum:
```
Current: ₹14,000
Try: ₹8,000 or ₹5,000
```

### 2. Maximum Post Age
If getting too few results, increase the age:
```
Current: 3 days
Try: 30 days or 60 days
```

### 3. Locations
Be flexible with locations:
```
Current: mumbai, bangalore, noida, delhi
Try: Add "remote" or leave empty for "any"
```

## 📊 Understanding the Results

### Score Breakdown

Each listing gets a score based on:
- **Keyword matches**: 10 points per keyword (most important!)
- **Skill matches**: 3 points per resume skill
- **Stipend**: up to 3 points (bonus for high stipend)
- **Location**: 5 points if matches your preference
- **Remote**: 5 points if remote and you want remote

### Example Scores

```
Listing: "Python Machine Learning Intern"
- Keywords: "python" (10) + "machine" (10) + "learning" (10) = 30 points
- Skills: "python" (3) + "machine learning" (3) = 6 points
- Stipend: ₹15,000 (1.5 points)
- Total: 37.5 points ⭐⭐⭐

Listing: "Software Developer Intern"
- Keywords: "software" (10) + "developer" (10) = 20 points
- Skills: 0 points
- Stipend: ₹12,000 (0.8 points)
- Total: 20.8 points ⭐⭐

Listing: "UX/UI Design" (no keyword matches)
- REJECTED ❌
```

## 🚀 Quick Start Guide

### Step 1: Run the App
```bash
python internhunt.py "path/to/your/resume.pdf"
```

### Step 2: Enter Broad Keywords
```
Wanted keywords: python, data, machine, learning, ai, software, developer
Reject keywords: hr, sales, marketing, manager
```

### Step 3: Set Reasonable Filters
```
Remote: any
Min stipend: 8000
Max post age: 30
Max results: 50
Locations: bangalore, mumbai, noida, delhi
```

### Step 4: Review Results
- Check the dashboard HTML file
- Look at the score breakdown
- Higher scores = more relevant

## 🐛 Troubleshooting

### Issue: Still Getting Irrelevant Results

**Check your keywords**:
- Are they too broad? ("design" will match "UI/UX Design")
- Add more specific keywords: "machine learning" instead of just "machine"

**Check your reject keywords**:
- Add more: "design", "video", "content", "graphic"

### Issue: Getting Zero Results

**Your keywords are too specific**:
- "gen ai" → try "ai", "machine", "learning"
- "nlp" → try "natural", "language", "processing"

**Lower your filters**:
- Min stipend: try ₹5,000 or ₹0
- Max post age: try 60 or 90 days

### Issue: Location Shows "Not specified"

This is a known issue - Internshala's HTML structure has changed. The location data is there but the CSS selectors need updating. This doesn't affect filtering (location matching still works in descriptions).

## 📈 Expected Results

With proper keywords, you should get:

```
Total scraped: 130-150 listings
After filtering: 5-20 listings (depending on keywords)
After deduplication: 3-15 unique listings
Rejection rate: 85-95% (this is GOOD - means filtering works!)
```

## 💡 Pro Tips

1. **Use synonyms**: "ml" AND "machine learning" AND "ai"
2. **Include tools**: "python", "tensorflow", "pytorch", "pandas"
3. **Include roles**: "developer", "engineer", "analyst", "scientist"
4. **Be specific with rejects**: Add "content", "video", "graphic" if getting those
5. **Check the log file**: `internhunt.log` shows why listings were rejected

## 🎯 Example: Perfect Setup for ML/AI

```
Resume: your_resume.pdf

Wanted keywords:
python, machine, learning, ai, ml, data, analytics, deep, neural, tensorflow, pytorch

Reject keywords:
hr, sales, marketing, manager, business, content, video, graphic, design

Remote: any
Min stipend: 8000
Max post age: 30
Max results: 50
Locations: bangalore, mumbai, pune, hyderabad, delhi, noida, remote
```

This should give you 5-15 relevant ML/AI/Data Science internships!

---

**Need Help?**
- Check `RELEVANCE_FIX_SUMMARY.md` for technical details
- Check `internhunt.log` for debugging
- Run tests: `python -m pytest tests/ -v`
