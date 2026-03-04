from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import JobDescription
from .serializers import JobDescriptionSerializer
from django.shortcuts import get_object_or_404
import re


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_job_descriptions(request):

    jds = JobDescription.objects.filter(user=request.user)

    serializer = JobDescriptionSerializer(jds, many=True)

    return Response(serializer.data)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_job_description(request):

    role = request.data.get("role")
    jd_text = request.data.get("original_text", "").lower()

    role_keywords = {
        "BACKEND": ["api", "database", "server", "backend"],
        "FRONTEND": ["ui", "react", "css", "frontend"],
        "FULLSTACK": ["frontend", "backend", "fullstack"],
        "DATA": ["machine learning", "data analysis", "python", "pandas"],
        "DEVOPS": ["docker", "kubernetes", "ci/cd"],
    }

    keywords = role_keywords.get(role, [])

    if not any(k in jd_text for k in keywords):
        return Response(
            {"error": f"This job description does not appear to match the selected role ({role})."},
            status=400
        )

    serializer = JobDescriptionSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data)

    return Response(serializer.errors, status=400)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_job_description(request, pk):

    jd = get_object_or_404(JobDescription, id=pk, user=request.user)

    jd.delete()

    return Response({"message": "Deleted successfully"})


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_job_description(request, pk):

    jd = JobDescription.objects.get(id=pk, user=request.user)

    serializer = JobDescriptionSerializer(jd, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)

    return Response(serializer.errors, status=400)