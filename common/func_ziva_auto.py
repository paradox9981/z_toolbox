import random

import maya.api.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel
import pymel.core as pm
import utility  # Assuming utility is a valid module in your environment
import zBuilder.builders.ziva as zva
import zBuilder.utils as utility
from PySide2 import QtWidgets

############################################################
#################   COMMON FUNCTIONS   #####################
############################################################


# List mesh from a selected mesh or group ##################
def list_mesh_nodes_in_selected_objects(selected_objects):
    """
    List all "mesh" nodes in the hierarchy of selected objects.

    Args:
        selected_objects (list): List of selected objects in the Maya scene.

    Returns:
        list: A list of "mesh" nodes in the hierarchy.
    """
    mesh_nodes_list = []

    if not selected_objects:
        cmds.warning("No objects selected. Please select one or more objects.")
        return mesh_nodes_list

    for obj in selected_objects:
        if cmds.objectType(obj, isType="transform"):
            child_meshes = (
                cmds.listRelatives(obj, allDescendents=True, type="mesh") or []
            )

            # Filter out only meshes with specific conditions (e.g., not ending with "Orig")
            filtered_meshes = [
                mesh
                for mesh in child_meshes
                if cmds.objExists(mesh) and not mesh.endswith("Orig")
            ]

            mesh_nodes_list.extend(filtered_meshes)

    return mesh_nodes_list


def find_selected_mesh():
    selected_objects = cmds.ls(selection=True)
    mesh_nodes_list = list_mesh_nodes_in_selected_objects(selected_objects)

    if mesh_nodes_list:
        print("Mesh nodes in selected objects:")
        for mesh_node in mesh_nodes_list:
            print(mesh_node)
    else:
        print(
            "No matching mesh nodes found in the selected objects or no objects selected."
        )

    return mesh_nodes_list


############################################################
#################   CREATE BLENDSHAPE   ####################
############################################################


def create_blendshape():
    # Get selected objects
    selected_objects = cmds.ls(selection=True)

    if not selected_objects:
        cmds.warning("Please select source and target objects.")
        return

    source_objects, target_objects = separate_source_and_target(selected_objects)

    if not source_objects or not target_objects:
        cmds.warning("Invalid selection. Please select both source and target objects.")
        return

    # Check if the selected objects are deformable
    if not all(
        cmds.objectType(obj, isType="transform")
        and is_group_with_deformable_meshes(obj)
        for obj in source_objects
    ):
        cmds.warning(
            "Selected source objects must be groups with deformable meshes in the hierarchy."
        )
        return

    if not all(
        cmds.objectType(obj, isType="transform")
        and is_group_with_deformable_meshes(obj)
        for obj in target_objects
    ):
        cmds.warning(
            "Selected target objects must be groups with deformable meshes in the hierarchy."
        )
        return

    # Create blendShape node
    blendshape_node = cmds.blendShape(
        target_objects, source_objects, name="{}_BS".format(source_objects[0])
    )

    # Enable blendShape node
    if blendshape_node:
        blendshape_node_attr = "{}.en".format(blendshape_node[0])
        cmds.setAttr(blendshape_node_attr, 1)
        # Lock the attribute to prevent further changes
        cmds.setAttr(blendshape_node_attr, lock=True)
        cmds.setAttr(blendshape_node[0] + "." + source_objects[0], 1)
        cmds.setAttr(blendshape_node[0] + ".origin", 0)

    print("BlendShape created successfully.")


def is_group_with_deformable_meshes(group):
    # Check if the group contains deformable meshes in its hierarchy
    meshes_in_group = cmds.listRelatives(group, ad=True, type="mesh")
    return meshes_in_group is not None and any(
        cmds.objectType(mesh, isType="mesh") for mesh in meshes_in_group
    )


def separate_source_and_target(objects):
    source_objects = []
    target_objects = []

    for obj in objects:
        if cmds.nodeType(obj) == "transform":
            source_objects.append(obj)
            target_objects.append(obj)
        elif cmds.nodeType(obj) == "mesh":
            # If it's a mesh, add it directly
            source_objects.append(obj)
            target_objects.append(obj)

    return source_objects, target_objects


# Run the script
# create_blendshape()


def create_duplicate_clean_mesh():
    # Check if the selected object is a mesh
    selected_object = cmds.ls(selection=True, long=True)

    for object in selected_object:
        if cmds.nodeType(find_shape_nodes_nonOrig(object)) == "mesh":
            # Duplicate the selected mesh
            duplicate_mesh = cmds.duplicate(
                object, ic=False, name=object + "_Duplicate"
            )[0]

    # Remove "Orig" shape nodes
    shapes = cmds.listRelatives(duplicate_mesh, shapes=True, fullPath=True) or []
    orig_shapes = [shape for shape in shapes if "ShapeOrig" in shape]
    for shape in orig_shapes:
        cmds.delete(shape)

    # Delete deformation nodes
    deform_nodes = (
        cmds.listHistory(duplicate_mesh, pruneDagObjects=True, historyAttr=False) or []
    )
    deform_nodes = [
        node for node in deform_nodes if cmds.nodeType(node) == "deformBend"
    ]  # Customize based on your deformation nodes
    if deform_nodes:
        cmds.delete(deform_nodes)

    # Freeze transformations
    cmds.makeIdentity(duplicate_mesh, apply=True, t=1, r=1, s=1, n=0)

    # Delete history
    cmds.delete(duplicate_mesh, constructionHistory=True)
    print("Mesh duplicated and cleaned successfully:", duplicate_mesh)

    return duplicate_mesh


def find_shape_nodes_nonOrig(selected_object):
    shapes = cmds.listRelatives(selected_object, shapes=True, fullPath=True) or []
    valid_shapes = [shape for shape in shapes if not "ShapeOrig" in shape]
    return valid_shapes


def ____create_ziva_components____():
    return


def create_ziva_BS__bone():
    selected_objects = cmds.ls(selection=True, long=True)

    if not selected_objects:
        print("No object selected. Please select an object.")
        return

    for obj in selected_objects:
        if cmds.objectType(obj, isType="transform"):
            child_meshes = (
                cmds.listRelatives(obj, allDescendents=True, type="mesh", fullPath=True)
                or []
            )
            for mesh in child_meshes:
                if (
                    cmds.objExists(mesh)
                    and (mesh.lower().startswith("bones") or "bone" in mesh.lower())
                    and not mesh.endswith("Orig")
                ):
                    # Check if the shape is intermediate
                    is_intermediate = cmds.getAttr(mesh + ".intermediateObject")
                    if is_intermediate:
                        # If the shape is intermediate, find the corresponding shapeDeformed node
                        deformed_shape = cmds.listConnections(
                            mesh + ".inMesh",
                            type="shapeDeformed",
                            source=True,
                            destination=False,
                        )
                        if deformed_shape:
                            mesh = deformed_shape[0]
                        else:
                            print(
                                f"Skipping intermediate shape {mesh}. Corresponding shapeDeformed node not found."
                            )
                            continue

                    # Check if the mesh has blend shapes
                    blend_shapes = cmds.listConnections(mesh, type="blendShape")
                    if not blend_shapes:
                        print(
                            f"Blend shapes not found. No blend shapes found in {mesh}."
                        )
                        continue

                    try:
                        bone_name = f"ZB_{mesh.split('|')[-1].split('Shape')[0].split('Deformed')[0]}"
                        mel.eval(f"ziva -b {mesh};")
                        bone_nodes = cmds.ls(type="zBone")

                        if bone_nodes:
                            cmds.rename(bone_nodes[-1], bone_name)
                            print(
                                f"Ziva bone created from {mesh} with name {bone_name}."
                            )
                        else:
                            print(f"Failed to create Ziva bone from {mesh}.")
                    except Exception as e:
                        print(
                            f"Failed to create Ziva bone from {mesh}. Error: {str(e)}"
                        )
        else:
            shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
            if shapes and cmds.nodeType(shapes[0]) == "mesh":
                if (
                    obj.lower().startswith("bones") or "bone" in obj.lower()
                ) and not obj.endswith("Orig"):
                    # Check if the shape is intermediate
                    is_intermediate = cmds.getAttr(obj + ".intermediateObject")
                    if is_intermediate:
                        # If the shape is intermediate, find the corresponding shapeDeformed node
                        deformed_shape = cmds.listConnections(
                            obj + ".inMesh",
                            type="shapeDeformed",
                            source=True,
                            destination=False,
                        )
                        if deformed_shape:
                            obj = deformed_shape[0]
                        else:
                            print(
                                f"Skipping intermediate shape {obj}. Corresponding shapeDeformed node not found."
                            )
                            continue

                    # Check if the mesh has blend shapes
                    blend_shapes = cmds.listConnections(mesh, type="blendShape")
                    if not blend_shapes:
                        print(
                            f"Blend shapes not found. No blend shapes found in {obj}."
                        )
                        continue

                    try:
                        bone_name = f"ZB_{obj.split('|')[-1].split('Shape')[0].split('Deformed')[0]}"
                        mel.eval(f"ziva -b {obj};")
                        bone_nodes = cmds.ls(type="zBone")

                        if bone_nodes:
                            cmds.rename(bone_nodes[-1], bone_name)
                            print(
                                f"Ziva bone created from {obj} with name {bone_name}."
                            )
                        else:
                            print(f"Failed to create Ziva bone from {obj}.")
                    except Exception as e:
                        print(f"Failed to create Ziva bone from {obj}. Error: {str(e)}")
                else:
                    print(
                        f"Object {obj} doesn't meet naming criteria for bones or contains 'Orig'."
                    )
            else:
                print(f"Object {obj} is not a mesh.")


