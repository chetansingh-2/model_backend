from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_caching import Cache
from groq import Groq
import os
import json

os.environ["GROQ_API_KEY"] = "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"

client = Groq()
app = Flask(__name__)
CORS(app)

# Configure caching
# app.config['CACHE_TYPE'] = 'simple'
cache = Cache(app)


def save_json(data, filename):
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
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
    return int(response.choices[0].message.content.strip())


@app.route('/predict', methods=['POST'])
# @cache.cached(timeout=3600, query_string=True)
def predict():
    data = request.json
    candidate_data = data['candidate_data']

    scores = {}
    divisions = [
        "Colombo Central", "Borella", "Colombo East", "Colombo West", "Dehiwala",
        "Ratmalana", "Kolonnawa", "Kotte", "Kaduwela", "Avissawella",
        "Homagama", "Maharagama", "Kesbewa", "Moratuwa"
    ]
    division_scores = {}
    demographic_alignment_score = None
    community_engagement_score = None
    support_index = None

    for division in divisions:
        print(f"\nCalculating scores for {division}...")

        scores = {}
        for category in ["Political", "Economic", "Social", "Technological", "Environmental", "Legal"]:
            scores[category] = get_pestel_score(candidate_data, category)
            print(f"{category} score: {scores[category]}")

        demographic_alignment_score = get_score(candidate_data, f"demographic alignment in {division}")
        community_engagement_score = get_score(candidate_data, f"community engagement in {division}")

        print(f"Demographic Alignment Score ({division}): {demographic_alignment_score}")
        print(f"Community Engagement Score ({division}): {community_engagement_score}")

        pestel_total = sum(scores.values())
        pestel_weighted_avg = pestel_total / len(scores)

        support_index = (int(pestel_weighted_avg) * 0.75) + (int(demographic_alignment_score) * 0.125) + (
                int(community_engagement_score) * 0.125)

        division_scores[division] = {
            "pestel_scores": scores,
            "demographic_alignment_score": demographic_alignment_score,
            "community_engagement_score": community_engagement_score,
            "support_index": support_index
        }

        print(f"Support Index for {division}: {support_index:.2f}")

    final_si_score = sum([division_scores[division]["support_index"] for division in divisions]) / len(divisions)
    print(f"\nFinal Aggregate Support Index for Colombo: {final_si_score:.2f}")
    save_json({
        "division_scores": division_scores,
        "final_si_score": final_si_score
    }, 'output.json')

    return jsonify({
        "division_scores": division_scores,
        "final_si_score": final_si_score
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
