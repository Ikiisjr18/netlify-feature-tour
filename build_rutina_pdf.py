import os, io, requests
from PIL import Image as PILImage, ImageOps
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

OUT="rutina_mujer_real_fotos.pdf"
IMGDIR="exercise_photos"
os.makedirs(IMGDIR, exist_ok=True)

regular="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
if os.path.exists(regular):
    pdfmetrics.registerFont(TTFont("DV",regular)); pdfmetrics.registerFont(TTFont("DVB",bold))
    FONT,FONTB="DV","DVB"
else:
    FONT,FONTB="Helvetica","Helvetica-Bold"

days=[
("LUNES - GLUTEOS + FEMORALES", "#C83F83", [
("Hip thrust con barra","Barbell_Hip_Thrust","4","8-12","90-120 s","Espalda alta en el banco; termina apretando gluteos, sin arquear la zona lumbar."),
("Peso muerto rumano","Romanian_Deadlift","3","8-10","90-120 s","Cadera hacia atras, espalda neutra y barra cerca de las piernas."),
("Sentadilla dividida con mancuernas","Split_Squat_with_Dumbbells","3","10 por pierna","75-90 s","Pie delantero firme; baja con control y empuja con toda la planta."),
("Curl femoral sentado","Seated_Leg_Curl","3","10-15","60-90 s","Ajusta bien la maquina; flexiona y vuelve lento, sin rebote."),
("Abduccion de cadera en maquina","Thigh_Abductor","3","15-20","60 s","Tronco estable; abre con control y no rebotes.")
]),
("MARTES - TREN SUPERIOR A", "#287B63", [
("Jalon al pecho","Wide-Grip_Lat_Pulldown","3","8-12","75-90 s","Lleva la barra hacia la parte alta del pecho; evita balancearte."),
("Remo sentado en polea","Seated_Cable_Rows","3","8-12","75-90 s","Pecho estable; lleva los codos atras y junta escapulas."),
("Press de pecho con mancuernas","Dumbbell_Bench_Press","3","8-12","75-90 s","Pies firmes; baja con control y empuja sin chocar las mancuernas."),
("Press de hombros con mancuernas","Dumbbell_Shoulder_Press","3","8-12","75-90 s","Abdomen firme; no arquees la espalda."),
("Curl de biceps con mancuernas","Dumbbell_Bicep_Curl","3","10-15","60 s","Codos pegados al cuerpo; evita balancearte.")
]),
("MIERCOLES - PIERNAS: CUADRICEPS + PANTORRILLA", "#E07A2D", [
("Sentadilla con barra","Barbell_Squat","4","8-10","90-120 s","Rodillas en linea con los pies y espalda estable; baja solo hasta donde controles."),
("Prensa de piernas","Leg_Press","3","10-12","90-120 s","No bloquees las rodillas y no despegues la cadera del respaldo."),
("Extension de cuadriceps","Leg_Extensions","3","12-15","60-75 s","Sube y baja controlado; no lances el peso."),
("Zancadas caminando","Barbell_Walking_Lunge","3","10 por pierna","75-90 s","Paso estable; rodilla alineada con el pie."),
("Elevacion de pantorrillas de pie","Standing_Calf_Raises","4","12-20","60 s","Sube al maximo, pausa corta y baja lentamente.")
]),
("JUEVES - TREN SUPERIOR B", "#2F73B5", [
("Remo con mancuerna a una mano","One-Arm_Dumbbell_Row","3","10-12 por lado","75-90 s","Espalda neutra; lleva el codo hacia la cadera sin rotar el torso."),
("Press inclinado con mancuernas","Incline_Dumbbell_Press","3","8-12","75-90 s","Inclinacion moderada; hombros estables y bajada controlada."),
("Face pull en polea","Face_Pull","3","12-15","60 s","Tira hacia la cara con los codos altos; no arquees la espalda."),
("Elevaciones laterales","Side_Lateral_Raise","3","12-15","60 s","Sube hasta la altura del hombro sin balancear el cuerpo."),
("Jalon de triceps","Triceps_Pushdown","3","10-15","60 s","Codos quietos junto al cuerpo; extiende sin mover los hombros.")
]),
("VIERNES - GLUTEOS + PIERNA COMPLETA", "#8B4AAE", [
("Peso muerto sumo","Sumo_Deadlift","3","8-10","90-120 s","Pies abiertos; espalda neutra; empuja el suelo y extiende la cadera."),
("Step-up con mancuernas","Dumbbell_Step_Ups","3","10 por pierna","75-90 s","Sube empujando con la pierna que esta sobre el cajon; controla la bajada."),
("Hip thrust con barra","Barbell_Hip_Thrust","3","10-12","90 s","Pausa arriba 1 segundo y evita hiperextender la espalda."),
("Patada de gluteo en polea","One-Legged_Cable_Kickback","3","12-15 por pierna","Mueve desde la cadera y manten el tronco quieto."),
("Abduccion de cadera en maquina","Thigh_Abductor","3","15-20","60 s","Abre con control y mantente estable.")
])
]

