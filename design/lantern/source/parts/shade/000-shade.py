from math import cos, sin, radians, pi, sqrt, atan2
shade_height = param("shade_height",76.0)
shade_top_inset = param("shade_top_inset",4.0)
shade_belly_diameter = param("shade_belly_diameter",106.0)
shade_wall_thickness = param("shade_wall_thickness",1.8)
shade_ring_outer_diameter = param("shade_ring_outer_diameter",94.0)
shade_ring_inner_diameter = param("shade_ring_inner_diameter",69.2)
shade_ring_height = param("shade_ring_height",4.0)
shade_rib_count = param("shade_rib_count",40)
shade_rib_radius = param("shade_rib_radius",1.8)
shade_magnet_pocket_diameter = param("shade_magnet_pocket_diameter",7.2)
shade_magnet_pocket_depth = param("shade_magnet_pocket_depth",2.15)
shade_magnet_radius = param("shade_magnet_radius",39.2)
shade_magnet_count = param("shade_magnet_count",2)
shade_magnet_angle = param("shade_magnet_angle",0.0)
shade_rim_wave_depth = param("shade_rim_wave_depth",0.6)
shade_body_wall_thickness = param("shade_body_wall_thickness",1.2)
outer_radius=shade_belly_diameter/2+shade_rib_radius
end_radius=shade_ring_outer_diameter/2
outer_round=outer_radius-end_radius
inner_radius=shade_belly_diameter/2-shade_wall_thickness
inner_end=end_radius-shade_wall_thickness
inner_round=inner_radius-inner_end
top_end_radius=end_radius-shade_top_inset
top_outer_round=outer_radius-top_end_radius
top_inner_end=top_end_radius-shade_wall_thickness
top_inner_round=inner_radius-top_inner_end
assert outer_round>0 and inner_round>0
assert shade_top_inset>=0 and top_inner_end>shade_ring_inner_diameter/2
assert shade_height>outer_round+top_outer_round+shade_ring_height
assert shade_ring_height>shade_magnet_pocket_depth
assert shade_magnet_radius-shade_magnet_pocket_diameter/2>shade_ring_inner_diameter/2
assert 0 < shade_rim_wave_depth <= shade_rib_radius
shoulder_z=shade_height-top_outer_round
def wave_wire(peak_radius, depth, height):
    wave_edges=[]
    for flute_index in range(int(shade_rib_count)):
        points=[]
        for sample_index in range(33):
            angle=(flute_index+sample_index/32)*2*pi/int(shade_rib_count)
            radius=peak_radius-depth*(1-cos(int(shade_rib_count)*angle))/2
            points.append((radius*cos(angle),radius*sin(angle),height))
        start_angle=flute_index*2*pi/int(shade_rib_count)
        end_angle=(flute_index+1)*2*pi/int(shade_rib_count)
        wave_edges.append(Edge.make_spline(points,parameters=[sample_index/32 for sample_index in range(33)],tangents=[(-peak_radius*2*pi/int(shade_rib_count)*sin(start_angle),peak_radius*2*pi/int(shade_rib_count)*cos(start_angle),0),(-peak_radius*2*pi/int(shade_rib_count)*sin(end_angle),peak_radius*2*pi/int(shade_rib_count)*cos(end_angle),0)],scale=False))
    return Wire(wave_edges)
lower_edges=[
 Edge.make_line((0,0,0),(end_radius,0,0)),
 Edge.make_three_point_arc((end_radius,0,0),(end_radius+outer_round/sqrt(2),0,outer_round-outer_round/sqrt(2)),(outer_radius,0,outer_round)),
 Edge.make_line((outer_radius,0,outer_round),(outer_radius,0,shoulder_z)),
 Edge.make_line((outer_radius,0,shoulder_z),(0,0,shoulder_z)),
 Edge.make_line((0,0,shoulder_z),(0,0,0))
]
lower_solid=revolve(Face(Wire(lower_edges)),axis=Axis.Z)
wave_prism=extrude(Face(wave_wire(outer_radius,shade_rib_radius,0)),amount=shoulder_z)
lower_solid=lower_solid & wave_prism
shoulder_sections=[]
for section_index in range(9):
    sweep_angle=section_index*pi/16
    blend=sin(sweep_angle)**2
    peak_radius=top_end_radius+top_outer_round*cos(sweep_angle)+shade_rim_wave_depth*blend
    depth=shade_rib_radius*(1-blend)+shade_rim_wave_depth*blend
    height=shoulder_z+top_outer_round*sin(sweep_angle)
    shoulder_sections.append(Face(wave_wire(peak_radius,depth,height)))
