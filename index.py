from ursina import *

app = Ursina()

# Configurar la ventana
window.color = color.hsv(235, 0.75, 0.26)
camera.orthographic = True
camera.fov = 1.08

# Establecer la imagen de fondo
fondo = Entity(model='quad', texture='uni10.png', scale=(1.37, 1))
# Puedes cambiar los fondos bajo el formato de ejemplo: uni1.png; cambia el número del nombre para obtener otro fondo, del 1 al 18.

# Establecer la ventana en modo pantalla completa
window.fullscreen = True

    # Cuerpo del juego: crear principales variables

# Crear portal azul
paleta_izquierda = Entity(scale=(4/32, 8/32), x=-.75, model='quad', origin_x=.5, collider='quad', texture='agujero_negro1.png')

# Crear portal verde
paleta_derecha = duplicate(paleta_izquierda, x=paleta_izquierda.x*-1, rotation_z=paleta_izquierda.rotation_z+180, texture='agujero_negro.png')

# Crear margenes del escenario para el juego: (El nombre de las varibles es directo con su funcionalidad)
piso = Entity(model='quad', y=-.5, origin_y=.5, collider='box', scale=(2,10), visible=True)
techo = duplicate(piso, y=.5, rotation_z=180, visible=True)
pared_izquierda = duplicate(piso, x=-.5*window.aspect_ratio, rotation_z=90, visible=False)
pared_derecha = duplicate(piso, x=.5*window.aspect_ratio, rotation_z=-90, visible=False)

# Crear margenes del escenario para el juego:
collision_cooldown = .15
# Crear pelota(alien invasor):
pelota = Entity(model='cube', scale=.15, collider='box', speed=0, collision_cooldown=collision_cooldown, texture='extraterrestre.png')

# Imagen de los heroes de ambos bandos, que desaparecerán con la tecla espacio.
mi_imagen_azul = Entity(model='quad', texture='saitama_azul.png', scale=(0.4, 0.4), position=(0.5, -0.15), enabled=True)
mi_imagen_azul.z = -1  # Asegurar que esté delante

mi_imagen_rojo = Entity(model='quad', texture='saitama_rojo.png', scale=(0.4, 0.4), position=(-0.5, -0.15), enabled=True)
mi_imagen_rojo.z = -1  # Asegurar que esté delante

# Variables de puntuación
score_left = 0
score_right = 0

# Texto del marcador
score_text = Text(text=f" |{score_left}|:|{score_right}|", position=(0, 0.40), origin=(0.22, 0), scale=1.4, color=color.yellow)

# Variables para controlar el estado del juego

# Variable encargada de finalizar las acciones del juego
game_over = False
# Variable para declarar al ganador.
winner_text = None

# Cargar la música de fondo
background_music = Audio('seiya.mp3', loop=True, autoplay=True)

# Movilidad de la pelota(marciano):
def update():
    global game_over
    if game_over:
        return
    # Reduce el tiempo de espera para la siguiente colisión en cada fotograma.
    pelota.collision_cooldown -= time.dt
    # Actualiza la posición de la pelota basado en su dirección y velocidad.
    pelota.position += pelota.right * time.dt * pelota.speed

    # Actualiza la posición vertical de la paleta izquierda, basada en las teclas 'w' y 's' presionadas.
    paleta_izquierda.y += (held_keys['w'] - held_keys['s']) * time.dt * 1
    # Actualiza la posición vertical de la paleta derecha, basada en las teclas de flecha 'arriba' y 'abajo' presionadas.
    paleta_derecha.y += (held_keys['up arrow'] - held_keys['down arrow']) * time.dt * 1

    if pelota.collision_cooldown > 0:
        # después de una colisión, espere un poco antes de que pueda ocurrir otra colisión.
        # esto es para evitar que la pelota choque varias veces con la misma pared porque
        # todavía no ha tenido tiempo de alejarse de él.
        return
