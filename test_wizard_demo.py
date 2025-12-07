"""
Demo script to test the preference wizard interactively.
Run this to see the wizard in action.
"""

from src.preference_wizard import PreferenceWizard

def main():
    wizard = PreferenceWizard()
    
    # Example with resume skills
    resume_skills = ['Python', 'Machine Learning', 'Django', 'PostgreSQL']
    
    print("Testing Preference Wizard")
    print("=" * 60)
    print("\nThis is a demo. You can test the wizard with sample inputs.")
    print("Try entering invalid values to see validation in action!\n")
    
    try:
        preferences = wizard.run_wizard(resume_skills=resume_skills)
        
        print("\n" + "=" * 60)
        print("Collected Preferences:")
        print("=" * 60)
        print(f"Wanted Keywords: {preferences.wanted_keywords}")
        print(f"Reject Keywords: {preferences.reject_keywords}")
        print(f"Remote Preference: {preferences.remote_preference}")
        print(f"Min Stipend: ₹{preferences.min_stipend}")
        print(f"Max Post Age: {preferences.max_post_age_days} days")
        print(f"Max Results: {preferences.max_results}")
        print(f"Preferred Locations: {preferences.preferred_locations}")
        print(f"Resume Skills: {len(preferences.resume_skills)} skills")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye!")

if __name__ == "__main__":
    main()