def create_ziva_bone():
    selected_objects = cmds.ls(selection=True, long=True)

    if not selected_objects:
        print("No object selected. Please select an object.")
        return

    for obj in selected_objects:
        if cmds.objectType(obj, isType="transform"):
            child_meshes = (
                cmds.listRelatives(obj, allDescendents=True, type="mesh", fullPath=True)
                or []
            )
            for mesh in child_meshes:
                if (
                    cmds.objExists(mesh)
                    and (mesh.lower().startswith("bones") or "bone" in mesh.lower())
                    and not mesh.endswith("Orig")
                ):
                    try:
                        bone_name = f"ZB_{mesh.split('|')[-1]}"
                        mel.eval(f"ziva -b {mesh};")
                        bone_nodes = cmds.ls(type="zBone")

                        if bone_nodes:
                            cmds.rename(bone_nodes[-1], bone_name)
                            print(
                                f"Ziva bone created from {mesh} with name {bone_name}."
                            )
                        else:
                            print(f"Failed to create Ziva bone from {mesh}.")
                    except Exception as e:
                        print(
                            f"Failed to create Ziva bone from {mesh}. Error: {str(e)}"
                        )
        else:
            shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
            if shapes and cmds.nodeType(shapes[0]) == "mesh":
                if (
                    obj.lower().startswith("bones") or "bone" in obj.lower()
                ) and not obj.endswith("Orig"):
                    try:
                        bone_name = f"ZB_{obj.split('|')[-1]}"
                        mel.eval(f"ziva -b {obj};")
                        bone_nodes = cmds.ls(type="zBone")

                        if bone_nodes:
                            cmds.rename(bone_nodes[-1], bone_name)
                            print(
                                f"Ziva bone created from {obj} with name {bone_name}."
                            )
                        else:
                            print(f"Failed to create Ziva bone from {obj}.")
                    except Exception as e:
                        print(f"Failed to create Ziva bone from {obj}. Error: {str(e)}")
                else:
                    print(
                        f"Object {obj} doesn't meet naming criteria for bones or contains 'Orig'."
                    )
            else:
                print(f"Object {obj} is not a mesh.")


def create_ziva_tissue():
    selected_objects = cmds.ls(selection=True, long=True)

    if not selected_objects:
        print("No object selected. Please select an object.")
        return

    for obj in selected_objects:
        if cmds.objectType(obj, isType="transform"):
            children = (
                cmds.listRelatives(obj, allDescendents=True, type="mesh", fullPath=True)
                or []
            )
            for shape in children:
                # if cmds.objExists(shape) and (shape.lower().startswith("tissue*_") or "tissue*_" in shape.lower()) and not shape.endswith("Orig"):
                if not shape.endswith("Orig"):
                    try:
                        tissue_name = f"ZT_{shape.split('|')[-1].split('Shape')[0]}"
                        emb_name = f"ZEM_{shape.split('|')[-1].split('Shape')[0]}"
                        geo_name = f"ZGEO_{shape.split('|')[-1].split('Shape')[0]}"
                        mat_name = f"ZMAT_{shape.split('|')[-1].split('Shape')[0]}"
                        tet_name = f"ZTET_{shape.split('|')[-1].split('Shape')[0]}"
                        mel.eval(f"ziva -t {shape};")
                        tissue_nodes = cmds.ls(type="zTissue")
                        # emb_nodes = cmds.ls(type="zEmbedder")
                        geo_nodes = cmds.ls(type="zGeo")
                        mat_nodes = cmds.ls(type="zMaterial")
                        tet_nodes = cmds.ls(type="zTet")

                        if tissue_nodes:
                            cmds.rename(tissue_nodes[-1], tissue_name)
                            # cmds.rename(emb_nodes[-1],emb_name)
                            cmds.rename(geo_nodes[-1], geo_name)
                            cmds.rename(mat_nodes[-1], mat_name)
                            cmds.rename(tet_nodes[-1], tet_name)
                            print(
                                f"Ziva tissue created from {shape} with name {tissue_name}."
                            )
                        else:
                            print(f"Failed to create Ziva tissue from {shape}.")
                    except Exception as e:
                        print(
                            f"Failed to create Ziva tissue from {shape}. Error: {str(e)}"
                        )
        else:
            shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
            if shapes and cmds.nodeType(shapes[0]) == "mesh":
                try:
                    tissue_name = f"ZT_{obj.split('|')[-1]}"
                    emb_name = f"ZEM_{shape.split('|')[-1].split('Shape')[0]}"
                    geo_name = f"ZGEO_{shape.split('|')[-1].split('Shape')[0]}"
                    mat_name = f"ZMAT_{shape.split('|')[-1].split('Shape')[0]}"
                    tet_name = f"ZTET_{shape.split('|')[-1].split('Shape')[0]}"
                    mel.eval(f"ziva -t {obj};")
                    tissue_nodes = cmds.ls(type="zTissue")
                    # emb_nodes = cmds.ls(type="zEmbedder")
                    geo_nodes = cmds.ls(type="zGeo")
                    mat_nodes = cmds.ls(type="zMaterial")
                    tet_nodes = cmds.ls(type="zTet")

                    if tissue_nodes:
                        cmds.rename(tissue_nodes[-1], tissue_name)
                        # cmds.rename(emb_nodes[-1],emb_name)
                        cmds.rename(geo_nodes[-1], geo_name)
                        cmds.rename(mat_nodes[-1], mat_name)
                        cmds.rename(tet_nodes[-1], tet_name)
                        print(
                            f"Ziva tissue created from {obj} with name {tissue_name}."
                        )
                    else:
                        print(f"Failed to create Ziva tissue from {obj}.")
                except Exception as e:
                    print(f"Failed to create Ziva tissue from {obj}. Error: {str(e)}")
            else:
                print(f"Object {obj} isn't a mesh or a group with mesh descendants.")


# def create_ziva_fiber():
#     selected_objects = cmds.ls(selection=True, long=True)

#     if not selected_objects:
#         print("No object selected. Please select an object.")
#         return

#     for obj in selected_objects:
#         if cmds.objectType(obj, isType="transform"):
#             child_meshes = (
#                 cmds.listRelatives(obj, allDescendents=True, type="mesh", fullPath=True)
#                 or []
#             )
#             for mesh in child_meshes:
#                 has_tissue = cmds.ls(type="zTissue")
#                 if has_tissue:
#                     fiber_nodes = cmds.ls(type="zFiber")
#                     num_fibers = len(fiber_nodes)
#                     if cmds.objExists(mesh) and not mesh.endswith("Orig"):
#                         try:
#                             fiber_name = (
#                                 f"ZF_{mesh.split('|')[-1]}_{num_fibers + 1}_fiber"
#                             )
#                             mel.eval(f"ziva -f {mesh};")
#                             new_fiber_nodes = cmds.ls(type="zFiber")
#                             if len(new_fiber_nodes) > len(fiber_nodes):
#                                 new_fiber_node = list(
#                                     set(new_fiber_nodes) - set(fiber_nodes)
#                                 )[0]
#                                 cmds.rename(new_fiber_node, fiber_name)
#                                 print(
#                                     f"Ziva fiber created from {mesh} with name {fiber_name}."
#                                 )
#                             else:
#                                 print(f"Failed to create Ziva fiber from {mesh}.")
#                         except Exception as e:
#                             print(
#                                 f"Failed to create Ziva fiber from {mesh}. Error: {str(e)}"
#                             )
#                 else:
#                     print("No Ziva tissue present. Please create tissue first.")
#                     return
#         else:
#             shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
#             if shapes and cmds.nodeType(shapes[0]) == "mesh":
#                 has_tissue = cmds.ls(type="zTissue")
#                 if has_tissue:
#                     fiber_nodes = cmds.ls(type="zFiber")
#                     num_fibers = len(fiber_nodes)
#                     if not obj.endswith("Orig"):
#                         try:
#                             fiber_name = (
#                                 f"ZF_{obj.split('|')[-1]}_{num_fibers + 1}_fiber"
#                             )
#                             mel.eval(f"ziva -f {obj};")
#                             new_fiber_nodes = cmds.ls(type="zFiber")
#                             if len(new_fiber_nodes) > len(fiber_nodes):
#                                 new_fiber_node = list(
#                                     set(new_fiber_nodes) - set(fiber_nodes)
#                                 )[0]
#                                 cmds.rename(new_fiber_node, fiber_name)
#                                 print(
#                                     f"Ziva fiber created from {obj} with name {fiber_name}."
#                                 )
#                             else:
#                                 print(f"Failed to create Ziva fiber from {obj}.")
#                         except Exception as e:
#                             print(
#                                 f"Failed to create Ziva fiber from {obj}. Error: {str(e)}"
#                             )
#                 else:
#                     print("No Ziva tissue present. Please create tissue first.")
#                     return
#             else:
#                 print(f"Object {obj} is not a mesh.")


