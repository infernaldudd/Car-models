#!/usr/bin/env python3
"""Five original fictional sports car concept meshes for Helvetia.

All surfaces are authored with original parametric geometry. No third-party
car models, logos, or texture assets are used. These are technical prototypes,
not a legal opinion or quality certification.
"""
import json, math, hashlib, os
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import trimesh
from scipy.interpolate import CubicSpline
from trimesh.visual.material import PBRMaterial

TAU=math.tau
OUT=Path(__file__).resolve().parent / 'models'
OUT.mkdir(parents=True,exist_ok=True)

@dataclass
class Spec:
    code:str; architecture:str
    length:float; width:float; height:float; wheelbase:float
    front_overhang:float; rear_overhang:float
    roof_start:float; roof_end:float; roof_height:float; roof_width:float
    belt:float; nose:float; tail:float; shoulder:float; belly:float
    tire_r:float; tire_w:float; fender:float
    paint:tuple; trim:tuple; highlight:tuple
    kind:str; headlight:str; taillight:str; roof_style:str

SPECS=[
Spec('HV-S01','front-mid engine grand tourer',4.58,1.91,1.27,2.78,.91,.89,-.93,.89,1.262,.68,.91,.79,.79,.98,.35,.344,.245,.368,(0.046,0.122,0.236,1),(0.09,0.105,0.12,1),(0.58,0.77,0.94,1),'gt','spear','hex','fastback'),
Spec('HV-S02','mid engine two-seat supercar',4.41,1.96,1.17,2.64,.80,.97,-.69,.98,1.160,.59,.83,.70,.77,.91,.30,.354,.270,.377,(0.50,0.083,0.055,1),(0.045,0.055,0.063,1),(0.95,0.49,0.24,1),'super','slash','blade','buttress'),
Spec('HV-S03','front-engine lightweight open roadster',4.13,1.83,1.18,2.51,.79,.83,-.50,.72,1.06,.53,.77,.68,.71,.88,.305,.326,.226,.352,(0.07,0.305,0.22,1),(0.11,0.13,0.14,1),(0.76,0.9,0.71,1),'roadster','diagonal','dot','open'),
Spec('HV-S04','battery electric 2+2 fastback',4.69,1.94,1.29,2.98,.82,.89,-1.02,.99,1.282,.73,.92,.77,.83,.97,.345,.347,.241,.370,(0.31,0.29,0.41,1),(0.085,0.09,0.12,1),(0.69,0.82,1.0,1),'ev','pixel','fins','kamm'),
Spec('HV-S05','mid-engine lightweight track coupe',4.23,1.90,1.20,2.58,.72,.93,-.78,.70,1.194,.56,.80,.67,.70,.91,.29,.353,.274,.374,(0.72,0.68,0.51,1),(0.045,0.047,0.053,1),(1.0,0.85,0.48,1),'track','recess','step','sails'),
]


def mat(name, color, metallic=.0, roughness=.5, alpha=None):
    params=dict(name=name,baseColorFactor=np.array(color,float),metallicFactor=float(metallic),roughnessFactor=float(roughness),doubleSided=True)
    if alpha:params['alphaMode']=alpha
    return PBRMaterial(**params)

