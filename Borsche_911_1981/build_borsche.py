#!/usr/bin/env python3
"""Borsche 911 1981 | An original 911SC-inspired game asset.

Generates two glTF 2.0 scenes (closed-engine-lid + exposed-engine) using
parametric geometry, deliberate part boundaries, and PBR materials.
Coordinates: +X = front, +Y = vehicle left, +Z = up. Units = metres.
Dependencies: numpy, scipy, trimesh, Pillow. Copyright 2026, generated asset.
"""
import math, os, copy, json
from collections import defaultdict
import numpy as np
from scipy.interpolate import PchipInterpolator
import trimesh
from trimesh.visual.material import PBRMaterial
from PIL import Image, ImageDraw, ImageFont

OUT=os.path.dirname(__file__)
PI=math.pi
RGB={
 'paint':(109,145,163,255), 'paint_high':(122,161,180,255), 'paint_shadow':(78,109,123,255),
 'rubber':(24,26,29,255), 'tire':(27,30,31,255), 'tire_tread':(39,42,43,255),
 'seam':(22,24,26,255), 'silhouette':(32,34,38,255),
 'chrome':(174,188,190,255), 'silver':(154,161,161,255), 'alloy':(111,119,123,255),
 'wheel':(128,146,154,255), 'brake':(112,117,119,255), 'dark_metal':(55,61,63,255),
 'engine':(143,143,133,255), 'engine_light':(183,177,158,255), 'bronze':(172,138,76,255),
 'copper':(148,88,43,255), 'belt':(17,21,23,255), 'hose':(39,42,41,255),
 'glass':(59,103,117,115), 'side_glass':(42,78,92,112), 'rear_glass':(38,71,76,145),
 'lens':(227,233,209,210), 'rear_red':(191,24,22,235), 'amber':(255,133,15,245),
 'white_light':(231,224,204,255), 'fog':(231,232,220,190),
 'interior':(31,32,34,255), 'leather':(61,61,59,255), 'cloth':(81,83,81,255),
 'metal_black':(56,59,63,255), 'steering':(38,39,41,255), 'badge':(198,170,94,255),
 'dashboard':(44,47,49,255), 'lights':(220,211,191,255)
}
MET={'paint':(.24,.27),'paint_high':(.27,.25),'paint_shadow':(.25,.31),'chrome':(.93,.15),
     'silver':(.82,.29),'alloy':(.82,.34),'wheel':(.78,.32),'brake':(.77,.42),
     'glass':(.15,.09),'side_glass':(.1,.10),'rear_glass':(.1,.14),'lens':(.08,.21),
     'engine':(.84,.45),'engine_light':(.88,.41),'bronze':(.8,.4),'copper':(.73,.42),
     'badge':(.72,.21),'amber':(.0,.25),'rear_red':(.03,.21),'fog':(.09,.15)}
MATS={}
for name,c in RGB.items():
 m,r=MET.get(name,(0.02,0.68))
 MATS[name]=PBRMaterial(name=name, baseColorFactor=c, metallicFactor=m,
                       roughnessFactor=r, doubleSided=name in ['glass','side_glass','rear_glass','lens','fog'],
                       alphaMode='BLEND' if c[3]<250 else 'OPAQUE')
parts=[]
def add(n, mesh, mat='paint', group='fixed'):
 if mesh is None: return
 mesh=mesh.copy()
 if not isinstance(mesh,trimesh.Trimesh): raise TypeError(n)
 mesh.visual=trimesh.visual.TextureVisuals(material=MATS[mat])
 parts.append((group,mat,n,mesh))
def surface(name, coords, faces, mat='paint', group='fixed'):
 mesh=trimesh.Trimesh(vertices=np.asarray(coords,dtype=float),faces=np.asarray(faces,dtype=int),process=False)
 add(name,mesh,mat,group)
def quadmesh(name, fn, na,nb, mat='paint',group='fixed', reverse=False):
 # Higher curved-panel tessellation avoids faceting in glTF viewers.
 upgrades={
  'continuous_stamped_side':(481,27),
  'curved_front_bonnet':(159,73),
  'formed_solid_coupe_roof':(109,75),
  'rear_quarter_deck_edge':(99,29),
  'engine_hatch_skin':(127,59),
  'front_windscreen_laminated':(65,49),
  'rear_windscreen_laminated':(79,43),
 }
 for prefix, (a,b) in upgrades.items():
  if name.startswith(prefix):na,nb=max(na,a),max(nb,b);break
 vs=[fn(i/(na-1),j/(nb-1)) for i in range(na) for j in range(nb)]
 fs=[]
 for i in range(na-1):
  for j in range(nb-1):
   a=i*nb+j; b=a+nb
   fs += [[a,a+1,b+1],[a,b+1,b]] if reverse else [[a,b,a+1],[a+1,b,b+1]]
 surface(name,vs,fs,mat,group)
def vec(a): return np.asarray(a,float)
def cyl(n, a,b,r, mat='silver', sections=20, group='fixed'):
 a=vec(a); b=vec(b); h=np.linalg.norm(b-a)
 if h<1e-7:return
 sections=max(sections,24) if r >= .012 else sections
 m=trimesh.creation.cylinder(radius=r,height=h,sections=sections)
 m.apply_transform(trimesh.geometry.align_vectors([0,0,1],(b-a)/h))
 m.apply_translation((a+b)/2)
 add(n,m,mat,group)
def box(n, c,size, mat='paint',group='fixed'):
 m=trimesh.creation.box(extents=size);m.apply_translation(c);add(n,m,mat,group)
def sph(n,c,radii,mat='silver',subdivisions=2,group='fixed'):
 if n in {'formed_headlamp_fender_socket','circular_headlight_glass','outside_rearview_mirror','mirror_reflective_surface','front_seat_headrest'}:subdivisions=max(4,subdivisions)
 m=trimesh.creation.icosphere(subdivisions=subdivisions,radius=1.0)
 m.apply_scale(radii);m.apply_translation(c);add(n,m,mat,group)