def create_ziva_fiber():
    selected_objects = cmds.ls(selection=True, long=True)

    if not selected_objects:
        print("No object selected. Please select an object.")
        return

    for obj in selected_objects:
        if cmds.objectType(obj, isType="transform"):
            child_meshes = (
                cmds.listRelatives(obj, allDescendents=True, type="mesh", fullPath=True)
                or []
            )
            for mesh in child_meshes:
                # Check if the object is associated with Ziva tissue
                tissue_nodes = cmds.zQuery(mesh, type="zTissue") or []
                for tissue_node in tissue_nodes:
                    fiber_nodes = cmds.zQuery(tissue_node , type="zFiber") or []
                    num_fibers = len(fiber_nodes)
                    if cmds.objExists(mesh) and not mesh.endswith("Orig"):
                        try:
                            tissue_node = tissue_node.replace('ZT_' , '')
                            fiber_name = f"ZF_{tissue_node}_{num_fibers + 1}_fiber"
                            mel.eval(f"ziva -f {mesh};")
                            new_fiber_nodes = cmds.zQuery(tissue_node , type="zFiber") or []
                            new_fiber_node = list(set(new_fiber_nodes) - set(fiber_nodes))
                            if new_fiber_node:
                                cmds.rename(new_fiber_node[0], fiber_name)
                                print(f"Ziva fiber created from {mesh} with name {fiber_name}.")
                            else:
                                print(f"Failed to create Ziva fiber from {mesh}.")
                        except Exception as e:
                            print(f"Failed to create Ziva fiber from {mesh}. Error: {str(e)}")
                    else:
                        print(f"No Ziva tissue present for {mesh}. Please create tissue first.")
        else:
            shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
            if shapes and cmds.nodeType(shapes[0]) == "mesh":
                # Check if the object is associated with Ziva tissue
                tissue_nodes = cmds.zQuery(obj, type="zTissue") or []
                for tissue_node in tissue_nodes:
                    fiber_nodes = cmds.zQuery(tissue_node , type="zFiber") or []
                    num_fibers = len(fiber_nodes)
                    if not obj.endswith("Orig"):
                        try:
                            tissue_node = tissue_node.replace('ZT_' , '')
                            fiber_name = f"ZF_{tissue_node}_{num_fibers + 1}_fiber"
                            mel.eval(f"ziva -f {obj};")
                            new_fiber_nodes = cmds.zQuery(type="zFiber") or []
                            new_fiber_node = list(set(new_fiber_nodes) - set(fiber_nodes))
                            if new_fiber_node:
                                cmds.rename(new_fiber_node[0], fiber_name)
                                print(f"Ziva fiber created from {obj} with name {fiber_name}.")
                            else:
                                print(f"Failed to create Ziva fiber from {obj}.")
                        except Exception as e:
                            print(f"Failed to create Ziva fiber from {obj}. Error: {str(e)}")
                    else:
                        print(f"No Ziva tissue present for {obj}. Please create tissue first.")
            else:
                print(f"Object {obj} is not a mesh.")



def select_mesh(node):
    meshes = cmds.listRelatives(node, ad=True, ni=True, type="mesh") or []
    parents = [cmds.listRelatives(mesh, p=True, fullPath=True)[0] for mesh in meshes]
    unique_parents = list(set(parents))
    return unique_parents


def create_ziva_cloth():
    # Get selected objects
    selected_objects = cmds.ls(selection=True, long=True)

    # Check if an object is selected
    if not selected_objects:
        cmds.warning("Please select a mesh object.")
        return

    # Select meshes from the hierarchy
    zcloth_selection = select_mesh(selected_objects)

    # Check if a mesh is selected
    if not zcloth_selection:
        cmds.warning("Please select a valid mesh object.")
        return

    # Create Ziva zCloth
    for zc in zcloth_selection:
        cmds.select(zc, r=True)
        zcloth_nodes = cmds.ziva(c=True)

        # Check if zCloth is created
        if not zcloth_nodes:
            cmds.warning(f"Failed to create Ziva zCloth for {zc}.")
            continue

        # Rename zCloth node
        zemb = cmds.zQuery(type="zEmbedder")
        emb_name = f"ZEM_{zc.split('|')[-1].split('Shape')[0]}"
        geo_name = f"ZGEO_{zc.split('|')[-1].split('Shape')[0]}"
        zct_name = f"ZCTH_{zc.split('|')[-1].split('Shape')[0]}"
        mat_name = f"ZMAT_{zc.split('|')[-1].split('Shape')[0]}"

        zemb_name = cmds.rename(zemb[0], emb_name)
        zgeo_name = cmds.rename(zcloth_nodes[0], geo_name)
        zct_name = cmds.rename(zcloth_nodes[1], zct_name)
        zmat_name = cmds.rename(zcloth_nodes[2], mat_name)

        print(
            f"Ziva zCloth and zMaterial created for {zc}. zCloth Name: {zct_name}, zMaterial Name: {mat_name}"
        )


def create_ziva_zmaterials():
    # Get selected objects
    selected_objects = cmds.ls(selection=True, long=True)

    # Check if an object is selected
    if not selected_objects:
        cmds.warning("Please select a mesh object.")
        return

    # Select meshes from the hierarchy
    zmat_selection = select_mesh(selected_objects)

    # Check if a mesh is selected
    if not zmat_selection:
        cmds.warning("Please select a valid mesh object.")
        return

    # Create Ziva Materials
    for zc in zmat_selection:
        cmds.select(zc, r=True)
        zmaterial_nodes = cmds.ziva(m=True)

        # Check if zMaterials is created
        if not zmaterial_nodes:
            cmds.warning(f"Failed to create Ziva zMaterials for {zc}.")
            continue

        # Find existing zMaterial nodes with the same name convention
        existing_materials = cmds.ls(f"ZMAT_{zc.split('|')[-1].split('_',0)[-1]}_*")
        if existing_materials:
            # Increment the num_materials
            num_materials = len(existing_materials) + 1
        else:
            num_materials = 1

        # Create a zMaterial name with a numeric suffix
        mat_name = f"ZMAT_{zc.split('|')[-1].split('_',0)[-1]}_{num_materials}"
        zmat_name = cmds.rename(zmaterial_nodes[0], mat_name)

        print(f"Ziva zMaterial created for {zc}. zMaterial Name: {mat_name}")


# Apply Mirror with L and R objects selected
# def create_zMirror_():
#     sel = pm.ls(sl=True)

#     # Check if exactly two objects are selected
#     if len(sel) != 2:
#         cmds.warning("Please select exactly two objects.")


#     source_mesh = None
#     dest_mesh = None

#     # Identify source and destination meshes
#     for s in sel:
#         if "l_" in s.name():
#             source_mesh = s
#         elif "r_" in s.name():
#             dest_mesh = s

#     # Check if both source and destination meshes are identified
#     if not (source_mesh and dest_mesh):
#         cmds.warning("Please select a 'l_' object as source and a 'r_' object as destination.")

#     # Generate mirrored name for the source mesh
#     newname = source_mesh.name().replace("l_", "r_")

#     # Print the new name
#     print("Mirrored name:", newname)

#     # Remove Ziva setup from the destination mesh
#     pm.select(dest_mesh)
#     pm.ziva(rm=True)
#     pm.select(cl=True)
#     # Copy-paste attributes with name substitution
#     pm.select(source_mesh,dest_mesh)
#     utility.copy_paste_with_substitution("(^|_)l($|_)", "r")


def create_zMirror():
    # Get selected objects
    sel = pm.ls(sl=True)

    # Check if at least one object is selected
    if not sel:
        cmds.warning("Please select at least one object.")
        return

    for source_transform in sel:
        # Check if the selected object is a transform
        if not pm.nodeType(source_transform) == "transform":
            cmds.warning(f"Skipping non-transform object: {source_transform}")
            continue

        # Check if the transform has a shape node (indicating it's a mesh)
        shapes = pm.listRelatives(source_transform, shapes=True)
        if not shapes:
            cmds.warning(f"Skipping non-mesh object: {source_transform}")
            continue

        # Filter out intermediate objects (Orig nodes)
        mesh_shape = None
        for shape in shapes:
            if not pm.getAttr(shape + ".intermediateObject"):
                mesh_shape = shape
                break

        # If no valid mesh shape is found, skip
        if not mesh_shape:
            cmds.warning(
                f"Skipping non-mesh or intermediate object: {source_transform}"
            )
            continue

        # Generate mirrored name for the source mesh
        newname = source_transform.name().replace("l_", "r_")

        # Print the new name
        print("Mirrored name:", newname)

        # Identify destination mesh based on mirrored name
        dest_transform = pm.PyNode(newname)

        # Check if destination transform exists
        if not dest_transform:
            cmds.warning(f"Destination transform not found for {source_transform}.")
            continue

        # Remove Ziva setup from the destination mesh
        pm.select(dest_transform)
        if not cmds.zQuery(type="zTissue"):
            cmds.warning(f"Skipping non-tissue object")
            continue
        pm.ziva(rm=True)
        pm.select(cl=True)

        # Copy-paste attributes with name substitution
        pm.select(source_transform, dest_transform)
        utility.copy_paste_with_substitution("(^|_)l($|_)", "r")


def create_zMirror_lr():
    sel = pm.ls(sl=True)

    # Check if exactly two objects are selected
    if len(sel) != 1:
        cmds.warning("Please select exactly one object.")
        return

    selected_object = sel[0]

    # Check if the selected object contains "_l_"
    if "_l_" not in selected_object.name():
        cmds.warning("The selected object should contain '_l_' in its name.")
        return

    utility.copy_paste_with_substitution("(^|_)l($|_)", "r")