class Builder:
 def __init__(self,s):
  self.s=s; self.scene=trimesh.Scene(); self.materials={}
  self.M={
    'paint':mat('original_primary_paint',s.paint,.86,.20),
    'accent':mat('secondary_trim',s.trim,.45,.33),
    'highlight':mat('design_highlight',s.highlight,.8,.27),
    'glass':mat('tinted_smoked_glass',(0.067,0.117,0.155,.43),.14,.085,'BLEND'),
    'windshield':mat('windscreen_blue_tint',(0.12,0.21,0.26,.36),.14,.055,'BLEND'),
    'rubber':mat('rubber',(0.018,0.018,0.022,1),.0,.88),
    'seat':mat('upholstery',(0.15,0.18,0.19,1),.0,.72),
    'seat2':mat('stitch_color',(0.32,0.37,0.38,1),.0,.79),
    'dash':mat('interior_dash',(0.075,0.078,0.087,1),.0,.55),
    'metal':mat('anodized_brushed_metal',(0.44,0.48,0.52,1),.88,.28),
    'black':mat('dark_metal',(0.09,0.103,0.13,1),.65,.27),
    'light':mat('LED_daytime_running',(0.86,0.96,1,1),.15,.18),
    'red':mat('rear_LED',(0.83,0.036,0.032,1),.2,.21),
    'orange':mat('amber_reflector',(0.96,0.40,0.09,1),.25,.27),
    'brake':mat('brake_disc',(0.33,0.34,0.355,1),.88,.34),
    'caliper':mat('brake_caliper',(0.9,0.60,0.13,1),.67,.25),
    'engine':mat('cast_engine',(0.31,0.34,0.355,1),.68,.43),
    'copper':mat('power_electronics',(0.59,0.28,0.10,1),.84,.30)
  }
  self.n=0;self.groups={};self.current_group='body'
 def add(self,name,mesh,m):
  if mesh is None or len(mesh.vertices)<3 or len(mesh.faces)<1:return
  if not np.all(np.isfinite(mesh.vertices)):raise ValueError(name)
  mesh.visual=trimesh.visual.TextureVisuals(material=self.M[m])
  key=(self.current_group,m)
  self.groups.setdefault(key,[]).append(mesh);self.n+=1
 def box(self,name,center,size,m):
  x=trimesh.creation.box(extents=size);x.apply_translation(center);self.add(name,x,m)
 def tube(self,name,points,radius,m,sides=10):
  pts=np.asarray(points,dtype=float)
  for a,b in zip(pts[:-1],pts[1:]):
   u=b-a; h=np.linalg.norm(u)
   if h<1e-5:continue
   x=trimesh.creation.cylinder(radius=radius,height=h,sections=sides)
   x.apply_transform(trimesh.geometry.align_vectors([0,0,1],u/h));x.apply_translation((a+b)*.5)
   self.add(name,x,m)
 def icos(self,name,center,scale,m,sub=2):
  x=trimesh.creation.icosphere(subdivisions=sub,radius=1);x.apply_scale(scale);x.apply_translation(center);self.add(name,x,m)
 def panel(self,name,points,m,uv=10,vv=3):
  """Bilinearly subdivided curved quad; point order bottom left, bottom right, top right, top left."""
  a,b,c,d=[np.asarray(p,float) for p in points]
  verts=[];faces=[]
  for i in range(uv+1):
   u=i/uv
   for j in range(vv+1):
    v=j/vv
    p=(1-u)*(1-v)*a+u*(1-v)*b+u*v*c+(1-u)*v*d
    verts.append(p)
  for i in range(uv):
   for j in range(vv):
    q=i*(vv+1)+j
    faces.extend([[q,q+vv+1,q+1],[q+1,q+vv+1,q+vv+2]])
  self.add(name,trimesh.Trimesh(vertices=verts,faces=faces,process=False),m)
 def annulus(self,name,center,normal_axis,outer,inner,width,m,sections=64):
  # radial disc annulus in x-z plane, normal along Y, centered on wheel
  x,y,z=center;v=[];f=[]
  for yi in [y-width/2,y+width/2]:
   for r in [inner,outer]:
    for i in range(sections):
     t=TAU*i/sections;v.append([x+math.cos(t)*r,yi,z+math.sin(t)*r])
  for a,b in [(0,1),(2,3),(0,2),(1,3)]:
   for i in range(sections):
    j=(i+1)%sections; q=a*sections+i; qj=a*sections+j; k=b*sections+i;kj=b*sections+j
    f.extend([[q,qj,k],[k,qj,kj]])
  self.add(name,trimesh.Trimesh(vertices=v,faces=f,process=False),m)
 def wheel(self,wx,side,front):
  s=self.s;self.current_group=f'wheel_{"front" if front else "rear"}_{"L" if side<0 else "R"}'; cy=side*(s.width*.48-.03);cz=s.tire_r
  # Tire carcass surface of revolution around y; radial profile is continuous incl inner bead
  prof=[(-.115,.242),(-.125,.273),(-.123,s.tire_r-.018),(-.110,s.tire_r),(-.080,s.tire_r+.004),(.080,s.tire_r+.004),(.112,s.tire_r),(.125,s.tire_r-.018),(.125,.264),(.115,.242)]
  prof=[(p[0]*s.tire_w/.245,p[1]*s.tire_r/.344) for p in prof]
  v=[];f=[];N=80
  for j,(dy,r) in enumerate(prof):
   for i in range(N):
    t=i*TAU/N
    v.append([wx+r*math.cos(t),cy+dy,cz+r*math.sin(t)])
  for j in range(len(prof)):
   jj=(j+1)%len(prof)
   for i in range(N):
    k=(i+1)%N;f.extend([[j*N+i,jj*N+i,jj*N+k],[j*N+i,jj*N+k,j*N+k]])
  self.add('tire_carcass',trimesh.Trimesh(vertices=v,faces=f,process=False),'rubber')
  # 2 tread grooves, periodic raised shallow shoulder blocks
  for yoff in (-.052,.052):
   yy=cy+yoff*s.tire_w/.245
   pts=[[wx+(s.tire_r+.004)*math.cos(i*TAU/96),yy,cz+(s.tire_r+.004)*math.sin(i*TAU/96)] for i in range(97)]
   self.tube('tire_longitudinal_tread_channel',pts,.003,'black',6)
  outside=cy+side*(s.tire_w*.55)
  inside=cy-side*(s.tire_w*.55)
  for yi in (outside,inside):
   self.annulus('alloy_wheel_lip',(wx,yi,cz),'y',.249,.209,.012,'metal')
   self.annulus('dark_rim_recess',(wx,yi-side*.008,cz),'y',.219,.068,.008,'black')
   self.annulus('ventilated_brake_disc',(wx,yi-side*.038,cz),'y',.191,.053,.013,'brake')
   spoke_count=7 if s.kind in ('gt','ev') else 9 if s.kind=='track' else 6
   for k in range(spoke_count):
    a=TAU*k/spoke_count+(.11 if front else 0)
    mid=(wx+.13*math.cos(a), yi+side*.013, cz+.13*math.sin(a))
    direction=np.array([math.cos(a),0,math.sin(a)])
    tang=np.array([-math.sin(a),0,math.cos(a)])
    # tapered single-spoke polygon, overlapping rim ring
    verts=[np.array([wx,yi+side*.023,cz])+direction*.049+tang*.022,
           np.array([wx,yi+side*.023,cz])+direction*.049-tang*.022,
           np.array([wx,yi+side*.020,cz])+direction*.202-tang*.035,
           np.array([wx,yi+side*.020,cz])+direction*.202+tang*.035]
    self.panel('original_radial_wheel_spoke',[verts[0],verts[1],verts[2],verts[3]],'metal',2,1)
   self.icos('center_hub',(wx,yi+side*.022,cz),(.052,.008,.052),'black',2)
  self.icos('brake_caliper',(wx,cy+side*.062,cz+.15),(.041,.024,.075),'caliper',2)
  self.current_group='body'
 def arch_z(self,x):
  s=self.s
  for wx in (s.wheelbase/2,-s.wheelbase/2):
   dx=abs(x-wx)
   r=s.fender
   if dx<r:
    return max(s.belly, s.tire_r+math.sqrt(max(0,r*r-dx*dx))+.014)
  return s.belly
 def sides(self):
  s=self.s
  # continuous original body upper skin, shoulder, flanks and wheel cutouts
  rear=-s.length/2;front=s.length/2
  xs=np.linspace(rear,front,108)
  # controlled front/rear taper, broad fenders and physically plausible silhouette
  def width_at(x):
   t=(x-rear)/s.length
   base=s.width/2
   if t<.12: base*=.79+.21*math.sin(t/.12*math.pi/2)
   if t>.88: base*=.81+.19*math.sin((1-t)/.12*math.pi/2)
   for w in (-s.wheelbase/2,s.wheelbase/2):base+=.025*math.exp(-((x-w)/.32)**2)
   # different waist shape by character
   base-=.035*math.exp(-((x-.08)/.85)**2) if s.kind=='super' else 0
   return base
  def surface_z(x):
   t=(x-rear)/s.length
   # rear deck/cowl/hood, separate design curves
   rear_z=s.tail+.03*math.sin(min(1,t/.22)*math.pi/2)
   nose_z=s.nose+.04*math.sin(max(0,min(1,(1-t)/.24))*math.pi/2)
   # cowl modest rise at windshield start
   if x<s.roof_end:return rear_z+.025*math.sin(max(0,min(1,(x-rear)/(s.roof_end-rear)))*math.pi)
   return nose_z+.018*math.sin((t*.8)*math.pi)
  self.width_at=width_at; self.surface_z=surface_z
  # top continuous widthwise with 17 lateral positions, ensures no hood holes
  v=[];f=[];nY=24
  for x in xs:
   w=width_at(x)
   z=surface_z(x)
   for j in range(nY+1):
    u=(j/nY)*2-1
    yy=u*w
    # crown with shoulder bevel and sculpting, no giant planar top
    vz=z+.028*(1-u*u)-.023*pow(abs(u),8)
    if s.kind=='super':vz+=.016*math.cos((x+.42)*6)*math.exp(-((abs(u)-.68)/.2)**2)
    if s.kind=='ev':vz+=.024*(1-u*u)
    v.append([x,yy,vz])
  for i in range(len(xs)-1):
   for j in range(nY):
    a=i*(nY+1)+j;b=a+nY+1;f.extend([[a,b,a+1],[a+1,b,b+1]])
  self.add('curved_continuous_body_top',trimesh.Trimesh(vertices=v,faces=f,process=False),'paint')
  for side in (-1,1):
   # SIDE WALL with wheel arch cutouts and material break line
   v=[];f=[];cols=15
   for x in xs:
    w=width_at(x)
    upper=surface_z(x)-.017
    # large cladding along bottom, recessed into silhouette
    bottom=self.arch_z(x)
    if bottom>upper-.03: bottom=upper-.03
    for j in range(cols+1):
     frac=j/cols
     z=bottom+frac*(upper-bottom)
     bulge=.023*math.sin(math.pi*frac) + (.022 if s.kind=='track' else 0)*pow(math.sin(frac*math.pi),6)
     yy=side*(w+bulge-.015)
     v.append([x,yy,z])
   for i in range(len(xs)-1):
    for j in range(cols):
     a=i*(cols+1)+j;b=a+cols+1;f.extend([[a,a+1,b],[b,a+1,b+1]])
   self.add('contoured_body_sides',trimesh.Trimesh(vertices=v,faces=f,process=False),'paint')
   # wheel arch lip exactly follows cutout, doesn't float far beyond
   for cx in (s.wheelbase/2,-s.wheelbase/2):
    path=[]
    for t in np.linspace(math.pi,.0,44):
     x=cx+s.fender*math.cos(t)
     z=s.tire_r+s.fender*math.sin(t)+.016
     path.append([x,side*(width_at(x)+.023),z])
    self.tube('continuous_wheelarch_rolled_lip',path,.010,'accent',8)
   # stepped rocker panel between wheel wells
   px=[-s.wheelbase/2+s.fender+.055,s.wheelbase/2-s.fender-.055]
   if px[0]<px[1]:
    self.tube('side_rocker_sill',[[x,side*(width_at(x)+.010),s.belly+.011] for x in np.linspace(px[0],px[1],16)],.019,'accent')
   # continuous waist accent upper shoulder; straight below door glazing
   xa=-s.wheelbase/2+s.fender+.16;xb=s.wheelbase/2-s.fender-.08
   self.tube('waistline_transition',[[x,side*(width_at(x)+.006),surface_z(x)-.115] for x in np.linspace(xa,xb,21)],.0055,'black',6)
   # body panel flush door seam, no carved 3d holes
   dx=xb
   self.tube('door_panel_reveal',[[dx,side*(width_at(dx)+.009),z] for z in np.linspace(s.belly+.055,s.belt-.025,13)],.0035,'black',6)
  # front rear fascia: convex span between top and bottom, adds bumper volume
  for x,nom in ((front,'nose'),(rear,'tail')):
   w=width_at(x)*.995;z=surface_z(x)
   pts=[[x,y,z-.01] for y in np.linspace(-w,w,28)]
   self.tube(nom+'_upper_ridge',pts,.017,'paint')
   self.box(nom+'_bumper_core',(x,0,s.belly+.12),(.045,2*w*.96,.235),'paint')
   self.box(nom+'_lower_air_dam',(x,0,s.belly+.035),(.064,2*w*.88,.047),'accent')
  # belly and chassis
  self.box('structural_underfloor',(0,0,s.belly+.016),(s.length*.80,s.width*.77,.085),'black')
  for side in (-1,1):
   self.box('underbody_longitudinal_rail',(0,side*.60,s.belly-.018),(s.wheelbase+.40,.085,.10),'metal')
  # smooth hood edge / front contour, dark gasket style
  front_start=s.roof_end+.09
  for side in (-1,1):
   path=[[x,side*width_at(x)*.72,surface_z(x)+.020] for x in np.linspace(front_start,front-.15,36)]
   self.tube('hood_inset_precision_seam',path,.0035,'black',6)
  if s.kind=='track':
   for side in (-1,1):
    # sculpted aero tunnels through front fascia, replace with contrasting recessed parts
    for j in range(6):
     self.box('front_arch_aero_louvre',(front-.33-j*.055,side*(s.width*.35),surface_z(front-.30)-.02),(.031,.185,.007),'black')
  if s.kind=='super':
   for side in (-1,1):
    self.box('low_front_aero_strake',(front-.23,side*(s.width*.33),s.belly+.07),(.36,.06,.035),'accent')

 def greenhouse(self):
  s=self.s
  if s.roof_style=='open':
   # open roadster: no invented closed-roof shell. short transparent windscreen, visible seats.
   a=s.roof_end-.08;b=s.roof_end+.13
   self.panel('roadster_windscreen',[(b,-s.roof_width,s.belt+.005),(b,s.roof_width,s.belt+.005),(a,s.roof_width,1.10),(a,-s.roof_width,1.10)],'windshield',18,7)
   for side in (-1,1):
    self.tube('windscreen_edge_frame',[[b,side*s.roof_width,s.belt],[a,side*s.roof_width,1.10]],.013,'black')
    self.tube('roadster_hoop_support',[[-.40,side*.32,s.belt+.03],[-.42,side*.34,1.14],[-.55,side*.34,1.15],[-.60,side*.32,s.belt+.03]],.027,'metal')
   self.tube('windscreen_upper_frame',[[a,y,1.10] for y in np.linspace(-s.roof_width,s.roof_width,17)],.012,'black')
   self.box('rear_cockpit_tonneau',(-.75,0,s.belt+.01),(.40,s.width*.81,.06),'paint')
   return
  # A pillar/front windshield and angled C pillar/rear glass. All shapes original.
  front_bot=s.roof_end+.30;front_top=s.roof_end-.30
  rear_bot=s.roof_start-.42;rear_top=s.roof_start+.24
  roof_front=front_top;roof_rear=rear_top
  hw=s.roof_width
  for side in (-1,1):
   # windshield side A-pillar
   self.tube('integrated_A_pillar',[[front_bot,side*hw*1.13,s.belt-.020],[front_top,side*hw,s.roof_height-.024]],.022,'black',12)
   # rear C pillar
   self.tube('sculpted_C_pillar',[[rear_bot,side*hw*1.16,s.belt-.01],[rear_top,side*hw,s.roof_height-.012]],.034 if s.roof_style in ('sails','buttress') else .026,'paint',12)
  self.panel('curved_front_glazing',[
   [front_bot,-hw*1.12,s.belt],[front_bot,hw*1.12,s.belt],
   [front_top,hw,s.roof_height-.020],[front_top,-hw,s.roof_height-.020]],'windshield',22,12)
  self.panel('sloped_rear_glazing',[
   [rear_bot,-hw*1.15,s.belt],[rear_bot,hw*1.15,s.belt],
   [rear_top,hw,s.roof_height-.02],[rear_top,-hw,s.roof_height-.02]],'glass',22,9)
  # roof semi-curved plane, rounded via width contour
  xs=np.linspace(roof_rear,roof_front,35);ys=np.linspace(-1,1,20);v=[];f=[]
  for x in xs:
   for u in ys:
    z=s.roof_height-.018*(abs(u)**2)+.008*math.sin((x-roof_rear)/(roof_front-roof_rear)*math.pi)
    v.append([x,u*hw,z])
  for i in range(len(xs)-1):
   for j in range(len(ys)-1):
    a=i*len(ys)+j;b=a+len(ys);f.extend([[a,b,a+1],[a+1,b,b+1]])
  self.add('curved_canopy_roof',trimesh.Trimesh(vertices=v,faces=f,process=False),'paint')
  for side in (-1,1):
   self.tube('roof_side_weatherstrip',[[x,side*hw,s.roof_height-.019] for x in xs],.012,'black')
   # front and rear quarter glass, distinct triangular/polygonal windows
   mid=(front_bot+rear_bot)*.50
   left_lower=[rear_bot,side*hw*1.14,s.belt+.015]
   right_lower=[front_bot,side*hw*1.12,s.belt+.015]
   roof_mid=[mid,side*hw,s.roof_height-.026]
   self.panel('integral_driver_side_glass',[
    left_lower,right_lower,[front_top,side*hw,s.roof_height-.033],[mid,side*hw,s.roof_height-.031]],'glass',13,8)
   self.tube('mid_window_division',[[mid,side*hw*1.12,s.belt+.015],roof_mid],.012,'black',8)
   self.tube('window_belt_seal',[[x,side*hw*1.13,s.belt+.018] for x in np.linspace(rear_bot,front_bot,25)],.010,'black',8)
   if s.roof_style in ('sails','buttress'):
    # aerodynamic rear shoulders are independent bespoke sculpted shapes
    self.tube('roof_sail_arch',[[rear_top-.03,side*hw*.91,s.roof_height-.03],
      [rear_bot+.10,side*(hw+.07),s.belt+.15],[rear_bot-.26,side*(hw+.16),s.belt+.055]],.034,'paint',12)
  self.tube('upper_windshield_border',[[front_top,y,s.roof_height-.024] for y in np.linspace(-hw,hw,21)],.014,'black')
  self.tube('lower_windshield_border',[[front_bot,y,s.belt+.007] for y in np.linspace(-hw*1.11,hw*1.11,21)],.013,'black')
  self.tube('rear_glazing_upper_border',[[rear_top,y,s.roof_height-.026] for y in np.linspace(-hw,hw,21)],.010,'black')
 def interior(self):
  s=self.s
  # cabin center point chosen for roof and generous legroom
  cx=(s.roof_start+s.roof_end)*.50
  floor=.425 if s.kind!='roadster' else .415
  seatx=cx-.19
  self.box('interior_floor_pan',(cx,0,floor),((s.roof_end-s.roof_start)+.54,s.width*.68,.060),'dash')
  self.box('lower_dashboard',(s.roof_end+.06,0,s.belt-.155),(.28,s.width*.68,.23),'dash')
  self.box('dashboard_anodized_rail',(s.roof_end-.025,0,s.belt-.061),(.046,s.width*.69,.019),'metal')
  for side in (-1,1):
   pos_y=side*min(.42,s.width*.255)
   self.icos('bucket_seat_cushion',(seatx+.085,pos_y,floor+.13),(.275,.235,.092),'seat',2)
   self.icos('seat_side_bolster_inboard',(seatx+.065,pos_y-side*.17,floor+.17),(.235,.050,.110),'seat2',2)
   self.icos('seat_side_bolster_outboard',(seatx+.065,pos_y+side*.17,floor+.17),(.235,.050,.110),'seat2',2)
   self.icos('reclining_integrated_seat_back',(seatx-.15,pos_y,floor+.35),(.105,.215,.235),'seat',3)
   self.icos('head_rest',(seatx-.235,pos_y,floor+.605),(.082,.128,.083),'seat',2)
   self.box('seat_belt_attachment',(seatx-.20,pos_y-side*.23,floor+.35),(.045,.016,.06),'metal')
  # dashboard gauge and screens, wheel near left
  self.box('driver_instrument_cluster',(s.roof_end-.075,-.36,s.belt-.018),(.13,.29,.078),'black')
  self.box('infotainment_screen',(s.roof_end-.065,.10,s.belt-.056),(.065,.27,.17),'black')
  # steering ring standing in plane YZ; column directed x
  xc=s.roof_end-.20;yc=-.36;zc=s.belt-.145;r=.158
  path=[[xc,yc+r*math.cos(t),zc+r*math.sin(t)] for t in np.linspace(0,TAU,48)]
  self.tube('steering_wheel_grip',path,.015,'dash',10)
  for k in range(3):
   th=TAU*k/3+.2
   self.tube('steering_wheel_spoke',[[xc,yc,zc],[xc,yc+r*.85*math.cos(th),zc+r*.85*math.sin(th)]],.017,'metal')
  self.box('center_gear_control',(cx+.26,0,floor+.12),(.24,.24,.16),'black')
  self.box('center_armrest',(cx-.25,0,floor+.18),(.38,.23,.10),'seat')
  # cabin back bulkhead; behind seat but below beltline
  self.box('bulkhead_reinforcement',(s.roof_start-.08,0,floor+.20),(.075,s.width*.70,.29),'accent')
  if s.kind in ('gt','ev'):
   for side in (-1,1):self.icos('rear_seat',(s.roof_start-.19,side*.38,floor+.12),(.17,.17,.07),'seat',2)
 def lamps(self):
  s=self.s;front=s.length/2;rear=-s.length/2
  for side in (-1,1):
   y=side*s.width*.36
   # independent front LED signature sets - geometrically different
   if s.headlight=='spear':
    self.panel('forward_swept_headlight_housing',[[front-.29,y-side*.17,s.nose+.011],[front-.10,y-side*.17,s.nose+.008],
       [front-.07,y+side*.19,s.nose+.003],[front-.40,y+side*.19,s.nose+.022]],'black',6,2)
    for j in range(2):
     self.tube('split_triangular_DRL',[[front-.33+j*.07,y+side*.13,s.nose+.034],
      [front-.13+j*.04,y-side*.105,s.nose+.019]],.010,'light',12)
   elif s.headlight=='slash':
    for j in range(3):
     yy=y+side*(-.14+j*.085)
     self.tube('slanted_three_bar_DRL',[[front-.30,yy,s.nose+.03],[front-.075,yy+side*.07,s.nose-.011]],.013,'light',12)
   elif s.headlight=='diagonal':
    self.tube('diagonal_angular_DRL',[[front-.33,y-side*.12,s.nose+.02],
      [front-.09,y+side*.17,s.nose+.025]],.014,'light',12)
    self.icos('small_projector',(front-.20,y,s.nose+.025),(.055,.082,.015),'light')
   elif s.headlight=='pixel':
    for j in range(5):
     yy=y-side*.17+j*side*.081
     self.box('offset_pixel_array',(front-.10-j*.027,yy,s.nose+.020),(.055,.043,.021),'light')
   else:
    self.box('deep_headlamp_recess',(front-.18,y,s.nose+.002),(.34,.31,.034),'black')
    for j in range(2):
     self.tube('recessed_hex_headlamp',[[front-.29,y-side*.11+j*side*.11,s.nose+.028],
       [front-.06,y+side*.03+j*side*.11,s.nose+.026]],.016,'light')
   # rear signature
   yr=side*s.width*.32
   if s.taillight=='hex':
    self.tube('six_sided_rear_light',[[rear-.030,yr-side*.10,s.tail-.017],
      [rear-.045,yr-side*.14,s.tail+.022],[rear-.045,yr-side*.06,s.tail+.053],
      [rear-.045,yr+side*.13,s.tail+.050],[rear-.042,yr+side*.18,s.tail+.015],
      [rear-.031,yr+side*.13,s.tail-.020]],.013,'red',8)
   elif s.taillight=='blade':
    self.box('vertical_tail_light',(rear-.028,yr,s.tail+.003),(.048,.053,.158),'red')
    self.box('blade_tail_root',(rear-.030,yr-side*.066,s.tail-.032),(.043,.158,.033),'red')
   elif s.taillight=='dot':
    for i in range(4):self.icos('independent_lens_array',(rear-.038,yr+side*(i-.5)*.075,s.tail+.004),(.025,.023,.023),'red',1)
   elif s.taillight=='fins':
    for j in range(4):
     self.box('rear_LED_fin',(rear-.035,yr+side*(j-1.5)*.060,s.tail+.035-j*.016),(.024,.031,.073-j*.006),'red')
   else:
    for j in range(3):self.box('stepped_rear_LED',(rear-.036,yr+side*j*.075,s.tail+.035-j*.02),(.025,.041,.048),'red')
  if s.kind=='ev':
   # electric car horizontal broken rear bar
   for i in range(13):
    self.box('modular_rear_continuous_lamp',(rear-.035,(i-6)*.054,s.tail+.008),(.022,.040,.012),'red')
  # original clear panel for number plate
  self.box('front_plate_blank',(front+.039,0,s.belly+.18),(.007,.36,.087),'accent')
  self.box('rear_plate_blank',(rear-.039,0,s.belly+.17),(.007,.36,.089),'accent')
 def aero(self):
  s=self.s;rear=-s.length/2;front=s.length/2
  self.box('front_air_scoop_dark',(front+.025,0,s.belly+.11),(.017,s.width*.53,.076),'black')
  for side in (-1,1):
   # shallow side intake: geometrically recessed rib array, bespoke placement
   if s.kind in ('super','track'):
    x=-.42
    for j in range(7):
     y=side*(s.width/2+.026)
     self.box('side_intake_gill',(x-j*.036,y,s.belt-.25-j*.015),(.012,.009,.10),'black')
   elif s.kind=='gt':
    for j in range(5):
     x=front-.48-j*.054
     self.box('front_fender_heat_slit',(x,side*(s.width/2+.009),s.belt-.12),(.013,.016,.07),'black')
   elif s.kind=='ev':
    self.tube('EV_aero_side_blade',[[.48,side*(s.width*.47),s.belt-.18],[.08,side*(s.width*.47),s.belt-.23],[-.45,side*(s.width*.47),s.belt-.28]],.010,'highlight',8)
   else:
    self.box('roadster_fender_vent',(front-.47,side*(s.width*.48),s.belt-.16),(.155,.013,.071),'black')
  if s.kind=='track':
   self.box('track_rear_wing_plane',(rear+.32,0,s.tail+.29),(.35,s.width*.96,.034),'accent')
   for side in (-1,1):self.box('track_wing_stanchion',(rear+.32,side*.53,s.tail+.16),(.035,.042,.24),'metal')
   self.box('track_front_splitter',(front+.052,0,s.belly+.032),(.22,s.width*.90,.028),'black')
  if s.kind=='super':
   self.box('supercar_rear_active_lip',(rear+.09,0,s.tail+.060),(.12,s.width*.72,.042),'accent')
  if s.kind=='gt':
   self.tube('grand_tourer_handraised_deck_lip',[[rear+.12,y,s.tail+.050] for y in np.linspace(-.66,.66,21)],.017,'paint')
  if s.kind=='ev':
   self.box('electric_diffuser_vanes',(rear-.06,0,s.belly+.05),(.12,s.width*.77,.067),'accent')
  if s.kind=='roadster':
   self.box('integrated_rear_lip',(rear+.22,0,s.tail+.045),(.13,s.width*.71,.022),'paint')
  # two real shaped mirrors offset from A-pillar; held by stems
  for side in (-1,1):
   x=s.roof_end+.19;y=side*(s.width*.49)
   self.tube('wing_mirror_pedestal',[[x,y,s.belt-.035],[x+.11,y+side*.072,s.belt+.035]],.013,'black')
   self.icos('mirror_aero_housing',(x+.13,y+side*.09,s.belt+.045),(.090,.070,.045),'paint')
   self.box('side_mirror_glass',(x+.14,y+side*.15,s.belt+.042),(.115,.006,.050),'metal')
 def machinery(self):
  s=self.s
  if s.kind=='ev':
   self.box('underfloor_battery_pack',(0,0,.445),(s.wheelbase-.43,s.width*.71,.092),'black')
   for j in range(9):self.box('battery_module_rib',(j-4)*.27,0,.497) if False else None
   for j in range(9):
    self.box('battery_module_rib',((j-4)*.27,0,.497),(.016,s.width*.68,.020),'metal')
   for ex in (-s.wheelbase/2+.26,s.wheelbase/2-.26):
    self.box('electric_drive_unit',(ex,0,.42),(.28,.45,.22),'metal')
    self.box('inverter_power_electronics',(ex+.08,0,.56),(.22,.30,.065),'copper')
  else:
   is_front=s.kind in ('gt','roadster')
   x=s.wheelbase*.26 if is_front else -s.wheelbase*.25
   n=6 if s.kind=='gt' else 8 if s.kind=='super' else 4 if s.kind=='roadster' else 5
   block_l=.55 if n>=6 else .43
   self.box('engine_cast_block',(x,0,.59),(block_l,.48,.38),'engine')
   self.box('valvetrain_top_cover',(x,0,.84),(block_l*.93,.39,.095),'black')
   for i in range(n):
    dx=(i-(n-1)/2)*block_l/(n+.45)
    side=(-1 if i%2==0 else 1)
    self.icos('individual_cylinder_manifold',(x+dx,side*.23,.75),(.065,.064,.082),'metal',1)
    self.tube('ignition_or_fuel_line',[[x+dx,side*.24,.80],[x+dx+.05,side*.32,.86]],.011,'black',7)
   self.box('transmission_case',(x+(-.34 if is_front else .39),0,.49),(.32,.37,.29),'engine')
   for side in (-1,1):
    self.tube('engine_cooling_hose',[[x+.10,side*.26,.67],[x+.34,side*.37,.65],[x+.39,side*.37,.52]],.018,'black')
  for wx in (-s.wheelbase/2,s.wheelbase/2):
   for side in (-1,1):
    start=[wx,side*.48,.39]
    end=[wx,side*(s.width*.40),s.tire_r-.02]
    self.tube('double_wishbone_control_arm',[start,end],.022,'metal')
    self.tube('coilover_strut',[wx+.09,side*.64,.43],[.01,.01,.01],'black') if False else None
    self.tube('coilover_damper',[[wx+.09,side*.64,.42],[wx+.02,side*.67,.79]],.028,'engine')
    self.tube('antiroll_link',[[wx-.08,side*.60,.40],[wx-.11,side*.78,.44]],.014,'metal')
 def finish(self):
  s=self.s
  self.sides();self.greenhouse();self.interior();self.lamps();self.aero();self.machinery()
  for x in (-s.wheelbase/2,s.wheelbase/2):
   for side in (-1,1):self.wheel(x,side,x>0)
  # source geometry centered; no OEM/trademark meshes or logos.
  # Batch thousands of procedural detail pieces by material while preserving four wheel assemblies.
  for (group,m),parts in self.groups.items():
   merged=trimesh.util.concatenate(parts) if len(parts)>1 else parts[0]
   merged.visual=trimesh.visual.TextureVisuals(material=self.M[m])
   self.scene.add_geometry(merged,geom_name=f'{group}_{m}',node_name=f'{group}_{m}')
  return self.scene