def tube(n, pts, r, mat='rubber', sides=12,group='fixed', caps=True):
 # continuous swept parallel-transport round tube (minimizes visible seam artifacts)
 p=np.array(pts,dtype=float); p=p[np.r_[True,np.linalg.norm(np.diff(p,axis=0),axis=1)>1e-6]]
 if len(p)<2:return
 t=np.gradient(p,axis=0); t/=np.linalg.norm(t,axis=1)[:,None]
 u=np.zeros_like(t); v=np.zeros_like(t)
 n0=np.array([0,0,1]) if abs(t[0,2])<.9 else np.array([0,1,0]);
 u[0]=np.cross(t[0],n0);u[0]/=np.linalg.norm(u[0]);v[0]=np.cross(t[0],u[0]);
 for i in range(1,len(p)):
  d=u[i-1]-np.dot(u[i-1],t[i])*t[i];
  if np.linalg.norm(d)<1e-8:d=np.cross(t[i],[0,1,0])
  u[i]=d/np.linalg.norm(d);v[i]=np.cross(t[i],u[i])
 if np.isscalar(r):r=np.ones(len(p))*r
 vv=[p[i]+float(r[i])*(math.cos(a)*u[i]+math.sin(a)*v[i]) for i in range(len(p)) for a in np.arange(sides)*2*PI/sides]
 ff=[]
 for i in range(len(p)-1):
  for j in range(sides):
   a=i*sides+j;b=i*sides+(j+1)%sides;c=(i+1)*sides+j;d=(i+1)*sides+(j+1)%sides
   ff.extend([[a,c,b],[b,c,d]])
 if caps:
  vv.extend([p[0],p[-1]]);s=len(vv)-2
  for j in range(sides):ff.extend([[s,(j+1)%sides,j],[s+1,(len(p)-1)*sides+j,(len(p)-1)*sides+(j+1)%sides]])
 surface(n,vv,ff,mat,group)
def path(n, pts, r,mat='chrome',group='fixed',sides=12):tube(n,pts,r,mat,sides,group)
def polygon_extrude(n,points,delta,mat='silver',group='fixed'):
 # polygon outline assumed convex; 3D extrusion with triangular caps
 pts=np.array(points,dtype=float); npt=len(pts); vertices=np.vstack([pts,pts+delta]);fs=[]
 for i in range(1,npt-1):fs.extend([[0,i,i+1],[npt,npt+i+1,npt+i]])
 for i in range(npt):j=(i+1)%npt;fs.extend([[i,j,npt+j],[i,npt+j,npt+i]])
 surface(n,vertices,fs,mat,group)
def cylinder_axis(n,c,radius,depth,axis,mat,sections=32,group='fixed'):
 a=vec(c); veca=np.array({'x':[1,0,0],'y':[0,1,0],'z':[0,0,1]}[axis],float)
 cyl(n,a-veca*depth/2,a+veca*depth/2,radius,mat,sections,group)
def ring(n,center,major,minor,axis,mat,segments=80,sides=12,group='fixed'):
 segments=max(segments,88) if major>.075 else segments
 sides=max(sides,12) if minor>.006 else sides
 c=vec(center)
 axial=np.asarray(axis,float);axial/=np.linalg.norm(axial)
 ref=np.array([0.,0.,1.]) if abs(axial[2])<0.9 else np.array([0.,1.,0.])
 u=np.cross(axial,ref);u/=np.linalg.norm(u);v=np.cross(axial,u)
 vs=[];fs=[]
 for i in range(segments):
  th=2*PI*i/segments;rr=math.cos(th)*u+math.sin(th)*v;tan=-math.sin(th)*u+math.cos(th)*v
  for j in range(sides):
   a=2*PI*j/sides;vs.append(c+(major+minor*math.cos(a))*rr+minor*math.sin(a)*axial)
 for i in range(segments):
  for j in range(sides):
   a=i*sides+j;b=((i+1)%segments)*sides+j;k=(j+1)%sides;d=i*sides+k;e=((i+1)%segments)*sides+k
   fs.extend([[a,b,d],[d,b,e]])
 surface(n,vs,fs,mat,group)
# Mechanical guides: x-axis facing forward, midplane y=0, wheels ±1.135m apart.
WBASE=2.271; XF=1.179; XR=-1.092; wheel_z=.326
profile_x=[-2.14,-2.03,-1.88,-1.68,-1.48,-1.24,-.90,-.5,0,.45,.85,1.1,1.45,1.70,1.90,2.1,2.145]
profile_w=[.52,.67,.735,.763,.777,.782,.77,.755,.735,.747,.771,.787,.789,.755,.72,.61,.52]
profile_h=[.73,.78,.82,.85,.89,.90,.91,.93,.93,.92,.90,.85,.79,.76,.72,.66,.61]
WIDTH=PchipInterpolator(profile_x,profile_w);BELT=PchipInterpolator(profile_x,profile_h)
def wid(x,z=0.65):
 x=np.clip(x,-2.14,2.145)
 return float(WIDTH(x)) + (.018 if z<.55 else .0)* (math.exp(-((x-XR)/.48)**4)+math.exp(-((x-XF)/.48)**4))
def belt(x):return float(BELT(np.clip(x,-2.14,2.145)))
def arch(x):
 base=.205;radius=.515; half=.49
 return max([base+.515*math.sqrt(max(0,1-((x-xc)/half)**2)) for xc in [XF,XR] if abs(x-xc)<half] or [base])
def bodyside(sign):
 def fn(u,v):
  x=-2.135 + u*4.274;low=arch(x);zz=low+(belt(x)-low)*v
  # rounded upper shoulder and mild door hollow to evoke stamped metal
  y=sign*(wid(x,zz)-.009*math.sin(PI*v)+.010*math.sin(PI*v)*math.exp(-((x+.25)/.70)**4))
  return [x,y,zz]
 quadmesh('continuous_stamped_side_{}'.format(sign),fn,281,12,'paint',reverse=(sign>0))
 # actual dark wheel-well inner lip follows purpose-built wheel arch
 for xc in [XR,XF]:
  xs=np.linspace(xc-.485,xc+.485,90)
  ps=[[x,sign*(wid(x,arch(x))-.003),arch(x)-.009] for x in xs]
  path('formed_arch_edge',ps,.0065,'paint_shadow')
  # slightly inset black underbody liner inside the arches -- circles can't be seen through body
  cylinder_axis('wheel_liner', [xc,sign*.655,.328],.310,.035,'y','silhouette',48)
 # crease highlight runs over rocker (not a detached strip)
 pts=[[x,sign*(wid(x,.34)+.001),.344] for x in np.linspace(-.59,.79,32)]
 path('lower_door_sill_trim',pts,.011,'silhouette')
 # door panel gaps: genuine panel border with two vertical lines and lower return
 p1=[]; p2=[]
 for z in np.linspace(.37,.90,22):
  for x,arr in [(-.55,p1),(.70,p2)]:
   arr.append([x,sign*(wid(x,z)+.008),z])
 path('door_front_seam',p2,.0035,'seam');path('door_rear_seam',p1,.0035,'seam')
 p=[[x,sign*(wid(x,.37)+.008),.371] for x in np.linspace(-.55,.70,30)]
 path('door_bottom_seam',p,.0035,'seam')
 # handles at rear edge of door, thin black surround and plated lever
 x=-.37;y=sign*(wid(x,.8)+.014);z=.812
 box('door_handle_base',[x,y,z],[.164,.024,.048],'silhouette')
 box('door_pull_metal',[x+.005,y+sign*.017,z+.005],[.130,.022,.016],'chrome')
 cylinder_axis('key_cylinder',[x-.113,y+sign*.007,z],.014,.012,'y','chrome')
 # fender side marker, near rear of front bumper
 x=1.65; y=sign*(wid(x,.62)+.014)
 box('amber_wraparound_marker',[x,y,.615],[.31,.015,.073],'amber')
 path('front_side_marker_outline',[[x0,y+sign*.009,z0] for x0,z0 in [(1.50,.57),(1.82,.57),(1.82,.66),(1.50,.66),(1.50,.57)]],.003,'seam')

