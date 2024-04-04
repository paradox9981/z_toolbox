import maya.cmds as cmds
import maya.OpenMayaUI as omui
import zBuilder.zMaya as zMaya
from PySide2 import QtCore, QtGui, QtWidgets


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return long(main_window_ptr)

class CheckPointsUI(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(CheckPointsUI, self).__init__(parent)
        self.setWindowTitle("Check Points")
        self.setFixedWidth(500)
        self.setFixedHeight(250)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setStyleSheet("QDialog { border: 2px solid gray; }")
        self.create_ui()

    def create_ui(self):
        main_layout = QtWidgets.QVBoxLayout(self)

        check_points_label = QtWidgets.QLabel("Check Points:")
        main_layout.addWidget(check_points_label)

        checkboxes_layout = QtWidgets.QGridLayout()

        self.create_checkbox("CheckZivaPluginCheckbox", "Check if Ziva Plugin is Loaded", checkboxes_layout, 0)
        self.create_checkbox("CheckBoneTissueGroupsCheckbox", "Check Bone and Tissue Groups", checkboxes_layout, 1)
        self.create_checkbox("CheckTissueGroupsCheckbox", "Check Tissue Groups", checkboxes_layout, 2)
        self.create_checkbox("CheckBoneTissueMeshesCheckbox", "Check Meshes for Bone and Tissue Names", checkboxes_layout, 3)
        self.create_checkbox("CheckTissueMeshesCheckbox", "Check Meshes for Tissue Names", checkboxes_layout, 4)
        self.create_checkbox("CheckMeshesPrefixCheckbox", "Check Meshes for Reference Prefix", checkboxes_layout, 5)

        main_layout.addLayout(checkboxes_layout)

        check_button = QtWidgets.QPushButton("Check")
        check_button.clicked.connect(self.update_checkboxes)
        main_layout.addWidget(check_button)

    def create_checkbox(self, checkbox_name, checkbox_label, layout, row):
        checkbox = QtWidgets.QCheckBox(checkbox_label)
        checkbox.setCheckable(False)
        checkbox.setStyleSheet("QCheckBox::indicator { width: 20px; height: 20px; }")
        layout.addWidget(checkbox, row, 0)

        status_label = QtWidgets.QLabel(f"{checkbox_label} - Not Checked")
        status_label.setStyleSheet("QLabel { background-color: red; padding: 5px; }")
        layout.addWidget(status_label, row, 1)

        setattr(self, checkbox_name, checkbox)
        setattr(self, f"{checkbox_name}StatusLabel", status_label)

    def update_checkboxes(self):
        ziva_plugin_status = self.is_ziva_plugin_loaded()
        bone_tissue_groups_status = self.has_bone_and_tissue_groups()
        tissue_groups_status = self.has_tissue_groups()
        bone_tissue_meshes_status = self.meshes_have_bone_and_tissue_names()
        tissue_meshes_status = self.meshes_have_tissue_names()
        meshes_prefix_status = self.meshes_have_reference_prefix()

        self.update_checkbox_status(self.CheckZivaPluginCheckbox, self.CheckZivaPluginCheckboxStatusLabel, ziva_plugin_status)
        self.update_checkbox_status(self.CheckBoneTissueGroupsCheckbox, self.CheckBoneTissueGroupsCheckboxStatusLabel, bone_tissue_groups_status)
        self.update_checkbox_status(self.CheckTissueGroupsCheckbox, self.CheckTissueGroupsCheckboxStatusLabel, tissue_groups_status)
        self.update_checkbox_status(self.CheckBoneTissueMeshesCheckbox, self.CheckBoneTissueMeshesCheckboxStatusLabel, bone_tissue_meshes_status)
        self.update_checkbox_status(self.CheckTissueMeshesCheckbox, self.CheckTissueMeshesCheckboxStatusLabel, tissue_meshes_status)
        self.update_checkbox_status(self.CheckMeshesPrefixCheckbox, self.CheckMeshesPrefixCheckboxStatusLabel, meshes_prefix_status)

    def update_checkbox_status(self, checkbox, status_label, status):
        checkbox.setChecked(status)
        status_label.setText(f"{checkbox.text()} - {'Satisfied' if status else 'Not Satisfied'}")
        status_label.setStyleSheet(f"QLabel {{ background-color: {'green' if status else 'red'}; padding: 5px; }}")

    def is_ziva_plugin_loaded(self):
        result = cmds.pluginInfo('ziva', q=True, loaded=True)
        return result

    def has_bone_and_tissue_groups(self):
        _, bone_groups, tissue_groups = self.get_top_level_groups()
        return bool(bone_groups) and bool(tissue_groups)

    def has_tissue_groups(self):
        _, _, tissue_groups = self.get_top_level_groups()
        return bool(tissue_groups)

    def meshes_have_bone_and_tissue_names(self):
        _, bone_groups, _ = self.get_top_level_groups()
        bone_meshes = [mesh for group in bone_groups for mesh in cmds.listRelatives(group, ad=True, type='mesh', fullPath=True) if 'bone' in mesh]
        return bool(bone_meshes)

    def meshes_have_tissue_names(self):
        _, _, tissue_groups = self.get_top_level_groups()
        tissue_meshes = [mesh for group in tissue_groups for mesh in cmds.listRelatives(group, ad=True, type='mesh', fullPath=True) if 'tissue' in mesh]
        return bool(tissue_meshes)

    def meshes_have_reference_prefix(self):
        result = any('|' in mesh for mesh in cmds.ls(type='mesh', long=True))
        return result

    def get_top_level_groups(self):
        top_level_groups = cmds.ls(assemblies=True)
        bone_groups = [group for group in top_level_groups if group.startswith("bone")]
        tissue_groups = [group for group in top_level_groups if group.startswith("tissue")]
        return top_level_groups, bone_groups, tissue_groups

def run_check_points_ui():
    global check_points_ui
    try:
        check_points_ui.close()
    except:
        pass
    check_points_ui = CheckPointsUI()
    check_points_ui.show()


def ziva_rename_all_nodes():
    zMaya.rename_ziva_nodes()   
