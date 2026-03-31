from __future__ import annotations

from typing import List

from models.schemas import InterviewQAResult, ParsedCV, QuestionItem

CATEGORIES = [
    "Giới thiệu bản thân",
    "CV screening",
    "Dự án",
    "Kỹ năng chuyên môn",
    "Hành vi / behavioral",
    "Tình huống / problem solving",
    "Điểm yếu - thất bại - học hỏi",
    "Định hướng nghề nghiệp",
    "Đào sâu từ CV",
]


def _build_item(category: str, question: str, target_role: str) -> QuestionItem:
    return QuestionItem(
        category=category,
        question=question,
        why_this_is_asked="Để đánh giá mức độ phù hợp với vai trò và năng lực giao tiếp/chuyên môn.",
        what_interviewer_looks_for="Câu trả lời có cấu trúc, trung thực, có ví dụ cụ thể từ CV.",
        answer_outline=[
            "Nêu bối cảnh ngắn gọn",
            "Nêu hành động cá nhân",
            "Nêu kết quả hoặc bài học",
            "Liên hệ với vị trí ứng tuyển",
        ],
        sample_answer=f"Trong vai trò sinh viên định hướng {target_role}, em đã... Cần sinh viên bổ sung thông tin.",
        common_mistakes=[
            "Trả lời quá dài, không vào trọng tâm",
            "Nói chung chung, thiếu ví dụ cụ thể",
            "Bịa thông tin không có trong CV",
        ],
        follow_up_questions=[
            "Bạn đo lường kết quả như thế nào?",
            "Nếu làm lại bạn sẽ cải thiện điều gì?",
        ],
    )


def generate_interview_qa(parsed: ParsedCV, target_role: str, language: str, mode: str = "Thường") -> InterviewQAResult:
    total = 15 if mode == "Thường" else 25
    base_questions: List[str] = [
        "Hãy giới thiệu ngắn gọn về bạn và định hướng nghề nghiệp.",
        "Vì sao bạn ứng tuyển vị trí này?",
        "Dự án nào trong CV thể hiện tốt nhất năng lực của bạn?",
        "Bạn đã gặp khó khăn kỹ thuật nào và xử lý ra sao?",
        "Bạn đóng góp cụ thể gì trong dự án nhóm?",
        "Bạn ưu tiên học công nghệ mới như thế nào?",
        "Bạn xử lý feedback tiêu cực từ mentor ra sao?",
        "Một thất bại gần đây và bài học bạn rút ra?",
        "Mục tiêu nghề nghiệp 1-2 năm tới của bạn?",
        "Nếu yêu cầu thay đổi gấp deadline, bạn làm gì?",
    ]
    while len(base_questions) < total:
        base_questions.append(f"Từ CV của bạn, hãy giải thích sâu hơn về nội dung số {len(base_questions)+1}.")

    items = []
    for i in range(total):
        category = CATEGORIES[i % len(CATEGORIES)]
        items.append(_build_item(category, base_questions[i], target_role))

    return InterviewQAResult(
        student_info=parsed.student_info.model_dump(),
        target_role=target_role,
        language=language,
        question_set=items,
    )
