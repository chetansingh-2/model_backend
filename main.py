# from flask import Flask, request, jsonify
# from flask_cors import CORS
# from groq import Groq
# import os
# import json
# from concurrent.futures import ThreadPoolExecutor
# import re
#
# os.environ["GROQ_API_KEY"] = "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"
# client = Groq()
# app = Flask(__name__)
# CORS(app)
# executor = ThreadPoolExecutor(max_workers=10)
# def save_json(data, filename):
#     with open(filename, 'w') as file:
#         json.dump(data, file, indent=4)
#
# def generate_content(prompt):
#     response = client.chat.completions.create(
#         messages=[{"role": "user", "content": prompt}],
#         model="llama-3.1-8b-instant",
#         temperature=0.001
#     )
#     return response
#
# def get_combined_score(candidate_data, division):
#     prompt = f"""
#      You are a political analyst. Given the following candidate data, evaluate how the candidate performs in demographic alignment and community engagement in {division} on a scale of 1 to 100.
#      Please provide only the numerical scores in the following format without any additional text:
#
#      Demographic Alignment: <score>
#      Community Engagement: <score>
#
#      Candidate Data: {candidate_data}
#      """
#     response = generate_content(prompt)
#     scores = response.choices[0].message.content.strip()
#     combined_scores = {}
#     for line in scores.splitlines():
#         try:
#             category, score = line.split(":")
#             combined_scores[category.strip()] = int(score.strip())
#         except ValueError:
#             # Handle unexpected formats
#             print(f"Unexpected format in response: {line.strip()}")
#             continue
#
#     return combined_scores
# def get_combined_scores(candidate_data, division):
#     prompt = f"""
#     You are a political analyst. Given the following candidate data, evaluate how the candidate performs in demographic alignment and community engagement in {division} on a scale of 1 to 100.
#     Provide the scores in the following format:
#
#     Demographic Alignment: <score>
#     Community Engagement: <score>
#
#     Candidate Data: {candidate_data}
#     """
#     response = generate_content(prompt)
#     scores = response.choices[0].message.content.strip()
#     score_pattern = re.compile(r"(?P<category>Demographic Alignment|Community Engagement):\s*(?P<score>\d+)")
#     combined_scores = {}
#     for match in score_pattern.finditer(scores):
#         category = match.group("category")
#         score = match.group("score")
#         combined_scores[category] = int(score)
#     if not combined_scores:
#         print(f"Unexpected format in response: {scores}")
#
#     return combined_scores
# def get_pestel_score(candidate_data):
#     prompt = f"""
#     You are a political analyst with expertise in the PESTEL framework. Given the following candidate data, evaluate how closely they are related to each aspect of PESTEL on a scale of 1 to 100.
#     Please provide only the numerical scores in the following format without any additional text:
#
#     Political: <score>
#     Economic: <score>
#     Social: <score>
#     Technological: <score>
#     Environmental: <score>
#     Legal: <score>
#
#     Candidate Data: {candidate_data}
#     """
#     response = generate_content(prompt)
#     scores = response.choices[0].message.content.strip()
#
#     pestel_scores = {}
#     for line in scores.splitlines():
#         try:
#             category, score = line.split(":")
#             pestel_scores[category.strip()] = int(score.strip())
#         except ValueError:
#             print(f"Unexpected format in response: {line.strip()}")
#             continue
#     return pestel_scores
# def calculate_scores_for_division(candidate_data, division):
#     scores = get_pestel_score(candidate_data)
#     combined_scores = get_combined_scores(candidate_data,
#                                           division)
#     demographic_alignment_score = combined_scores["Demographic Alignment"]
#     community_engagement_score = combined_scores["Community Engagement"]
#
#     pestel_total = sum(scores.values())
#     pestel_weighted_avg = pestel_total / len(scores)
#
#     support_index = (int(pestel_weighted_avg) * 0.75) + (int(demographic_alignment_score) * 0.125) + (
#             int(community_engagement_score) * 0.125)
#     return {
#         "division": division,
#         "pestel_scores": scores,
#         "demographic_alignment_score": demographic_alignment_score,
#         "community_engagement_score": community_engagement_score,
#         "support_index": support_index
#     }
#
# @app.route('/predict', methods=['POST'])
# def predict():
#     data = request.json
#     candidate_data = data['candidate_data']
#
#     divisions = [
#         "Colombo Central", "Borella", "Colombo East", "Colombo West", "Dehiwala",
#         "Ratmalana", "Kolonnawa", "Kotte", "Kaduwela", "Avissawella",
#         "Homagama", "Maharagama", "Kesbewa", "Moratuwa"
#     ]
#     results = list(executor.map(lambda division: calculate_scores_for_division(candidate_data, division), divisions))
#     division_scores = {result["division"]: {
#         "pestel_scores": result["pestel_scores"],
#         "demographic_alignment_score": result["demographic_alignment_score"],
#         "community_engagement_score": result["community_engagement_score"],
#         "support_index": result["support_index"]
#     } for result in results}
#     final_si_score = sum([division_scores[division]["support_index"] for division in divisions]) / len(divisions)
#     save_json({
#         "division_scores": division_scores,
#         "final_si_score": final_si_score
#     }, 'output.json')
#
#     return jsonify({
#         "division_scores": division_scores,
#         "final_si_score": final_si_score
#     })
#
# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host='0.0.0.0', port=port, debug=True)