def create_ziva_line_of_action():
    selected_objects = cmds.ls(selection=True, long=True)

    if not selected_objects:
        print("No object selected. Please select an object.")
        return

    line_of_action_group = "lineofaction_grp"
    if not cmds.objExists(line_of_action_group):
        line_of_action_group = cmds.createNode("transform", name=line_of_action_group)

    for obj in selected_objects:
        if cmds.objectType(obj, isType="transform"):
            child_meshes = (
                cmds.listRelatives(obj, allDescendents=True, type="mesh", fullPath=True)
                or []
            )
            for mesh in child_meshes:
                fibers = cmds.zQuery(mesh, type="zFiber")
                if not fibers:
                    print(f"No fibers found on {mesh}.")
                    continue

                for fiber in fibers:
                    # Using the last part of the full path as LOA name
                    loa_name = f"LOA_{fiber.split('|')[-1]}"
                    existing_loa = cmds.ls(loa_name)
                    if existing_loa:
                        print(
                            f"Line of action curve {loa_name} already exists. Skipping creation."
                        )
                        continue

                    try:
                        has_tissue = cmds.ls(type="zTissue")
                        has_bone = cmds.ls(type="zBone")
                        has_cloth = cmds.ls(type="zCloth")

                        if not has_tissue and not has_bone and not has_cloth:
                            print(
                                "No Ziva tissues, bones, or cloth present. Please create the necessary nodes first."
                            )
                            return

                        mel.eval(f"zLineOfActionUtil {fiber};")
                        loa_curves = cmds.ls("curve*", type="nurbsCurve", long=True)
                        if loa_curves:
                            loa_transform = cmds.listRelatives(
                                loa_curves[0], parent=True, fullPath=True
                            )[0]
                            cmds.rename(loa_curves[0], f"{loa_name}Shape")
                            cmds.rename(loa_transform, loa_name)
                            cmds.parent(loa_name, line_of_action_group)
                            print(
                                f"Line of action curve created for {fiber} as {loa_name}."
                            )
                        else:
                            print(f"Failed to create line of action curve for {fiber}.")
                    except Exception as e:
                        print(
                            f"Failed to create line of action curve for {fiber}. Error: {str(e)}"
                        )


def create_ziva_attachment(value, radio):
    print(value, radio)
    selected_objects = cmds.ls(selection=True, long=True)
    print(value)
    if len(selected_objects) != 2:
        print("Please select exactly two objects for creating an attachment.")
        return

    ztissue_count = len(cmds.ls(cmds.zQuery(selected_objects, type="zTissue"))) or len(
        cmds.ls(cmds.zQuery(selected_objects, type="zCloth"))
    )
    zbone_count = len(cmds.ls(cmds.zQuery(selected_objects, type="zBone")))

    if ztissue_count + zbone_count != 2:
        print(
            "Invalid selection. Please select one zTissue and one zBone or two zTissues."
        )
        return

    meshes = [
        obj
        for obj in selected_objects
        if cmds.listRelatives(obj, shapes=True, type="mesh")
    ]
    if len(meshes) != 2:
        print("Please select two meshes for creating an attachment.")
        return

    try:
        source_mesh = meshes[0].split("|")[-1].split("_", 1)[-1].rsplit("_", 1)[0]
        target_mesh = meshes[1].split("|")[-1].split("_", 1)[-1].rsplit("_", 1)[0]

        # Perform zFindVerticesByProximity to get vertices within a radius
        radius = value  # Set your desired radius value
        vertices = cmds.zFindVerticesByProximity(meshes[0], meshes[1], r=radius)
        cmds.select(vertices, meshes[1])
        mel_command = cmds.ziva(a=True)
        cmds.setAttr(mel_command[0] + ".attachmentMode", radio)

        # Find existing attachments with the same name convention
        existing_attachments = cmds.ls(f"ZA_{source_mesh}_to_{target_mesh}_*_att")
        if existing_attachments:
            print(
                f"An attachment with the same name already exists: {existing_attachments[0]}"
            )
            num_attachments = int(existing_attachments[0].split("_")[-2]) + 1
            attachment_name = f"ZA_{source_mesh}_to_{target_mesh}_{num_attachments}_att"

            # Check if the new attachment name matches any existing names
            while attachment_name in existing_attachments:
                num_attachments += 1
                attachment_name = (
                    f"ZA_{source_mesh}_to_{target_mesh}_{num_attachments}_att"
                )

            # Rename the new attachment
            cmds.rename(mel_command[-1], attachment_name)
            return

        # Find the last created attachment node
        last_attachment = mel_command[-1]

        # Create a zAttachment name with a numeric suffix
        num_attachments = len(mel_command)
        attachment_name = f"ZA_{source_mesh}_to_{target_mesh}_{num_attachments}_att"

        # Check if the new attachment name matches any existing names
        while attachment_name in existing_attachments:
            num_attachments += 1
            attachment_name = f"ZA_{source_mesh}_to_{target_mesh}_{num_attachments}_att"

        # Rename the last created zAttachment
        cmds.rename(last_attachment, attachment_name)

        print(
            f"Ziva attachment created between {source_mesh} and {target_mesh} as {attachment_name}."
        )
    except Exception as e:
        print(f"Failed to create Ziva attachment. Error: {str(e)}")


def ____create_rivets____():
    return


def get_bones_mesh_list():
    bone_meshes = [
        obj
        for obj in cmds.ls(type="mesh", noIntermediate=True)
        if obj.lower().startswith("bones")
    ]
    transform_nodes = []
    for shape in bone_meshes:
        transform_node = cmds.listRelatives(shape, parent=True)
        if transform_node:
            transform_nodes.extend(transform_node)
    return transform_nodes


def find_closest_mesh(meshes, position):
    closest_mesh = None
    min_distance = float("inf")

    for mesh_name in meshes:
        selection_list = om.MSelectionList()
        selection_list.add(mesh_name)

        # Get the MDagPath from the MSelectionList
        mesh_path = selection_list.getDagPath(0)
        mesh_fn = om.MFnMesh(mesh_path)

        # Create an MPoint for the position
        point = om.MPoint(position[0], position[1], position[2])

        # Get the closest point on the mesh
        point = mesh_fn.getClosestPoint(point, om.MSpace.kWorld)[0]
        distance = point.distanceTo(om.MPoint(position[0], position[1], position[2]))

        if distance < min_distance:
            min_distance = distance
            closest_mesh = mesh_name

    return closest_mesh


def zRivetToBone(source, destination):
    source_split = source.split(".")
    destination_split = destination.split(".")

    # Extracting useful names
    src_name = source_split[0].split("|")[-1]
    dst_name = destination_split[0].split("|")[-1]

    src_name = (
        src_name.replace("LOA_ZF_tissues_", "")
        .replace("bones_", "")
        .replace("Shape", "")
    )
    dst_name = (
        dst_name.replace("ZF_tissues", "").replace("bones_", "").replace("Shape", "")
    )

    source_cv = source_split[1].replace("cv[", "cv").replace("]", "")
    destination_cv = destination_split[0]

    new_attname = f"ZRIV_{src_name}_{source_cv}_TO_{dst_name}_{destination_cv}".replace(
        "_1_fiber", ""
    )
    new_name = f"ZRIV_{src_name}_{destination_cv}".replace("_1_fiber", "")

    if cmds.ls(new_name):
        print(f"Rivets {new_name} already exists. Skipping creation.")
        return

    zrivet_attr, zrivet_name = cmds.zRivetToBone(source, destination)
    zrivet_nattr = cmds.rename(zrivet_attr, new_attname)
    zrivet_nname = cmds.rename(zrivet_name, new_name)

    existing_grp = cmds.ls("zrivets_grp")
    if not existing_grp:
        # Create an empty group
        zrivet_grp = cmds.group(em=True, name="zrivets_grp")
    else:
        zrivet_grp = existing_grp[0]

    # Check if the rivet is already a child of 'zrivets_grp'
    if cmds.listRelatives(zrivet_nname, parent=True) != zrivet_grp:
        try:
            cmds.parent(zrivet_nname, zrivet_grp)
        except RuntimeError as err:
            print(f"Error while parenting: {err}")


def create_ziva_rivet_to_bone():
    meshes = get_bones_mesh_list()
    # Assuming one or more curves are selected
    selected_curve = cmds.ls(selection=True)
    for selected in selected_curve:
        if not selected:
            print("No valid curve selected.")
            return
        cvs = cmds.ls(selected + ".cv[*]", flatten=True)
        if not cvs:
            print("No CVs found in the selected curve.")
            return

        for cv in cvs:
            cv_pos = cmds.pointPosition(cv, world=True)
            closest_bone = find_closest_mesh(meshes, cv_pos)
            if closest_bone:
                print(f"Closest mesh to CV {cv}: {closest_bone}")
                zRivetToBone(cv, closest_bone)
            else:
                print(f"No zBone found for CV: {cv}")


def ____create_muscle_to_loa____():
    return


def create_ziva_muscle_loa():
    # Get selected curve
    selected_curve = cmds.ls(selection=True)
    if not selected_curve:
        print("Please select exactly one curve.")
        return
    for curve in selected_curve:
        # Extract fiber name
        fiber_name = curve.replace("LOA_", "")

        # Validate if the ZLOA already exists
        zloa_name = f"ZLOA_{fiber_name}"
        if cmds.ls(zloa_name):
            print(f"ZLOA for {fiber_name} already exists. Skipping.")
            return

        # Get zFiber node
        zfiber_nodes = cmds.ls(fiber_name)
        if not zfiber_nodes:
            print("No zFiber nodes found.")
            return

        # Create zLineOfAction with ZLOA naming convention
        try:
            cmds.select(zfiber_nodes[0], selected_curve[0])
            zloa_node = cmds.ziva(loa=True)
            cmds.rename(zloa_node, zloa_name)
            print(f"Created ZLOA: {zloa_name}")
        except RuntimeError as err:
            print(f"Error creating ZLOA: {err}")


############################################################
#################   ZATTACH ALL OBJECTS BOTH WAY ATTACHMENT
############################################################

# This function will attach each bones and tissues
# Each Pair have both directions attachments apart from bones which will have only 1
# Mostly works with a fresh scene without any attachment


