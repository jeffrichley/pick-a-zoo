
# Story 2 — Add a New Live Cam Feed
## /specify

## 🎯 Summary
Allow the user to add a new cam feed by entering a name and a URL, with automatic detection of whether the URL is a direct stream or a webpage containing an embedded feed.

## 🧠 Why This Matters
Users should be able to personalize Pick-a-Zoo by adding any publicly available live stream. This keeps the app flexible and demonstrates feed discovery and modular UX.

## 🔍 User Story
> “As a user, I want to add a new cam feed by providing a URL so that I can watch additional animals or locations.”

## 📌 Acceptance Criteria
- Prompts user for name + URL.
- Detects direct vs HTML URL.
- Finds playable stream if HTML contains an embedded player.
- If multiple streams exist, user chooses one.
- Saves feed in YAML.
- Produces clear error messages.

## 📂 Data / State Requirements
- Feeds stored in feeds.yaml.
- Each feed entry contains: name, url, optional window_size.
- YAML must be validated and recovered if corrupted.

## 🛣️ Primary Flow
1. User selects “Add Cam”.
2. User enters feed name.
3. User enters URL.
4. System inspects URL and extracts streams.
5. User confirms or selects from list.
6. System saves feed.

## 🔄 Alternate Flows
- No internet → retry message.
- No streams found → user prompted to try another URL.
