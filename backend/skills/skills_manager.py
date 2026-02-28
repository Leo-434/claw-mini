import os
import re

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SKILLS_DIR = os.path.join(PROJECT_ROOT, "backend", "skills")
SNAPSHOT_FILE = os.path.join(SKILLS_DIR, "SKILLS_SNAPSHOT.md")

class SkillsManager:
    @staticmethod
    def _parse_yaml_frontmatter(content: str) -> dict:
        """Parses simple YAML frontmatter to extract name and description."""
        metadata = {}
        # Match --- ... --- at the start
        match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if match:
            lines = match.group(1).split('\n')
            for line in lines:
                if ':' in line:
                    key, val = line.split(':', 1)
                    metadata[key.strip()] = val.strip().strip("'\"")
        return metadata

    @classmethod
    def generate_snapshot(cls) -> str:
        """Scans the skills directory and generates the XML SKILLS_SNAPSHOT.md file."""
        skills_xml = []
        
        # Add a strong system prompt directive to stop the agent from using `ls` to check its skills
        skills_xml.append("### SYSTEM DIRECTIVE: YOUR SKILLS SOURCE OF TRUTH ###")
        skills_xml.append("The following `<available_skills>` block is the **ONLY** source of truth for your currently available skills.")
        skills_xml.append("Do NOT use terminal commands (like `ls`) or code to search the file system to check what skills you have.")
        skills_xml.append("If a skill is listed below, you have it. If it is NOT listed below, you DO NOT have it.")
        skills_xml.append("")
        
        skills_xml.append("<available_skills>")
        
        if not os.path.exists(SKILLS_DIR):
            os.makedirs(SKILLS_DIR, exist_ok=True)
            
        # Scan subdirectories for SKILL.md
        for item in os.listdir(SKILLS_DIR):
            item_path = os.path.join(SKILLS_DIR, item)
            if os.path.isdir(item_path):
                skill_file = os.path.join(item_path, "SKILL.md")
                if os.path.exists(skill_file):
                    with open(skill_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    meta = cls._parse_yaml_frontmatter(content)
                    
                    # Fallback if no frontmatter found
                    name = meta.get('name', item)
                    desc = meta.get('description', 'No description provided.')
                    
                    # Location must be a relative path standard to the project
                    relative_location = f"./backend/skills/{item}/SKILL.md"
                    
                    xml_block = f"""  <skill>
    <name>{name}</name>
    <description>{desc}</description>
    <location>{relative_location}</location>
  </skill>"""
                    skills_xml.append(xml_block)
                    
        skills_xml.append("</available_skills>")
        snapshot_content = "\n".join(skills_xml)
        
        # Write to SKILLS_SNAPSHOT.md
        with open(SNAPSHOT_FILE, 'w', encoding='utf-8') as f:
            f.write(snapshot_content)
            
        return snapshot_content

if __name__ == "__main__":
    snapshot = SkillsManager.generate_snapshot()
    print("Generated SKILLS_SNAPSHOT.md:\n")
    print(snapshot)
