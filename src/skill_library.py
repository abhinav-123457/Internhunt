"""
Skill Library Module

Provides predefined technical and professional skills organized by category
for matching against resume content and job listings.
"""

from typing import List, Dict


class SkillLibrary:
    """Central repository of technical and professional skills"""
    
    # Programming Languages
    PROGRAMMING_LANGUAGES = [
        "Python", "Java", "JavaScript", "TypeScript", "C++", "C", "C#",
        "Go", "Rust", "Ruby", "PHP", "Swift", "Kotlin", "Scala",
        "R", "MATLAB", "Perl", "Shell Scripting", "Bash"
    ]
    
    # Machine Learning & AI
    ML_AI = [
        "Machine Learning", "Deep Learning", "Natural Language Processing",
        "Computer Vision", "TensorFlow", "PyTorch", "Keras", "Scikit-learn",
        "Neural Networks", "Reinforcement Learning", "Data Science",
        "Statistical Analysis", "Pandas", "NumPy", "OpenCV"
    ]
    
    # Web Development
    WEB_DEVELOPMENT = [
        "React", "Angular", "Vue.js", "Node.js", "Express.js",
        "Django", "Flask", "FastAPI", "HTML", "CSS", "SASS",
        "Bootstrap", "Tailwind CSS", "jQuery", "REST API",
        "GraphQL", "WebSockets", "Redux", "Next.js"
    ]
    
    # Databases
    DATABASES = [
        "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
        "SQLite", "Oracle", "Microsoft SQL Server", "Cassandra",
        "DynamoDB", "Elasticsearch", "Neo4j"
    ]
    
    # Cloud & DevOps
    CLOUD_DEVOPS = [
        "AWS", "Azure", "Google Cloud Platform", "Docker", "Kubernetes",
        "CI/CD", "Jenkins", "GitLab CI", "GitHub Actions", "Terraform",
        "Ansible", "Linux", "Unix", "Nginx", "Apache"
    ]
    
    # Tools & Technologies
    TOOLS = [
        "Git", "GitHub", "GitLab", "Bitbucket", "JIRA", "Confluence",
        "Postman", "Swagger", "VS Code", "IntelliJ IDEA", "Eclipse",
        "Vim", "Jupyter Notebook"
    ]
    
    # Mobile Development
    MOBILE = [
        "Android", "iOS", "React Native", "Flutter", "Xamarin",
        "Swift UI", "Jetpack Compose"
    ]
    
    # Other Skills
    OTHER = [
        "Agile", "Scrum", "Test-Driven Development", "Unit Testing",
        "Integration Testing", "Debugging", "Problem Solving",
        "Data Structures", "Algorithms", "Object-Oriented Programming",
        "Functional Programming", "Microservices", "System Design",
        "API Development", "Version Control"
    ]
    
    @staticmethod
    def get_all_skills() -> List[str]:
        """
        Returns a flat list of all predefined skills across all categories.
        
        Returns:
            List[str]: Complete list of 50+ skills
        """
        return (
            SkillLibrary.PROGRAMMING_LANGUAGES +
            SkillLibrary.ML_AI +
            SkillLibrary.WEB_DEVELOPMENT +
            SkillLibrary.DATABASES +
            SkillLibrary.CLOUD_DEVOPS +
            SkillLibrary.TOOLS +
            SkillLibrary.MOBILE +
            SkillLibrary.OTHER
        )
    
    @staticmethod
    def get_skill_categories() -> Dict[str, List[str]]:
        """
        Returns skills organized by category for structured access.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping category names to skill lists
        """
        return {
            "Programming Languages": SkillLibrary.PROGRAMMING_LANGUAGES,
            "Machine Learning & AI": SkillLibrary.ML_AI,
            "Web Development": SkillLibrary.WEB_DEVELOPMENT,
            "Databases": SkillLibrary.DATABASES,
            "Cloud & DevOps": SkillLibrary.CLOUD_DEVOPS,
            "Tools & Technologies": SkillLibrary.TOOLS,
            "Mobile Development": SkillLibrary.MOBILE,
            "Other Skills": SkillLibrary.OTHER
        }
    
    @staticmethod
    def get_skill_count() -> int:
        """
        Returns the total number of skills in the library.
        
        Returns:
            int: Total skill count
        """
        return len(SkillLibrary.get_all_skills())
