# 🌐 Social Network Analyzer

A Python-based social network analysis tool that processes user data to clean it, display it, and generate intelligent recommendations — such as **people you may know** and **pages you might like** — based on mutual connections and shared interests.

---

## 📁 Project Structure

```
social-network-analyzer/
│
├── data.json               # Sample dataset
├── massive_data.json        # Large-scale dataset for recommendations
│
├── clean_data.py            # Data cleaning module
├── display_data.py          # Data loading and display module
├── pages_you_might_like.py  # Page recommendation engine
└── people_you_may_know.py   # Friend suggestion engine
```

---

## ✨ Features

### 🧹 1. Data Cleaning (`clean_data.py`)
Cleans and normalizes raw JSON data before processing:
- Removes users with **missing or blank names**
- Eliminates **duplicate friend entries** for each user
- Filters out **inactive users** (those with no friends and no liked pages)
- Resolves **duplicate page IDs**, keeping only unique pages

### 📋 2. Display Data (`display_data.py`)
A utility module that:
- Loads JSON data from a specified file
- Makes the data available for inspection and further processing

### 👍 3. Pages You Might Like (`pages_you_might_like.py`)
Recommends pages to a user based on **shared interest patterns** across the network:
- Finds other users who share liked pages with the target user
- Suggests pages liked by those users that the target user hasn't liked yet
- Ranks suggestions by **overlap score** (higher shared pages = higher priority)

### 🤝 4. People You May Know (`people_you_may_know.py`)
Suggests potential friends based on **mutual connections**:
- Identifies all direct friends of the target user
- Finds friends-of-friends who aren't already connected
- Ranks suggestions by **number of mutual friends**

---

## 🚀 Getting Started

### Prerequisites
- Python 3.x
- A `data.json` or `massive_data.json` file in the following format:

```json
{
  "users": [
    {
      "id": 1,
      "name": "Amit",
      "friends": [2, 3],
      "liked_pages": [101, 102]
    }
  ],
  "pages": [
    {
      "id": 101,
      "name": "Tech News"
    }
  ]
}
```

### Installation

```bash
git clone https://github.com/your-username/social-network-analyzer.git
cd social-network-analyzer
```

No external dependencies — uses Python's built-in `json` module only.

---

## 🧪 Usage

### Clean your data
```python
import json
from clean_data import clean_data

data = json.load(open('data.json'))
cleaned = clean_data(data)
```

### Load and display data
```python
from display_data import load_data

data = load_data("data.json")
print(data)
```

### Get page recommendations for a user
```python
from pages_you_might_like import find_pages_you_might_like, load_data

data = load_data("massive_data.json")
user_id = 1
recommendations = find_pages_you_might_like(user_id, data)
print(f"Pages You Might Like for User {user_id}: {recommendations}")
```

### Get friend suggestions for a user
```python
from people_you_may_know import find_people_you_may_know, load_data

data = load_data("massive_data.json")
user_id = 1
suggestions = find_people_you_may_know(user_id, data)
print(f"People You May Know for User {user_id}: {suggestions}")
```

---

## 🔍 How the Recommendation Algorithms Work

### Pages You Might Like
```
For a given user U:
1. Find all pages liked by U → user_liked_pages
2. For every other user V:
   a. Find shared pages between U and V → shared_pages
   b. For each page P liked by V but not U:
      score[P] += len(shared_pages)
3. Return pages sorted by score (highest first)
```

### People You May Know
```
For a given user U:
1. Find U's direct friends → direct_friends
2. For each friend F in direct_friends:
   For each friend-of-friend M in friends[F]:
     If M ≠ U and M ∉ direct_friends:
       mutual_count[M] += 1
3. Return users sorted by mutual_count (highest first)
```

---

## 📌 Notes

- All recommendation functions return an **empty list** if the given `user_id` is not found in the dataset.
- The cleaning step should be run **before** generating recommendations for best results.
- `massive_data.json` is intended for larger datasets; swap in `data.json` for quick testing.

---

## 📄 License

This project is open source. Feel free to use, modify, and distribute it.