upper_solid=loft(shoulder_sections)
outer_solid=lower_solid+upper_solid
assert 0 < shade_body_wall_thickness < shade_wall_thickness
upper_faces=[face for face in upper_solid.faces() if face.geom_type != GeomType.PLANE]
assert len(upper_faces)==int(shade_rib_count)
upper_faces.sort(key=lambda face: atan2(face.position_at(0.5,0.5).Y,face.position_at(0.5,0.5).X)%(2*pi))
inner_sections=[]
template_face=upper_faces[0]
for section_index in range(25):
    inner_height=shoulder_z+(shade_height-shade_body_wall_thickness-shoulder_z)*sin(section_index*pi/48)
    points=[]
    for sample_index in range(65):
        across=sample_index/64
        low=0.0
        high=1.0
        for iteration in range(25):
            fraction=(low+high)/2
            point=template_face.position_at(across,fraction)
            normal=template_face.normal_at(across,fraction)
            inset=point-normal*shade_body_wall_thickness
            if inset.Z < inner_height:
                low=fraction
            else:
                high=fraction
        point=template_face.position_at(across,(low+high)/2)
        normal=template_face.normal_at(across,(low+high)/2)
        inset=point-normal*shade_body_wall_thickness
        points.append(Vector(inset.X,inset.Y,inner_height))
    if (atan2(points[-1].Y,points[-1].X)-atan2(points[0].Y,points[0].X))%(2*pi)>pi:
        points.reverse()
    seam_radius=(sqrt(points[0].X**2+points[0].Y**2)+sqrt(points[-1].X**2+points[-1].Y**2))/2
    period=2*pi/int(shade_rib_count)
    assert abs(atan2(points[0].Y,points[0].X))<0.01
    points[0]=Vector(seam_radius,0,inner_height)
    points[-1]=Vector(seam_radius*cos(period),seam_radius*sin(period),inner_height)
    flute_edge=Edge.make_spline(points,parameters=[sample_index/64 for sample_index in range(65)],tangents=[(0,1,0),(-sin(period),cos(period),0)])
    inner_sections.append(Wire([Rot(0,0,flute_index*360/int(shade_rib_count))*flute_edge for flute_index in range(int(shade_rib_count))]))
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
loft_builder=BRepOffsetAPI_ThruSections(True,False,0.000001)
loft_builder.CheckCompatibility(False)
loft_builder.SetMaxDegree(3)
for inner_wire in inner_sections:
    loft_builder.AddWire(inner_wire.wrapped)
loft_builder.Build()
inner_upper=Solid(loft_builder.Shape()).fix()
wall_samples=[]
for face in upper_faces[:1]:
    for across in (0.1,0.25,0.5,0.75,0.9):
        for fraction in (0.05,0.2,0.4,0.6,0.8,0.95):
            wall_samples.append(Vertex(*face.position_at(across,fraction)).distance_to(inner_upper))
print("upper_wall_sample_min_max_mm",min(wall_samples),max(wall_samples))
assert min(wall_samples)>shade_body_wall_thickness-0.02, ("min", min(wall_samples), max(wall_samples))
assert max(wall_samples)<shade_body_wall_thickness+0.02, ("max", min(wall_samples), max(wall_samples))

inner_section=Pos(0,0,-shoulder_z)*inner_sections[0]
seam_overlap=0.0
inner_prism=extrude(Face(inner_section),amount=shoulder_z+seam_overlap,dir=(0,0,1))
inner_bottom_round=outer_round-shade_body_wall_thickness+shade_body_wall_thickness/1000
round_edges=[
 Edge.make_line((0,0,outer_round-inner_bottom_round),(end_radius,0,outer_round-inner_bottom_round)),
 Edge.make_three_point_arc((end_radius,0,outer_round-inner_bottom_round),(end_radius+inner_bottom_round/sqrt(2),0,outer_round-inner_bottom_round/sqrt(2)),(end_radius+inner_bottom_round,0,outer_round)),
 Edge.make_line((end_radius+inner_bottom_round,0,outer_round),(end_radius+inner_bottom_round,0,shoulder_z+seam_overlap)),
 Edge.make_line((end_radius+inner_bottom_round,0,shoulder_z+seam_overlap),(0,0,shoulder_z+seam_overlap)),
 Edge.make_line((0,0,shoulder_z+seam_overlap),(0,0,outer_round-inner_bottom_round))
]
inner_lower=(revolve(Face(Wire(round_edges)),axis=Axis.Z) & inner_prism).fix()
assert inner_lower.volume > 100000, ("lower_cavity_volume",inner_lower.volume)
assert inner_lower.is_valid and inner_upper.is_valid, ('cutters',inner_lower.is_valid,inner_upper.is_valid)
inner_core=inner_lower.fuse(inner_upper,tol=0.0001)
assert inner_core.is_valid and len(inner_core.solids())==1, ('core',inner_core.is_valid,len(inner_core.solids()))
shade=outer_solid-inner_core
shade-=Cylinder(top_inner_end,shade_height+shade_ring_height,align=(Align.CENTER,Align.CENTER,Align.MIN))
magnet_ring=Cylinder(end_radius,shade_ring_height,align=(Align.CENTER,Align.CENTER,Align.MIN))-Cylinder(shade_ring_inner_diameter/2,shade_ring_height,align=(Align.CENTER,Align.CENTER,Align.MIN))
shade+=magnet_ring
for index in range(int(shade_magnet_count)):
    angle=shade_magnet_angle+index*360/int(shade_magnet_count)
    pocket=Pos(shade_magnet_radius*cos(radians(angle)),shade_magnet_radius*sin(radians(angle)),0)*Cylinder(shade_magnet_pocket_diameter/2,shade_magnet_pocket_depth,align=(Align.CENTER,Align.CENTER,Align.MIN))
    shade-=pocket
shade=shade.fix()
assert len(shade.solids())==1 and shade.is_valid, (len(shade.solids()),shade.is_valid,shade.volume)
assert shade.volume<80000, ('shadevolume',shade.volume)
shade.color=Color(0.16,0.70,0.40)
publish("shade",shade,"等厚波纹灯罩",material="petg")
