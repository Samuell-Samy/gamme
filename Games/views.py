# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q
import json
from .models import Folder, Game

def index(request):
    return render(request, "index.html")

def home(request):
    """Home page view for regular users to browse games and folders"""
    folders = Folder.objects.all().order_by("name")
    return render(request, "home.html", {"folders": folders})

def game_detail(request, game_id: int):
    """Public game detail view for regular users"""
    try:
        game = get_object_or_404(Game, pk=game_id)
        folders = list(game.folders.all())
        return render(request, 'game_detail.html', {
            'game': game,
            'folders': folders,
        })
    except Game.DoesNotExist:
        return render(request, 'game_detail.html', {
            'error': 'Game not found'
        })
def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        if not username or not password:
            return render(request, "login.html", {"error": "Username and password are required."})

        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(request, "login.html", {"error": "Invalid username or password."})

        if not user.is_superuser:
            return render(request, "login.html", {"error": "Only superusers are allowed to sign in here."})

        auth_login(request, user)
        return redirect("admin_dashboard")

    return render(request, "login.html")

@user_passes_test(lambda u: u.is_authenticated and u.is_superuser, login_url='login')
def admin_dashboard(request):
    folders = Folder.objects.all()
    games = Game.objects.all()
    return render(request, "admin_Dash.html", {
        "folders": folders,
        "folder_count": folders.count(),
        "game_count": games.count()
    })

@user_passes_test(lambda u: u.is_authenticated and u.is_superuser, login_url='login')
def admin_panel(request):
    folders = Folder.objects.all()
    return render(request, "admin.html", {"folders": folders})

@user_passes_test(lambda u: u.is_authenticated and u.is_superuser, login_url='login')
def admin_game_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        number_of_players = request.POST.get('number_of_players', '').strip()
        time = request.POST.get('time', '').strip()
        materials = request.POST.get('materials', '').strip() or None
        description = request.POST.get('description', '').strip()
        video_link = request.POST.get('video_link', '').strip() or None
        folder_ids = request.POST.getlist('folder_ids')

        if not name or not number_of_players or not time:
            folders = Folder.objects.all()
            error = 'Name, Number of Players, and Time are required.'
            return render(request, 'admin_game_form.html', {'folders': folders, 'error': error, 'form': request.POST})

        game = Game.objects.create(
            name=name,
            number_of_players=number_of_players,
            time=time,
            materials=materials,
            description=description,
            video_link=video_link,
        )
        if folder_ids:
            valid_folders = Folder.objects.filter(id__in=folder_ids)
            game.folders.set(valid_folders)
        return redirect('admin_panel')

    folders = Folder.objects.all()
    return render(request, 'admin_game_form.html', {'folders': folders})

@user_passes_test(lambda u: u.is_authenticated and u.is_superuser, login_url='login')
def admin_game_detail(request, game_id: int):
    game = get_object_or_404(Game, pk=game_id)
    folders = list(game.folders.all())
    return render(request, 'admin_game_detail.html', {
        'game': game,
        'folders': folders,
    })

# ------------------------ JSON API (Superuser only) ------------------------ #

