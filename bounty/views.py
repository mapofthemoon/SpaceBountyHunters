import json
from decimal import Decimal, InvalidOperation
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.core.exceptions import ValidationError

from .models import WantedCriminal, HuntLog


# Convert a criminal into JSON-friendly data
def criminal_to_dict(criminal):
    return {
        "id": criminal.id,
        "name": criminal.name,
        "nickname": criminal.nickname,
        "reward": str(criminal.reward),
        "latitude": criminal.latitude,
        "longitude": criminal.longitude,
        "last_known_note": criminal.last_known_note,
        "difficulty": criminal.difficulty,
        "armed": criminal.armed,
        "has_crew": criminal.has_crew,
        "escape_master": criminal.escape_master,
    }


# Convert a hunt log into JSON-friendly data
def hunt_to_dict(hunt):
    return {
        "id": hunt.id,
        "criminal_id": hunt.criminal_id,
        "success": hunt.success,
        "notes": hunt.notes,
        "created_at": hunt.created_at.isoformat(),
    }


# Read JSON submitted by Postman
def read_json(request):
    try:
        data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return None, "Invalid JSON."

    if not isinstance(data, dict):
        return None, "JSON body must be an object."

    return data, None


# ========================================
# WANTED CRIMINALS
# ========================================

# GET /api/criminals/
def criminal_list(request):

    if request.method != "GET":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    criminals = WantedCriminal.objects.all()

    # Minimum and maximum reward filters
    for parameter in ["min_reward", "max_reward"]:

        value = request.GET.get(parameter)

        if value is not None:
            try:
                amount = Decimal(value)

                if not amount.is_finite() or amount < 0:
                    raise ValueError()

            except (InvalidOperation, ValueError):
                return JsonResponse(
                    {"error": f"Invalid {parameter}"},
                    status=400
                )

            if parameter == "min_reward":
                criminals = criminals.filter(
                    reward__gte=amount
                )
            else:
                criminals = criminals.filter(
                    reward__lte=amount
                )

    # Boolean filters
    for field in ["armed", "has_crew", "escape_master"]:

        value = request.GET.get(field)

        if value is not None:

            if value.lower() not in ["true", "false"]:
                return JsonResponse(
                    {"error": f"{field} must be true or false"},
                    status=400
                )

            criminals = criminals.filter(
                **{field: value.lower() == "true"}
            )

    # Sorting
    sort = request.GET.get("sort")

    if sort:
        if sort not in ["reward", "-reward"]:
            return JsonResponse(
                {"error": "Sort must be reward or -reward"},
                status=400
            )

        criminals = criminals.order_by(sort)
    else:
        criminals = criminals.order_by("id")

    return JsonResponse({
        "criminals": [
            criminal_to_dict(c)
            for c in criminals
        ]
    })


# GET /api/criminals/<id>/
def criminal_detail(request, criminal_id):

    if request.method != "GET":
        return JsonResponse(
            {"error": "Method not allowed"},
            status=405
        )

    criminal = WantedCriminal.objects.filter(
        id=criminal_id
    ).first()

    if criminal is None:
        return JsonResponse(
            {"error": "Criminal not found"},
            status=404
        )

    return JsonResponse(criminal_to_dict(criminal))


# ========================================
# HUNT JOURNAL
# ========================================

# GET list or POST new hunt
@csrf_exempt
def hunt_list(request):

    if request.method == "GET":

        hunts = HuntLog.objects.all().order_by("id")

        criminal_id = request.GET.get("criminal_id")

        if criminal_id is not None:

            if not criminal_id.isdigit() or int(criminal_id) < 1:
                return JsonResponse(
                    {"error": "Invalid criminal_id"},
                    status=400
                )

            hunts = hunts.filter(
                criminal_id=int(criminal_id)
            )

        return JsonResponse({
            "hunts": [
                hunt_to_dict(h)
                for h in hunts
            ]
        })

    elif request.method == "POST":

        data, error = read_json(request)

        if error:
            return JsonResponse(
                {"error": error},
                status=400
            )

        required = ["criminal_id", "success", "notes"]

        for field in required:
            if field not in data:
                return JsonResponse(
                    {"error": f"Missing field: {field}"},
                    status=400
                )

        if set(data) != set(required):
            return JsonResponse(
                {"error": "Only criminal_id, success and notes are allowed"},
                status=400
            )

        criminal_id = data["criminal_id"]

        if (
            type(criminal_id) is not int
            or criminal_id < 1
        ):
            return JsonResponse(
                {"error": "criminal_id must be a positive integer"},
                status=400
            )

        criminal = WantedCriminal.objects.filter(
            id=criminal_id
        ).first()

        if criminal is None:
            return JsonResponse(
                {"error": "Criminal does not exist"},
                status=400
            )

        if type(data["success"]) is not bool:
            return JsonResponse(
                {"error": "success must be true or false"},
                status=400
            )

        if not isinstance(data["notes"], str):
            return JsonResponse(
                {"error": "notes must be text"},
                status=400
            )

        hunt = HuntLog(
            criminal=criminal,
            success=data["success"],
            notes=data["notes"]
        )

        try:
            hunt.full_clean()
        except ValidationError as error:
            return JsonResponse(
                {"error": error.message_dict},
                status=400
            )

        hunt.save()

        return JsonResponse(
            hunt_to_dict(hunt),
            status=201
        )

    return JsonResponse(
        {"error": "Method not allowed"},
        status=405
    )

@csrf_exempt
def hunt_detail(request, hunt_id):

    hunt = HuntLog.objects.filter(
        id=hunt_id
    ).first()

    if hunt is None:
        return JsonResponse(
            {"error": "Hunt log not found"},
            status=404
        )

    if request.method == "GET":
        return JsonResponse(hunt_to_dict(hunt))

    elif request.method == "PATCH":

        data, error = read_json(request)

        if error:
            return JsonResponse(
                {"error": error},
                status=400
            )

        if not data:
            return JsonResponse(
                {"error": "No fields provided"},
                status=400
            )

        if not set(data).issubset({"success", "notes"}):
            return JsonResponse(
                {"error": "Only success and notes can be updated"},
                status=400
            )

        if "success" in data:
            if type(data["success"]) is not bool:
                return JsonResponse(
                    {"error": "success must be true or false"},
                    status=400
                )

            hunt.success = data["success"]

        if "notes" in data:
            if not isinstance(data["notes"], str):
                return JsonResponse(
                    {"error": "notes must be text"},
                    status=400
                )

            hunt.notes = data["notes"]

        try:
            hunt.full_clean()
        except ValidationError as error:
            return JsonResponse(
                {"error": error.message_dict},
                status=400
            )

        hunt.save()

        return JsonResponse(hunt_to_dict(hunt))

    elif request.method == "DELETE":

        hunt.delete()
        return HttpResponse(status=204)

    return JsonResponse(
        {"error": "Method not allowed"},
        status=405
    )
