"""
deadline_tracker/views.py
─────────────────────────
Endpoints:

  GET    /api/deadlines/                  → list all universities (sorted by deadline)
  GET    /api/deadlines/<university_id>/  → single university with full computed fields
  GET    /api/deadlines/summary/          → aggregated counts + next deadline
  POST   /api/deadlines/upload/           → upload an Excel file → import universities
  GET    /api/deadlines/uploads/          → history of uploads
  DELETE /api/deadlines/<university_id>/  → remove a university
  POST   /api/deadlines/clear/            → wipe ALL universities (use with care)

Reading is public; uploading, deleting, clearing and upload history are admin-only (is_staff).
"""

from __future__ import annotations

import os
import tempfile

from django.db.models import QuerySet
from rest_framework import permissions, status
from rest_framework.authentication import SessionAuthentication
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ExcelUpload, University
from .serializers import (
    DeadlineSummarySerializer,
    ExcelUploadSerializer,
    UniversitySerializer,
)
from .services import parse_and_import


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return


class AdminOnlyMixin:
    """Only staff/admin users may call these endpoints."""
    authentication_classes = [CsrfExemptSessionAuthentication]
    permission_classes = [permissions.IsAdminUser]


# ── helpers ───────────────────────────────────────────────────────────────────

def _sorted_universities() -> QuerySet:
    """Return all universities ordered by deadline (soonest first)."""
    return University.objects.all().order_by("deadline")


def _priority_counts(qs: QuerySet) -> dict:
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "expired": 0}
    for u in qs:
        counts[u.priority] += 1
    return counts


# ── views ─────────────────────────────────────────────────────────────────────

class UniversityListView(APIView):
    """
    GET  /api/deadlines/
    Returns all universities sorted by deadline with computed fields.

    Query params:
      ?priority=critical|high|medium|low|expired   filter by priority
      ?search=<text>                               filter by name / city
    """

    def get(self, request: Request) -> Response:
        qs = _sorted_universities()

        priority_filter = request.query_params.get("priority", "").strip().lower()
        search = request.query_params.get("search", "").strip()

        if search:
            qs = qs.filter(name__icontains=search) | qs.filter(city__icontains=search)

        unis = list(qs)

        # priority filter happens in Python (it's a computed property)
        if priority_filter:
            unis = [u for u in unis if u.priority == priority_filter]

        # sort by priority_order then days_remaining
        unis.sort(key=lambda u: (u.priority_order, u.days_remaining))

        return Response(
            {
                "count": len(unis),
                "universities": UniversitySerializer(unis, many=True).data,
            }
        )


