from langchain_core.prompts import ChatPromptTemplate

prompt_template = """
    You are an expert medical documentation assistant. Your job is to structure rough patient notes.
    Use the provided medical reference context to guide your extraction.
    
    Context from Medical Reference Documents:
    {context}
    
    Rough Patient Notes:
    {notes}
    
    INSTRUCTIONS:
    You must return ONLY a valid JSON object. Do not include any markdown formatting or conversational text.
    The JSON object must have exactly these three keys:
    
    1. "structured_summary": A clear, professional summary of the visit (string).
    
    2. "extracted_details": A JSON object containing key-value pairs of the extracted medical data. 
       Example format: {{"Patient Name": "John Doe", "Age": 45, "Blood Pressure": "120/80", "Medications": "Albuterol"}}
       
    3. "missing_fields": A list of strings. Compare the 'Rough Patient Notes' against standard required fields. 
       STRICT RULES FOR MISSING FIELDS:
       - ONLY list a field if it is completely absent from the notes.
       - NEVER include explanations like "(already included)" or "(for completeness)". 
       - If no required fields are missing, you MUST return exactly an empty list: []
    """
prompt = ChatPromptTemplate.from_template(prompt_template)