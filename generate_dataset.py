from pymongo import MongoClient
import random

# MongoDB
client = MongoClient("mongodb+srv://chandana05:mongoDB26@cluster0.isrnuwh.mongodb.net/?retryWrites=true&w=majority")
db = client["ai_interview"]
questions_collection = db["questions"]

# Roles (20)
roles = [
    "Python Developer", "Java Developer", "Frontend Developer",
    "Backend Developer", "Full Stack Developer", "Data Analyst",
    "Data Scientist", "Machine Learning Engineer", "DevOps Engineer",
    "Cloud Engineer", "Cyber Security", "Android Developer",
    "iOS Developer", "Software Tester", "UI/UX Designer",
    "System Design", "Database Engineer", "Network Engineer",
    "Embedded Systems", "HR"
]

# Question templates
templates = [
    "What is {}?",
    "Explain {}.",
    "How does {} work?",
    "What are advantages of {}?",
    "What are disadvantages of {}?",
    "Difference between {} and {}.",
    "Where is {} used?",
    "Explain real-world example of {}.",
    "Why is {} important?",
    "Explain architecture of {}."
]

# Topic pool
topics = [
    "OOP", "API", "REST", "Microservices", "Database", "Cloud",
    "Docker", "Kubernetes", "Machine Learning", "Deep Learning",
    "Authentication", "Authorization", "Encryption", "Agile",
    "Testing", "Debugging", "Data Structures", "Algorithms",
    "Networking", "Operating System", "Threads", "Concurrency",
    "Caching", "Load Balancing", "CI/CD", "Git", "Version Control"
]

dataset = []
seen = set()

for role in roles:
    for _ in range(100):   # 100 per role → 2000 total

        template = random.choice(templates)

        if "{} and {}" in template:
            t1, t2 = random.sample(topics, 2)
            question = template.format(t1, t2)
        else:
            t = random.choice(topics)
            question = template.format(t)

        key = (role + question).lower()

        if key not in seen:
            seen.add(key)

            dataset.append({
                "role": role,
                "question": question,
                "difficulty": random.choice(["Easy", "Medium", "Hard"])
            })

# Insert into MongoDB
questions_collection.delete_many({})  # clear old
questions_collection.insert_many(dataset)

print("✅ 2000+ Questions Inserted Successfully!")