def zattach_all_objects_button(tissue_radius, bone_radius):
    print(tissue_radius, bone_radius)
    bone_meshes = [
        obj
        for obj in cmds.ls(type="mesh", noIntermediate=True)
        if obj.lower().startswith("bones")
    ]
    tissue_meshes = [
        obj
        for obj in cmds.ls(type="mesh", noIntermediate=True)
        if obj.lower().startswith("tissue") and not obj.startswith("Orig")
    ]

    for tissue_mesh in tissue_meshes:
        for other_tissue_mesh in tissue_meshes:
            if tissue_mesh == other_tissue_mesh:
                continue  # Skip the same tissue mesh for attachment
            try:
                if (
                    "tissue" in tissue_mesh.lower()
                    and "tissue" in other_tissue_mesh.lower()
                ):
                    radius = tissue_radius
                    if radius <= 0.1:
                        attachment_mode = "sliding"
                    else:
                        attachment_mode = "fixed"
                else:
                    radius = bone_radius
                    attachment_mode = "fixed"
                vertices = cmds.zFindVerticesByProximity(
                    tissue_mesh, other_tissue_mesh, r=radius
                )
                cmds.select(vertices, other_tissue_mesh)
                attachments = cmds.ls(type="zAttachment")
                # Update source mesh extraction
                source_mesh = tissue_mesh.split("_", 1)[-1].rsplit("_", 1)[0]
                target_mesh = other_tissue_mesh.split("_", 1)[-1].rsplit("_", 1)[
                    0
                ]  # Update target mesh extraction
                attachment_name = f"ZA_{source_mesh}_to_{target_mesh}_att"
                existing_attachments = [
                    att for att in attachments if attachment_name in att
                ]
                if existing_attachments:
                    print(
                        f"An attachment with the name '{attachment_name}' already exists."
                    )
                    cmds.delete(existing_attachments)
                    continue
                mel_command = cmds.ziva(a=True)
                attachments = cmds.ls(type="zAttachment")
                num_attachments = len(attachments)

                attachment_name = f"ZA_{source_mesh}_to_{target_mesh}_att"
                # attachment_name = f"ZA_{source_mesh}_to_{target_mesh}_{num_attachments}_att"
                cmds.rename(attachments[-1], attachment_name)

                print(
                    f"Ziva attachment created between {source_mesh} and {target_mesh} as {attachment_name} with mode: {attachment_mode}."
                )

                # Set the attachment mode based on the radius
                cmds.setAttr(
                    f"{attachment_name}.attachmentMode",
                    2 if attachment_mode == "sliding" else 1,
                )

            except Exception as e:
                print(
                    f"Failed to create Ziva attachment between {tissue_mesh} and {other_tissue_mesh}. Error: {str(e)}"
                )

    for bone_mesh in bone_meshes:
        for tissue_mesh in tissue_meshes:
            try:
                vertices = cmds.zFindVerticesByProximity(
                    bone_mesh, tissue_mesh, r=bone_radius
                )
                cmds.select(vertices, tissue_mesh)
                attachments = cmds.ls(type="zAttachment")

                # Update source mesh extraction
                source_mesh = (
                    bone_mesh.split("|")[-1]
                    .split("_", 1)[-1]
                    .replace("ShapeDeformed", "Bone")
                )
                # Update target mesh extraction
                target_mesh = (
                    tissue_mesh.split("|")[-1].split("_", 1)[-1].replace("Shape", "")
                )
                attachment_name = f"ZA_{source_mesh}_to_{target_mesh}_att"

                existing_attachments = [
                    att for att in attachments if attachment_name in att
                ]
                if existing_attachments:
                    print(
                        f"An attachment with the name '{attachment_name}' already exists."
                    )
                    cmds.delete(existing_attachments)
                    continue

                mel_command = cmds.ziva(a=True)
                attachments = cmds.ls(type="zAttachment")
                num_attachments = len(attachments)

                attachment_name = f"ZA_{source_mesh}_to_{target_mesh}_att"
                # attachment_name = f"ZA_{source_mesh}_to_{target_mesh}_{num_attachments}_att"
                cmds.rename(attachments[-1], attachment_name)

                print(
                    f"Ziva attachment created between {source_mesh} and {target_mesh} as {attachment_name}."
                )
            except Exception as e:
                print(
                    f"Failed to create Ziva attachment between {bone_mesh} and {tissue_mesh}. Error: {str(e)}"
                )


############################################################
#################   ZATTACH ALL OBJECTS ONE WAY ATTACHMENT
############################################################

# This function will attach each bones and tissues but if there is already an attachment exists
# It will not connect in both directions making it only 1 attachment per pair


def zattach_all_objects_button_one_time(tissue_radius, bone_radius):
    print(tissue_radius, bone_radius)
    bone_meshes = [
        obj
        for obj in cmds.ls(type="mesh", noIntermediate=True)
        if obj.lower().startswith("bones")
    ]
    tissue_meshes = [
        obj
        for obj in cmds.ls(type="mesh", noIntermediate=True)
        if obj.lower().startswith("tissue") and not obj.startswith("Orig")
    ]

    processed_pairs = set()  # Keep track of processed pairs

    for i, tissue_mesh in enumerate(tissue_meshes):
        for j, other_tissue_mesh in enumerate(tissue_meshes):
            if i == j:
                continue  # Skip the same tissue mesh for attachment
            try:
                if (
                    "tissue" in tissue_mesh.lower()
                    and "tissue" in other_tissue_mesh.lower()
                ):
                    radius = tissue_radius
                    if radius <= 0.1:
                        attachment_mode = "sliding"
                    else:
                        attachment_mode = "fixed"
                else:
                    radius = bone_radius
                    attachment_mode = "fixed"

                source_mesh = tissue_mesh.split("_", 1)[-1].rsplit("_", 1)[0]
                target_mesh = other_tissue_mesh.split("_", 1)[-1].rsplit("_", 1)[0]

                # Check if the pair has already been processed
                pair_key = tuple(sorted([source_mesh, target_mesh]))
                if pair_key in processed_pairs:
                    print(
                        f"Attachment between {source_mesh} and {target_mesh} already processed. Skipping."
                    )
                    continue

                attachment_name = f"ZA_{source_mesh}_to_{target_mesh}_att"

                # Check if an attachment with the same source and target mesh names exists
                existing_attachments = cmds.ls(type="zAttachment")
                for existing_att in existing_attachments:
                    (
                        existing_source_mesh,
                        existing_target_mesh,
                    ) = get_source_and_target_mesh_names(existing_att)
                    if (
                        source_mesh == existing_source_mesh
                        and target_mesh == existing_target_mesh
                    ):
                        print(
                            f"An attachment already exists for {source_mesh} and {target_mesh}. Skipping."
                        )
                        break
                else:
                    # Continue if no existing attachment with the same source and target mesh names
                    vertices = cmds.zFindVerticesByProximity(
                        tissue_mesh, other_tissue_mesh, r=radius
                    )
                    cmds.select(vertices, other_tissue_mesh)
                    mel_command = cmds.ziva(a=True)
                    attachments = cmds.ls(type="zAttachment")
                    num_attachments = len(attachments)

                    # Update attachment name to include source and target mesh names
                    attachment_name = f"ZA_{source_mesh}_to_{target_mesh}_att"
                    cmds.rename(attachments[-1], attachment_name)

                    print(
                        f"Ziva attachment created between {source_mesh} and {target_mesh} as {attachment_name} with mode: {attachment_mode}."
                    )

                    # Set the attachment mode based on the radius
                    cmds.setAttr(
                        f"{attachment_name}.attachmentMode",
                        2 if attachment_mode == "sliding" else 1,
                    )

                    # Mark the pair as processed
                    processed_pairs.add(pair_key)

            except Exception as e:
                print(
                    f"Failed to create Ziva attachment between {tissue_mesh} and {other_tissue_mesh}. Error: {str(e)}"
                )

    for bone_mesh in bone_meshes:
        for tissue_mesh in tissue_meshes:
            try:
                vertices = cmds.zFindVerticesByProximity(
                    bone_mesh, tissue_mesh, r=bone_radius
                )
                cmds.select(vertices, tissue_mesh)
                attachments = cmds.ls(type="zAttachment")

                # Update source mesh extraction
                source_mesh = (
                    bone_mesh.split("|")[-1]
                    .split("_", 1)[-1]
                    .replace("ShapeDeformed", "Bone")
                )
                # Update target mesh extraction
                target_mesh = (
                    tissue_mesh.split("|")[-1].split("_", 1)[-1].replace("Shape", "")
                )
                attachment_name = f"ZA_{source_mesh}_to_{target_mesh}_att"

                existing_attachments = [
                    att for att in attachments if attachment_name in att
                ]
                if existing_attachments:
                    print(
                        f"An attachment with the name '{attachment_name}' already exists."
                    )
                    cmds.delete(existing_attachments)
                    continue

                mel_command = cmds.ziva(a=True)
                attachments = cmds.ls(type="zAttachment")
                num_attachments = len(attachments)

                attachment_name = f"ZA_{source_mesh}_to_{target_mesh}_att"
                # attachment_name = f"ZA_{source_mesh}_to_{target_mesh}_{num_attachments}_att"
                cmds.rename(attachments[-1], attachment_name)

                print(
                    f"Ziva attachment created between {source_mesh} and {target_mesh} as {attachment_name}."
                )
            except Exception as e:
                print(
                    f"Failed to create Ziva attachment between {bone_mesh} and {tissue_mesh}. Error: {str(e)}"
                )


def get_source_and_target_mesh_names(attachment_name):
    # Extract source and target mesh names from the attachment name
    attachment_parts = attachment_name.split("_")
    source_mesh = "_".join(attachment_parts[1:-3])
    target_mesh = "_".join(attachment_parts[-3:-1])
    return source_mesh, target_mesh


############################################################
#################   DELETE RIVETS   ########################
############################################################


def find_shape_node(selected_object):
    shapes = cmds.listRelatives(selected_object, shapes=True, fullPath=True) or []
    valid_shapes = [shape for shape in shapes if not shape.endswith("Orig")]
    return valid_shapes


def find_zRivetToBone_connections(shape_node):
    zRivetToBone_nodes = []
    connections = cmds.listConnections(shape_node, source=True, destination=False) or []
    for connection in connections:
        if cmds.nodeType(connection) == "zRivetToBone":
            zRivetToBone_nodes.append(connection)
    return zRivetToBone_nodes


