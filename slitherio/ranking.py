import json
import os

FILE = "ranking.json"

def load():
    """Carga el ranking desde el archivo JSON"""
    if not os.path.exists(FILE):
        return []
    try:
        with open(FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save(name, score):
    """Guarda un nuevo score en el ranking"""
    if not name or score < 0:
        return
    
    ranking = load()
    ranking.append({"name": name, "score": int(score)})
    ranking = sorted(ranking, key=lambda x: x["score"], reverse=True)[:10]
    
    try:
        with open(FILE, 'w', encoding='utf-8') as f:
            json.dump(ranking, f, indent=2, ensure_ascii=False)
    except IOError as e:
        print(f"Error al guardar ranking: {e}")

def get_top_scores(limit=10):
    """Obtiene los mejores scores"""
    ranking = load()
    return ranking[:limit]