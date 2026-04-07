# Cloned Code Repositories

Reference repositories for research on LLM information leakage, secret-keeping, and prompt leakage.

**Hypothesis**: "LLMs leak information they are told to conceal more than information they are told neutrally."

---

## 1. ethz-spylab/satml-llm-ctf

- **URL**: https://github.com/ethz-spylab/satml-llm-ctf
- **Description**: Platform code for the 2024 SaTML LLM Capture-the-Flag competition. A FastAPI web server with MongoDB/Redis backend where teams designed attack prompts to extract secrets from LLM defenders and defense prompts to protect secrets.
- **Key files**: `app/` (FastAPI server), `app/api/` (endpoints), `app/internals/` (core logic), `app/schemas/` (data models)
- **Dependencies**: FastAPI, MongoDB, Redis, Docker
- **Relevance**: The CTF directly tests whether LLMs can keep secrets. Attack/defense dynamics mirror our hypothesis -- defenders instruct LLMs to conceal, attackers try to extract. The platform architecture shows how to set up secret-keeping experiments.

## 2. ethz-spylab/ctf-satml24-data-analysis

- **URL**: https://github.com/ethz-spylab/ctf-satml24-data-analysis
- **Description**: Data analysis scripts for the SaTML CTF dataset. Companion to the competition report (arXiv:2406.07954).
- **Dataset**: https://huggingface.co/datasets/ethz-spylab/ctf-satml24
- **Key files**: `chat_diversity.py` (main analysis), `utils.py`, `raw_data_manipulation/`
- **Dependencies**: HuggingFace `datasets`
- **Relevance**: PRIMARY DATA SOURCE. Contains real attack/defense interaction logs. Can analyze how different defense framings (concealment instructions) affect leakage rates. The HuggingFace dataset includes defense configurations and attack chat histories.

## 3. lakeraai/dsec-gandalf

- **URL**: https://github.com/lakeraai/dsec-gandalf
- **Description**: Code to reproduce experiments from "Gandalf the Red: Adaptive Security for LLMs" (arXiv:2501.07927). Analyzes Gandalf game data across multiple defense levels.
- **Key files**: `analysis/adaptive_defenses/`, `analysis/attack_classification/`, `analysis/defense_in_depth/`, `analysis/supporting_analyses/`, `data.py`, `create_all_paper_plots_and_tables.py`
- **Datasets**: https://huggingface.co/collections/Lakera/gandalf-65a034d1074bfce80224f6dc
- **Dependencies**: See `requirements.txt`
- **Relevance**: HIGHLY RELEVANT. Gandalf is the canonical secret-keeping game (LLM given password, told not to reveal it). Analysis includes attack classification, defense-in-depth evaluation, and level difficulty progression -- directly tests concealment instructions vs. leakage.

## 4. microsoft/gandalf_vs_gandalf

- **URL**: https://github.com/microsoft/gandalf_vs_gandalf
- **Description**: Uses LLMs to automatically attack Lakera's Gandalf challenge. Turns Gandalf Level 1 (undefended) into an attacker against defended levels, using questioner/guesser prompt architecture.
- **Key files**: `Gandalf_vs_Gandalf.py`, `Gandalf_vs_Gandalf.ipynb`
- **Dependencies**: `requests` (queries Gandalf API endpoints directly)
- **Relevance**: Demonstrates automated LLM-vs-LLM secret extraction. The questioner/guesser architecture and prompt strategies are directly applicable to designing attack experiments. Shows that even simple 0-shot prompts can extract secrets across all 7 Gandalf defense levels.

## 5. salesforce/prompt-leakage

