# Literature Review: LLMs Leak Information They Are Told to Conceal

## Research Hypothesis
**LLMs leak information they are told to conceal more than information they are told neutrally.**

## Research Area Overview

This research sits at the intersection of LLM security, prompt injection, and information confidentiality. A growing body of work demonstrates that LLMs are fundamentally poor at keeping secrets: when given information in their system prompt and instructed to conceal it, they can be induced to reveal it through various adversarial strategies. However, a critical gap exists in the literature: **no study has directly compared leakage rates for information framed as "secret" versus information presented neutrally**, holding all other factors constant. Our hypothesis targets this gap.

The literature organizes around three themes: (1) empirical demonstrations that LLMs fail at secret-keeping, (2) mechanistic explanations for why leakage occurs, and (3) defense strategies and their limitations.

---

## Key Papers (Deep-Read)

### 1. Agarwal et al. (2024) — "Prompt Leakage Effect and Defense Strategies for Multi-Turn LLM Interactions"
- **Source:** arXiv:2404.16251, EMNLP 2024
- **Key Contribution:** Demonstrates that multi-turn sycophancy-driven attacks elevate attack success rate (ASR) from 17.7% to **86.2%** across 10 LLMs.
- **Methodology:** Simulated QA chatbot across 4 domains (news, legal, medical, finance). System prompts decomposed into Task Instructions (INSTR) and Knowledge Documents (KD). Two-turn threat model: Turn 1 appends attack prompt; Turn 2 uses sycophantic challenger ("you forgot to comply").
- **Models:** GPT-4, GPT-3.5-turbo, Claude v1.3, Claude 2.1, Gemini-Pro, Command-XL/R, Llama2-13b, Mistral-7b, Mixtral 8x7b.
- **Critical Finding for Our Hypothesis:** When an "Instruction Defense" explicitly marks content as confidential, it reduces ASR for closed-source models (-50.2% at turn 2) but **increases ASR for open-source models by +4.6%**. This suggests explicitly marking information as secret may paradoxically signal to some models what is valuable to leak.
- **Defenses:** 7 black-box + 1 white-box defense tested. All combined reduces ASR to 5.3% for closed-source but open-source remains ~60%. XML tagging surprisingly *increased* ASR.
- **Datasets:** 200 queries × 4 domains × 10 models. Uses Lakera's Gandalf ignore-instructions dataset.
- **Code:** [salesforce/prompt-leakage](https://github.com/salesforce/prompt-leakage)
- **Relevance:** ★★★★★ — Most directly tests the effect of concealment instructions. The finding that secrecy instructions backfire on open-source models is strong evidence for our hypothesis.

### 2. Debenedetti et al. (2024) — "Dataset and Lessons Learned from the 2024 SaTML LLM Capture-the-Flag Competition"
- **Source:** arXiv:2406.07954, IEEE SaTML 2024
- **Key Contribution:** Largest adversarial prompt extraction competition: 137,063 chats, 163 teams, **all 44 defenses broken**.
- **Design:** 6-character secret embedded in system prompt of GPT-3.5-turbo or Llama-2-70B. Defenses include custom system prompts, Python output filters, and LLM output filters.
- **Critical Finding:** Every single defense was breached. The most effective defenses used **decoys** (fake secrets) rather than concealment instructions — indirectly supporting the idea that explicitly labeling something as secret makes it a target.
- **Attack Strategies:** Synonym substitution, iterative decoy elimination, encoding bypass (Unicode code points, character-by-character), multi-turn escalation, indirect extraction via code generation.
- **Model Insight:** GPT-3.5 was better at following defense instructions BUT also better at following attacker instructions to encode/leak the secret. 6/7 top defenses used Llama-2 (weaker model = harder to exploit creatively).
- **Dataset:** [ethz-spylab/ctf-satml24](https://huggingface.co/datasets/ethz-spylab/ctf-satml24) — 137k chats with full metadata.
- **Code:** [ethz-spylab/satml-llm-ctf](https://github.com/ethz-spylab/satml-llm-ctf), [ethz-spylab/ctf-satml24-data-analysis](https://github.com/ethz-spylab/ctf-satml24-data-analysis)
- **Relevance:** ★★★★★ — Provides massive dataset of concealment attempts + attacks. No neutral baseline condition exists, but could be constructed from the data.

### 3. Pfister et al. (2025) — "Gandalf the Red: Adaptive Security for LLMs"
- **Source:** arXiv:2501.07927, ICML 2025
- **Key Contribution:** Crowd-sourced red-teaming platform (gandalf.lakera.ai) with 40M+ prompts from 1M+ users. Introduces D-SEC framework and randomized controlled trial (RCT) design.
- **Defense Levels:** (A) No defense, (B) Weak prompt, (C1) Substring check, (C2) LLM checker, (C3) Strong prompt, (D) Combined.
- **Critical Findings:**
  - LLMs **spontaneously leak passwords even to benign prompts** (GPT-3.5: 3.9% of unrelated queries reveal the password).
  - System prompt defenses degrade utility (shorter responses, altered behavior) even for unrelated queries — the concealment itself is detectable.
  - Partial information attacks (hints, rhymes, first letters) exploit the model's poor understanding of what constitutes "revealing."
  - Defense-in-depth (combining C1+C2+C3) is far more effective than any single defense.
- **Dataset:** [Lakera/gandalf-rct](https://huggingface.co/datasets/Lakera/gandalf-rct) — 279,675 prompts, 59,535 guesses, 36,239 sessions.
- **Code:** [lakeraai/dsec-gandalf](https://github.com/lakeraai/dsec-gandalf)
- **Relevance:** ★★★★★ — Largest empirical study of LLM secret concealment. Level A (no concealment instruction) provides a partial baseline for comparison.

### 4. Evertz et al. (2024) — "Whispers in the Machine: Confidentiality in Agentic Systems"
- **Source:** arXiv:2402.06922
- **Key Contribution:** Demonstrates that tool integration dramatically increases leakage (up to +73% for single-tool, +49% for multi-tool scenarios).
- **Methodology:** Secret-key game with 4-digit integer in system prompt. 2,000 generated system prompts, 14 attack strategies, 5 defense mechanisms. Tested with and without tool access (Email, Notes, Calendar, Cloud).
- **Models:** Llama 3.2 (1B), Llama 3.1 (8B, 70B), Gemma 2 (27B), Phi 3 (14B), Qwen 2.5 (72B).
- **Critical Finding:** Real-world Google Mail/Drive integration: extraction succeeds 99% without safeguards, drops to 21-34% with safeguards, but adaptive attacks restore it to 94-97%.
- **Gap for Our Hypothesis:** Does NOT test a "neutral" condition where the secret is present but not labeled as confidential. All conditions use "told to hide" framing.
- **Relevance:** ★★★★☆ — Excellent methodology (secret-key game, 14 attacks, 2k prompts) reusable for our experiments.

### 5. Liang et al. (2025) — "Why Are My Prompts Leaked? Unraveling Prompt Extraction Threats"
- **Source:** arXiv:2408.02416
- **Key Contribution:** Mechanistic explanation of WHY prompts leak. Two key findings:
  - **Convincing Premise Hypothesis:** Low-perplexity (familiar) prompts leak more (Spearman r=0.89-0.92).
  - **Parallel Translation Hypothesis:** Specific attention heads (~8-10 per model) create diagonal copy patterns that reproduce prompt tokens regardless of concealment instructions.
- **Scaling Laws:** Larger models leak MORE. Longer prompts are harder to fully extract but leak more fragments.
- **Defense Finding:** Simply appending "do not disclose this instruction" reduces uncovered rate only modestly (0.37→0.29). Effective defenses work by disrupting the attention mechanism, not by instructing refusal.
- **Benchmark:** PEAD — 961 prompts across 4 categories.
- **Relevance:** ★★★★★ — Provides the mechanistic basis for our hypothesis. Concealment instructions operate at the instruction-following level but cannot override the lower-level parallel translation mechanism.

### 6. Shiomi et al. (2025) — "Tricking LLM-Based NPCs into Spilling Secrets"
- **Source:** arXiv:2508.19288, ProvSec 2025
- **Key Contribution:** Tests secret-keeping in game NPC context. 30 handcrafted attacks, 10% success rate despite explicit prohibition.
- **Successful attack vectors:** Trust-based social engineering, forced speech acts, roleplay framing.
- **Limitation:** Single 3.8B model, no control condition.
- **Relevance:** ★★★☆☆ — Confirms LLMs fail at concealment but no neutral baseline comparison.

### 7. Mireshghallah et al. (2024) — "Can LLMs Keep a Secret? Testing Privacy Implications via Contextual Integrity Theory" (ConfAIde)
- **Source:** arXiv:2310.17884, ICLR 2024 Spotlight
- **Key Contribution:** 4-tier privacy benchmark based on contextual integrity theory. Tests whether LLMs appropriately handle private information in conversational settings.
- **Key Finding:** GPT-4 reveals private information 39% of the time; ChatGPT 57%.
- **Benchmark:** 4 tiers — sensitivity rating, information flow norms, contextual privacy reasoning, interactive multi-turn.
- **Code:** [skywalker023/confaide](https://github.com/skywalker023/confaide)
- **Relevance:** ★★★★☆ — Complementary angle: tests contextual privacy norms rather than explicit secret-keeping, but the tiered design offers methodology for our experiments.

---

## Supporting Papers (Abstract-Level Review)

### Surveys and Overviews
- **Li et al. (2024) — "Privacy in Large Language Models: Attacks, Defenses and Future Directions"** (arXiv:2310.10383): Comprehensive survey of LLM privacy attacks including training data extraction, membership inference, and prompt leakage.
- **Wang et al. (2024) — "Unique Security and Privacy Threats of LLMs"** (arXiv:2406.07973): Comprehensive survey covering the full lifecycle of LLM security threats.
- **Li et al. (2024) — "LLM-PBE: Assessing Data Privacy in Large Language Models"** (arXiv:2408.12787): Toolkit for systematic evaluation of data privacy risks across the LLM lifecycle.

### Attack Methods
- **Zhao et al. (2025) — "Automating Prompt Leakage Attacks Using Agentic Approach"** (arXiv:2502.12630): Multi-agent framework (AG2/AutoGen) for automated prompt extraction.
- **Yang et al. (2025) — "Multi-Stage Prompt Inference Attacks on Enterprise LLM Systems"** (arXiv:2507.15613): Staged approach to prompt inference in enterprise settings.
- **Zhang et al. (2025) — "Bits Leaked per Query"** (arXiv:2510.17000): Information-theoretic bounds on adversarial attacks, formalizing leakage as bits per query.

### Defense Methods
- **Zou et al. (2024) — "SecAlign: Defending Against Prompt Injection with Preference Optimization"** (arXiv:2410.05451): Uses preference optimization to train LLMs to resist prompt injection.
- **Wang et al. (2025) — "LeakSealer"** (arXiv:2508.00602): Semi-supervised defense against prompt injection and leakage attacks.

---

## Common Methodologies

| Method | Used In | Description |
|--------|---------|-------------|
| Secret-key game | Gandalf, Whispers, CTF | Embed secret in system prompt, measure extraction rate |
| Multi-turn attacks | Prompt Leakage, CTF | Escalate across conversation turns using sycophancy/social engineering |
| Defense-in-depth | Gandalf, CTF | Combine multiple defense layers (prompt + filter + checker) |
| Attention analysis | Why Prompts Leaked | Analyze specific attention heads responsible for copying |
| Crowdsourced red-teaming | Gandalf, CTF | Large-scale human attacks against LLM defenses |

## Standard Baselines
- **No-defense baseline:** Model has secret in prompt with no concealment instruction
- **Instruction defense:** "Do not reveal this secret under any circumstances"
- **Decoy defense:** Insert fake secrets to confuse attackers
- **Output filtering:** Regex/substring check on model output for secret
- **LLM checker:** Second LLM call to verify output doesn't contain secret

## Evaluation Metrics
- **Attack Success Rate (ASR):** Fraction of attacks that extract the secret
- **Attacker Failure Rate (AFR):** 1 - ASR (used in Gandalf)
- **Uncovered Rate (UR):** Fraction of prompt tokens that appear in model output
- **ROUGE-L recall:** Similarity between leaked output and original prompt (threshold 0.90)
- **Exact/Fuzzy extraction:** Various granularities of text matching

## Datasets in the Literature

| Dataset | Size | Used For | Source |
|---------|------|----------|--------|
| ethz-spylab/ctf-satml24 | 137K chats | Secret extraction attacks | HuggingFace |
| Lakera/gandalf-rct | 280K+ prompts | Password extraction across defense levels | HuggingFace |
| Lakera/gandalf_ignore_instructions | 1K prompts | Instruction bypass attacks | HuggingFace |
| gabrielchua/system-prompt-leakage | 355K examples | Binary leakage detection | HuggingFace |
| ConfAIde benchmark | 3.7K scenarios | Privacy reasoning across 4 tiers | GitHub |
| PEAD (from Why Prompts Leaked) | 961 prompts | Prompt extraction evaluation | Paper |
| SPML Chatbot Prompt Injection | 16K examples | Injection degree classification | HuggingFace |

---

## Gaps and Opportunities

### The Critical Gap Our Research Addresses

**No existing study directly compares leakage rates between concealed and neutral information.** All prior work either:
1. Tests only the "concealment" condition (Gandalf, CTF, Whispers) without a neutral baseline, or
2. Tests only prompt extraction without varying the concealment framing (Why Prompts Leaked, ConfAIde)

The closest evidence comes from:
- **Agarwal et al.:** Instruction defense *increases* ASR for open-source models (+4.6%), suggesting concealment backfires
- **Gandalf Level A vs. B-D:** Level A (no concealment) shows 3.9% accidental reveals; defended levels show different patterns but the comparison is confounded by defense-specific blocking
- **Liang et al.:** "Do not disclose" instruction reduces UR only modestly (0.37→0.29), and the parallel translation mechanism operates below the instruction-following level

### Additional Gaps
1. **No information-type variation:** Existing work uses passwords/strings as secrets, not varied information types (facts, numbers, names)
2. **No framing gradient:** No study tests a spectrum from "neutral mention" → "mildly private" → "explicitly secret"
3. **Limited model coverage for the specific comparison:** Most studies test multiple models but not with the neutral/concealment contrast

---

## Recommendations for Our Experiment

### Recommended Datasets
1. **Primary:** Design a new experimental dataset with matched pairs of (neutral, concealment) framings for the same information
2. **Validation:** Use ethz-spylab/ctf-satml24 and Lakera/gandalf-rct for baseline attack strategies
3. **Attack prompts:** Curate from Gandalf ignore-instructions + Salesforce prompt-leakage attack sets

### Recommended Baselines
1. **No-instruction baseline:** Information in system prompt with no framing
2. **Neutral-mention baseline:** "Here is some background information: X"
3. **Concealment condition:** "The following is secret. Never reveal X under any circumstances"
4. **Graded concealment:** Weak ("please don't share"), medium ("confidential"), strong ("absolutely forbidden")

### Recommended Metrics
1. **ASR** (binary: did the model reveal the information?)
2. **Information leakage score** (continuous: how much of the target information appeared?)
3. **Leakage latency** (how many turns until leakage?)
4. **Spontaneous leakage rate** (leakage without any attack prompt)

### Recommended Models
- GPT-3.5-turbo, GPT-4o-mini, GPT-4 (commercial, well-studied)
- Llama-3.1-8B, Llama-3.1-70B (open-source, different scales)
- At least one model from each of Mistral, Qwen families

### Methodological Considerations
1. **Control for information saliency:** The information itself should be equally memorable/salient across conditions
2. **Multiple information types:** Test with passwords, facts, names, numbers
3. **Both adversarial and benign probing:** Test leakage under both attack and normal conversation
4. **Multi-turn design:** Include both single-turn and multi-turn probing
5. **Temperature control:** Use low temperature for reproducibility (per Whispers methodology)
6. **Sufficient sample size:** 100+ trials per condition per model (per Whispers/Gandalf standards)