from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
import os
import json
from concurrent.futures import ThreadPoolExecutor
import re

os.environ["GROQ_API_KEY"] = "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"
client = Groq()
app = Flask(__name__)
CORS(app)
executor = ThreadPoolExecutor(max_workers=10)


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


def get_scores(candidate_data, division):
    prompt = f"""
    You are a political analyst with expertise in the PESTEL framework and political performance evaluation. 
    Given the following candidate data, evaluate how the candidate performs in the {division} division across the following aspects:

    1. PESTEL (Political, Economic, Social, Technological, Environmental, Legal)
    2. Demographic Alignment
    3. Community Engagement

    Provide the scores on a scale of 1 to 100. Ensure you only output the scores in the following format:

    Political: <score>
    Economic: <score>
    Social: <score>
    Technological: <score>
    Environmental: <score>
    Legal: <score>
    Demographic Alignment: <score>
    Community Engagement: <score>

    Candidate Data: {candidate_data}
    """

    response = generate_content(prompt)
    scores = response.choices[0].message.content.strip()

    score_pattern = re.compile(
        r"(?P<category>Political|Economic|Social|Technological|Environmental|Legal|Demographic Alignment|Community Engagement):\s*(?P<score>\d+)"
    )
    combined_scores = {}
    for match in score_pattern.finditer(scores):
        category = match.group("category")
        score = match.group("score")
        combined_scores[category] = int(score)

    # Check if any expected scores are missing
    expected_categories = ["Political", "Economic", "Social", "Technological", "Environmental", "Legal",
                           "Demographic Alignment", "Community Engagement"]
    missing_categories = [cat for cat in expected_categories if cat not in combined_scores]

    if missing_categories:
        print(f"Missing categories in response for {division}: {missing_categories}")
        print(f"Full response: {scores}")

        # Fill missing categories with a default score of 0
        for category in missing_categories:
            combined_scores[category] = 0

    return combined_scores


def calculate_scores_for_division(candidate_data, division):
    scores = get_scores(candidate_data, division)

    if scores is None:
        # Handle the error case gracefully
        return {
            "division": division,
            "pestel_scores": {cat: 0 for cat in
                              ["Political", "Economic", "Social", "Technological", "Environmental", "Legal"]},
            "demographic_alignment_score": 0,
            "community_engagement_score": 0,
            "support_index": 0
        }

    # Extract PESTEL scores
    pestel_scores = {
        "Political": scores["Political"],
        "Economic": scores["Economic"],
        "Social": scores["Social"],
        "Technological": scores["Technological"],
        "Environmental": scores["Environmental"],
        "Legal": scores["Legal"],
    }

    # Extract other scores
    demographic_alignment_score = scores["Demographic Alignment"]
    community_engagement_score = scores["Community Engagement"]

    # Calculate PESTEL weighted average
    pestel_total = sum(pestel_scores.values())
    pestel_weighted_avg = pestel_total / len(pestel_scores)

    # Calculate Support Index
    support_index = (pestel_weighted_avg * 0.75) + (demographic_alignment_score * 0.125) + (
            community_engagement_score * 0.125)

    return {
        "division": division,
        "pestel_scores": pestel_scores,
        "demographic_alignment_score": demographic_alignment_score,
        "community_engagement_score": community_engagement_score,
        "support_index": support_index
    }


@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    candidate_data = data['candidate_data']

    divisions = [
        "Colombo Central", "Borella", "Colombo East", "Colombo West", "Dehiwala",
        "Ratmalana", "Kolonnawa", "Kotte", "Kaduwela", "Avissawella",
        "Homagama", "Maharagama", "Kesbewa", "Moratuwa"
    ]
    results = list(executor.map(lambda division: calculate_scores_for_division(candidate_data, division), divisions))
    division_scores = {result["division"]: {
        "pestel_scores": result["pestel_scores"],
        "demographic_alignment_score": result["demographic_alignment_score"],
        "community_engagement_score": result["community_engagement_score"],
        "support_index": result["support_index"]
    } for result in results}
    final_si_score = sum([division_scores[division]["support_index"] for division in divisions]) / len(divisions)
    # save_json({
    #     "division_scores": division_scores,
    #     "final_si_score": final_si_score
    # }, 'output.json')

    return jsonify({
        "division_scores": division_scores,
        "final_si_score": final_si_score
    })


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