def get_related_zRivetToBone_nodes(zRivetToBone_nodes):
    related_nodes = zRivetToBone_nodes[:]
    while True:
        new_related_nodes = []
        for node in related_nodes:
            connections = (
                cmds.listConnections(node, source=True, destination=False) or []
            )
            for connection in connections:
                if (
                    cmds.nodeType(connection) == "zRivetToBone"
                    and connection not in related_nodes
                ):
                    new_related_nodes.append(connection)
        if not new_related_nodes:
            break
        related_nodes.extend(new_related_nodes)
    return related_nodes


def find_zRivetsandDelete():
    # Get selected object
    selected_objects = cmds.ls(selection=True)
    if selected_objects:
        selected_object = selected_objects[0]
        shape_nodes = find_shape_node(selected_object)
        for shape_node in shape_nodes:
            zRivetToBone_nodes = find_zRivetToBone_connections(shape_node)
            related_zRivetToBone_nodes = get_related_zRivetToBone_nodes(
                zRivetToBone_nodes
            )
            if related_zRivetToBone_nodes:
                cmds.select(related_zRivetToBone_nodes, add=True)
                break

    # Execute the given Python command
    python_command = "from zBuilder.utils import remove_zRivetToBone_nodes; from maya import cmds; remove_zRivetToBone_nodes(cmds.ls(sl=True))"
    cmds.evalDeferred(python_command)


############################################################
#################   DELETE ZLINEOFACTION  ##################
############################################################


def find_shape_nodes(selected_objects):
    shape_nodes = []
    for obj in selected_objects:
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        valid_shapes = [shape for shape in shapes if not shape.endswith("Orig")]
        shape_nodes.extend(valid_shapes)
    return shape_nodes


def delete_zLineOfAction_connections(shape_nodes):
    zLineOfAction_nodes = []
    for shape_node in shape_nodes:
        connections = (
            cmds.listConnections(shape_node, source=False, destination=True) or []
        )
        for connection in connections:
            if cmds.nodeType(connection) == "zLineOfAction":
                zLineOfAction_nodes.append(connection)
    if zLineOfAction_nodes:
        cmds.select(zLineOfAction_nodes, replace=True)
        cmds.delete()


def find_zLineOfActionandDelete():
    # Get selected objects
    selected_objects = cmds.ls(selection=True)
    if selected_objects:
        shape_nodes = find_shape_nodes(selected_objects)
        delete_zLineOfAction_connections(shape_nodes)
    else:
        print("Please select at least one object.")


############################################################
#################   DELETE zAll  ###########################
############################################################


def deleteall_zivaNodes():
    selected = find_selected_mesh()
    if selected:
        for obj in selected:
            cmds.select(obj)
            cmds.ziva(rm=True)
    else:
        python_command = "import zBuilder.utils as utility; utility.remove_all_solvers(confirmation=False)"
        cmds.evalDeferred(python_command)


def ____delete_ziva_component____():
    return


############################################################
#################   DELETE COMPONENTS  #####################
############################################################


def delete_component_action(value):
    # value = self.component_dropdown.currentText()
    print(f"Deleting {value}")
    if value == "zRivetToBone":
        find_zRivetsandDelete()
    elif value == "zLineOfAction":
        find_zLineOfActionandDelete()
    elif value == "zAll":
        deleteall_zivaNodes()
    elif value == "zMaterial":
        selected_objects = find_selected_mesh()
        for obj in selected_objects:
            # Query zMaterial components
            z_components = cmds.zQuery(obj, type="zMaterial")
            # Check if there are more than 1 zMaterial components
            if len(z_components) > 1:
                # Delete all but the first material (keeping array[0])
                materials_to_delete = z_components[1:]
                cmds.select(materials_to_delete, r=True)
                mel.eval("ZivaDeleteSelection")
                print(f"Deleted additional zMaterial components for {obj}.")
            else:
                print(
                    f"Only one zMaterial component found for {obj}. No deletion needed."
                )
    else:
        selected_objects = find_selected_mesh()
        for obj in selected_objects:
            z_components = cmds.zQuery(obj, type=value)
            cmds.select(z_components)
            mel.eval("ZivaDeleteSelection")
            print(f"Deleted zMaterials for {obj}.")

    print("Action after Delete zivaComponents button click")


def ____modify_ziva_tets____():
    return


############################################################
#################   MODIFY zTET SIZE  ######################
############################################################


def modify_ztet_size(percentage):
    selection = cmds.ls(selection=True)

    if not selection:
        print("Nothing selected. Please select an object or a group.")
        return

    for selected_object in selection:
        ztet_nodes = []

        if cmds.objectType(selected_object) == "transform":
            ztet_nodes.extend(cmds.ls(cmds.listHistory(selected_object), type="zTet"))

            descendants = (
                cmds.listRelatives(selected_object, allDescendents=True, fullPath=True)
                or []
            )
            for descendant in descendants:
                ztet_nodes.extend(cmds.ls(cmds.listHistory(descendant), type="zTet"))

        elif cmds.objectType(selected_object) == "zTet":
            ztet_nodes.append(selected_object)

        for ztet in ztet_nodes:
            if "Orig" in ztet:
                continue  # Skip Orig mesh

            try:
                current_size = cmds.getAttr(f"{ztet}.tetSize")
                new_size = current_size / (1 + percentage / 100)
                cmds.setAttr(f"{ztet}.tetSize", new_size)

                print(f"Adjusted zTet size for '{ztet}' by {percentage}%.")
            except ValueError as e:
                print(f"Error modifying zTet size for '{ztet}': {e}")


############################################################
#################   CHANGE zTET SIZE  ######################
############################################################


def list_meshes_in_group(group):
    meshes = (
        cmds.listRelatives(group, allDescendents=True, type="mesh", fullPath=True) or []
    )
    return meshes


def find_ztet_nodes(mesh):
    ztet_nodes = cmds.zQuery(mesh, type="zTet") or []
    return ztet_nodes


def change_ztet_size(percentage):
    selection = cmds.ls(selection=True)

    if not selection:
        print("Nothing selected. Please select an object or a group.")
        return

    for selected_object in selection:
        if cmds.objectType(selected_object) == "transform":
            meshes = list_meshes_in_group(selected_object)
        elif cmds.objectType(selected_object) == "mesh":
            meshes = [selected_object]
        else:
            print(
                f"Skipping selection: {selected_object}. It is neither a group nor a mesh."
            )
            continue

        for mesh in meshes:
            ztet_nodes = find_ztet_nodes(mesh)

            for ztet in ztet_nodes:
                if "Orig" in ztet:
                    continue  # Skip Orig mesh

                try:
                    current_size = cmds.getAttr(f"{ztet}.tetSize")
                    if percentage > 0:
                        new_size = current_size * (1 + percentage / 100)
                    else:
                        new_size = current_size / (1 - percentage / 100)
                    cmds.setAttr(f"{ztet}.tetSize", new_size)

                    print(f"Adjusted zTet size for '{ztet}' by {percentage}%.")
                except ValueError as e:
                    print(f"Error modifying zTet size for '{ztet}': {e}")


# Example usage:
# Select objects or groups containing zTet nodes and run the function
# change_ztet_size(10)  # Adjust the percentage as needed


############################################################
#################   CREATE SET   ###########################
############################################################


def create_set(elements, set_name):
    cmds.select(cl=True)
    if elements:
        for element in elements:
            if not cmds.objExists(set_name):
                cmds.select(element)
                cmds.sets(n=set_name)
            else:
                cmds.sets(element, add=set_name)
    else:
        print(f"No elements found for '{set_name}'.")


def sets_create_mesh(type_):
    set_geo = f"{type_}_GEO"
    if not cmds.objExists(set_geo):
        all_elements = cmds.zQuery(type=type_)
        elements_to_select = []

        for element in all_elements:
            z_geo = cmds.listConnections(element, type="zGeo")
            if z_geo:
                z_msh = cmds.listConnections(z_geo, sh=True, type="transform")
                if z_msh:
                    elements_to_select.append(z_msh[0])

        if elements_to_select:
            cmds.select(elements_to_select)
            cmds.sets(n=set_geo)
    else:
        all_elements = cmds.zQuery(type=type_)
        elements_to_add = []

        for element in all_elements:
            z_geo = cmds.listConnections(element, type="zGeo")
            if z_geo:
                z_msh = cmds.listConnections(z_geo, sh=True, type="transform")
                if z_msh:
                    elements_to_add.append(z_msh[0])

        if elements_to_add:
            cmds.select(elements_to_add)
            cmds.sets(set_geo, add=True)


def sets_create(type_):
    all_elements = cmds.zQuery(type=type_)
    print(f"all_elements = {all_elements}")
    create_set(all_elements, f"{type_}_GEO")


def sets_create_curves(type_):
    all_curves_rivets = cmds.ls(type=type_)
    all_curve_shapes = [
        x for x in all_curves_rivets if not ("RefShape" in x or "ShapeOrig" in x)
    ]
    create_set(all_curve_shapes, f"{type_}_loa_SET")


def sets_create_comp(type_):
    all_elements = cmds.zQuery(type=type_)
    print(f"all_elements = {all_elements}")
    create_set(all_elements, f"{type_}_SET")
    print(f"component = {type_}_SET")


def sets_create_zloa():
    all_elements = cmds.zQuery(loa=True)
    create_set(all_elements, "zlineOfAction_SET")