bodyside(1);bodyside(-1)
# Thin underfloor chassis + longitudinal sills; no external random gap on lower body.
box('monocoque_floor',[0,0,.245],[3.18,1.39,.122],'paint_shadow')
for s in [-1,1]:
 box('rocker_undertray',[-.03,s*.68,.275],[1.63,.13,.115],'paint_shadow')
 box('sill_black_rubber_strip',[.04,s*.746,.342],[1.40,.024,.035],'rubber')
 # Arch trim follows ONLY the painted upper wheel opening; lower ring not visible on the real car.
 for xc in [XR,XF]:
  xs=np.linspace(xc-.480,xc+.480,80)
  pts=[[xx,s*(wid(xx,arch(xx))+.003),arch(xx)] for xx in xs]
  path('rubber_sealed_upper_wheel_lip',pts,.006,'rubber')

# Front hood/fenders: continuously sampled shaped sheet with authentic 911 raised haunches.
def hz(x,t):
 # center falls toward the nose, with pronounced shoulder to side near headlamps
 z=np.interp(x,[.68,1.04,1.45,1.75,2.145],[.915,.86,.785,.737,.656])
 archbulge=.075*math.exp(-((x-1.73)/.46)**2)*(max(0,1-abs(t-.85)/.36))
 return z+.014*(abs(t)**1.7)+archbulge
quadmesh('curved_front_bonnet_raised_fenders',lambda u,v:(.68+u*1.46, (2*v-1)*wid(.68+u*1.46, .83)*.985, hz(.68+u*1.46, abs(2*v-1))),83,39)
# Hood panel line: only two thin purposeful curves on painted surface.
for s in [-1,1]:
 xs=np.linspace(.76,2.075,48)
 p=[[x,s*(.500-.065*(x-.76)/1.315),hz(x,(.500-.065*(x-.76)/1.315)/wid(x))+.002] for x in xs]
 path('front_hood_panel_line',p,.0030,'seam')
# front hatch edge at base windshield
path('front_hatch_back_seam',[[.722,y,.905] for y in np.linspace(-.46,.46,20)],.003,'seam')
# Cool air-slot stripe/bonnet seal
path('front_hood_shut_line',[[2.048,y,hz(2.048,abs(y)/wid(2.048))+.003] for y in np.linspace(-.43,.43,24)],.0027,'seam')
# Tail end profile and painted rear quarter-deck lips; opening is an intentional engine service panel.
def rz(x,t):
 t=abs(t)
 return np.interp(x,[-2.14,-1.93,-1.69,-1.34],[.74,.805,.875,.961])+.027*(t**1.7)
for s in [-1,1]:
 quadmesh('rear_quarter_deck_edge',lambda u,v:(-2.13+u*.82,s*(.535+v*(wid(-2.13+u*.82)-.535)),rz(-2.13+u*.82, ( .535+v*(wid(-2.13+u*.82)-.535))/wid(-2.13+u*.82))),47,11,reverse=(s<0))
# front rear engine-deck sill around hatch
quadmesh('forward_engine_lid_flange',lambda u,v:(-1.32+u*.074, (v*2-1)*.575,rz(-1.32+u*.074,abs(v*2-1)*.76)),5,19)
# rear deck hard body lip
quadmesh('rear_engine_lid_flange',lambda u,v:(-2.14+u*.09, (v*2-1)*.55,rz(-2.14+u*.09,abs(v*2-1)*.8)),5,19)
# rear-most panel below tail grille
box('rear_back_sheet',[-2.082,0,.650],[.091,1.25,.238],'paint')
# rear engine lid proper, modeled as removable articulated part
quadmesh('engine_hatch_skin',lambda u,v:(-2.055+u*.741,(v*2-1)*.535,rz(-2.055+u*.741,abs(v*2-1)*.72)+.003),56,30,'paint',group='lid')
# side & trailing panel gap only when closed / engine lid open has real aperture
for s in [-1,1]:
 p=[[x,s*.539,rz(x,.75)+.003] for x in np.linspace(-2.052,-1.318,55)]
 path('engine_lid_flange_black_seal',p,.005,'seam',group='fixed')
# ventilation grille is embedded in engine-lid paint, separated into deliberate thin slats
for k in range(15):
 x=-1.94 + k*.027
 box('engine_lid_vent_opening',[x,0,rz(x,0)+.011],[.009,.78,.008],'silhouette',group='lid')
for s in [-1,1]:
 path('engine_hatch_longitudinal_pinstripe',[[x,s*.455,rz(x,.77)+.013] for x in np.linspace(-1.95,-1.47,25)],.003,'paint_shadow',group='lid')
# Photo resembles small raised rear aerodynamic black rubber lip
path('subtle_rear_deck_black_lip',[[ -2.052,y,rz(-2.052,abs(y)/.77)+.035 ] for y in np.linspace(-.49,.49,25)],.035,'rubber',group='lid')

# Glazed 911 coupe cabin: original defining roof drop, raked windshield and rear quarters
rx=[-.70,-.53,-.28,.0,.15];rh=[1.258,1.303,1.318,1.312,1.275]
RH=PchipInterpolator(rx,rh)
def roof_fn(u,v):
 x=-.70+u*.85;y=(2*v-1)*.567
 z=float(RH(x))-.039*(abs(y)/.567)**2
 return [x,y,z]
