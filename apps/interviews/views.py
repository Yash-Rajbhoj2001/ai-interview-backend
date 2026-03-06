from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView

from django.utils import timezone
from django.http import FileResponse
from django.http import HttpResponse

from django.shortcuts import get_object_or_404
from django.db.models import Avg
from datetime import timedelta

from .models import Score
from .models import InterviewSession, InterviewQuestion, InterviewAnswer, InterviewReport
from .serializers import InterviewStartSerializer, InterviewHistorySerializer
# from .services.ai_question_service import generate_question
from .services.question_engine import generate_question
from .services.ai_evaluation_service import evaluate_answer
from .services.ai_report_service import generate_interview_report
from .services.pdf_report_service import generate_report_pdf
from .constants import PLAN_LIMITS


from apps.job_descriptions.models import JobDescription


# PLAN_LIMITS = {
#     "FREE": {"duration": 300, "questions": 5, "interviews": 100},
#     "SINGLE": {"duration": 600, "questions": None, "interviews": 1},
#     "PRO": {"duration": 900, "questions": None, "interviews": 10},
#     "PREMIUM": {"duration": 900, "questions": None, "interviews": 16},
# }


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_interview(request):

    plan = request.user.plan
    limits = PLAN_LIMITS[plan]

    month_start = timezone.now().replace(day=1)

    count = InterviewSession.objects.filter(
        user=request.user,
        status="completed",
        created_at__gte=month_start
    ).count()

    # if limits.get("interviews_per_month") and count >= limits.get("interviews_per_month"):
    #     raise PermissionDenied("Monthly interview limit reached.")
    
    limit = limits.get("interviews_per_month")

    if limit and count >= limit:
        return Response(
            {"error": "Monthly interview limit reached"},
            status=403
        )

    serializer = InterviewStartSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    jd_id = serializer.validated_data["jd_id"]
    interview_type = serializer.validated_data["interview_type"]

    user = request.user

    try:
        jd = JobDescription.objects.get(id=jd_id, user=user)
    except JobDescription.DoesNotExist:
        return Response({"error": "JD not found"}, status=404)

    plan = user.plan

    plan_limits = PLAN_LIMITS.get(plan)

    if not plan_limits:
        return Response({"error": "Invalid plan"}, status=400)

    interview_count = InterviewSession.objects.filter(
        user=user,
        created_at__month=timezone.now().month
    ).count()

    if interview_count >= plan_limits["interviews_per_month"]:
        return Response(
            {"error": "Interview limit reached for your plan"},
            status=403
        )

    session = InterviewSession.objects.create(
        user=user,
        jd=jd,
        interview_type=interview_type,
        status="created"
    )

    session.status = "in_progress"
    session.started_at = timezone.now()
    session.save()

    return Response(
        {
            "session_id": session.id,
            "duration_seconds": plan_limits["duration_minutes"],
            "question_limit": plan_limits["max_questions"]
        }
    )


class GenerateQuestionView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, interview_id):

        

        interview = InterviewSession.objects.get(
            id=interview_id,
            user=request.user
        )

        # PLAN CHECK
        plan = request.user.plan
        limits = PLAN_LIMITS[plan]

        question_count = interview.questions.count()

        if limits["max_questions"] and question_count >= limits["max_questions"]:
            raise PermissionDenied("Question limit reached for your plan.")
        
        # TIME LIMIT
        duration_limit = limits["duration_minutes"]

        if timezone.now() > interview.started_at + timedelta(minutes=duration_limit):
            raise PermissionDenied("Interview time expired.")

        # previous_questions = list(
        #     interview.questions.values_list("question_text", flat=True)
        # )

        # question_text = generate_question(
        #     interview.jd.job_role,
        #     interview.interview_type,
        #     previous_questions
        # )

        answers = InterviewAnswer.objects.filter(
            question__interview=interview
        ).select_related("question").order_by("created_at")

        question_text = generate_question(
            interview,
            answers,
            "medium"
        )

        question = InterviewQuestion.objects.create(
            interview=interview,
            question_text=question_text,
            order=interview.questions.count() + 1
        )

        # answers = InterviewAnswer.objects.filter(
        #     question__interview=interview
        # ).order_by("created_at")

        # question_text = generate_question(interview, answers)

        return Response({
            "question_id": question.id,
            "question": question.question_text,
            "order": question.order
        })
    


