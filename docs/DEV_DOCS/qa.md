# QA Checks for Alpha Release

## Testing

### Commands
[x] WORKING - `egit summarize --staged`
[x] WORKING - `egit summarize --branch`
[] UNTESTED - `egit summarize --commit`
[] UNTESTED - `egit release-notes 1.0.0 --draft`
[] UNTESTED - `egit release-notes 1.0.0 --from v0.9.0 --to main`
[] UNTESTED - `egit release-notes 1.0.0 --tag`
[x] WORKING - `egit --help`
[x] WORKING - `egit config --show`
[x] WORKING - `egit config --help`
[X] WORKING - `egit config --set provider` # Get the provider
[X] WORKING - `egit config --set llm_model` # Get the model
[X] WORKING - `egit config --set llm_api_key` # Get the API key
[X] WORKING - `egit config --set llm_api_base` # Get the API base
[X] WORKING - `egit config --set llm_max_tokens` # Get the max tokens
[X] WORKING - `egit config --set llm_temperature` # Get the temperature
[] TESTING - `egit config --set provider --value ollama` # Set the provider
[] TESTING - `egit config --set llm_model --value openai/llama3.2:3b` # Set the model
[] TESTING - `egit config --set llm_api_key --value <api_key>` # Set the API key
[] TESTING - `egit config --set llm_api_base --value http://localhost:11434` # Set the API base
[] TESTING - `egit config --set llm_max_tokens --value 4096` # Set the max tokens
[] TESTING - `egit config --set llm_temperature --value 0.7` # Set the temperature

### Response Quality

[] UNTESTED - `egit summarize --staged`
[] UNTESTED - `egit summarize --branch`
[] UNTESTED - `egit summarize --commit`