quadmesh('formed_solid_coupe_roof',roof_fn,39,29,'paint')
# roof supporting ribs / front and back header, deliberate no-missing-panels.
for x in [-.70,.145]:
 path('roof_lip_outer_header',[[x,y,float(RH(x))-.039*(abs(y)/.567)**2] for y in np.linspace(-.565,.565,33)],.013,'paint')
# windshield & back glass surfaces curvature
def windshield(u,v):
 y=(2*v-1)*(.606-.064*u)
 x=.727-.580*u + .022*(1-(2*v-1)**2)*math.sin(PI*u)
 z=.910+.359*u+ .010*(1-(2*v-1)**2)*math.sin(PI*u)
 return [x,y,z]
quadmesh('front_windscreen_laminated',windshield,34,27,'glass')
def rearwin(u,v):
 y=(2*v-1)*(.592-.040*u)
 x=-1.430 + .730*u - .026*(1-(2*v-1)**2)*math.sin(PI*u)
 z=.957+.311*u+.015*(1-(2*v-1)**2)*math.sin(PI*u)
 return [x,y,z]
quadmesh('rear_windscreen_laminated',rearwin,40,23,'rear_glass')
# Curved glass seal / aluminum windscreen surround = exact boundary edges rather than random gaps
for fn,key in [(windshield,'windscreen'),(rearwin,'rear_window')]:
 for v in [0.,1.]:path(key+'_pillar_seal',[fn(u,v) for u in np.linspace(0,1,33)],.013,'rubber')
 for u in [0.,1.]:path(key+'_header_seal',[fn(u,v) for v in np.linspace(0,1,28)],.012,'rubber')
# Side window triangles follow the same body belt and roof leading/trailing edges
for s in [-1,1]:
 y=s*.754
 # Solid B-pillar to physically divide front & rear glazing
 poly_front=[[-.430,s*.739,.951],[.612,s*.738,.925],[.113,s*.558,1.259],[-.427,s*.568,1.272]]
 # Curved-ish side forward window (4-point with glazing divided into quarter detail)
 polygon_extrude('door_glass_'+str(s),poly_front,[0,-s*.003,0],'side_glass')
 poly_rear=[[-1.386,s*.758,.946],[-.453,s*.741,.951],[-.445,s*.568,1.268],[-.691,s*.565,1.258]]
 polygon_extrude('fixed_rear_quarter_glass_'+str(s),poly_rear,[0,-s*.003,0],'side_glass')
 # perimeter seals
 for label,poly in [('door',poly_front),('rear_quarter',poly_rear)]:
  path(label+'_weatherstrip_'+str(s),poly+[poly[0]],.012,'rubber')
 # black B pillar spans from side belt to roof, thick enough to be intentional
 polygon_extrude('formed_B_pillar_'+str(s),[[-.470,s*.749,.933],[-.416,s*.747,.94],[-.421,s*.571,1.274],[-.473,s*.570,1.273]],[0,-s*.02,0],'rubber')
 # anodized thin window trims on lower door glass line
 path('window_beltline_trim_'+str(s),[[x,s*(wid(x,.934)-.025),.930] for x in np.linspace(-1.4,.67,60)],.008,'chrome')
 # Front slanted windshield A-pillar painted steel channel above glazing border
 path('metal_A_pillar_'+str(s),[[.727-.580*t,s*(.607-.065*t),.908+.36*t] for t in np.linspace(0,1,30)],.019,'paint')
 # Original teardrop door mirrors, housings, stems, reflective panels
 cyl('mirror_base_stalk',[.55,s*.733,.96],[.53,s*.793,1.007],.021,'chrome')
 sph('outside_rearview_mirror',[.545,s*.825,1.023],[.108,.068,.048],'paint_high',3)
 sph('mirror_reflective_surface',[.549,s*.890,1.026],[.084,.009,.031],'chrome',2)
 path('mirror_mount_black_gasket',[[.49,s*.742,.942],[.567,s*.743,.944]],.012,'silhouette')
 # tiny door quarter glass divider behind mirror
 path('window_vent_divider',[[.490,s*.735,.935],[.305,s*.590,1.180]],.007,'chrome')
# Front windscreen wipers rest above lower seal
for s in [-1,1]:
 y0=s*.26
 path('windscreen_wiper_arm',[[.746,y0,.936],[.706,y0-s*.055,.961],[.671,y0-s*.285,.990]],.008,'metal_black')
 path('windscreen_wiper_rubber',[[.665,y0-s*.31,.998],[.670,y0+s*.23,.998]],.012,'rubber')

# Front & rear bumper assemblies, integrated rubber impact trim like early-80s 911.
box('front_impact_bumper_painted_shell',[2.095,0,.535],[.182,1.286,.135],'paint_shadow')
box('front_bumper_black_rubber_strip',[2.190,0,.587],[.029,1.390,.044],'rubber')
box('front_bumper_lower_valance',[2.050,0,.408],[.155,1.230,.116],'paint_shadow')
box('front_air_inlet_black',[2.136,0,.429],[.016,.445,.057],'silhouette')
for s in [-1,1]:
 box('front_bumper_corner_rubber',[2.10,s*.656,.575],[.20,.116,.075],'rubber')
 box('front_amber_indicator',[2.183,s*.505,.647],[.032,.218,.087],'amber')
 box('front_indicator_side_white',[2.188,s*.369,.650],[.027,.05,.081],'lens')
 box('rectangular_front_fog_lamp',[2.194,s*.520,.392],[.051,.136,.071],'fog')
 box('fog_lamp_dark_recess',[2.155,s*.525,.392],[.035,.171,.085],'rubber')
 # vertical accordion corner rubber bumper bellows
 for k in range(4):
  box('front_bumper_bellows',[1.984-k*.031,s*.738,.574],[.012,.038,.147],'rubber')
# authentic round headlights: curved recess, enamel painted rim, reflector & glass
for s in [-1,1]:
 c=[1.950,s*.628,.832]
 # Rounded integrated metal headlight bucket: compact, no oversized floating dome.
 sph('formed_headlamp_fender_socket',[1.853,s*.627,.809],[.112,.139,.114],'paint',3)
 # body-colored flange lays almost flush, swept orientation to face front
 axis=np.array([.95,s*.17,.22]);axis/=np.linalg.norm(axis)
 ring('headlight_outer_bezel',c,.112,.013,axis,'chrome',segments=52,sides=10)
 cylinder_axis('headlight_reflector_bowl',[1.955,s*.629,.830],.102,.020,'x','silver',48)
 sph('circular_headlight_glass',[1.980,s*.630,.837],[.029,.105,.104],'lens',3)
 sph('headlamp_lightbulb',[2.008,s*.630,.838],[.017,.021,.021],'white_light',2)
 # thin circular lens fluting grooves
 for r0 in [.062,.082,.096]:ring('headlamp_glass_internal_groove',[1.997,s*.631,.836],r0,.0025,[1,0,0],'lens',48,6)