class UniversityDetailView(APIView):
    """
    GET    /api/deadlines/<university_id>/
    DELETE /api/deadlines/<university_id>/   (admin only)
    """
    authentication_classes = [CsrfExemptSessionAuthentication]

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [permissions.IsAdminUser()]
        return [permissions.AllowAny()]

    def _get_obj(self, university_id: str):
        try:
            return University.objects.get(university_id=university_id)
        except University.DoesNotExist:
            return None

    def get(self, request: Request, university_id: str) -> Response:
        u = self._get_obj(university_id)
        if u is None:
            return Response(
                {"error": f"University '{university_id}' not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(UniversitySerializer(u).data)

    def delete(self, request: Request, university_id: str) -> Response:
        u = self._get_obj(university_id)
        if u is None:
            return Response(
                {"error": f"University '{university_id}' not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        u.delete()
        return Response(
            {"message": f"University '{university_id}' deleted."},
            status=status.HTTP_200_OK,
        )


class DeadlineSummaryView(APIView):
    """
    GET /api/deadlines/summary/

    Returns:
    {
      "total": 4,
      "critical": 1,
      "high": 1,
      "medium": 1,
      "low": 1,
      "expired": 0,
      "next_deadline": { ...university object... },
      "universities": [ ...all sorted by priority then days... ]
    }
    """

    def get(self, request: Request) -> Response:
        all_unis = list(_sorted_universities())

        # sort: expired last, then by days_remaining ascending
        active = [u for u in all_unis if u.days_remaining >= 0]
        expired = [u for u in all_unis if u.days_remaining < 0]
        active.sort(key=lambda u: u.days_remaining)

        next_deadline = active[0] if active else None
        counts = _priority_counts(all_unis)

        payload = {
            "total": len(all_unis),
            **counts,
            "next_deadline": next_deadline,
            "universities": sorted(
                all_unis, key=lambda u: (u.priority_order, u.days_remaining)
            ),
        }

        serializer = DeadlineSummarySerializer(payload)
        return Response(serializer.data)


class ExcelUploadView(AdminOnlyMixin, APIView):
    """
    POST /api/deadlines/upload/
    Accepts multipart/form-data with field `file` (.xlsx).

    Returns import summary:
    {
      "status": "success" | "partial" | "error",
      "rows_imported": 4,
      "rows_skipped": 0,
      "errors": [],
      "universities": [...],
      "upload_id": 1
    }
    """

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request: Request) -> Response:
        uploaded_file = request.FILES.get("file")

        if not uploaded_file:
            return Response(
                {"error": "No file provided. Send a .xlsx file in field 'file'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        filename = uploaded_file.name
        if not filename.lower().endswith((".xlsx", ".xlsm")):
            return Response(
                {"error": "Only .xlsx / .xlsm files are accepted."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Save upload record
        upload_record = ExcelUpload.objects.create(
            file=uploaded_file,
            original_filename=filename,
        )

        # Write to a temp file so openpyxl can open it
        suffix = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            for chunk in uploaded_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            result = parse_and_import(tmp_path, upload_record=upload_record)
        finally:
            os.unlink(tmp_path)

        if result.imported == 0 and result.errors:
            http_status = status.HTTP_400_BAD_REQUEST
            outcome = "error"
        elif result.errors:
            http_status = status.HTTP_200_OK
            outcome = "partial"
        else:
            http_status = status.HTTP_200_OK
            outcome = "success"

        return Response(
            {
                "status": outcome,
                "rows_imported": result.imported,
                "rows_skipped": result.skipped,
                "errors": result.errors,
                "upload_id": upload_record.id,
                "universities": UniversitySerializer(
                    result.universities, many=True
                ).data,
            },
            status=http_status,
        )


class UploadHistoryView(AdminOnlyMixin, APIView):
    """GET /api/deadlines/uploads/  — list all past uploads."""

    def get(self, request: Request) -> Response:
        uploads = ExcelUpload.objects.all().order_by("-uploaded_at")[:50]
        return Response(ExcelUploadSerializer(uploads, many=True).data)


class ClearAllView(AdminOnlyMixin, APIView):
    """
    POST /api/deadlines/clear/
    Deletes ALL university records. Useful before a fresh import.
    Body: { "confirm": true }
    """

    parser_classes = [JSONParser]

    def post(self, request: Request) -> Response:
        if not request.data.get("confirm"):
            return Response(
                {"error": "Send { \"confirm\": true } to wipe all universities."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        deleted, _ = University.objects.all().delete()
        return Response({"message": f"Deleted {deleted} university records."})


class DBStatusView(APIView):
    """
    GET /api/deadlines/db-status/
    Quick health-check so the frontend knows whether data exists.

    Returns:
    {
      "populated": true,
      "university_count": 8,
      "message": "OK"          // or "Database is empty — please upload an Excel file."
    }
    """

    def get(self, request: Request) -> Response:
        count = University.objects.count()
        populated = count > 0
        return Response({
            "populated": populated,
            "university_count": count,
            "message": "OK" if populated else (
                "Database is empty — please upload universities_deadlines.xlsx "
                "via POST /api/deadlines/upload/ or run: "
                "python manage.py import_deadlines universities_deadlines.xlsx"
            ),
        })