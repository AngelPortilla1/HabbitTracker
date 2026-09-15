from storage import cargar_usuarios, guardar_usuarios
from models import Usuario, Habito

USUARIO_LOCAL = 'LOCAL'


def mostrar_menu():
    print("\n--- Menú de Hábitos ---")
    print(" =====================================")
    print(" =====================================")
    print("1. Agregar hábito")
    print("2. Marcar hábito como completado")
    print("3. Mostrar hábitos del día")
    print("4. Ver Streaks")
    print("5. Listar todos los hábitos")
    print("6. Eliminar hábito")
    print("0. Salir")
    
def obtener_usuario(usuarios):
    
    if USUARIO_LOCAL not in usuarios:
        nombre = input("Hola, ¿Como te llamas?").strip()
        
        if not nombre:
            nombre = "Anonimo"
            
        usuarios[USUARIO_LOCAL]= Usuario(USUARIO_LOCAL, nombre)
        
    return usuarios[USUARIO_LOCAL]



def comando_agregar(usuario):
    nombre_habito = input("Que habito deseas agregar hoy? ").strip()
    if not nombre_habito:
        print('Aviso : el nombre no puede estar vacio')
        return 
    try:
        usuario.agregar_habito(nombre_habito)
        print("Listo. Hábito '" + nombre_habito.lower() + "' agregado")
    except ValueError as error:
            print('Aviso '+ str(error))
            
            
def comando_check(usuario):
    if usuario.habitos == {}:
        print("No tienes hábitos para marcar. Agrega uno primero.")
        return
    else:
        nombre_habito = input("Que habito deseas agregar hoy? ").strip()
        try:
            usuario.check(nombre_habito)
            print("Habito checkeado")
        except ValueError as error:
                    print('Aviso '+ str(error))
                    
                    
def comando_hoy(usuario):
    if not usuario.habitos:
        print("No tienes hábitos registrados aún.")
        return
    print("")
    print("Hábitos de hoy (" + usuario.nombre + "): ")
    for nombre,habito in usuario.habitos.items():
        estado = "[X]" if habito.hecho_hoy() else "[ ]"
        print("  " + estado + " " + nombre)


def comando_streaks(usuario):
    if not usuario.habitos:
        print("No tienes hábitos registrados aún.")
        return
    print("")
    print("Streaks de hábitos (" + usuario.nombre + "): ")
    for nombre,habito in usuario.habitos.items():
        streak = habito.streak()
        print(f"  {nombre}: {streak} días consecutivos")
        
        
def comando_listar(usuario):
    if not usuario.habitos:
            print("No tienes hábitos registrados aún.")
            return
    print("")
    print("Todos tus habitos")
    for nombre,habito in usuario.habitos.items():
        total = len(habito.checks)
        print(
              "-" + nombre +
                " (creado: " + habito.creado + ", " +
                "total checks: " + str(total) + ")"
        )
def eliminar_habito(usuario):
    if not usuario.habitos:
        print("No tienes habitos para eliminar.")
        return 
    
    nombre = input("¿Cual desea eliminar?").strip()
    
    if not nombre:
        print("Aviso : nombre vacio")
        return
    
    if usuario.eliminar_habito(nombre):
        print("Listo. Habito '" + nombre.lower() + "' eliminado")
    else:
        print("Aviso: no se encontró ese hábito")
        
        
        
def main():
    usuarios = cargar_usuarios()
    usuario = obtener_usuario(usuarios)
    while True:
        mostrar_menu()
        opcion = input("Opción: ").strip()
        if opcion == "1":
            comando_agregar(usuario)
        elif opcion == "2":
            comando_check(usuario)
        elif opcion == "3":
            comando_hoy(usuario)
        elif opcion == "4":
            comando_streaks(usuario)
        elif opcion == "5":
            comando_listar(usuario)
        elif opcion == "6":
            eliminar_habito(usuario)
        elif opcion == "0":
            guardar_usuarios(usuarios)
            print("Hasta mañana.")
        else:
            print("Aviso: opción inválida")
        guardar_usuarios(usuarios)
        
if __name__ == "__main__":
    main()