# rear impact bumper & lamps
box('rear_bumper_body_shell',[-2.135,0,.507],[.166,1.275,.170],'paint_shadow')
box('rear_bumper_rubber_bar',[-2.229,0,.575],[.025,1.440,.055],'rubber')
box('rear_valance_lower',[-2.097,0,.373],[.104,1.185,.125],'paint_shadow')
for s in [-1,1]:
 box('rear_bumper_corner',[-2.130,s*.650,.528],[.145,.120,.140],'rubber')
 box('rear_lamp_dark_housing',[-2.141,s*.537,.749],[.040,.33,.114],'rubber')
 box('rear_tail_light_red',[-2.168,s*.567,.757],[.018,.228,.083],'rear_red')
 box('rear_tail_light_indicator',[-2.170,s*.401,.757],[.02,.091,.083],'amber')
 box('rear_bumperette',[-2.222,s*.473,.46],[.099,.066,.174],'rubber')
 box('reverse_light',[-2.168,s*.254,.748],[.019,.073,.055],'lens')
# license panel, rear central black grille
box('rear_license_recess',[-2.202,0,.474],[.015,.370,.118],'silhouette')
box('rear_plate_silver_backing',[-2.211,0,.476],[.008,.315,.085],'silver')
# exhaust pipe physically exits rear lower valance
cyl('stainless_rear_tailpipe',[-2.01,-.48,.304],[-2.260,-.49,.302],.034,'dark_metal',24)
ring('exhaust_tail_chrome_tip',[-2.265,-.49,.302],.032,.005,[-1,0,0],'chrome',36,8)

# Underlying cabin volume and full interior furniture (not empty black box)
box('carpeted_floor',[-.275,0,.327],[2.00,1.210,.050],'interior')
box('rear_seat_shelf',[-1.15,0,.488],[.75,1.17,.09],'leather')
for s in [-1,1]:
 # Outer door cards, flush with shell
 box('inside_door_card',[.070,s*.676,.630],[1.130,.050,.29],'leather')
 box('door_armrest',[.06,s*.629,.632],[.52,.105,.072],'cloth')
 box('interior_door_pull',[-.25,s*.621,.787],[.185,.025,.028],'silver')
 # front sports seat cushion, curved bolsters, upright squab, integral headrest
 cx=-.33;sy=s*.315
 sph('front_seat_cushion',[cx,sy,.495],[.34,.234,.100],'leather',3)
 sph('front_seat_back',[cx-.223,sy,.761],[.107,.229,.312],'leather',3)
 sph('front_seat_inner_padded_insert',[cx-.115,sy,.736],[.065,.165,.228],'cloth',3)
 sph('front_seat_headrest',[cx-.266,sy,1.079],[.091,.173,.105],'leather',3)
 for yy in [-.169,.169]:
  path('bucket_seat_side_bolster',[[cx+.22,sy+yy,.51],[cx+.08,sy+yy,.555],[cx-.20,sy+yy,.942]],.030,'leather')
 # small folding rear seat
 sph('rear_seat_pad',[-1.166,s*.292,.544],[.265,.224,.068],'leather',2)
 sph('rear_seat_backrest',[-1.425,s*.294,.677],[.059,.232,.198],'leather',2)
# dash carrier and raised instrument cowling at front of passenger volume
box('dashboard_main',[.512,0,.804],[.328,1.236,.188],'dashboard')
sph('instrument_hood',[.562,.321,.925],[.22,.325,.109],'dashboard',2)
box('glove_box',[.46,-.310,.733],[.024,.382,.067],'leather')
# 5 gauges visible through windshield, directed towards driver seat (assume LHD +Y)
for i,(dy,rad) in enumerate([(-.205,.059),(-.103,.071),(0,.083),(.106,.071),(.212,.060)]):
 cy=.300+dy
 cylinder_axis('five_instrument_bezel_%s'%i,[.380,cy,.898],rad,.024,'x','chrome',24)
 cylinder_axis('gauge_black_face_%s'%i,[.361,cy,.898],rad*.86,.026,'x','silhouette',24)
 for k in range(8):
  a=2*PI*k/8
  cyl('gauge_ticks',[.340,cy+rad*.65*math.cos(a),.898+rad*.65*math.sin(a)],
      [.340,cy+rad*.76*math.cos(a),.898+rad*.76*math.sin(a)],.0025,'white_light',6)
 cyl('gauge_needle',[.339,cy,.898],[.338,cy+.018,.898+rad*.50],.003,'rear_red',7)
# wheel oriented approximately parallel to X wall, tilted slightly toward driver
steer=[.170,.322,.863]
ring('three_spoke_steering_wheel',steer,.166,.018,[.95,0,.31],'steering',64,10)
cylinder_axis('steering_hub',[.158,.322,.862],.062,.050,'x','leather')
for a in [0,2*PI/3,4*PI/3]:
 yy=.322+.148*math.cos(a);zz=.863+.148*math.sin(a)
 cyl('three_steering_spokes',[.156,.322,.863],[.155,yy,zz],.012,'metal_black',9)
cyl('steering_column',[.395,.322,.860],[.152,.322,.863],.043,'interior')
# central console + shift lever + knob + pedals
box('tunnel_centre_console',[-.03,0,.425],[.92,.220,.154],'leather')
cyl('manual_gear_shifter',[-.07,0,.49],[-.03,0,.702],.012,'chrome')
sph('leather_gear_knob',[-.025,0,.708],[.035,.032,.031],'steering',2)
for y in [.23,.32,.39]:box('pedal',[.612,y,.440],[.020,.046,.065],'metal_black')
# seat belts and door locks, diagonal rear side
for s in [-1,1]:
 path('seatbelt_webbing',[[ -.70,s*.635,1.18],[-.23,s*.39,.55]],.014,'rubber')