def sets_create_by_index(index):
    type_mappings = {
        0: "zBone",
        1: "zTissue",
        2: "zFiber",
        3: "zAttachment",
        4: "zRivetToBone",
        5: "zCloth",
        6: "zLineOfAction",
        7: "zBone",
        8: "zTissue",
        9: "nurbsCurve",  # LOA Curves handled separately
    }
    type_name = type_mappings.get(index)
    print(f"type name = {type_name}")
    cmds.select(cl=True)
    if type_name:
        print(f"type_name = {type_name}")
        if index == 0 or index == 1 or index == 2 or index == 3:
            sets_create_comp(type_name)
        if index == 4:
            sets_create_loa(type_name)
        elif index == 6:
            sets_create_zloa()
        elif index == 7 or index == 8:
            sets_create_mesh(type_name)
            # sets_create(type_name)
        elif index == 9:
            sets_create_curves(type_name)
        print("checked all")
    else:
        print("outer")
        sets_create_comp(type_name)


############################################################
# CREATE ATTACHMENTS WITH EVEN NUMBER SELECTION
############################################################


# create zAttachment parent child concept
def create_zattachments_for_selected(tissue_radius, bone_radius, radio_value):
    print(radio_value)
    selected_objects = cmds.ls(selection=True, long=True)
    bone_meshes = [
        obj
        for obj in cmds.ls(type="mesh", noIntermediate=True)
        if obj.lower().startswith("bones")
    ]
    tissue_meshes = selected_objects

    if not selected_objects or len(selected_objects) % 2 != 0:
        print(
            "Invalid selection. Please select an even number of objects for creating attachments."
        )
        return

    try:
        attachments_created = []
        objects = []

        # Separate the selected objects into tissues and bones
        for obj in selected_objects:
            if cmds.zQuery(obj, type="zTissue") or cmds.zQuery(obj, type="zBone"):
                objects.append(obj)
            else:
                print(f"Invalid object type: {obj}")

        for i in range(0, len(objects), 2):
            parent_obj = objects[i]
            child_obj = objects[i + 1]

            # Get source and target mesh names
            parent_mesh = get_mesh_name(parent_obj)
            child_mesh = get_mesh_name(child_obj)

            # Attach parent and child objects
            attachments_created.extend(
                create_zattach_tissues(
                    parent_obj,
                    child_obj,
                    parent_mesh,
                    child_mesh,
                    tissue_radius,
                    radio_value,
                )
            )

        for bone_mesh in bone_meshes:
            for tissue_mesh in tissue_meshes:
                try:
                    vertices = cmds.zFindVerticesByProximity(
                        bone_mesh, tissue_mesh, r=bone_radius
                    )
                    cmds.select(vertices, tissue_mesh)
                    attachments = cmds.ls(type="zAttachment")
                    # Update source mesh extraction
                    source_mesh = (
                        bone_mesh.split("|")[-1]
                        .split("_", 1)[-1]
                        .replace("ShapeDeformed", "Bone")
                    )
                    # Update target mesh extraction
                    target_mesh = (
                        tissue_mesh.split("|")[-1]
                        .split("_", 1)[-1]
                        .replace("Shape", "")
                    )
                    attachment_name = f"ZA_{source_mesh}_to_{target_mesh}_att"
                    existing_attachments = [
                        att for att in attachments if attachment_name in att
                    ]
                    if existing_attachments:
                        print(
                            f"An attachment with the name '{attachment_name}' already exists."
                        )
                        cmds.delete(existing_attachments)
                        continue
                    mel_command = cmds.ziva(a=True)
                    attachments = cmds.ls(type="zAttachment")
                    num_attachments = len(attachments)
                    attachment_name = f"ZA_{source_mesh}_to_{target_mesh}_att"
                    # attachment_name = f"ZA_{source_mesh}_to_{target_mesh}_{num_attachments}_att"
                    cmds.rename(attachments[-1], attachment_name)
                    print(
                        f"Ziva attachment created between {source_mesh} and {target_mesh} as {attachment_name}."
                    )
                except Exception as e:
                    print(
                        f"Failed to create Ziva attachment between {bone_mesh} and {tissue_mesh}. Error: {str(e)}"
                    )

        return attachments_created

    except Exception as e:
        print(f"Failed to create Ziva attachments. Error: {str(e)}")


def create_zattach_tissues(
    parent_obj, child_obj, parent_mesh, child_mesh, tissue_radius, radio_value
):
    # Common function to attach parent and child objects
    attachments_created = []

    # Perform zFindVerticesByProximity to get vertices within a radius
    radius = tissue_radius  # Set your desired radius value
    vertices = cmds.zFindVerticesByProximity(parent_obj, child_obj, r=radius)
    cmds.select(vertices, child_obj)
    mel_command = cmds.ziva(a=True)
    cmds.setAttr(mel_command[0] + ".attachmentMode", radio_value)

    # Find existing attachments with the same name convention
    existing_attachments = cmds.ls(f"ZA_{parent_mesh}_to_{child_mesh}_*_att")
    num_attachments = len(existing_attachments) + 1

    # Create a zAttachment name with a numeric suffix
    attachment_name = f"ZA_{parent_mesh}_to_{child_mesh}_{num_attachments}_att"

    # Check if the new attachment name matches any existing names
    while attachment_name in existing_attachments:
        num_attachments += 1
        attachment_name = f"ZA_{parent_mesh}_to_{child_mesh}_{num_attachments}_att"

    # Rename the last created zAttachment
    cmds.rename(mel_command[-1], attachment_name)

    print(
        f"Ziva attachment created between {parent_mesh} and {child_mesh} as {attachment_name}."
    )
    attachments_created.append(attachment_name)

    return attachments_created


def get_mesh_name(obj):
    # Extract the mesh name from the object
    shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
    for shape in shapes:
        if not shape.endswith("Orig") and cmds.nodeType(shape) == "mesh":
            return shape.split("|")[-1].split("_", 1)[-1].rsplit("_", 1)[0]


############################################################
#################   CREATE ZPAINT ATTACHMENTS   ############
############################################################


def get_zattachments_from_selected_mesh():
    # Get the selected objects
    selected_objects = cmds.ls(selection=True, long=True)
    # Check if an object is selected
    if not selected_objects:
        cmds.warning("Please select a mesh object.")
        return 0
    # Select meshes from the hierarchy
    selected_meshes = [
        obj
        for obj in selected_objects
        if cmds.listRelatives(obj, shapes=True, type="mesh")
    ]
    # Check if a mesh is selected
    if not selected_meshes:
        cmds.warning("Please select a valid mesh object.")
        return 0
    # Get the zAttachment nodes associated with the selected mesh
    zattachments = cmds.zQuery(type="zAttachment")
    # Check if zAttachment nodes were found
    if zattachments is None:
        cmds.warning("No zAttachment nodes found.")
        return 0
    # Check the number of zAttachment nodes
    num_zattachments = len(zattachments)
    attachment_names = [f"zAttachment_{i}" for i in range(1, num_zattachments + 1)]
    print(f"Number of zAttachment nodes: {zattachments}")
    return zattachments


def apply_zpaint_attachments(min_value, max_value):
    selected_objects = cmds.ls(sl=True)
    if not selected_objects:
        cmds.warning("Invalid selection. Please select an attachment.")
        return
    # Placeholder function: Replace with your logic to apply zPaintAttachmentsByProximity
    cmds.zPaintAttachmentsByProximity(min=min_value, max=max_value)
    print(
        f"Applying zPaintAttachmentsByProximity with min: {min_value}, max: {max_value}"
    )


############################################################
#################   CREATE PAINT SMOOTH   ##################
############################################################


def paint_tool():
    cmds.ArtPaintAttrToolOptions()


def apply_paint_operation(num_times):
    mel_command = "artAttrPaintOperation artAttrCtx Smooth;"
    mel_command += "artAttrCtx -e -clear `currentCtx`;"
    for _ in range(num_times):
        mel.eval(mel_command, lowestPriority=True)
    cmds.warning(f"Smooth Applied {num_times} Times")


def randomize_mesh_colors():
    # Get selected objects
    selected_objects = cmds.ls(selection=True, dag=True, long=True, shapes=True)

    if not selected_objects:
        cmds.warning("No meshes selected.")
        return

    # Filter out "Orig" nodes and keep only meshes
    meshes = [
        obj
        for obj in selected_objects
        if "Orig" not in obj and cmds.nodeType(obj) == "mesh"
    ]

    if not meshes:
        cmds.warning("No valid meshes selected.")
        return

    # Iterate through the meshes and assign random colors
    for mesh in meshes:
        # Get the base name of the mesh
        mesh_name = cmds.listRelatives(mesh, parent=True, fullPath=True)[0]
        # Generate a unique color node name based on the mesh name
        color_node_name = "{}_colorNode".format(mesh_name)
        # Create a shading node (e.g., lambert) for color
        shading_node = cmds.shadingNode("lambert", asShader=True, name=color_node_name)
        shading_group = cmds.sets(
            shading_node,
            renderable=True,
            noSurfaceShader=True,
            empty=True,
            name="{}_SG".format(color_node_name),
        )
        # Assign a random color
        color = [random.random(), random.random(), random.random()]
        cmds.setAttr("{}.color".format(shading_node), *color, type="double3")
        # Apply the shading node to the mesh
        cmds.select(mesh, replace=True)
        cmds.hyperShade(assign=shading_node)
    cmds.warning("Mesh colors randomized successfully.")


# This will create a new mesh from selected and transfer the info
# from selected mesh and change it to an OLD mesh
z = zva.Ziva()


