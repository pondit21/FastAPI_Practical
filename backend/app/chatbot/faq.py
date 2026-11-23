from dataclasses import dataclass

# বিরামচিহ্ন (বাংলা দাঁড়ি "।" সহ) সরিয়ে শব্দ আলাদা করা হয়, তাই বাংলা কীওয়ার্ডও চলবে
PUNCTUATION = ",.;:!?()[]{}\"'`/\\|।-_"
_TABLE = str.maketrans({ch: " " for ch in PUNCTUATION})


def normalize(text: str) -> str:
    return " ".join(text.lower().translate(_TABLE).split())


@dataclass(frozen=True)
class Faq:
    topic: str
    question: str                 # সাজেশন বাটনে যে প্রশ্ন দেখাবে
    keywords: tuple[str, ...]     # এই শব্দ/বাক্যাংশ প্রশ্নে থাকলে এই উত্তর যাবে
    answer: str
    suggest: bool = True          # সাজেশন বাটনে দেখাবে কিনা


GREETING = (
    "Hi! I'm the SchoolHub assistant. Ask me about your profile, photo, "
    "CGPA and more, or pick a question below."
)

FALLBACK_ANSWER = (
    "Sorry, I don't have an answer for that yet. Try one of the suggested "
    "questions, or contact your school administrator."
)

# নতুন প্রশ্ন-উত্তর যোগ করতে নিচের তালিকায় একটা Faq(...) যোগ করুন।
# কীওয়ার্ডে একই কথার বিভিন্ন রূপ দিন (যেমন "photo" ও "photos")।
# বাংলা কীওয়ার্ডও দিতে পারেন, যেমন: ("পাসওয়ার্ড", "পাসওয়ার্ড ভুলে গেছি")
FAQS: tuple[Faq, ...] = (
    Faq(
        topic="greeting",
        question="Hello",
        keywords=("hello", "hi", "hey", "salam", "assalamu alaikum", "assalamualaikum"),
        answer="Hello! How can I help you today? You can ask about your profile, photo, CGPA, password and more.",
        suggest=False,
    ),
    Faq(
        topic="capabilities",
        question="What can you help me with?",
        keywords=("what can you do", "what can you help", "help me with", "how can you help", "help"),
        answer=(
            "I can answer common questions about your profile, profile photo, CGPA, "
            "starting date, password and how to contact the school. Try one of the suggested questions."
        ),
    ),
    Faq(
        topic="update_profile",
        question="How do I update my profile?",
        keywords=(
            "update my profile", "update profile", "edit my profile", "edit profile",
            "change my details", "update my details", "change my name",
        ),
        answer=(
            "Open your dashboard, click “Edit profile”, change the details you want and "
            "press “Save changes”. Your name, class, CGPA, starting date and description "
            "can all be updated, and administrators can edit them too."
        ),
    ),
    Faq(
        topic="profile_photo",
        question="How do I change my profile picture?",
        keywords=(
            "profile picture", "profile photo", "upload photo", "upload picture",
            "upload a photo", "change photo", "change picture", "my photo", "my picture",
            "avatar", "remove photo", "delete photo", "remove picture",
            "update my profile picture", "update profile picture",
            "change my profile picture", "change profile picture",
            "delete my profile picture", "delete profile picture", "delete my photo",
        ),
        answer=(
            "Use the “Change photo” button on your profile card to upload a JPG, PNG or "
            "WebP image up to 5 MB. Use “Remove” to delete your current photo."
        ),
    ),
    Faq(
        topic="delete_profile",
        question="Can I delete my profile?",
        keywords=(
            "delete my profile", "delete profile", "remove my profile",
            "delete my account", "delete account", "remove my account", "can i delete",
        ),
        answer=(
            "Students can't delete their own profile. If you need your profile removed, "
            "please ask a school administrator."
        ),
    ),
    Faq(
        topic="cgpa",
        question="What is CGPA?",
        keywords=("cgpa", "gpa", "grade point", "what is cgpa"),
        answer=(
            "CGPA stands for Cumulative Grade Point Average. In SchoolHub it is stored on a "
            "0 to 5 scale on your profile and can be updated by you or an administrator."
        ),
    ),
    Faq(
        topic="password",
        question="I forgot my password",
        keywords=(
            "forgot my password", "forgot password", "reset password", "reset my password",
            "change password", "change my password", "lost password", "password",
        ),
        answer=(
            "Password reset isn't available yet. Please contact a school administrator "
            "for help with your account."
        ),
    ),
    Faq(
        topic="start_date",
        question="How do I set my starting date?",
        keywords=("starting date", "start date", "joining date", "admission date", "date of admission"),
        answer=(
            "Your school starting date is part of your profile. Click “Edit profile”, "
            "change the date and save."
        ),
    ),
    Faq(
        topic="privacy",
        question="Who can see my profile?",
        keywords=("who can see my profile", "who can see my data", "is my data safe", "privacy", "my data"),
        answer=(
            "Only you and school administrators can view your profile. Administrators can "
            "also edit or remove records."
        ),
    ),
    # ---- নিচের তিনটার উত্তর আপনার স্কুলের আসল তথ্য দিয়ে বদলে নিন ----
    Faq(
        topic="contact_admin",
        question="How can I contact the admin?",
        keywords=(
            "contact the admin", "contact admin", "contact", "administrator",
            "talk to admin", "speak to admin", "who is the admin", "who is admin",
        ),
        answer="For help from a person, please contact your school administrator through the school office.",
    ),
    Faq(
        topic="school_hours",
        question="What are the school hours?",
        keywords=(
            "school hours", "school time", "school timing", "school timings",
            "class time", "class timing", "opening hours", "what time",
        ),
        answer="The school timetable is managed by the school office. Please ask your administrator for the current hours.",
    ),
    Faq(
        topic="fees",
        question="How do I pay school fees?",
        keywords=("school fees", "school fee", "tuition", "pay fees", "pay fee", "fees", "fee"),
        answer="Fee payment details are managed by the school office. Please contact your administrator for the latest instructions.",
    ),
)

_INDEX = [(faq, [normalize(k) for k in faq.keywords]) for faq in FAQS]


def find_answer(question: str) -> Faq | None:
    """প্রশ্নে যে FAQ-র কীওয়ার্ড সবচেয়ে বেশি মেলে সেটা ফেরত দেয়, না মিললে None"""
    text = f" {normalize(question)} "
    best: Faq | None = None
    best_score = 0
    for faq, keywords in _INDEX:
        score = sum(len(kw.split()) for kw in keywords if kw and f" {kw} " in text)
        if score > best_score:
            best, best_score = faq, score
    return best


def suggested_questions() -> list[str]:
    return [faq.question for faq in FAQS if faq.suggest]