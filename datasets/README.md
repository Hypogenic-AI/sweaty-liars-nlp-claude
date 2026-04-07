# Datasets for "Sweaty Liars" NLP Research

Hypothesis: "LLMs leak information they are told to conceal more than information they are told neutrally."

## Downloaded Datasets

### 1. ethz-spylab/ctf-satml24
- **Source**: https://huggingface.co/datasets/ethz-spylab/ctf-satml24
- **Description**: Dataset from the 2024 SaTML LLM Capture-the-Flag Competition. Contains adversarial chats where attackers try to extract secrets from defended LLMs.
- **Configs**: `defense`, `interaction_chats`, `message_counts`, `teams`
- **Key config - interaction_chats**:
  - Split: `attack` - 137,063 rows
  - Columns: `_id`, `user`, `secret`, `model`, `defense`, `history`, `is_attack`, `is_evaluation`, `was_successful_secret_extraction`
  - Contains full chat histories with labeled success/failure for secret extraction
- **Defense config**: 44 rows with defense strategies
- **Teams config**: 44 teams
- **Note**: `message_counts` config failed to load (empty CSV on HuggingFace)
- **Directory**: `ctf-satml24/`

### 2. Lakera/gandalf-rct
- **Source**: https://huggingface.co/datasets/Lakera/gandalf-rct
- **Description**: Dataset from Gandalf the Red paper (randomized controlled trial). Contains attack prompts from users trying to extract passwords from LLMs with various defense levels.
- **Split**: `trial` - 339,210 rows
- **Columns**: `datetime`, `kind`, `user`, `level`, `password`, `success`, `guess`, `prompt`, `answer`, `llm`, `raw_answer`, `defender_time_sec`, `blocked_by`, `level_order`, `setup`, `defense`
- **Key features**: Multiple difficulty levels, success labels, defense mechanisms, user prompts and LLM responses
- **Directory**: `gandalf-rct/`

### 3. Lakera/gandalf_ignore_instructions
- **Source**: https://huggingface.co/datasets/Lakera/gandalf_ignore_instructions
- **Description**: Adversarial prompts for prompt injection / instruction bypass.
- **Splits**: train (777), validation (111), test (112)
- **Columns**: `text`, `similarity`
- **Directory**: `gandalf-ignore-instructions/`

### 4. gabrielchua/system-prompt-leakage
- **Source**: https://huggingface.co/datasets/gabrielchua/system-prompt-leakage
- **Description**: System prompt leakage detection dataset. Contains system prompts, LLM outputs, and binary labels indicating whether the output leaks the system prompt.
- **Splits**: train (283,353), test (71,351)
- **Columns**: `system_prompt`, `content`, `leakage` (0/1)
- **Highly relevant**: Directly measures prompt leakage with labeled examples
- **Directory**: `system-prompt-leakage/`

### 5. deepset/prompt-injections
- **Source**: https://huggingface.co/datasets/deepset/prompt-injections
- **Description**: Prompt injection detection dataset with binary classification labels.
- **Splits**: train (546), test (116)
- **Columns**: `text`, `label`
- **Directory**: `deepset-prompt-injections/`

### 6. reshabhs/SPML_Chatbot_Prompt_Injection
- **Source**: https://huggingface.co/datasets/reshabhs/SPML_Chatbot_Prompt_Injection
- **Description**: SPML (System Prompt Meta Language) chatbot prompt injection dataset with degree of injection severity.
- **Split**: train (16,012)
- **Columns**: `System Prompt`, `User Prompt`, `Prompt injection` (label), `Degree`, `Source`
- **Directory**: `spml-prompt-injection/`

### 7. cgoosen/prompt_injection_password_or_secret
- **Source**: https://huggingface.co/datasets/cgoosen/prompt_injection_password_or_secret
- **Description**: Small curated dataset of prompt injection attempts targeting password/secret extraction.
- **Split**: train (82)
- **Columns**: `label`, `text`
- **Directory**: `prompt-injection-password/`

## Not Downloaded (Gated/Unavailable)

### hackaprompt/hackaprompt-dataset
- **Source**: https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset
- **Status**: Gated dataset - requires HuggingFace authentication and access approval
- **Description**: Dataset from the HackAPrompt competition (1,020 downloads)

### Prompt Leakage Effect and Defense Strategies (arXiv 2404.16251)
- **Status**: No dedicated HuggingFace dataset found for this paper
- **Note**: The paper likely uses custom evaluation setups; `gabrielchua/system-prompt-leakage` covers similar ground

## Reproduction

```bash
source /workspaces/sweaty-liars-nlp-claude/.venv/bin/activate
uv pip install datasets huggingface-hub tzdata

python3 -c "
from datasets import load_dataset

# CTF-SaTML24 (use config names: defense, interaction_chats, teams)
ds = load_dataset('ethz-spylab/ctf-satml24', 'interaction_chats')

# Gandalf RCT
ds = load_dataset('Lakera/gandalf-rct')

# Gandalf Ignore Instructions
ds = load_dataset('Lakera/gandalf_ignore_instructions')

# System Prompt Leakage
ds = load_dataset('gabrielchua/system-prompt-leakage')

# Deepset Prompt Injections
ds = load_dataset('deepset/prompt-injections')

# SPML Prompt Injection
ds = load_dataset('reshabhs/SPML_Chatbot_Prompt_Injection')

# Prompt Injection Password
ds = load_dataset('cgoosen/prompt_injection_password_or_secret')
"
```

## File Structure

Each dataset directory contains:
- `*.parquet` - Full dataset (git-ignored due to size)
- `sample_10.json` - First 10 examples for quick inspection
