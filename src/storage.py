import json

from pathlib import Path
from datetime import date


from models import Usuario, Habito

DATA_FILE = Path(__file__).parent /"data"/"usuarios.json"

def cargar_usuarios():
    
    if not DATA_FILE.exists():
        return {}
    try:
        with open(DATA_FILE,'r',encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print("Error al decodificar el archivo JSON. Se devolverá un diccionario vacío.")
        return {}

    usuarios = {}
    
    for user_id,info in  data.items():
        usuario = Usuario(
                user_id=user_id,
                nombre=info.get("nombre","Anonimo")
                )
        for nombre_habito, habito_data in info.get("habitos",{}).items():
            
            habito = Habito(nombre_habito)
            
            habito.creado = habito_data["creado"]
            habito.checks = habito_data["checks"]
            
            usuario.habitos[nombre_habito] = habito
        usuarios[user_id] = usuario
    
    return usuarios

def guardar_usuarios(usuarios):
    """
        Convierte los objetos a diccionario plano y los escribe en JSON.
        indent=2 hace el JSON legible. ensure_ascii=False permite tildes.
        """
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    data = {}
    
    for user_id, usuario in usuarios.items():
            data[user_id] = {
            "nombre": usuario.nombre,
            "habitos": {
                    nombre: {
                        "creado": habito.creado,
                        "checks": habito.checks,
                    }
                for nombre, habito in usuario.habitos.items()
                },
            }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)