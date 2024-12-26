# QA Checks for Alpha Release

## Testing
Beta Release TODO:

- [x] Test that all commands work as expected
    - [x] summarize
    - [x] release-notes
    - [x] config
    - [x] --help
- [X] Test that all configuration options work as expected
    - [x] Ollama
    - [x] LM Studio
    - [X] OpenAI
    - [X] Anthropic
    - [X] Gemini
    - [-] Vertex AI (Not supported yet)
- [x] Address major bugs
- [x] Ensure Documentation is up to date
    - [x] Core command documentation
    - [x] Configuration documentation
    - [x] LLM provider documentation
    - [x] LLM model documentation

## Post Development TODO:
- [] Test the app end to end for general feedback and bug reports
- [] Ensure repository is clean and ready for release
- [] Update the docs with marketing materals and branding
- [] Update the SPT Website / Add Blog Section
- [] Update the SPT Social Media Accounts
    - [] Twitter
    - [] Discord
    - [] GitHub
    - [] Facebook
    - [] BlueSky
- [] Create blog post
- [] Create dev.to post
- [] Post app to Socials

### Commands
[x] WORKING - `egit summarize --staged`
[x] WORKING - `egit summarize --branch`
[X] WORKING - `egit summarize --commit`
[X] WORKING - `egit release-notes 1.0.0 --draft`
[X] WORKING - `egit release-notes 0.4.3 --tag`
[x] WORKING - `egit --help`
[x] WORKING - `egit config --show`
[x] WORKING - `egit config --help`
[X] WORKING - `egit config --set llm_provider` # Get the provider
[X] WORKING - `egit config --set llm_model` # Get the model
[X] WORKING - `egit config --set llm_api_key` # Get the API key
[X] WORKING - `egit config --set llm_api_base` # Get the API base
[X] WORKING - `egit config --set llm_max_tokens` # Get the max tokens
[X] WORKING - `egit config --set llm_temperature` # Get the temperature
[X] WORKING - `egit config --set llm_provider --value ollama` # Set the provider
[X] WORKING - `egit config --set llm_model --value openai/llama3.2:3b` # Set the model
[X] WORKING - `egit config --set llm_api_key --value <api_key>` # Set the API key
[X] WORKING - `egit config --set llm_api_base --value http://localhost:11434` # Set the API base
[X] WORKING - `egit config --set llm_max_tokens --value 4096` # Set the max tokens
[X] WORKING - `egit config --set llm_temperature --value 0.7` # Set the temperature

### Response Quality

- Ollama API
- LM Studio API
- OpenAI API
- Anthropic API
- Gemini API
