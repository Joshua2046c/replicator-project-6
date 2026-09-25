handle_center_spacing = param("handle_center_spacing",130.0)
handle_foot_spacing = param("handle_foot_spacing",102.0)
handle_band_width = param("handle_band_width",10.0)
handle_thickness = param("handle_thickness",10.0)
handle_height = param("handle_height",198.0)
handle_jog_start = param("handle_jog_start",4.0)
handle_jog_height = param("handle_jog_height",20.0)
handle_tenon_size = param("handle_tenon_size",7.8)
handle_tenon_length = param("handle_tenon_length",8.0)
handle_edge_radius = param("handle_edge_radius",0.7)
handle_beam_width = param("handle_beam_width",180.0)
handle_beam_flat_width = param("handle_beam_flat_width",100.0)
handle_beam_rise = param("handle_beam_rise",14.0)
handle_beam_height = param("handle_beam_height",12.0)
handle_beam_depth = param("handle_beam_depth",14.0)
handle_beam_tip_height = param("handle_beam_tip_height",8.0)
handle_beam_tip_bevel = param("handle_beam_tip_bevel",4.0)
tip = handle_beam_width/2
flat = handle_beam_flat_width/2
top_tip = tip-handle_beam_tip_bevel
middle_top = handle_height-handle_beam_rise
middle_bottom = middle_top-handle_beam_height
tip_bottom = handle_height-handle_beam_tip_height
span = top_tip-flat
upper_left=Edge.make_bezier((-top_tip,0,handle_height),(-top_tip+span*0.25,0,middle_top),(-flat-span*0.55,0,middle_top),(-flat,0,middle_top))
upper_middle=Edge.make_line((-flat,0,middle_top),(flat,0,middle_top))
upper_right=Edge.make_bezier((flat,0,middle_top),(flat+span*0.55,0,middle_top),(top_tip-span*0.25,0,middle_top),(top_tip,0,handle_height))
right_end=Edge.make_line((top_tip,0,handle_height),(tip,0,tip_bottom))
lower_right=Edge.make_bezier((tip,0,tip_bottom),(tip-span*0.15,0,middle_bottom),(flat+span*0.55,0,middle_bottom),(flat,0,middle_bottom))
lower_middle=Edge.make_line((flat,0,middle_bottom),(-flat,0,middle_bottom))
lower_left=Edge.make_bezier((-flat,0,middle_bottom),(-flat-span*0.55,0,middle_bottom),(-tip+span*0.15,0,middle_bottom),(-tip,0,tip_bottom))
left_end=Edge.make_line((-tip,0,tip_bottom),(-top_tip,0,handle_height))
beam_outline=Wire([upper_left,upper_middle,upper_right,right_end,lower_right,lower_middle,lower_left,left_end])
handle=extrude(Face(beam_outline),amount=handle_beam_depth/2,both=True,dir=(0,1,0))
foot=handle_foot_spacing/2
upper=handle_center_spacing/2
jog_top=handle_jog_start+handle_jog_height
for side in (-1,1):
    foot_profile=RectangleRounded(handle_band_width,handle_thickness,handle_edge_radius)
    rod_profile=Ellipse(handle_band_width/2,handle_thickness/2)
    sections=[
        Pos(side*foot,0,0)*foot_profile,
        Pos(side*foot,0,handle_jog_start)*foot_profile,
        Pos(side*upper,0,jog_top)*rod_profile,
        Pos(side*upper,0,middle_top)*rod_profile
    ]
    handle += loft(sections,ruled=True)
    handle += Pos(side*foot,0,-handle_tenon_length)*Box(handle_tenon_size,handle_tenon_size,handle_tenon_length+1,align=(Align.CENTER,Align.CENTER,Align.MIN))
assert handle_beam_width > handle_center_spacing+handle_band_width
assert middle_bottom > jog_top
assert len(handle.solids()) == 1 and handle.is_valid
handle.color=Color(0.63,0.36,0.16)
publish("handle",handle,"翘头横梁提手",material="petg")
