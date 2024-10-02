import arcpy
import os

# Set environment settings
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"F:\temp2"

# Input parameters
clip_target = r"F:\papers\LSM\vectors\inventory_poly.shp"
input_polygons = r"F:\papers\LSM\vectors\dempoly_finall_wgs.shp"
output_folder = r'H:\LSM_DATA\masked_layers\vectors\inv'

# Check and repair geometry for both input shapefiles to avoid invalid topology
arcpy.RepairGeometry_management(input_polygons)
arcpy.RepairGeometry_management(clip_target)

# Create a search cursor to loop through each polygon in the input shapefile
with arcpy.da.SearchCursor(input_polygons, ['FID', 'SHAPE@', 'feuillet']) as cursor:
    for row in cursor:
        fid = row[0]  # Get the FID of the current polygon
        geometry = row[1]  # Get the geometry (shape) of the current polygon
        dem_name = row[2]  # Get the 'feuillet' attribute

        # Create a feature layer for selecting the current polygon
        where_clause = f"FID = {fid}"
        arcpy.MakeFeatureLayer_management(input_polygons, 'current_polygon', where_clause)

        # Ensure the spatial reference of the clip target matches the input polygons
        input_sr = arcpy.Describe(input_polygons).spatialReference
        target_sr = arcpy.Describe(clip_target).spatialReference
        if input_sr.name != target_sr.name:
            print("Projecting clip_target to match input polygons' spatial reference.")
            projected_clip_target = os.path.join(arcpy.env.workspace, "projected_clip_target.shp")
            arcpy.Project_management(clip_target, projected_clip_target, input_sr)
        else:
            projected_clip_target = clip_target

        # Try clipping the target shapefile with the current polygon
        try:
            output_file = os.path.join(output_folder, f"{dem_name}.shp")
            arcpy.Clip_analysis(projected_clip_target, 'current_polygon', output_file)
            print(f"Clipped polygon saved as {output_file}")
        except arcpy.ExecuteError as e:
            print(f"Error clipping polygon with FID {fid}: {e}")

        # Clean up feature layer
        arcpy.Delete_management('current_polygon')

print("Clipping completed!")