# Drive and suspension/chassis details: axles, front brake calipers, disc and wheel wells
for x in [XR,XF]:
 cyl('axle_steel',[x,-.755,wheel_z],[x,.755,wheel_z],.037,'alloy',20)
 for s in [-1,1]:
  # vented cast-iron discs behind forged 5-spoke wheels
  y=s*.734
  cylinder_axis('vented_brake_disc',[x,y,wheel_z],.234,.025,'y','brake',44)
  cylinder_axis('brake_hub',[x,s*.752,wheel_z],.10,.044,'y','dark_metal',36)
  sph('fixed_brake_caliper',[x-.11,s*.753,wheel_z+.166],[.075,.050,.064],'alloy',2)
  for i in range(8):
   a=2*PI*i/8
   cylinder_axis('brake_rotor_drill',[x+.14*math.cos(a),s*.747,wheel_z+.14*math.sin(a)],.009,.012,'y','silhouette',9)
  # suspension arm meets underbody and carrier
  cyl('forged_wishbone',[x,s*.67,wheel_z-.068],[x+(-.16 if x>0 else .20),s*.48,.225],.029,'alloy')

# Handmade 5-petal Fuchs-inspired forged wheels; full tire sidewalls and tread blocks.
def wheel_assembly(x,s,rear):
 rad=.328 if rear else .324; cy=s*.702
 tirew=.238 if rear else .210
 # radial ring with accurate rounded sidewalls and inward bead. Profile is closed.
 profile=[(.223,-.097),(.251,-.115),(.289,-.112),(.312,-.104),(.325,-.085),
          (rad,-.055),(rad,.055),(.325,.085),(.312,.104),(.289,.112),(.251,.115),(.223,.097)]
 # adapt width based rear tire
 stretch=tirew/.210
 vs=[];fs=[];N=144;M=len(profile)
 for i in range(N):
  a=2*PI*i/N
  for radius,yy in profile:
   vs.append([x+radius*math.cos(a),cy+yy*stretch,wheel_z+radius*math.sin(a)])
 for i in range(N):
  for j in range(M):
   a=i*M+j;b=((i+1)%N)*M+j; k=i*M+(j+1)%M;d=((i+1)%N)*M+(j+1)%M
   fs.extend([[a,b,k],[k,b,d]])
 surface('radial_tire_rubber_%s_%s'%(x,s),vs,fs,'tire')
 # cut tread blocks and thin radial sidewall ribs
 for i in range(74):
  a=2*PI*i/74;xr=x+rad*math.cos(a);zz=wheel_z+rad*math.sin(a)
  path('tire_tread_groove',[ [x+(rad+.001)*math.cos(a), cy+signy*tirew*.42, wheel_z+(rad+.001)*math.sin(a)] for signy in [-1,1]],.0029,'tire_tread',sides=5)
 for yy in [-.078,.078]:
  ring('tire_sidewall_radial_ridge',[x,cy+yy*stretch,wheel_z],.278,.0025,[0,1,0],'tire_tread',72,5)
 # Rim behind open spokes, lips forged / polished
 outside=cy+s*tirew*.49
 cylinder_axis('dark_wheel_barrel',[x,cy,wheel_z],.226,tirew*.59,'y','silhouette',52)
 cylinder_axis('forged_rim_face_shadow',[x,outside-s*.021,wheel_z],.203,.015,'y','dark_metal',48)
 ring('Fuchs_dished_outer_polished_lip',[x,outside,wheel_z],.223,.017,[0,1,0],'chrome',72,10)
 ring('rim_forged_inner_lip',[x,outside+s*.004,wheel_z],.185,.008,[0,1,0],'alloy',68,7)
 # Fuchs sculpted 5-spoke petals, aluminum/colored metallic paint on face
 for k in range(5):
  a=2*PI*k/5 + PI/2
  def polar(r,offset):return [x+r*math.cos(a+offset),outside+s*.012,wheel_z+r*math.sin(a+offset)]
  p=[polar(.053,-.38),polar(.206,-.18),polar(.220,0),polar(.206,.18),polar(.053,.38)]
  polygon_extrude('five_petaled_forged_wheel_spoke',p,[0,-s*.020,0],'wheel')
  c0=[x+.11*math.cos(a),outside+s*.018,wheel_z+.11*math.sin(a)]
  path('machined_spoke_center_groove',[polar(.082,0),polar(.173,0)],.005,'chrome')
  cylinder_axis('lug_stud_bolt',[x+.078*math.cos(a),outside+s*.020,wheel_z+.078*math.sin(a)],.012,.014,'y','chrome',10)
 cylinder_axis('centre_axle_cap',[x,outside+s*.020,wheel_z],.063,.024,'y','alloy',36)
 ring('wheel_centre_cap_ring',[x,outside+s*.037,wheel_z],.059,.004,[0,1,0],'chrome',42)
for x in [XR,XF]:
 for s in [-1,1]:wheel_assembly(x,s,x<0)

# The 1981 rear air-cooled horizontally-opposed 3.0 litre six-cylinder engine.
# Entire unit has correct rear location and separately identifiable parts.
box('rear_engine_subframe',[-1.580,0,.502],[.85,.97,.070],'dark_metal')
box('flat_six_engine_main_crankcase',[-1.545,0,.574],[.596,.505,.285],'engine')
box('flat_six_sump_lower_case',[-1.550,0,.397],[.410,.380,.140],'alloy')
# cast cooling fins for 3 cylinders on each opposing bank
for side in [-1,1]:
 y=side*.325
 for i,xx in enumerate([-1.785,-1.585,-1.385]):
  box('horizontally_opposed_cylinder_barrel_%s_%s'%(side,i),[xx,y,.543],[.171,.267,.139],'engine')
  box('three_cylinder_rocker_cover_%s_%s'%(side,i),[xx,side*.469,.555],[.183,.059,.190],'engine_light')
  for j in range(7):
   box('machined_cooling_fin',[xx-.064+j*.022,side*.450,.551],[.012,.207,.152],'alloy')
  for zz in [.47,.625]:
   cyl('rocker_cover_hex_fastener',[xx-.071,side*.496,zz],[xx-.061,side*.500,zz],.011,'silver',9)
# pulley and the signature upright metal cooling fan, front axis toward rear of car
fan_center=[-1.914,0,.763];axis=[1,0,0]
ring('signature_911_fan_housing',fan_center,.173,.029,axis,'engine_light',76,12)
ring('fan_outer_dark_recess',[-1.946,0,.763],.151,.008,axis,'silhouette',72,8)
# Fan blades directed radially through circular opening
for i in range(11):
 a=2*PI*i/11
 p=[]
 for rr,da in [(.040,-.22),(.146,-.20),(.146,.07),(.054,.40)]:
  p.append([-1.977,rr*math.cos(a+da),.763+rr*math.sin(a+da)])
 polygon_extrude('eleven_curved_aircooled_fan_blades',p,[.008,0,0],'silver')
