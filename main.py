from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os

os.environ["GROQ_API_KEY"] = os.getenv("API_KEY")

client = Groq()

app = Flask(__name__)
CORS(app)  # Enable CORS for all origins

def generate_content(prompt):
    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.1-8b-instant",
        temperature=0.001
    )
    return response

def get_pestel_score(candidate_data, category):
    prompt = f"""
    You are a political analyst with expertise in the PESTEL framework. Given the following candidate data, evaluate how closely they are related to the {category} aspect of PESTEL on a scale of 1 to 100. Consider their background, experience, political positions, and focus areas. Provide only the numerical score.

    Candidate Data: {candidate_data}
    """
    response = generate_content(prompt)
    return int(response.choices[0].message.content.strip())

def get_score(candidate_data, area):
    prompt = f"""
    You are a political analyst. Given the following candidate data, evaluate how the candidate performs in {area} on a scale of 1 to 100. Consider their background, experience, political positions, and focus areas. Provide only the numerical score.

    Candidate Data: {candidate_data}
    """
    response = generate_content(prompt)
    return response.choices[0].message.content.strip()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    candidate_data = data['candidate_data']

    scores = {}
    for category in ["Political", "Economic", "Social", "Technological", "Environmental", "Legal"]:
        scores[category] = get_pestel_score(candidate_data, category)

    demographic_alignment_score = get_score(candidate_data, "demographic alignment in his constituency Colombo")
    community_engagement_score = get_score(candidate_data, "community engagement in his constituency Colombo")

    pestel_total = sum(scores.values())
    pestel_weighted_avg = pestel_total / len(scores)

    support_index = (pestel_weighted_avg * 0.75) + (int(demographic_alignment_score) * 0.125) + (int(community_engagement_score) * 0.125)

    return jsonify({
        "scores": scores,
        "demographic_alignment_score": demographic_alignment_score,
        "community_engagement_score": community_engagement_score,
        "support_index": support_index
    })

if __name__ == '__main__':
    app.run(debug=True)