def ziva_cloth_transfer():
    selected_objects = cmds.ls(selection=True)

    if not selected_objects:
        cmds.warning("Please select a mesh to transfer Ziva cloth settings.")
        return

    selected_object = selected_objects[0]

    # Check if the selected object is a zCloth
    if cmds.zQuery(selected_object, type="zCloth"):
        # Rename the selected object without "_OLD" suffix
        zcth = cmds.zQuery(type="zCloth")
        rest_scale_frames = cmds.keyframe(zcth[0] + ".restScaleEnvelope", query=True)
        rest_scale_values = cmds.keyframe(
            zcth[0] + ".restScaleEnvelope", query=True, valueChange=True
        )

        pressure_frames = cmds.keyframe(zcth[0] + ".pressureEnvelope", query=True)
        pressure_values = cmds.keyframe(
            zcth[0] + ".pressureEnvelope", query=True, valueChange=True
        )

        surface_tension_frames = cmds.keyframe(
            zcth[0] + ".surfaceTensionEnvelope", query=True
        )
        surface_tension_values = cmds.keyframe(
            zcth[0] + ".surfaceTensionEnvelope", query=True, valueChange=True
        )

        z.retrieve_from_scene()
        old_mesh = cmds.rename(selected_object, selected_object + "_OLD")
        # Duplicate the selected mesh and rename the original with "_OLD" suffix
        new_mesh = cmds.duplicate(old_mesh, name=selected_object)[0]
        cmds.select(old_mesh)
        cmds.ziva(rm=True)
        cmds.hide(old_mesh)
        # Build Ziva on the new mesh
        cmds.select(new_mesh)
        # cmds.ziva(rm=True)
        z.build()
        # Apply keyframes and values to the new mesh
        for frame, value in zip(rest_scale_frames, rest_scale_values):
            cmds.setKeyframe(zcth[0] + ".restScaleEnvelope", time=frame, value=value)

        for frame, value in zip(pressure_frames, pressure_values):
            cmds.setKeyframe(zcth[0] + ".pressureEnvelope", time=frame, value=value)

        for frame, value in zip(surface_tension_frames, surface_tension_values):
            cmds.setKeyframe(
                zcth[0] + ".surfaceTensionEnvelope", time=frame, value=value
            )

        print("Ziva cloth settings transferred successfully.")

    elif cmds.zQuery(selected_object, type="zTissue"):
        # Rename the selected object without "_OLD" suffix
        ztis = cmds.zQuery(type="zTissue")
        rest_scale_frames = cmds.keyframe(ztis[0] + ".restScaleEnvelope", query=True)
        rest_scale_values = cmds.keyframe(
            ztis[0] + ".restScaleEnvelope", query=True, valueChange=True
        )

        pressure_frames = cmds.keyframe(ztis[0] + ".pressureEnvelope", query=True)
        pressure_values = cmds.keyframe(
            ztis[0] + ".pressureEnvelope", query=True, valueChange=True
        )

        surface_tension_frames = cmds.keyframe(
            ztis[0] + ".surfaceTensionEnvelope", query=True
        )
        surface_tension_values = cmds.keyframe(
            ztis[0] + ".surfaceTensionEnvelope", query=True, valueChange=True
        )

        z.retrieve_from_scene()
        old_mesh = cmds.rename(selected_object, selected_object + "_OLD")
        # Duplicate the selected mesh and rename the original with "_OLD" suffix
        new_mesh = cmds.duplicate(old_mesh, name=selected_object)[0]
        cmds.select(old_mesh)
        cmds.ziva(rm=True)
        cmds.hide(old_mesh)
        # Build Ziva on the new mesh
        cmds.select(new_mesh)
        # cmds.ziva(rm=True)
        z.build()
        # Apply keyframes and values to the new mesh
        for frame, value in zip(rest_scale_frames, rest_scale_values):
            cmds.setKeyframe(ztis[0] + ".restScaleEnvelope", time=frame, value=value)

        for frame, value in zip(pressure_frames, pressure_values):
            cmds.setKeyframe(ztis[0] + ".pressureEnvelope", time=frame, value=value)

        for frame, value in zip(surface_tension_frames, surface_tension_values):
            cmds.setKeyframe(
                ztis[0] + ".surfaceTensionEnvelope", time=frame, value=value
            )

        print("Ziva cloth settings transferred successfully.")
    else:
        cmds.warning("Please select a valid Ziva cloth mesh to transfer settings.")


def ziva_get_mesh_nodes():
    # Get the selected objects
    selected_objects = cmds.ls(selection=True, long=True)
    # Check if an object is selected
    if not selected_objects:
        cmds.warning("Please select a mesh object.")
        return []

    # Select meshes from the hierarchy
    selected_meshes = [
        obj
        for obj in selected_objects
        if cmds.listRelatives(obj, shapes=True, type="mesh")
    ]
    # Check if a mesh is selected
    if not selected_meshes:
        cmds.warning("Please select a valid mesh object.")
        return []

    # Get the zAttachment nodes associated with the selected mesh
    zattachments = cmds.zQuery(type="zAttachment") or []
    # Get zFiber nodes associated with the selected mesh
    zfiber_nodes = cmds.zQuery(type="zFiber") or []
    # Get zCloth nodes associated with the selected mesh
    zcloth_nodes = cmds.zQuery(type="zCloth") or []
    # Get zTet nodes associated with the selected mesh
    ztet_nodes = cmds.zQuery(type="zTet") or []
    # Get zMaterial nodes associated with the selected mesh
    zmaterial_nodes = cmds.zQuery(type="zMaterial") or []

    ztissue_nodes = cmds.zQuery(type="zTissue") or []
    zbone_nodes = cmds.zQuery(type="zBone") or []
    zLineOfAction_nodes = cmds.zQuery(type="zLineOfAction") or []
    # Combine all node types into a single list
    all_nodes = (
        zattachments
        + zfiber_nodes
        + zcloth_nodes
        + ztet_nodes
        + zmaterial_nodes
        + ztissue_nodes
        + zbone_nodes
        + zLineOfAction_nodes
    )

    print(f"zAttachment nodes: {zattachments}")
    print(f"zFiber nodes: {zfiber_nodes}")
    print(f"zCloth nodes: {zcloth_nodes}")
    print(f"zTet nodes: {ztet_nodes}")
    print(f"zMaterial nodes: {zmaterial_nodes}")

    return all_nodes


def get_z_components(selected_object):
    """
    Get Ziva components (zAttachment, zMaterial, zTet) associated with the selected object.

    Args:
        selected_object (str): The selected object in the Maya scene.

    Returns:
        dict: A dictionary containing lists of zComponents for each type.
    """
    z_components = {
        "zAttachment": [],
        "zMaterial": [],
        "zTet": [],
        "zTissue": [],
        "zBone": [],
        "zFiber": [],
        "zCloth": [],
        "zLineOfAction": [],
    }

    # Check if the selected object is valid
    if not cmds.objExists(selected_object):
        cmds.warning("Invalid object. Please select a valid object.")
        return z_components

    # Get zAttachment nodes associated with the selected object
    z_attachments = cmds.zQuery(type="zAttachment") or []
    z_components["zAttachment"] = z_attachments
    # Get zMaterial nodes associated with the selected object
    z_materials = cmds.zQuery(type="zMaterial") or []
    z_components["zMaterial"] = z_materials
    # Get zTet nodes associated with the selected object
    z_tets = cmds.zQuery(type="zTet") or []
    z_components["zTet"] = z_tets

    z_tissues = cmds.zQuery(type="zTissue") or []
    z_components["zTissue"] = z_tissues

    z_bones = cmds.zQuery(type="zBone") or []
    z_components["zBone"] = z_bones

    z_fibers = cmds.zQuery(type="zFiber") or []
    z_components["zFiber"] = z_fibers

    z_cloths = cmds.zQuery(type="zCloth") or []
    z_components["zCloth"] = z_cloths

    # z_loas = cmds.zQuery(type="zLineOfAction") or []
    # z_components["zLineOfAction"] = z_loas

    return z_components


def is_nurbs_curve(obj):
    # Check if the object has a shape node and the type of the shape node is 'nurbsCurve'
    shape_nodes = cmds.listRelatives(obj, shapes=True, type='nurbsCurve')
    return shape_nodes is not None and len(shape_nodes) > 0

def create_point_on_curve_and_remap():
    # Get the selected object
    selected_objects = cmds.ls(selection=True)
    if not selected_objects:
        cmds.warning("Please select an object.")
        return None, None, None
    curve_name = selected_objects[0]
    # Check if it's a NURBS curve
    if not is_nurbs_curve(curve_name):
        cmds.warning("Selected object is not a NURBS curve.")
        return None, None, None
    # Get the shape node of the NURBS curve
    curve_shape = cmds.listRelatives(curve_name, shapes=True)[0]
    # Create a pointOnCurveInfo node
    point_info_node = cmds.createNode('pointOnCurveInfo', name='pointOnCurveInfo1')
    # Connect the curve's worldSpace attribute to the pointOnCurveInfo node
    cmds.connectAttr(curve_shape + '.worldSpace', point_info_node + '.inputCurve')
    # Create a remapValue node
    remap_node = cmds.createNode('remapValue', name='remapValue1')
    # Connect the positionZ of the pointOnCurveInfo node to the input value of the remapValue node
    cmds.connectAttr(point_info_node + '.positionZ', remap_node + '.inputValue')
    # Connect the input value of remapValue to the input min of remapValue
    in_value = cmds.getAttr(remap_node + '.inputValue')
    cmds.setAttr(remap_node + '.inputMin' , in_value)
    # Change the output min and output max to reverse values
    cmds.setAttr(remap_node + '.outputMin', 1.0)
    cmds.setAttr(remap_node + '.outputMax', 0.0)

    # Extract the new name by removing "LOA_"
    fiber_name = curve_name.replace("LOA_", "")

    # Select the new object
#    cmds.select(new_curve_name, replace=True)


    # Connect the outValue of the original remapValue node to the excitation attribute of the new object
    cmds.connectAttr(remap_node + '.outValue', fiber_name + '.excitation')

    return point_info_node, remap_node
