from openai import OpenAI

client = OpenAI()

def explain_diagnosis(diagnosis, observations):
    prompt = f"""
    Observations: {observations}
    Diagnosis: {diagnosis}

    Explain in simple engineering language.
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content