- **URL**: https://github.com/salesforce/prompt-leakage
- **Description**: Code and data for "Prompt Leakage effect and defense strategies for multi-turn LLM interactions" (EMNLP 2024, arXiv:2404.16251). Tests 10 LLMs across 4 domains with 7 defense strategies.
- **Key files**: `run_inference_no_defenses.py`, `run_inference_all_defenses.py`, `gpt4_leakage_judge.py`, `prompts/`, `data/`, `safetyfinetuning/`, `model_*.py` (Anthropic, OpenAI, Cohere, Google, Ollama wrappers)
- **Dependencies**: API keys for Anthropic/OpenAI/Cohere/Google, Ollama for open-source models
- **Relevance**: MOST DIRECTLY RELEVANT. Systematically measures prompt leakage with and without defenses. Key finding: sycophancy effect elevates ASR from 17.7% to 86.2% in multi-turn. Tests exactly our hypothesis -- comparing leakage under concealment instructions vs. baseline. Includes defense evaluation and cost analysis.

## 6. skywalker023/confaide

- **URL**: https://github.com/skywalker023/confaide
- **Description**: "Can LLMs Keep a Secret?" (ICLR 2024 Spotlight). Benchmark for privacy implications of LLMs grounded in contextual integrity theory. 4-tier evaluation.
- **Key files**: `eval.py` (main evaluation), `benchmark/` (dataset tiers 1, 2a, 2b, 3, 4), `agents/`
- **Dependencies**: Conda environment (`environment.yml`)
- **Relevance**: HIGHLY RELEVANT. Directly tests secret-keeping across increasing complexity. GPT-4 reveals private info 39% of the time; ChatGPT 57%. Tests privacy reasoning, not just password extraction. Complementary angle to Gandalf/CTF approaches.

## 7. M0gician/RaccoonBench

- **URL**: https://github.com/M0gician/RaccoonBench
- **Description**: "Raccoon: Prompt Extraction Benchmark of LLM-Integrated Applications" (ACL 2024 Findings). 14 categories of prompt extraction attacks with compound attacks and defense templates.
- **Key files**: `run_raccoon_gang.py`, `Data/attacks/singular_attacks/`, `Data/attacks/compound_attacks/`, `Data/defenses/defense_template.json`, `Data/gpts/`
- **Dependencies**: Conda, tiktoken
- **Relevance**: Comprehensive attack taxonomy for prompt extraction. Tests both defenseless and defended scenarios. The 14 attack categories and defense templates provide a structured framework for our experiments. Can be adapted to test concealment framing effects.

## 8. tldrsec/prompt-injection-defenses

- **URL**: https://github.com/tldrsec/prompt-injection-defenses
- **Description**: Curated list of every practical and proposed defense against prompt injection, including prompt leakage defenses.
- **Relevance**: Reference catalog. Useful for surveying defense strategies and understanding the landscape of mitigation approaches.

## 9. chawins/llm-sp

- **URL**: https://github.com/chawins/llm-sp
- **Description**: Curated list of papers and resources related to LLM security and privacy.
- **Relevance**: Literature reference. Useful for finding additional related work and ensuring comprehensive coverage of the field.

---

## Priority for Our Research

| Priority | Repository | Why |
|----------|-----------|-----|
| P0 | salesforce/prompt-leakage | Directly measures leakage with/without defenses across models |
| P0 | ethz-spylab/ctf-satml24-data-analysis | Real attack/defense interaction dataset |
| P0 | lakeraai/dsec-gandalf | Gandalf game data + analysis code |
| P1 | skywalker023/confaide | Privacy/secret-keeping benchmark (ICLR 2024) |
| P1 | M0gician/RaccoonBench | Prompt extraction attack taxonomy |
| P1 | ethz-spylab/satml-llm-ctf | CTF platform (for understanding experimental setup) |
| P2 | microsoft/gandalf_vs_gandalf | Automated attack strategies |
| P2 | tldrsec/prompt-injection-defenses | Defense catalog |
| P2 | chawins/llm-sp | Paper/resource list |

## Key Datasets

- **SaTML CTF**: `ethz-spylab/ctf-satml24` on HuggingFace (defense configs, attack chats, team data)
- **Gandalf**: HuggingFace collection `Lakera/gandalf-65a034d1074bfce80224f6dc`
- **Salesforce Prompt Leakage**: `data/` directory (news, legal, finance, medical domains)
- **ConfAIde**: `benchmark/` directory (4 tiers of privacy scenarios)
- **Raccoon**: `Data/` directory (196 GPTs, 14 attack categories, defense templates)
