# Github-Automated-Analysis-Mercor
I built a Python-based tool which, when given a GitHub user's URL, returns the most technically complex and challenging repository from that user's profile. The tool will use GPT and LangChain to assess each repository individually before determining the most technically challenging one.

The Technical Complexity Analyzer is a web application built with Flask that assesses the complexity of GitHub repositories. It leverages the power of OpenAI's GPT-3 model and LangChain to analyze code repositories and provide insights on their technical complexity.

## Features

- Fetches repositories from a GitHub user's profile using the GitHub API.
- Preprocesses code files, splitting large files into smaller chunks for analysis.
- Uses GPT-3 to evaluate the technical complexity of the code based on provided prompts.
- Analyzes README files using GPT-3 to gain additional insights.
- Utilizes LangChain to extract code metrics, such as complexity scores, from repositories.
- Calculates an overall complexity score based on the combined analysis from GPT-3 and LangChain.
- Identifies the most technically complex repository for a given user.

## Installation

To run the Technical Complexity Analyzer locally, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/technical-complexity-analyzer.git
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API credentials:

   - Sign up for an OpenAI account and obtain an API key.
   - Replace `'YOUR_API_KEY'` in `app.py` with your actual OpenAI API key.

4. Run the application:

   ```bash
   python app.py
   ```

5. Access the application in your web browser at `http://localhost:5000`.

## Usage

1. Open the code Complexity Analyzer in your web browser.
2. Enter a GitHub user's URL in the provided input field.
3. Click the "Analyze" button.
4. The application will fetch the user's repositories, assess their complexity, and display the username , most complex repository and its complexity score.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Contributing

Contributions are welcome! If you would like to contribute to this project, please open an issue or submit a pull request.

## Acknowledgements

- This project utilizes the [Flask](https://flask.palletsprojects.com/) framework for web development.
- Code analysis and metrics are performed using [OpenAI's GPT-3](https://openai.com/) and [LangChain](https://langchain.dev/).
- GitHub repository data is obtained using the [GitHub API](https://docs.github.com/en/rest).
- [nbconvert](https://nbconvert.readthedocs.io/) is used for converting Jupyter Notebooks to Python scripts.

## Contact

For any questions or inquiries, please contact shephinphilipj404@gmail.com.

Feel free to customize and expand upon this template to provide more specific information about your Github Automation Analayzer project.
