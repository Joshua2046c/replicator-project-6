from math import sin,cos,pi,sqrt
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.Approx import Approx_IsoParametric
height=param("water_shade_height",76.0)
maximum_diameter=param("water_shade_maximum_diameter",109.6)
wall=param("water_shade_wall",1.2)
top_opening=param("water_shade_top_opening",82.4)
top_outer=param("water_shade_top_outer",87.2)
bottom_opening=param("water_shade_bottom_opening",69.2)
ring_outer=param("water_shade_ring_outer",94.0)
ring_height=param("water_shade_ring_height",4.0)
magnet_diameter=param("water_shade_magnet_diameter",7.2)
magnet_depth=param("water_shade_magnet_depth",2.15)
magnet_radius=param("water_shade_magnet_radius",39.2)
ripple_pitch=param("water_shade_ripple_pitch",13.0)
wave_depth=param("water_shade_wave_depth",3.2)
ridge_count=param("water_shade_ridge_count",5)
broad_fraction=param("water_shade_broad_face_fraction",0.72)
wave_rise=param("water_shade_wave_rise",4.0)
secondary_rise=param("water_shade_secondary_rise",1.2)
flow_variation=param("water_shade_flow_variation",1.0)
valley_blend=param("water_shade_valley_blend",0.65)
assert 0.2<valley_blend<0.85
peak_radius=maximum_diameter/2
bottom_radius=ring_outer/2
top_radius=top_outer/2
first_crest=(height-ripple_pitch*(int(ridge_count)-1))/2
last_crest=height-first_crest
assert int(ridge_count)>=3
assert first_crest>ring_height+wall
assert peak_radius-wave_depth*1.4>bottom_radius
assert 0.5<broad_fraction<0.85
assert 0<=flow_variation<=1.3
assert magnet_radius-magnet_diameter/2>bottom_opening/2
assert magnet_radius+magnet_diameter/2<bottom_radius
assert ring_height>magnet_depth
gap_weights=[0.9,1.2,0.85,1.05]
phase_offsets=[-0.35,0.55,-0.6,0.3,1.1]
rise_factors=[0.8,1.2,0.95,1.25,0.75]
secondary_phases=[1.0,-0.7,1.7,0.1,-1.2]
secondary_factors=[0.9,0.55,1.05,0.7,0.85]
radius_offsets=[0.0,0.18,0.0,0.12,0.04]
depth_factors=[0.94,1.10,0.83,1.04]
width_offsets=[-0.12,0.015,-0.11,-0.035]
width_amplitudes=[0.10,0.07,0.11,0.095]
width_phases=[-0.3,1.5,-1.0,0.8]
total_gap_weight=sum(gap_weights[index%len(gap_weights)] for index in range(int(ridge_count)-1))
crest_heights=[first_crest]
for index in range(int(ridge_count)-1):
    crest_heights.append(crest_heights[-1]+(last_crest-first_crest)*gap_weights[index%len(gap_weights)]/total_gap_weight)
crest_radii=[peak_radius-wave_depth*radius_offsets[index%len(radius_offsets)]*flow_variation for index in range(int(ridge_count))]
def crest_at(theta,index):
    slot=index%len(phase_offsets)
    axial=crest_heights[index]+wave_rise*rise_factors[slot]*sin(theta+phase_offsets[slot])+secondary_rise*secondary_factors[slot]*sin(2*theta+secondary_phases[slot])
    derivative=wave_rise*rise_factors[slot]*cos(theta+phase_offsets[slot])+2*secondary_rise*secondary_factors[slot]*cos(2*theta+secondary_phases[slot])
    return crest_radii[index],axial,derivative
def valley_at(theta,index):
    low_radius,low_height,low_derivative=crest_at(theta,index)
    high_radius,high_height,high_derivative=crest_at(theta,index+1)
    slot=index%len(width_offsets)
    phase=width_phases[slot]
    fraction=broad_fraction+width_offsets[slot]+flow_variation*(width_amplitudes[slot]*sin(theta+phase)+0.015*sin(2*theta+0.6*phase))
    fraction_derivative=flow_variation*(width_amplitudes[slot]*cos(theta+phase)+0.03*cos(2*theta+0.6*phase))
    assert 0.45<fraction<0.86
    radius=(low_radius+high_radius)/2-wave_depth*depth_factors[index%len(depth_factors)]
    axial=low_height+fraction*(high_height-low_height)
    derivative=low_derivative+fraction_derivative*(high_height-low_height)+fraction*(high_derivative-low_derivative)
    return radius,axial,derivative
profile=[]
for index in range(7):
    profile.append(("lower",0,index*pi/12))
for index in range(int(ridge_count)-1):
    profile.append(("valley",index,0.0))
    profile.append(("crest",index+1,0.0))
for index in range(1,7):
    profile.append(("upper",int(ridge_count)-1,index*pi/12))