def fetch_img(exid):
    path=os.path.join(IMGDIR, exid+".jpg")
    if os.path.exists(path): return path
    url=f"https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/{exid}/0.jpg"
    r=requests.get(url,timeout=30)
    r.raise_for_status()
    im=PILImage.open(io.BytesIO(r.content)).convert("RGB")
    # crop gently to 4:3, then resize for PDF
    w,h=im.size
    target=4/3
    if w/h > target:
        nw=int(h*target); x=(w-nw)//2; im=im.crop((x,0,x+nw,h))
    else:
        nh=int(w/target); y=(h-nh)//2; im=im.crop((0,y,w,y+nh))
    im=im.resize((720,540))
    im.save(path,"JPEG",quality=85,optimize=True)
    return path

def unpack_row(row):
    if len(row) == 6:
        return row
    if len(row) == 5:
        ex, eid, sets, reps, cue = row
        return ex, eid, sets, reps, "60-90 s", cue
    raise ValueError(f"Fila de ejercicio invalida: {row}")

for _,_,exs in days:
    for row in exs:
        fetch_img(unpack_row(row)[1])

styles=getSampleStyleSheet()
title=ParagraphStyle("t",parent=styles["Title"],fontName=FONTB,fontSize=21,leading=25,alignment=TA_CENTER,textColor=colors.HexColor("#4A245E"),spaceAfter=7)
sub=ParagraphStyle("s",parent=styles["BodyText"],fontName=FONT,fontSize=10,leading=14,alignment=TA_CENTER,textColor=colors.HexColor("#555555"))
body=ParagraphStyle("b",parent=styles["BodyText"],fontName=FONT,fontSize=8.7,leading=11.2,textColor=colors.HexColor("#222222"))
small=ParagraphStyle("sm",parent=styles["BodyText"],fontName=FONT,fontSize=7.4,leading=9.2,textColor=colors.HexColor("#555555"))
name=ParagraphStyle("n",parent=body,fontName=FONTB,fontSize=10.3,leading=12.5,textColor=colors.HexColor("#222222"))
dayst=ParagraphStyle("d",parent=styles["Heading2"],fontName=FONTB,fontSize=14.5,leading=18,textColor=colors.white)
note=ParagraphStyle("note",parent=body,fontSize=8.6,leading=12,backColor=colors.HexColor("#F5F0F8"),borderColor=colors.HexColor("#CDB7D8"),borderWidth=0.7,borderPadding=7)

