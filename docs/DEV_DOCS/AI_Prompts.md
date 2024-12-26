# Prompts

## Development Prompts
- I am making a CLI app written in Python to help me with Git commit messages and other common tasks. Can you please review the Planning.md file and build out: 1) The app itself and 2) The installer script? Be sure to follow the requirements listed in the Planning.md file, and use all of the specifications and resources as mentioned in the Planning.md file.

- Based off the README.MD file and looking at the app code itself, can you make a basic but complete set of MD files for a user guide in this folder: docs\USER_DOCS

Ensure the guide coveres all possible commands and features, includes examples, and is easy to read and follow. This should be easy for a junior developer to read and understand.

## Application Prompts

### Sumarize
```python
SUMMARY_PROMPT = f"""
You are a helpful assistant that summarizes GitLab commit messages. Please summarize all of the changes this person has made to their code based off the commit messages.
{context}
"""
```