def main():
 report=[]
 for s in SPECS:
  scene=Builder(s).finish()
  path=OUT/(s.code+'.glb')
  scene.export(path)
  load=trimesh.load(path,force='scene')
  tris=sum(len(m.faces) for m in load.geometry.values())
  verts=sum(len(m.vertices) for m in load.geometry.values())
  if tris<25000:raise ValueError(f'Geometry unexpectedly crude: {s.code} {tris}')
  if len(load.geometry)<20:raise ValueError(f'Part count unexpectedly small: {s.code}')
  if not np.all(np.isfinite(load.bounds)):raise ValueError(s.code)
  size=path.stat().st_size
  sha=hashlib.sha256(path.read_bytes()).hexdigest()
  entry={'id':s.code,'architecture':s.architecture,'geometry_parts':len(load.geometry),'triangles':tris,'vertices':verts,'bytes':size,'sha256':sha,'bounds_m':load.bounds.tolist(),
    'production_status':'prototype_geometry_only','authorship':'authored by procedural Python generator for Helvetia; no sourced car meshes or brand assets',
    'commercial_legal_status':'requires independent review for design similarity and trademark/name clearance',
    'visual_qa':'not photorealism-certified; verify geometry, engine placement, glass, wheel collision and PBR in Blender/Unreal'}
  report.append(entry);print(json.dumps(entry))
 (OUT/'GENERATION_REPORT.json').write_text(json.dumps(report,indent=2)+'\n')
 print('Generated five original concept cars; file totals',sum(x['bytes'] for x in report))
if __name__=='__main__':main()