from django.urls import path
from .views import start_interview, GenerateQuestionView, SubmitAnswerView, InterviewReportView
from .views import InterviewHistoryView, InterviewTranscriptView, DownloadReportView

urlpatterns = [
    path("start/", start_interview),
    path(
        "<int:interview_id>/question/",
        GenerateQuestionView.as_view(),
        name="generate-question"
    ),
    # path("<int:session_id>/question/", get_question),
    path(
        "<int:interview_id>/answer/",
        SubmitAnswerView.as_view(),
        name="submit-answer"
    ),
    path(
        "<int:interview_id>/report/",
        InterviewReportView.as_view(),
        name="interview-report"
    ),
    path(
        "",
        InterviewHistoryView.as_view(),
        name="interview-history"
    ),
    path(
        "<int:interview_id>/transcript/",
        InterviewTranscriptView.as_view(),
        name="interview-transcript"
    ),
    path(
        "<int:interview_id>/report/download/",
        DownloadReportView.as_view(),
        name="download-report"
    ),
]