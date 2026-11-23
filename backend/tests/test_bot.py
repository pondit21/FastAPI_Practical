from app.chatbot.faq import FAQS, find_answer


def test_every_suggested_question_matches_its_own_answer():
    for faq in FAQS:
        if faq.suggest:
            assert find_answer(faq.question) is faq, faq.question


def test_unknown_text_has_no_match():
    assert find_answer("zzz qqq xyz") is None


def test_longer_phrase_wins():
    faq = find_answer("How do I update my profile picture?")
    assert faq is not None and faq.topic == "profile_photo"


def test_bot_requires_profile(client, student_headers):
    res = client.post("/bot/ask", json={"question": "What is CGPA?"}, headers=student_headers)
    assert res.status_code == 403


def test_bot_requires_login(client):
    assert client.post("/bot/ask", json={"question": "hi"}).status_code == 401


def test_bot_answers_known_question(client, student_headers, student_data):
    client.post("/students/me", json=student_data, headers=student_headers)
    res = client.post("/bot/ask", json={"question": "what is cgpa??"}, headers=student_headers)
    assert res.status_code == 200
    body = res.json()
    assert body["matched"] is True
    assert "Cumulative" in body["answer"]


def test_bot_fallback_for_unknown_question(client, student_headers, student_data):
    client.post("/students/me", json=student_data, headers=student_headers)
    res = client.post("/bot/ask", json={"question": "zzz qqq xyz"}, headers=student_headers)
    assert res.json()["matched"] is False


def test_bot_topics(client, student_headers, student_data):
    client.post("/students/me", json=student_data, headers=student_headers)
    res = client.get("/bot/topics", headers=student_headers)
    assert res.status_code == 200
    assert len(res.json()["suggestions"]) >= 5


def test_every_student_gets_the_same_answer(client, create_student_user, student_data):
    first = create_student_user("a@example.com")
    second = create_student_user("b@example.com")
    client.post("/students/me", json=student_data, headers=first)
    client.post("/students/me", json=student_data, headers=second)

    question = {"question": "I forgot my password"}
    answer_a = client.post("/bot/ask", json=question, headers=first).json()
    answer_b = client.post("/bot/ask", json=question, headers=second).json()
    assert answer_a == answer_b