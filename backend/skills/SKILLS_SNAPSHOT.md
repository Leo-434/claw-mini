### SYSTEM DIRECTIVE: YOUR SKILLS SOURCE OF TRUTH ###
The following `<available_skills>` block is the **ONLY** source of truth for your currently available skills.
Do NOT use terminal commands (like `ls`) or code to search the file system to check what skills you have.
If a skill is listed below, you have it. If it is NOT listed below, you DO NOT have it.

<available_skills>
  <skill>
    <name>get_weather</name>
    <description>获取指定城市的实时天气信息</description>
    <location>./backend/skills/get_weather/SKILL.md</location>
  </skill>
  <skill>
    <name>pdf</name>
    <description>Use this skill whenever the user wants to do anything with PDF files. This includes reading or extracting text/tables from PDFs, combining or merging multiple PDFs into one, splitting PDFs apart, rotating pages, adding watermarks, creating new PDFs, filling PDF forms, encrypting/decrypting PDFs, extracting images, and OCR on scanned PDFs to make them searchable. If the user mentions a .pdf file or asks to produce one, use this skill.</description>
    <location>./backend/skills/pdf/SKILL.md</location>
  </skill>
</available_skills>