def contour_at(theta,index):
    kind,ridge,angle=profile[index]
    if kind=="crest":
        return crest_at(theta,ridge)
    if kind=="valley":
        return valley_at(theta,ridge)
    radius,axial,derivative=crest_at(theta,ridge)
    if kind=="lower":
        fraction=1-cos(angle)
        return bottom_radius+(radius-bottom_radius)*sin(angle),axial*fraction,derivative*fraction
    fraction=sin(angle)
    return top_radius+(radius-top_radius)*cos(angle),axial+(height-axial)*fraction,derivative*(1-fraction)
for angle_index in range(64):
    theta=2*pi*angle_index/64
    for index in range(int(ridge_count)-1):
        lower=crest_at(theta,index)[1]
        valley=valley_at(theta,index)[1]
        upper=crest_at(theta,index+1)[1]
        assert upper-lower>4*wall,("crest_gap",index,theta,upper-lower)
        assert min(valley-lower,upper-valley)>wall,("band_width",index,theta,valley-lower,upper-valley)
def point_at(theta,index):
    radius,axial,derivative=contour_at(theta,index)
    return Vector(radius*cos(theta),radius*sin(theta),axial)
def tangent_at(theta,index):
    radius,axial,derivative=contour_at(theta,index)
    return Vector(-radius*sin(theta),radius*cos(theta),derivative)
def inset_point(theta,index):
    point=point_at(theta,index)
    tangent=tangent_at(theta,index)
    if index==0:
        lower_normal=Vector(0,0,-1)
    else:
        lower_normal=tangent.cross(point-point_at(theta,index-1)).normalized()
    if index==len(profile)-1:
        upper_normal=Vector(0,0,1)
    else:
        upper_normal=tangent.cross(point_at(theta,index+1)-point).normalized()
    denominator=1+lower_normal.dot(upper_normal)
    assert denominator>0.5
    return point-(lower_normal+upper_normal)*(wall/denominator)
segments=[]
for index in range(6):
    segments.append(("original",index))
for index in range(int(ridge_count)-1):
    segments.extend([("approach",index),("arc",index),("return",index)])
for index in range(6+2*(int(ridge_count)-1),len(profile)-1):
    segments.append(("original",index))
def valley_points(theta,ridge):
    low=point_at(theta,6+2*ridge)
    valley=point_at(theta,7+2*ridge)
    high=point_at(theta,8+2*ridge)
    return low,valley,high,valley*(1-valley_blend)+low*valley_blend,valley*(1-valley_blend)+high*valley_blend
def outer_segment(theta,segment,amount):
    kind,index=segments[segment]
    if kind=="original":
        return point_at(theta,index)*(1-amount)+point_at(theta,index+1)*amount
    low,valley,high,start,finish=valley_points(theta,index)
    if kind=="approach":
        return low*(1-amount)+start*amount
    if kind=="return":
        return finish*(1-amount)+high*amount
    return start*((1-amount)**2)+valley*(2*amount*(1-amount))+finish*(amount**2)
def surface_normal(theta,segment,amount):
    epsilon=0.00001
    tangent=(outer_segment(theta+epsilon,segment,amount)-outer_segment(theta-epsilon,segment,amount))/(2*epsilon)
    kind,index=segments[segment]
    if kind=="arc":
        low,valley,high,start,finish=valley_points(theta,index)
        along=(valley-start)*(2*(1-amount))+(finish-valley)*(2*amount)
    else:
        along=outer_segment(theta,segment,1)-outer_segment(theta,segment,0)
    return tangent.cross(along).normalized()
def inner_endpoint(theta,segment,amount):
    kind,index=segments[segment]
    if kind=="original":
        return inset_point(theta,index+int(amount))
    if kind=="approach" and amount==0:
        return inset_point(theta,6+2*index)
    if kind=="return" and amount==1:
        return inset_point(theta,8+2*index)
    return outer_segment(theta,segment,amount)-surface_normal(theta,segment,amount)*wall
def segment_point(theta,segment,amount,inset):
    if not inset:
        return outer_segment(theta,segment,amount)
    if segments[segment][0]=="arc":
        return outer_segment(theta,segment,amount)-surface_normal(theta,segment,amount)*wall
    return inner_endpoint(theta,segment,0)*(1-amount)+inner_endpoint(theta,segment,1)*amount
wire_cache={}
def segment_wire(segment,amount,inset):
    key=(segment,amount,inset)
    if key not in wire_cache:
        edges=[]
        for sector in range(8):
            start=sector*pi/4
            finish=(sector+1)*pi/4
            points=[segment_point(start+(finish-start)*sample/16,segment,amount,inset) for sample in range(17)]
            epsilon=0.00001
            tangents=[(segment_point(theta+epsilon,segment,amount,inset)-segment_point(theta-epsilon,segment,amount,inset))*(finish-start)/(2*epsilon) for theta in (start,finish)]
            edges.append(Edge.make_spline(points,parameters=[sample/16 for sample in range(17)],tangents=tangents,scale=False))
        wire_cache[key]=Wire(edges)
    return wire_cache[key]
