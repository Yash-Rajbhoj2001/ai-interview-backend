from rest_framework import serializers
from .models import InterviewSession


class InterviewStartSerializer(serializers.Serializer):
    jd_id = serializers.IntegerField()
    interview_type = serializers.CharField()



# class InterviewHistorySerializer(serializers.ModelSerializer):

#     class Meta:
#         model = InterviewSession
#         fields = [
#             "id",
#             "job_role",
#             "difficulty",
#             "status",
#             "created_at"
#         ]

# class InterviewHistorySerializer(serializers.ModelSerializer):

#     job_role = serializers.CharField(source="jd.job_role", read_only=True)

#     class Meta:
#         model = InterviewSession
#         fields = [
#             "id",
#             "job_role",
#             "interview_type",
#             "status",
#             "created_at"
#         ]

class InterviewHistorySerializer(serializers.ModelSerializer):

    role = serializers.CharField(source="jd.role", read_only=True)

    final_score = serializers.FloatField(
        source="report.overall_score",
        default=0,
        read_only=True
    )

    ai_score = serializers.FloatField(
        source="report.technical_score",
        default=0,
        read_only=True
    )

    rule_score = serializers.FloatField(
        source="report.communication_score",
        default=0,
        read_only=True
    )

    duration_seconds = serializers.IntegerField(read_only=True)

    class Meta:
        model = InterviewSession
        fields = [
            "id",
            "role",
            "interview_type",
            "status",
            "created_at",
            "duration_seconds",
            "final_score",
            "ai_score",
            "rule_score"
        ]