doc=SimpleDocTemplate(OUT,pagesize=A4,leftMargin=10*mm,rightMargin=10*mm,topMargin=10*mm,bottomMargin=10*mm)
story=[]
story += [
 Paragraph("Rutina completa de gimnasio para mujer",title),
 Paragraph("5 dias - empieza el lunes con gluteos - piernas incluidas 3 dias - fotos reales de ejercicios reales",sub),
 Spacer(1,5),
 Paragraph("<b>Objetivo:</b> fuerza e hipertrofia general con prioridad en gluteos y piernas, manteniendo un tren superior equilibrado.",note),
 Spacer(1,7)
]
overview=[["Dia","Trabajo principal"],
["Lunes","Gluteos + femorales"],
["Martes","Tren superior A"],
["Miercoles","Cuadriceps + pantorrillas + core"],
["Jueves","Tren superior B"],
["Viernes","Gluteos + pierna completa"],
["Sabado","Descanso o caminata suave"],
["Domingo","Descanso"]]
ot=Table([[Paragraph(f"<b>{c}</b>",body) for c in overview[0]]]+[[Paragraph(c,body) for c in row] for row in overview[1:]],colWidths=[42*mm,138*mm])
ot.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#ECE4F1")),("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#D4D4D4")),("PADDING",(0,0),(-1,-1),6),("VALIGN",(0,0),(-1,-1),"MIDDLE")]))
story += [ot,Spacer(1,8),
 Paragraph("<b>Como usarla:</b> calienta 5-10 minutos y haz 1-2 series ligeras del primer ejercicio. Usa un peso que te deje aproximadamente 2 repeticiones posibles con buena tecnica al terminar cada serie. Cuando alcances el maximo de repeticiones de todas las series sin perder tecnica, sube el peso ligeramente.",body),
 Spacer(1,5),
 Paragraph("<b>Core:</b> al terminar el miercoles haz 3 series de plancha de 30-45 segundos. Cardio opcional: 10-20 minutos suaves al final de 2-3 sesiones.",body),
 Spacer(1,8),
 Paragraph("Las fotografias de ejercicio de esta guia proceden de free-exercise-db, un conjunto de datos e imagenes de dominio publico. Son fotos reales usadas como referencia visual; la tecnica debe adaptarse a tu movilidad y experiencia.",small),
 PageBreak()
]

for di,(dtitle,color,exs) in enumerate(days):
    hdr=Table([[Paragraph(dtitle,dayst)]],colWidths=[190*mm])
    hdr.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),colors.HexColor(color)),("LEFTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    story += [hdr,Spacer(1,4)]
    for row in exs:
        ex, eid, sets, reps, rest, cue = unpack_row(row)
        img=Image(fetch_img(eid),width=47*mm,height=35.25*mm)
        info=Paragraph(f"<b>{ex}</b><br/><b>{sets} series x {reps}</b> &nbsp; | &nbsp; Descanso: {rest}<br/>{cue}",body)
        card=Table([[img,info]],colWidths=[51*mm,135*mm],rowHeights=[38*mm])
        card.setStyle(TableStyle([
            ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
            ("BOX",(0,0),(-1,-1),0.55,colors.HexColor("#D8D8D8")),
            ("BACKGROUND",(0,0),(-1,-1),colors.white),
            ("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),6),
            ("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),
        ]))
        story += [card,Spacer(1,3.2*mm)]
    if di==2:
        story += [Paragraph("<b>Finisher de core:</b> Plancha - 3 x 30-45 s, descanso 45-60 s.",note)]
    story += [Spacer(1,2),Paragraph("Foto: free-exercise-db (dominio publico). La imagen sirve como referencia de posicion y equipo; realiza el movimiento de forma controlada.",small)]
    if di < len(days)-1: story.append(PageBreak())

story += [PageBreak(),Paragraph("Progresion y seguridad",title),
 Paragraph("<b>Progresion:</b> si un ejercicio indica 3 x 8-12, conserva el mismo peso hasta completar 12 repeticiones en las 3 series con tecnica limpia. En la siguiente sesion aumenta un poco la carga y vuelve cerca de 8-10 repeticiones.",body),Spacer(1,8),
 Paragraph("<b>No hace falta llegar al fallo.</b> Mantener 1-3 repeticiones en reserva en la mayoria de series suele permitir progresar con mejor control y recuperacion.",body),Spacer(1,8),
 Paragraph("<b>Dolor:</b> fatiga muscular y esfuerzo son normales; dolor agudo, pinchazo o dolor articular no lo son. Si aparece, detente y revisa el ejercicio.",body),Spacer(1,10),
 Paragraph("<b>Fuente de las fotos:</b> yuhonas/free-exercise-db - Public Domain / Unlicense. Fuente de programacion general: principios actuales de entrenamiento de resistencia del American College of Sports Medicine.",small)
]
doc.build(story)
print(OUT)