def closed_skin(inset):
    faces=[]
    for segment,(kind,index) in enumerate(segments):
        curved=kind=="arc"
        builder=BRepOffsetAPI_ThruSections(False,not curved,0.000001)
        builder.CheckCompatibility(False)
        builder.SetParType(Approx_IsoParametric)
        if curved:
            builder.SetMaxDegree(5 if inset else 2)
        samples=12 if curved and inset else 2 if curved else 1
        for sample in range(samples+1):
            builder.AddWire(segment_wire(segment,sample/samples,inset).wrapped)
        builder.Build()
        assert builder.IsDone(),("loft",inset,segment)
        faces.extend(Compound(builder.Shape()).faces())
    faces.extend([Face(segment_wire(0,0,inset)),Face(segment_wire(len(segments)-1,1,inset))])
    solid=Solid(Shell(faces)).fix()
    assert solid.is_valid and len(solid.solids())==1,("skin",inset,solid.is_valid)
    assert solid.volume>400000
    assert solid.is_inside((0,0,height/2))
    return solid
outer=closed_skin(False)
core=closed_skin(True)
core_faces=Compound(children=list(core.faces()))
wall_samples=[]
wall_locations=[]
arc_wall_samples=[]
for segment,(kind,index) in enumerate(segments):
    if kind=="original":
        continue
    for theta in (0.2,1.4,2.8,4.3):
        for amount in (0.2,0.5,0.8):
            point=outer_segment(theta,segment,amount)
            wall_samples.append(Vertex(*point).distance_to(core_faces))
            wall_locations.append((kind,index,theta,amount))
            if kind=="arc":
                arc_wall_samples.append(wall_samples[-1])
assert min(arc_wall_samples)>wall-0.035 and max(arc_wall_samples)<wall+0.035,("arc_walls",min(arc_wall_samples),max(arc_wall_samples))
assert min(wall_samples)>wall-0.035 and max(wall_samples)<wall*1.2,("ridge_neighborhood_walls",min(wall_samples),max(wall_samples))
crest_errors=[]
outer_faces=Compound(children=list(outer.faces()))
for ridge in range(int(ridge_count)):
    for angle_index in range(16):
        theta=2*pi*angle_index/16
        crest_errors.append(Vertex(*point_at(theta,6+2*ridge)).distance_to(outer_faces))
assert max(crest_errors)<0.0001,("crest_position",max(crest_errors))
print("arc_wall_samples",len(arc_wall_samples),min(arc_wall_samples),max(arc_wall_samples))
print("wall_samples",len(wall_samples),min(wall_samples),max(wall_samples))
print("unchanged_crest_samples",len(crest_errors),max(crest_errors))
from OCP.BRepAlgoAPI import BRepAlgoAPI_Cut,BRepAlgoAPI_Fuse
def boolean_solid(left,right,fuse=False):
    operation=BRepAlgoAPI_Fuse(left.wrapped,right.wrapped) if fuse else BRepAlgoAPI_Cut(left.wrapped,right.wrapped)
    operation.SetFuzzyValue(0.0001)
    operation.Build()
    pieces=Compound(operation.Shape()).solids()
    assert len(pieces)==1,("boolean_solids",len(pieces))
    result=pieces[0].fix()
    assert result.is_valid
    return result
shade=boolean_solid(outer,core)
shade=boolean_solid(shade,Cylinder(top_opening/2,height+ring_height,align=(Align.CENTER,Align.CENTER,Align.MIN)))
ring=Cylinder(bottom_radius,ring_height,align=(Align.CENTER,Align.CENTER,Align.MIN))-Cylinder(bottom_opening/2,ring_height,align=(Align.CENTER,Align.CENTER,Align.MIN))
shade=boolean_solid(shade,ring,True)
for direction in (-1,1):
    pocket=Pos(direction*magnet_radius,0,0)*Cylinder(magnet_diameter/2,magnet_depth,align=(Align.CENTER,Align.CENTER,Align.MIN))
    shade=boolean_solid(shade,pocket)
assert shade.is_inside((0,magnet_radius,ring_height/2)), "magnet ring missing"
assert not shade.is_inside((0,0,ring_height/2)), "lower opening blocked"
for direction in (-1,1):
    assert not shade.is_inside((direction*magnet_radius,0,magnet_depth/2))
    assert shade.is_inside((direction*magnet_radius,0,(magnet_depth+ring_height)/2))
assert len(shade.solids())==1 and shade.is_valid
assert 20000<shade.volume<120000,shade.volume
shade.color=srgb("#739F9A")
publish("water_shade",shade,"自然流动海浪灯罩",material="petg")