# class SubmitAnswerView(APIView):

#     permission_classes = [IsAuthenticated]

#     def post(self, request, interview_id):

#         question_id = request.data.get("question_id")
#         answer_text = request.data.get("answer")

#         question = InterviewQuestion.objects.get(
#             id=question_id,
#             interview_id=interview_id
#         )

#         evaluation = evaluate_answer(
#             question.question_text,
#             answer_text
#         )

#         answers = InterviewAnswer.objects.create(
#         question=question,
#         answer_text=answer_text,
#         ai_score=evaluation.get("score"),
#         feedback=evaluation.get("feedback")
# )

#         # answers = InterviewAnswer.objects.filter(
#         #     question__interview=interview
#         # )

#         answers = InterviewAnswer.objects.select_related("question").filter(
#             question__interview=interview
#         )

#         interview = InterviewSession.objects.get(
#         id=interview_id,
#         user=request.user
# )

#         avg_score = answers.aggregate(
#             Avg("ai_score")
#         )["ai_score__avg"] or 0

#         # return Response({
#         #     "message": "Answer submitted",
#         #     "evaluation": evaluation
#         # })
#         # GENERATE NEXT QUESTION
#         answers = InterviewAnswer.objects.filter(
#             question__interview=interview
#         ).select_related("question").order_by("created_at")

#         next_question_text = generate_question(
#             interview,
#             answers,
#             "medium"
#         )

#         next_question = InterviewQuestion.objects.create(
#             interview=interview,
#             question_text=next_question_text,
#             order=interview.questions.count() + 1
#         )

#         return Response({
#             "evaluation": evaluation,
#             "question_id": next_question.id,
#             "next_question": next_question.question_text
#         })

class SubmitAnswerView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, interview_id):

        question_id = request.data.get("question_id")
        answer_text = request.data.get("answer")

        # GET INTERVIEW
        interview = InterviewSession.objects.get(
            id=interview_id,
            user=request.user
        )

        # GET QUESTION
        question = InterviewQuestion.objects.get(
            id=question_id,
            interview=interview
        )

        # AI EVALUATION
        evaluation = evaluate_answer(
            question.question_text,
            answer_text
        )

        # SAVE ANSWER
        InterviewAnswer.objects.create(
            question=question,
            answer_text=answer_text
        )

        # GET ALL ANSWERS
        answers = InterviewAnswer.objects.filter(
            question__interview=interview
        ).select_related("question").order_by("created_at")

        # GENERATE NEXT QUESTION
        next_question_text = generate_question(
            interview,
            answers,
            "medium"
        )

        next_question = InterviewQuestion.objects.create(
            interview=interview,
            question_text=next_question_text,
            order=interview.questions.count() + 1
        )

        return Response({
            "evaluation": evaluation,
            "question_id": next_question.id,
            "next_question": next_question.question_text
        })
    

# class InterviewReportView(APIView):

#     permission_classes = [IsAuthenticated]

#     def get(self, request, interview_id):

#         interview = InterviewSession.objects.get(
#             id=interview_id,
#             user=request.user
#         )

#         # answers = InterviewAnswer.objects.filter(
#         #     question__interview=interview
#         # )

#         answers = InterviewAnswer.objects.select_related("question").filter(
#             question__interview=interview
#         )

#         transcript = ""

#         for ans in answers:
#             transcript += f"\nQuestion: {ans.question.question_text}"
#             transcript += f"\nAnswer: {ans.answer_text}\n"

#         ai_report = generate_interview_report(transcript)

#         # report = InterviewReport.objects.create(
#         #     interview=interview,
#         #     strengths=ai_report,
#         #     weaknesses="",
#         #     suggestions=""
#         # )
#         report, created = InterviewReport.objects.get_or_create(
#             interview=interview
#         )