# Interacción de la pelota(marciano) con las paletas(portales):
    hit_info = pelota.intersects()
    if hit_info.hit:
        pelota.collision_cooldown = collision_cooldown

        if hit_info.entity in (paleta_izquierda, paleta_derecha, pared_izquierda, pared_derecha):
            hit_info.entity.collision = False
            invoke(setattr, hit_info.entity, 'collision', False, delay=.1)
            direction_multiplier = 1
            if hit_info.entity == paleta_izquierda:
                direction_multiplier = -1

                paleta_izquierda.collision = False # deshabilitar la colisión de la paleta actual para que no colisione dos veces seguidas
                paleta_derecha.collision = True
            else:
                paleta_derecha.collision = False
                paleta_izquierda.collision = True
        # Rotación, y aumento de velocidad:
            pelota.rotation_z += 180 * direction_multiplier
            pelota.rotation_z -= (hit_info.entity.world_y - pelota.y) * 20 * 32 * direction_multiplier
            pelota.speed *= 1.1

        else:   # golpear la pared
            pelota.rotation_z *= -abs(hit_info.world_normal.normalized()[1])

        # crear una partícula en caso de colisión
        particle = Entity(model='quad', position=hit_info.world_point, scale=0, texture='circle', add_to_scene_entities=False)
        particle.animate_scale(.2, .5, curve=curve.out_expo)
        particle.animate_color(color.clear, duration=.5, curve=curve.out_expo)
        destroy(particle, delay=.5)

    # Puntaje:
    global score_left, score_right
    # Verificar si la pelota salió por el lado izquierdo de la pantalla
    if pelota.x < -0.5 * window.aspect_ratio:
        # Incrementar el puntaje del equipo derecho
        score_right += 1
        # Actualizar el marcador en la interfaz
        update_score()
        # Verificar si hay un ganador después de anotar
        check_winner()
        # Reiniciar el estado del juego para el próximo punto
        reset()
        
    # Verificar si la pelota salió por el lado derecho de la pantalla
    elif pelota.x > 0.5 * window.aspect_ratio:
        # Incrementar el puntaje del equipo izquierdo
        score_left += 1
        # Actualizar el marcador en la interfaz
        update_score()
        # Verificar si hay un ganador después de anotar
        check_winner()
        # Reiniciar el estado del juego para el próximo punto
        reset()

# Contador visible en el juego:
def update_score():
    score_text.text = f"|{score_left}| : |{score_right}|"

def check_winner():
    global game_over, winner_text
    
    #Victoria del jugador de la derecha
    if score_left >= 16:
        game_over = True
        # Imagen de fondo del mensaje de ganador
        winner_background = Entity(model='quad', texture='hero(izquierda).png', scale=(2, 1))
        winner_background.z = 1  # Asegurar que esté detrás de todo
        # Texto de fondo del mensaje de ganador
        create_winner_text("¡Ganador: El universo IZQUIERDO se salvó, y VENCIO!")

    #Victoria del jugador de la derecha
    elif score_right >= 16:
        game_over = True
        # Imagen de fondo del mensaje de ganador
        winner_background = Entity(model='quad', texture='hero(derecha).png', scale=(2, 1))
        winner_background.z = 1  # Asegurar que esté detrás de todo
        # Texto de fondo del mensaje de ganador
        create_winner_text("¡Ganador: El universo DERECHO se salvó, Y VENCIO!")

def create_winner_text(text):
    global winner_text
    # Crear texto del ganador
    winner_text = Text(text=text, position=(0, 0), origin=(0, 0), scale=2, color=color.cyan)
    # Asegurar que el texto del ganador esté en frente de la imagen de fondo
    winner_text.z = -0.5
    # Dar brillo al texto
    dar_brillo(winner_text)

def dar_brillo(text_entity):
    # Establece el color de resaltado del texto a verde lima.
    text_entity.highlight_color = color.lime
    # Anima el color del texto a blanco en 0.5 segundos usando una curva de animación de entrada, y salida exponencial.
    text_entity.animate_color(color.white, duration=0.5, curve=curve.in_out_expo)
    # Anima el color del texto de vuelta a verde lima en 0.5 segundos con un retraso de 0.5 segundos.
    # La animación se repetirá en bucle.
    text_entity.animate_color(color.lime, duration=0.5, curve=curve.in_out_expo, delay=0.5, loop=True)

