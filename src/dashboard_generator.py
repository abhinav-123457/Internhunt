"""
Dashboard Generator Module

Creates styled HTML dashboard with job cards for internship listings.
Implements responsive CSS Grid layout with proper formatting and accessibility.
"""

import html
import logging
from pathlib import Path
from datetime import datetime
from typing import List

from .scoring_engine import ScoredListing
from .preference_wizard import UserPreferences
from .logging_config import get_logger


logger = get_logger(__name__)


class DashboardGenerator:
    """
    Generates HTML dashboard with styled job cards.
    
    Features:
    - Valid HTML5 structure
    - Responsive CSS Grid layout
    - Proper stipend formatting with ₹ symbol
    - Links open in new tabs
    - Timestamped filenames
    - Special character escaping
    """
    
    def __init__(self, output_dir: Path = Path("output")):
        """
        Initialize dashboard generator.
        
        Args:
            output_dir: Directory to save generated HTML files
        """
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized DashboardGenerator with output directory: {output_dir}")
    
    def generate(self, listings: List[ScoredListing], preferences: UserPreferences) -> Path:
        """
        Generate HTML dashboard and return file path.
        
        Args:
            listings: List of scored listings to display
            preferences: User preferences for summary information
            
        Returns:
            Path: Path to generated HTML file
        """
        logger.info(f"Generating dashboard for {len(listings)} listings")
        
        # Generate HTML content
        html_content = self._generate_html(listings, preferences)
        
        # Generate timestamped filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"internhunt_results_{timestamp}.html"
        filepath = self.output_dir / filename
        
        # Write to file
        try:
            filepath.write_text(html_content, encoding='utf-8')
            logger.info(f"Dashboard saved to: {filepath}")
        except Exception as e:
            logger.error(f"Failed to write dashboard to {filepath}: {e}")
            raise
        
        return filepath
    
    def _generate_html(self, listings: List[ScoredListing], preferences: UserPreferences) -> str:
        """
        Generate complete HTML document.
        
        Args:
            listings: List of scored listings
            preferences: User preferences
            
        Returns:
            str: Complete HTML document
        """
        # Generate job cards
        job_cards_html = ""
        for scored_listing in listings:
            job_cards_html += self._generate_job_card(scored_listing)
        
        # Handle empty results
        if not listings:
            job_cards_html = '''
            <div class="col-span-full flex flex-col items-center justify-center py-16">
                <div class="text-6xl mb-4">🔍</div>
                <h3 class="text-2xl font-semibold text-gray-300 mb-2">No internships found</h3>
                <p class="text-gray-500">Try adjusting your search criteria</p>
            </div>
            '''
        
        # Build complete HTML with Tailwind CSS
        html_doc = f"""<!DOCTYPE html>
<html lang="en" class="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>InternHunt Results - Dark Mode</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {{
            darkMode: 'class',
            theme: {{
                extend: {{
                    colors: {{
                        border: "hsl(240 3.7% 15.9%)",
                        input: "hsl(240 3.7% 15.9%)",
                        ring: "hsl(240 4.9% 83.9%)",
                        background: "hsl(240 10% 3.9%)",
                        foreground: "hsl(0 0% 98%)",
                        primary: {{
                            DEFAULT: "hsl(263 70% 50%)",
                            foreground: "hsl(0 0% 98%)",
                        }},
                        secondary: {{
                            DEFAULT: "hsl(240 3.7% 15.9%)",
                            foreground: "hsl(0 0% 98%)",
                        }},
                        muted: {{
                            DEFAULT: "hsl(240 3.7% 15.9%)",
                            foreground: "hsl(240 5% 64.9%)",
                        }},
                        accent: {{
                            DEFAULT: "hsl(240 3.7% 15.9%)",
                            foreground: "hsl(0 0% 98%)",
                        }},
                        card: {{
                            DEFAULT: "hsl(240 10% 8%)",
                            foreground: "hsl(0 0% 98%)",
                        }},
                    }},
                    borderRadius: {{
                        lg: "0.5rem",
                        md: "calc(0.5rem - 2px)",
                        sm: "calc(0.5rem - 4px)",
                    }},
                }}
            }}
        }}
    </script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        
        .gradient-bg {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        }}
        
        .card-hover {{
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }}
        
        .card-hover:hover {{
            transform: translateY(-4px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2);
        }}
        
        .score-badge {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        .shimmer {{
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.05), transparent);
            animation: shimmer 2s infinite;
        }}
        
        @keyframes shimmer {{
            0% {{ transform: translateX(-100%); }}
            100% {{ transform: translateX(100%); }}
        }}
        
        .fade-in {{
            animation: fadeIn 0.5s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body class="bg-background text-foreground min-h-screen">
    <!-- Header -->
    <header class="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div class="container mx-auto px-4 py-6">
            <div class="flex flex-col md:flex-row items-center justify-between gap-4">
                <div class="flex items-center gap-3">
                    <div class="text-4xl">🎯</div>
                    <div>
                        <h1 class="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
                            InternHunt Results
                        </h1>
                        <p class="text-sm text-muted-foreground">Your personalized internship matches</p>
                    </div>
                </div>
                <div class="flex gap-4">
                    <div class="bg-secondary/50 backdrop-blur-sm px-4 py-2 rounded-lg border border-border">
                        <div class="text-xs text-muted-foreground">Total Listings</div>
                        <div class="text-2xl font-bold text-primary">{len(listings)}</div>
                    </div>
                    <div class="bg-secondary/50 backdrop-blur-sm px-4 py-2 rounded-lg border border-border">
                        <div class="text-xs text-muted-foreground">Max Results</div>
                        <div class="text-2xl font-bold text-primary">{preferences.max_results}</div>
                    </div>
                </div>
            </div>
        </div>
    </header>

    <!-- Main Content -->
    <main class="container mx-auto px-4 py-8">
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
{job_cards_html}
        </div>
    </main>

    <!-- Footer -->
    <footer class="border-t border-border mt-12 py-8">
        <div class="container mx-auto px-4 text-center">
            <p class="text-sm text-muted-foreground">
                Generated by <span class="font-semibold text-primary">InternHunt v6</span> • 
                {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
            </p>
            <p class="text-xs text-muted-foreground mt-2">
                Built with ❤️ for job seekers
            </p>
        </div>
    </footer>
</body>
</html>"""
        
        return html_doc
    
    def _generate_css(self) -> str:
        """
        Generate CSS styles for dashboard.
        Note: This method is kept for backward compatibility but is no longer used
        as we now use Tailwind CSS directly in the HTML.
        
        Returns:
            str: Empty string (CSS now handled by Tailwind)
        """
        return ""
    
    def _generate_job_card(self, scored_listing: ScoredListing) -> str:
        """
        Generate HTML for a single job card with Tailwind CSS and shadcn/ui styling.
        
        Args:
            scored_listing: ScoredListing to render
            
        Returns:
            str: HTML for job card
        """
        listing = scored_listing.listing
        
        # Escape HTML special characters
        title = html.escape(listing.title)
        company = html.escape(listing.company)
        location = html.escape(listing.location)
        url = html.escape(listing.url)
        platform = html.escape(listing.source_platform)
        
        # Format stipend
        stipend_display = self._format_stipend(listing.stipend)
        
        # Simple gradient color based on score (no labels or icons)
        if scored_listing.score >= 15:
            score_color = "from-green-400 to-emerald-500"
        elif scored_listing.score >= 10:
            score_color = "from-blue-400 to-purple-500"
        else:
            score_color = "from-purple-400 to-pink-500"
        
        card_html = f"""            <div class="bg-card border border-border rounded-lg p-6 card-hover fade-in relative overflow-hidden group">
                <!-- Shimmer effect on hover -->
                <div class="absolute inset-0 shimmer opacity-0 group-hover:opacity-100"></div>
                
                <!-- No score badge displayed -->
                
                <!-- Content -->
                <div class="relative z-10">
                    <!-- Title -->
                    <h2 class="text-xl font-bold text-foreground mb-2 pr-20 line-clamp-2 group-hover:text-primary transition-colors">
                        {title}
                    </h2>
                    
                    <!-- Company -->
                    <div class="flex items-center gap-2 mb-4">
                        <span class="text-2xl">🏢</span>
                        <p class="text-lg font-semibold text-primary">
                            {company}
                        </p>
                    </div>
                    
                    <!-- Stipend -->
                    <div class="flex items-center gap-2 mb-3">
                        <span class="text-2xl">💰</span>
                        <p class="text-lg font-bold text-green-400">
                            {stipend_display}
                        </p>
                    </div>
                    
                    <!-- Location -->
                    <div class="flex items-center gap-2 mb-4">
                        <span class="text-xl">📍</span>
                        <p class="text-sm text-muted-foreground">
                            {location}
                        </p>
                    </div>
                    
                    <!-- Platform Badge -->
                    <div class="mb-4">
                        <span class="inline-flex items-center gap-1 bg-secondary/50 text-muted-foreground px-3 py-1 rounded-full text-xs font-medium border border-border">
                            <span>🔗</span>
                            {platform}
                        </span>
                    </div>
                    
                    <!-- Apply Button -->
                    <a href="{url}" 
                       target="_blank" 
                       rel="noopener noreferrer" 
                       class="inline-flex items-center justify-center w-full bg-gradient-to-r {score_color} text-white font-semibold py-3 px-6 rounded-lg hover:opacity-90 transition-all duration-300 shadow-lg hover:shadow-xl group">
                        <span>View Details</span>
                        <svg class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6"></path>
                        </svg>
                    </a>
                </div>
            </div>
"""
        
        return card_html
    
    def _format_stipend(self, stipend: int | None) -> str:
        """
        Format stipend for display with ₹ symbol and separators.
        
        Args:
            stipend: Stipend amount in INR (or None)
            
        Returns:
            str: Formatted stipend string
        """
        if stipend is None:
            return "Stipend not specified"
        
        if stipend == 0:
            return "Unpaid"
        
        # Format with Indian numbering system (lakhs and thousands)
        # For simplicity, use comma separators
        formatted = f"₹{stipend:,}/month"
        
        return formatted