#         report.overall_score = ai_report.get("overall_score")
#         report.technical_score = ai_report.get("technical_score")
#         report.communication_score = ai_report.get("communication_score")
#         report.strengths = ai_report.get("strengths")
#         report.weaknesses = ai_report.get("weaknesses")
#         report.suggestions = ai_report.get("suggestions")
#         report.save()

#         return Response({
#             "interview_id": interview.id,
#             "report": ai_report
#         })
    
class InterviewReportView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, interview_id):

        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=401
            )

        interview = InterviewSession.objects.get(
            id=interview_id,
            user=request.user.id
        )

        answers = InterviewAnswer.objects.select_related("question").filter(
            question__interview=interview
        )

        transcript = ""

        for ans in answers:
            transcript += f"\nQuestion: {ans.question.question_text}"
            transcript += f"\nAnswer: {ans.answer_text}\n"

        ai_report = generate_interview_report(transcript)

        # If AI returned string convert to dict safely
        if isinstance(ai_report, str):

            report_data = {
                "overall_score": 0,
                "technical_score": 0,
                "communication_score": 0,
                "strengths": ai_report,
                "weaknesses": "",
                "suggestions": ""
            }

        else:
            report_data = ai_report

        report, created = InterviewReport.objects.get_or_create(
            interview=interview
        )

        report.overall_score = report_data.get("overall_score", 0)
        report.technical_score = report_data.get("technical_score", 0)
        report.communication_score = report_data.get("communication_score", 0)
        report.strengths = report_data.get("strengths", "")
        report.weaknesses = report_data.get("weaknesses", "")
        report.suggestions = report_data.get("suggestions", "")

        report.save()

        # -------------------------
        # Calculate Interview Score
        # -------------------------

        avg_ai_score = answers.aggregate(
            Avg("ai_score")
        )["ai_score__avg"] or 0

        # Example rule score
        rule_score = avg_ai_score * 0.9

        final_score = (avg_ai_score * 0.6) + (rule_score * 0.4)

        Score.objects.update_or_create(
            session=interview,
            defaults={
                "technical_score": report.technical_score,
                "communication_score": report.communication_score,
                "relevance_score": avg_ai_score,
                "confidence_score": avg_ai_score,
                "problem_solving_score": avg_ai_score,
                "ai_score": avg_ai_score,
                "rule_score": rule_score,
                "final_score": final_score,
                "feedback": report.strengths,
            }
        )

        # Mark interview completed
        interview.status = "completed"
        interview.save()

        return Response({
            "interview_id": interview.id,
            "report": report_data,
            "final_score": final_score
        })
    


class InterviewHistoryView(ListAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = InterviewHistorySerializer

    def get_queryset(self):
        return InterviewSession.objects.filter(
            user=self.request.user
        ).order_by("-created_at")
    

class InterviewTranscriptView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, interview_id):

        interview = InterviewSession.objects.get(
            id=interview_id,
            user=request.user
        )

        answers = InterviewAnswer.objects.filter(
            question__interview=interview
        )

        transcript = []

        for ans in answers:

            transcript.append({
                "question": ans.question.question_text,
                "answer": ans.answer_text,
                "score": ans.ai_score,
                "feedback": ans.feedback
            })

        return Response({
            "interview_id": interview.id,
            "transcript": transcript
        })
    

class DownloadReportView(APIView):

    permission_classes = [IsAuthenticated]

    # def get(self, request, interview_id):

    #     report = InterviewReport.objects.get(
    #         interview_id=interview_id,
    #         interview__user=request.user
    #     )

    #     pdf = generate_report_pdf(report, interview)

    #     return FileResponse(
    #         pdf,
    #         as_attachment=True,
    #         filename="interview_report.pdf"
    #     )
    def get(self, request, interview_id):

        interview = InterviewSession.objects.get(
            id=interview_id,
            user=request.user
        )

        report = InterviewReport.objects.get(
            interview=interview
        )

        pdf_buffer = generate_report_pdf(report, interview)

        response = HttpResponse(
            pdf_buffer,
            content_type="application/pdf"
        )

        response["Content-Disposition"] = f'attachment; filename="interview_report_{interview_id}.pdf"'

        return response