def _is_superuser(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(_is_superuser, login_url='login')
@require_http_methods(["GET", "POST"])
def api_folders(request):
    if request.method == "GET":
        data = [{"id": f.id, "name": f.name} for f in Folder.objects.all().order_by("name")]
        return JsonResponse(data, safe=False)

    # POST create
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    name = (payload.get("name") or "").strip()
    if not name:
        return JsonResponse({"error": "'name' is required"}, status=400)

    folder, created = Folder.objects.get_or_create(name=name)
    return JsonResponse({"id": folder.id, "name": folder.name}, status=201 if created else 200)

@user_passes_test(_is_superuser, login_url='login')
@require_http_methods(["GET"])
def api_folder_games(request, folder_id: int):
    try:
        folder = Folder.objects.get(pk=folder_id)
    except Folder.DoesNotExist:
        return JsonResponse({"error": "Folder not found"}, status=404)

    games = folder.games.all().order_by("name")
    data = [
        {
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "materials": g.materials or "",
            "number_of_players": g.number_of_players,
            "time": g.time,
            "video_link": g.video_link or "",
            "folder_ids": list(g.folders.values_list("id", flat=True)),
        }
        for g in games
    ]
    return JsonResponse(data, safe=False)

@user_passes_test(_is_superuser, login_url='login')
@require_http_methods(["POST"])
def api_games(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    name = (payload.get("name") or "").strip()
    description = (payload.get("description") or "").strip()
    materials = (payload.get("materials") or "").strip() or None
    number_of_players = (payload.get("number_of_players") or "").strip()
    time = (payload.get("time") or "").strip()
    video_link = (payload.get("video_link") or "").strip() or None
    folder_ids = payload.get("folder_ids") or []

    if not name:
        return JsonResponse({"error": "'name' is required"}, status=400)
    if not number_of_players:
        return JsonResponse({"error": "'number_of_players' is required"}, status=400)
    if not time:
        return JsonResponse({"error": "'time' is required"}, status=400)

    game = Game.objects.create(
        name=name,
        description=description,
        materials=materials,
        number_of_players=number_of_players,
        time=time,
        video_link=video_link,
    )

    if folder_ids:
        valid_folders = Folder.objects.filter(id__in=folder_ids)
        game.folders.set(valid_folders)

    return JsonResponse({
        "id": game.id,
        "name": game.name,
        "description": game.description,
        "materials": game.materials or "",
        "number_of_players": game.number_of_players,
        "time": game.time,
        "video_link": game.video_link or "",
        "folder_ids": list(game.folders.values_list("id", flat=True)),
    }, status=201)

@user_passes_test(_is_superuser, login_url='login')
@require_http_methods(["GET", "PUT", "PATCH", "DELETE"])
def api_game_detail(request, game_id: int):
    try:
        game = Game.objects.get(pk=game_id)
    except Game.DoesNotExist:
        return JsonResponse({"error": "Game not found"}, status=404)

    if request.method == "GET":
        return JsonResponse({
            "id": game.id,
            "name": game.name,
            "description": game.description,
            "materials": game.materials or "",
            "number_of_players": game.number_of_players,
            "time": game.time,
            "video_link": game.video_link or "",
            "folder_ids": list(game.folders.values_list("id", flat=True)),
        })

    if request.method in ("PUT", "PATCH"):
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except Exception:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        if "name" in payload:
            game.name = (payload.get("name") or "").strip() or game.name
        if "description" in payload:
            game.description = (payload.get("description") or "").strip()
        if "materials" in payload:
            materials = (payload.get("materials") or "").strip()
            game.materials = materials or None
        if "number_of_players" in payload:
            game.number_of_players = (payload.get("number_of_players") or "").strip() or game.number_of_players
        if "time" in payload:
            game.time = (payload.get("time") or "").strip() or game.time
        if "video_link" in payload:
            link = (payload.get("video_link") or "").strip()
            game.video_link = link or None
        game.save()

        if "folder_ids" in payload:
            ids = payload.get("folder_ids") or []
            valid_folders = Folder.objects.filter(id__in=ids)
            game.folders.set(valid_folders)

        return JsonResponse({"ok": True})

    # DELETE
    game.delete()
    return JsonResponse({"ok": True})

@user_passes_test(_is_superuser, login_url='login')
@require_http_methods(["GET"])
def api_search_games(request):
    """Search games across all folders by name, description, materials, etc."""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({"error": "Query parameter 'q' is required"}, status=400)
    
    # Search across multiple fields using Q objects for OR logic
    search_filter = Q(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(materials__icontains=query) |
        Q(number_of_players__icontains=query) |
        Q(time__icontains=query)
    )
    
    games = Game.objects.filter(search_filter).order_by("name")
    
    data = [
        {
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "materials": g.materials or "",
            "number_of_players": g.number_of_players,
            "time": g.time,
            "video_link": g.video_link or "",
            "folder_ids": list(g.folders.values_list("id", flat=True)),
            "folder_names": [f.name for f in g.folders.all()],
        }
        for g in games
    ]
    
    return JsonResponse({
        "results": data,
        "query": query,
        "count": len(data)
    }, safe=False)

@require_http_methods(["GET"])
def api_public_folder_games(request, folder_id: int):
    """Public API endpoint for regular users to fetch games from a folder"""
    try:
        folder = Folder.objects.get(pk=folder_id)
    except Folder.DoesNotExist:
        return JsonResponse({"error": "Folder not found"}, status=404)

    games = folder.games.all().order_by("name")
    data = [
        {
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "materials": g.materials or "",
            "number_of_players": g.number_of_players,
            "time": g.time,
            "video_link": g.video_link or "",
        }
        for g in games
    ]
    return JsonResponse(data, safe=False)

@require_http_methods(["GET"])
def api_public_search_games(request):
    """Public search API endpoint for regular users to search games across all folders"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({"error": "Query parameter 'q' is required"}, status=400)
    
    # Search across multiple fields using Q objects for OR logic
    search_filter = Q(
        Q(name__icontains=query) |
        Q(description__icontains=query) |
        Q(materials__icontains=query) |
        Q(number_of_players__icontains=query) |
        Q(time__icontains=query)
    )
    
    games = Game.objects.filter(search_filter).order_by("name")
    
    data = [
        {
            "id": g.id,
            "name": g.name,
            "description": g.description,
            "materials": g.materials or "",
            "number_of_players": g.number_of_players,
            "time": g.time,
            "video_link": g.video_link or "",
            "folder_names": [f.name for f in g.folders.all()],
        }
        for g in games
    ]
    
    return JsonResponse({
        "results": data,
        "query": query,
        "count": len(data)
    }, safe=False)

