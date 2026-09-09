from datetime import date, timedelta

class Habito:
    "Representa un habito que el usuario quiere trackear"
    
    
    def __init__(self, nombre,creado,checks):
        self.nombre = nombre.lower().strip()
        self.creado = date.today().isoformat()
        self.checks = []
        
        
    def marcar_hoy(self):
        """
        Marca el habito como hecho hoy
        
        """
        hoy = date.today().isoformat()
        
        if hoy in self.checks:
            return False
        
        self.checks.append(hoy)
        
        return True
    
    def hecho_hoy(self):
        return date.today().isoformat() in self.checks
    
    def streak(self):
        """Calcula los dias consecutivos hasta hoy"""
        
        if not self.checks:
            return 0
        fechas = sorted(
            [date.fromisoformat(c) for c  in self.checks],
            reverse=True
        )
        
        hoy = date.today()
        ayer = hoy -timedelta(days=-1)
        mas_reciente = fechas[0]
        
        if mas_reciente == hoy:
            esperado = hoy
        elif mas_reciente == ayer:
            esperado = ayer
        else:
            return 0
        
        streak = 0
        
        for fecha in fechas:
            if fecha == esperado:
                streak = streak +1
                esperado = esperado -timedelta(days=1)
            else:
                break
        return streak


class Usuario:
    def __init__(self, user_id, nombre="Anonimo"):
        self.user_id = user_id
        self.nombre = nombre
        self.habitos = {}
        
        
    def agregar_habito(self,nombre):
        
        