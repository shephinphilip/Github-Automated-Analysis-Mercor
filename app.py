import re
import os
from flask import Flask, render_template, request
from github import Github
import openai
import json
import requests
import base64
import langchain

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_url = request.form.get('users_url')  #  .get() to handle missing key 
        if user_url:
            username = extract_username(user_url)
            if username:
                try:
                    repositories = fetch_user_repositories(username)
                    most_complex_repo_name = None
                    most_complex_repo_score = float('-inf')

                    for repository in repositories:
                        repo_name, repo_url, overall_score = assess_repository(repository)

                        if overall_score > most_complex_repo_score:
                            most_complex_repo_name = repo_name
                            most_complex_repo_score = overall_score

                    analysis = {
                        'username': username,
                        'most_complex_repo_name': most_complex_repo_name,
                        'most_complex_repo_score': most_complex_repo_score
                    }

                    return render_template('result.html', analysis=analysis)

                except Exception as e:
                    error_message = f"Failed to fetch user repositories. Error: {str(e)}"
                    return render_template('result.html', error_message=error_message)

            error_message = "Invalid GitHub user URL. Please try again."
            return render_template('result.html', error_message=error_message)

        error_message = "Invalid GitHub user URL. Please try again."
        return render_template('result.html', error_message=error_message)

    return render_template('index.html')



def extract_username(user_url):
    """
    Extracts the username from a GitHub user URL.

    Args:
        user_url (str): The GitHub user URL.

    Returns:
        str: The extracted username or None if the URL is invalid.
    """
    pattern = r"github\.com\/([a-zA-Z0-9-_]+)"
    match = re.search(pattern, user_url)

    if match:
        return match.group(1)
    else:
        return None


openai.api_key = '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'


def fetch_user_repositories(username):
    """
    Fetches the repositories of a GitHub user.

    Args:
        username (str): The GitHub username.

    Returns:
        list: The list of repositories.
    """
    url = f'https://api.github.com/users/{username}/repos'
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        raise Exception(f"User repositories not found for username: {username}")
    else:
        raise Exception(f"Failed to fetch user repositories. Status code: {response.status_code}")

def preprocess_repository_code(repository_code):
    """
    Preprocesses the code of a repository.

    Args:
        repository_code (dict): The code data of the repository.

    Returns:
        str: The preprocessed code.
    """
    MAX_CHUNK_SIZE = 1000
    preprocessed_code = ""

    if "content" in repository_code:
        code_data = repository_code["content"]
        code = base64.b64decode(code_data).decode("utf-8")
        lines = code.split("\n")
        chunk = ""
        chunk_size = 0

        for line in lines:
            line_size = len(line) + 1
            if chunk_size + line_size <= MAX_CHUNK_SIZE:
                chunk += line + "\n"
                chunk_size += line_size
            else:
                preprocessed_code += chunk
                chunk = line + "\n"
                chunk_size = line_size

        preprocessed_code += chunk

    return preprocessed_code


class CodeMetrics:
    """
    Class for calculating code metrics.
    """

    def __init__(self, readme_content):
        self.complexity_score = 0
        self.maintainability_score = 0

        self.lines_of_code = len(readme_content.splitlines())
        self.number_of_comments = len(re.findall(r"//.*?\n", readme_content))

        self.complexity_score = self.lines_of_code / self.number_of_comments
        self.maintainability_score = self.number_of_comments / self.lines_of_code

    def get_complexity_score(self):
        return self.complexity_score

    def get_maintainability_score(self):
        return self.maintainability_score


def assess_repository(repo):
    """
    Assesses the complexity of a repository.

    Args:
        repo (dict): The repository data.

    Returns:
        tuple: The repository name, URL, and overall score.
    """
    repo_name = repo['name']
    repo_url = repo['html_url']
    readme_url = f"{repo_url}/blob/master/README.md"

    readme_response = requests.get(readme_url)
    readme_content = ''
    if readme_response.status_code == 200:
        readme_content = readme_response.text

    gpt_input = f"Assess the complexity of repository {repo_name}. {readme_content}"
    gpt_prompt = generate_prompt(gpt_input)
    gpt_response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=gpt_prompt,
        max_tokens=50,
        temperature=0.5,
        n=1,
        stop=None,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    completion_text = gpt_response.choices[0].text.strip()
    complexity_score = extract_complexity_score(completion_text)

    code_metrics = CodeMetrics(readme_content)
    complexity_score += code_metrics.complexity_score
    overall_score = complexity_score + code_metrics.maintainability_score

    return repo_name, repo_url, overall_score


def generate_prompt(preprocessed_code):
    """
    Generates a prompt for code assessment.

    Args:
        preprocessed_code (str): The preprocessed code.

    Returns:
        str: The generated prompt.
    """
    prompt = """Evaluate the complexity of the code:

    Code:
    {}

    """.format(preprocessed_code)

    # Shorten the prompt to fit within the maximum context length
    prompt = prompt[:4090]

    return prompt


def extract_complexity_score(completion):
    """
    Extracts the complexity score from GPT-3 completion text.

    Args:
        completion (str): The GPT-3 completion text.

    Returns:
        float: The extracted complexity score.
    """
    score_string = re.search(r"Complexity Score: (.+)", completion)
    if score_string:
        score = float(score_string.group(1))
    else:
        score = 0.0

    return score


def find_most_challenging_repository(username):
    """
    Finds the most challenging repository for a given GitHub username.

    Args:
        username (str): The GitHub username.

    Returns:
        tuple: The repository name, URL, and overall score of the most challenging repository.
    """
    try:
        repositories = fetch_user_repositories(username)

        if not repositories:
            raise Exception(f"No repositories found for user {username}")

        repository_scores = []
        for repo in repositories:
            repo_name, repo_url, overall_score = assess_repository(repo)
            repository_scores.append((repo_name, repo_url, overall_score))

        repository_scores.sort(key=lambda x: x[2], reverse=True)

        return repository_scores[0]

    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == '__main__':
    app.run(debug=True)
