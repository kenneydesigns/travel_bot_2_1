# 📂 /context Folder - TravelBot Prompt Enhancers

This folder contains persistent prompt files that are **always injected into TravelBot's prompt** before user queries.

## 🧠 Purpose

Unlike regulation chunks in `rag/jtr_chunks/`, the files in this folder are:

- **Not chunked or embedded**
- **Loaded directly into the prompt** for every question
- Used to shape **tone**, provide **examples**, inject **definitions**, and guide **bot behavior**

## ✍️ What to Add

You can create or edit any `.txt` files here. Here are examples of useful context files:

| Filename | Purpose |
|----------|---------|
| `bot_intro.txt` | Defines the bot's role, limitations, and assistant persona |
| `tone.txt` | Describes how the bot should sound (friendly, clear, concise) |
| `disclaimer.txt` | Adds legal disclaimers or policy warnings |
| `definitions.txt` | Helpful acronyms or term expansions (e.g. TLE, DLA) |
| `sample_questions.txt` | Few-shot examples of how to answer questions |
| `faq.txt` | Short, general-use answers to common questions |
| `user_tips.txt` | Coaching tips for how to ask better questions |

## 🛠 How It Works

The contents of all `.txt` files in this folder are:
1. **Concatenated together**
2. **Trimmed to fit within 200–300 tokens**
3. **Prepended to the user’s query in the final prompt**

This helps the model better understand how to respond — even without being fine-tuned.

## ⚠️ Tips

- Use short, clear language.
- Prefer bullet points and examples over long paragraphs.
- Keep files updated with any tone, policy, or instruction changes.

Happy prompting! 🎯