cylinder_axis('fan_rotor_center_cap',[-1.989,0,.763],.045,.026,'x','alloy',28)
# alternator below fan with belt pulley and leather-colored V belt
cylinder_axis('alternator_generator_body',[-1.90,-.083,.591],.087,.180,'x','alloy',32)
ring('alternator_pulley',[-2.003,-.082,.589],.065,.010,[1,0,0],'chrome',35)
for a in np.linspace(0,2*PI,8,endpoint=False):
  cyl('alternator_stator_cooling_slot',[-2.006,-.082+.051*math.cos(a),.589+.051*math.sin(a)],[-2.012,-.082+.065*math.cos(a),.589+.065*math.sin(a)],.007,'silhouette',8)
path('alternator_v_belt',[[-2.008,-.004,.933],[-2.008,.170,.763],[-2.008,.009,.589],[-2.008,-.082,.536],[-2.008,-.153,.608],[-2.008,-.161,.73],[-2.008,-.075,.900],[-2.008,-.004,.933]],.009,'belt')
# Bosch K-Jetronic air filter + injection fuel distributor and plenum
box('KJetronic_black_air_filter_box',[-1.301,-.405,.827],[.35,.385,.152],'silhouette')
box('air_filter_cover_molded_ribs',[-1.291,-.404,.908],[.300,.309,.016],'dark_metal')
for j in range(5):box('air_filter_lid_fastening_bands',[-1.43+j*.064,-.405,.921],[.016,.30,.007],'rubber')
sph('cast_metal_airflow_meter',[-1.29,.027,.778],[.189,.155,.089],'engine_light',2)
cylinder_axis('KJetronic_fuel_distributor',[-1.26,.05,.882],.075,.097,'z','bronze',32)
# rubber elbow connection goes to airbox
path('rubber_induction_hose',[[-1.25,-.294,.828],[-1.20,-.18,.848],[-1.257,0,.827]],.059,'hose')
# six separate intake ducts to each cylinder, metallic elbows and black sleeves
for side in [-1,1]:
 for i,xx in enumerate([-1.78,-1.58,-1.38]):
  p0=[-1.35+.045*i,side*.11,.838];p1=[xx+.075,side*.175,.886];p2=[xx,side*.30,.812];p3=[xx,side*.352,.69]
  path('six_curved_individual_intake_runners',[p0,p1,p2,p3],.029,'engine_light')
  path('manifold_sleeve',[[xx,side*.32,.744],[xx,side*.351,.703]],.036,'hose')
  path('fuel_injector_hard_line',[[-1.25,.05,.939],[xx,side*.34,.927],[xx,side*.385,.683]],.0045,'bronze')
  path('six_spark_plug_wires',[[-1.88,-.265,.749],[xx,side*.455,.754],[xx,side*.481,.631]],.005,'copper')
# orange ignition distributor and wires & central coil
cylinder_axis('red_brown_ignition_distributor_cap',[-1.877,-.350,.743],.064,.092,'z','copper',24)
cylinder_axis('ignition_coil',[-1.17,.385,.815],.037,.121,'z','silhouette',20)
# oil cap, filler neck, filter, ribbed cooler and hoses
cylinder_axis('engine_oil_filler_tube',[-1.223,.469,.776],.043,.126,'z','alloy',24)
cylinder_axis('orange_oil_filler_cap',[-1.223,.469,.850],.052,.028,'z','rubber',24)
cylinder_axis('rear_engine_oil_filter',[-1.40,.46,.458],.047,.160,'z','silhouette',24)
for k in range(8):
 box('oil_cooler_radial_fin',[-1.58+k*.032,-.472,.639],[.022,.045,.160],'alloy')
path('braided_oil_pressure_line',[[-1.19,.42,.782],[-1.04,.42,.671],[-1.08,.32,.45],[-1.51,.44,.49]],.016,'dark_metal')
path('rubber_ventilation_hose',[[-1.77,.40,.90],[-1.61,.39,.995],[-1.29,.27,.915]],.028,'hose')
# Exhaust manifolds = 6 separate curved header primaries, central muffler and tailpipe
for s in [-1,1]:
 for xx in [-1.78,-1.58,-1.38]:
  path('six_individual_stainless_exhaust_primaries',[[xx,s*.408,.467],[xx,s*.472,.365],[xx-.12,s*.340,.277],[-1.96,s*.2,.279]],.019,'dark_metal')
cylinder_axis('horizontally_mounted_exhaust_muffler',[-2.05,0,.289],.098,.73,'y','alloy',36)
# 915 five speed gearbox behind the engine toward front of car
box('915_transmission_case',[-.953,0,.438],[.456,.333,.225],'engine')
for k in range(7):
 box('gearbox_cast_cooling_rib',[-1.132+k*.055,0,.438],[.016,.354,.237],'alloy')
cyl('shift_linkage',[-.81,0,.45],[-.39,0,.396],.018,'alloy')
# engine mount bolts
for y in [-.47,.47]:
 cyl('engine_mounts',[-1.85,y,.468],[-1.85,y,.53],.034,'rubber')
# rear compartment dark surround panels and wires
box('engine_bay_front_firewall',[-1.087,0,.745],[.032,1.11,.340],'silhouette')
for s in [-1,1]:
 box('engine_compartment_inner_cheeks',[-1.59,s*.574,.711],[.97,.038,.300],'paint_shadow')
 path('engine_bay_wiring_looms',[[ -1.13,s*.54,.854],[-1.44,s*.48,.862],[-1.94,s*.39,.754]],.011,'rubber')
# separate over-engine rear hinges, matches closed lid
for s in [-1,1]:
 cyl('hinge_lid_knuckle',[-1.323,s*.47,.968],[-1.265,s*.47,.97],.015,'alloy')