def reset():
    global game_over
    if game_over:
        return
        
    # Si el juego ha terminado, sale de la función para evitar que se reinicie.

    # Reinicia la posición, rotación y velocidad de la pelota. 
    pelota.position = (0,0,0)
    pelota.rotation = (0,0,0)
    pelota.speed = 8
    
    # Reinicia las paletas izquierda y derecha.
    for paddle in (paleta_izquierda, paleta_derecha):
        paddle.collision = True # Habilita la colisión de las paletas.
        paddle.y = 0 # Coloca las paletas en su posición inicial en el eje Y.

def full_reset():
    global score_left, score_right, game_over, winner_text
    
    # Reinicia los puntajes izquierdo y derecho.
    score_left = 0
    score_right = 0
    # Reinicia el estado del juego.
    game_over = False
    # Si hay un texto del ganador, destrúyelo y establece la variable a None.
    if winner_text:
        destroy(winner_text)
        winner_text = None
        
    # Actualiza el marcador en la pantalla.
    update_score()

    # Reinicia las posiciones, propiedades de la pelota, y las paletas.
    reset()
    

# Crea los respectivos textos, con fines orientativos del juego, dandoles color y propiedades:
# Iniciar
info_text = Text("Presiona espacio para iniciar", y=-.36, color=color.cyan)
# Trama del juego
info_text1 = Text("¡NO DEJES QUE SE ROBE TU MUNDO!", position=(0.28, 0.14), origin=(0.22, 0), scale=3, color=color.hsv(180, 1.00, 1.00))
# Aviso de ubicación del marcador
info_text2 = Text("MARCADOR", y=.36, origin=(0.22, 0), color=color.yellow)
# Para subir la velocidad de la pelota(marciano)
info_text3 = Text("Acelerar = v", y=.40, origin=(-3, 0), color=color.green)
# Reglas de victoria
info_text4 = Text("(GANA 16 DUELOS, y SOBREVIVE) ", y=-.383, color=color.white)
# Reproducir música de fondo
info_text5 = Text("música = m", y=.40, origin=(-3, -1), color=color.green)
# Corregir mal impulso del balón, a la neutralidad del juego
info_text6 = Text("estabilizar = espacio", y=.40, origin=(-1.8, -2), color=color.green)
# Reiniciar el juego
info_text7 = Text("nuevo juego = r + espacio", y=.40, origin=(-1.5, 1), color=color.green)
# Comentar a su creador por valor de propiedad
info_text8 = Text("Programador: Vincent - (Waraq Coyllur)", y=-.43, origin=(-0.8, 0), color=color.green)
# Configuración del tamaño de pantalla
info_text9 = Text("Pantalla (-) o (+) = F11", y=.40, origin=(-1.7, 2.1), color=color.green)

def input(key):
    # Desactiva toda la información al presionar espacio.
    if key == 'space':
        # Ocultar la texto al presionar espacio
        info_text.enabled = False   
        info_text1.enabled = False   
        info_text2.enabled = False   
        info_text4.enabled = False
        info_text8.enabled = False   
        # Ocultar la imagen al presionar espacio
        mi_imagen_rojo.enabled = False  
        mi_imagen_azul.enabled = False 
        # Reinicia el juego.
        reset()

    if key == 'v':
        # Aumenta la velocidad de la pelota al presionar 'v'.
        pelota.speed += 1

        # Activa nuevamente todos los textos de información después del reinicio.
    if key == 'r':
        full_reset()
        # Mostrar el texto al presionar r
        info_text.enabled = True
        info_text1.enabled = True
        info_text2.enabled = True
        info_text4.enabled = True
        info_text8.enabled = True   
        # Mostrar la imagen al presionar r
        mi_imagen_rojo.enabled = True  
        mi_imagen_azul.enabled = True
        check_winner.enabled = False
        reset()
        
    if key == 'm':
        # Con la tecla (m) se activa, y desactiva la música de fondo en base a la preferencia de los jugadores:
        if not background_music.playing:
            background_music.play()
        else:
            background_music.stop()
   
app.run()