# branded imagery baked into glTF baseColor textures; not relying on trademark badges
from PIL import ImageFont
fontfiles=['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf','/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf']
font=next((p for p in fontfiles if os.path.exists(p)),None)
def decal(n, phrase, c, ext, front_axis, group='fixed',fg=(231,214,168,255),bg=(22,28,32,255),size=85):
 # flat 3D sticker/plate with 2-sided UV mapping
 im=Image.new('RGBA',(1024,256),bg); dr=ImageDraw.Draw(im)
 f=ImageFont.truetype(font,size) if font else ImageFont.load_default()
 bounds=dr.textbbox((0,0),phrase,font=f);w=bounds[2]-bounds[0];h=bounds[3]-bounds[1]
 if w>930:
  f=ImageFont.truetype(font,int(size*930/w)) if font else f
  bounds=dr.textbbox((0,0),phrase,font=f);w=bounds[2]-bounds[0];h=bounds[3]-bounds[1]
 dr.text(((1024-w)/2,(256-h)/2-bounds[1]),phrase,font=f,fill=fg)
 im.save(os.path.join(OUT,n+'_texture.png'))
 a,b=ext[0]/2,ext[1]/2
 # orientation: normal positive or negative x, like rear plate; or on top (z)
 if front_axis=='-x':
  vv=np.array([[c[0],c[1]-a,c[2]-b],[c[0],c[1]+a,c[2]-b],[c[0],c[1]+a,c[2]+b],[c[0],c[1]-a,c[2]+b]])
 elif front_axis=='+x':
  vv=np.array([[c[0],c[1]+a,c[2]-b],[c[0],c[1]-a,c[2]-b],[c[0],c[1]-a,c[2]+b],[c[0],c[1]+a,c[2]+b]])
 else:vv=np.array([[c[0]-a,c[1]-b,c[2]],[c[0]+a,c[1]-b,c[2]],[c[0]+a,c[1]+b,c[2]],[c[0]-a,c[1]+b,c[2]]])
 uv=[[0,0],[1,0],[1,1],[0,1]]
 mesh=trimesh.Trimesh(vertices=vv,faces=[[0,1,2],[0,2,3]],process=False)
 material=PBRMaterial(name='decal_'+n,baseColorTexture=im,baseColorFactor=[255]*4,metallicFactor=0,roughnessFactor=.75,doubleSided=True,alphaMode='OPAQUE')
 mesh.visual=trimesh.visual.TextureVisuals(uv=uv, material=material)
 parts.append((group,'texture_'+n,n,mesh))
decal('rear_brand_BORSCHE_911','B O R S C H E   9 1 1',[-2.232,0,.682],[.465,.078],'-x',fg=(217,224,224,255),bg=(31,34,37,255),size=66)
decal('rear_plate_BSC_1981','BSC - 1981',[-2.217,0,.478],[.291,.073],'-x',fg=(35,45,51,255),bg=(224,223,204,255),size=109)
decal('bonnet_custom_crest_B','B',[1.598,0,.748],[.082,.057],'z',fg=(53,56,59,255),bg=(199,163,81,255),size=154)

# Grouping batches by material ensures compact, performant game engine meshes.
# Engine lid stays an independent node and can be moved/hidden in engine inspection apps.
def construct_scene(lid_open=False):
 sc=trimesh.Scene()
 by_group=defaultdict(list)
 for group,mat,name,mesh in parts:
  if mat.startswith('texture_'):
   m=mesh.copy();x=m.vertices[:,0];m.vertices[:,0]=np.where(x>2.140,2.140+(x-2.140)*.20,np.where(x< -2.140,-2.140+(x+2.140)*.20,x));sc.add_geometry(m,node_name=name,geom_name=name)
  else:by_group[(group,mat)].append(mesh)
 for (group,mat),meshes in by_group.items():
  merged=trimesh.util.concatenate(meshes)
  # Collapse only impact-bar overhang to match original 4.29 m G-body body length;
  # keep 2.271 m wheelbase and all wheel placements unchanged.
  x=merged.vertices[:,0]
  merged.vertices[:,0]=np.where(x>2.140,2.140+(x-2.140)*.20, np.where(x< -2.140,-2.140+(x+2.140)*.20,x))
  if group=='lid' and lid_open:
   hinge=np.array([-1.32,0,.964]);T=trimesh.transformations.rotation_matrix(np.deg2rad(63),[0,1,0],hinge)
   merged.apply_transform(T)
  sc.add_geometry(merged,geom_name=f'{group}__{mat}',node_name=f'{group}__{mat}')
 return sc

def export_all():
 out=[]
 for lidopen,fn in [(False,'Borsche_911_1981_Smooth_Closed.glb'),(True,'Borsche_911_1981_Smooth_Engine_Open.glb')]:
  sc=construct_scene(lidopen)
  filepath=os.path.join(OUT,fn)
  sc.export(filepath,file_type='glb')
  out.append((filepath,len(sc.geometry)))
  print('exported',fn,os.path.getsize(filepath),'bytes',len(sc.geometry),'material meshes',flush=True)
 # low-effort engine-only standalone inspection in GLB (retains unique parts)
 engtags=('flat_six','engine_','signature_911','fan_','alternator_','eleven_','KJetronic_','air_filter_','six_','manifold_','red_brown_','ignition_','oil_','rear_engine_oil_filter','horizontally_mounted_exhaust','915_','gearbox_','three_cylinder_','machined_cooling_','rocker_','cast_metal_','rubber_induction_','KJetronic','fuel_','exhaust_','braided_','ventilation_','shift_linkage','KJetronic','rubber_ventilation','engine_mount')
 eng=trimesh.Scene()
 for group,mat,name,m in parts:
  if name.startswith(engtags):eng.add_geometry(m,geom_name=name,node_name=name)
 eng.export(os.path.join(OUT,'Borsche_911_1981_Smooth_Flat_Six_Engine.glb'))
 # Metadata for import/engine use
 stats={
  'name':'Borsche 911 1981', 'category':'Original G-body rear-engine sports coupe',
  'reference':'User-provided 1981 coupe photograph',
  'units':'metres','axes':'+X forward, +Y left, +Z up',
  'inspired_by_approximate_dimensions_m':{'length':4.29,'width':1.65,'height':1.32,'wheelbase':2.271},
  'variants':['Closed','Engine_Open','Flat_Six_Engine'],
  'mesh_count_unbatched':len(parts),
  'scene_materials':sorted(RGB),
  'license':'Original user-requested 3D model. No source Porsche CAD or commercial car mesh was copied.',
  'smooth_revision':'Curved-panel quad resolution raised 2-3x; spherical headlamps/mirrors upgraded, radial tire faces upgraded, cylindrical tubes and wheel trims refined; boundary panels and hard details protected.', 'note':'Game-art interpretation. Not a scanned or mechanically verified original vehicle.'}
 with open(os.path.join(OUT,'Borsche_911_1981_Asset_Info.json'),'w') as f:json.dump(stats,f,indent=2)
 for fn,mc in out:
  r=trimesh.load(fn,force='scene')
  print('Reopen validation:',os.path.basename(fn),'bounds:',np.round(r.bounds,3).tolist(),'geometry:',len(r.geometry),'triangles:',sum(len(g.faces) for g in r.geometry.values()),flush=True)
 return stats
if __name__=='__main__':
 print('Parts:',len(parts),flush=True)
 print(export_all())
