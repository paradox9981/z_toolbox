from functools import partial
from importlib import reload

import maya.OpenMayaUI as omui
import z_toolbox.common.func_ziva_auto as zi
import z_toolbox.common.func_ziva_validator as valid
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin
from PySide2 import QtCore, QtGui, QtWidgets
from shiboken2 import wrapInstance

# reload(zi)


class Window(MayaQWidgetDockableMixin, QtWidgets.QWidget):
    def __init__(self, parent=None):
        # Normal Qt stuff
        parent = wrapInstance(
            int(omui.MQtUtil.mainWindow()), QtWidgets.QWidget)
        super(Window, self).__init__(parent)
        self.setGeometry(200, 200, 200, 200)
        # self.setMinimumHeight(600)
        self.setMinimumWidth(300)
        # self.setMaximumHeight(800)
        self.setMaximumWidth(400)
        self.setWindowTitle("[          Ziva Toolbox V2          ]")
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.left_buttons_widgets = []  # Define the attribute here
        self.create_widgets()  # Call create_widgets() before create_layout()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.left_buttons = [
            "Create Bones",
            "Create Bones_w/BS",
            "Create Tissues",
            "Create Fiber",
            "Create Cloth",
        ]

        self.right_buttons = [
            "Create LOA",
            "Create Rivets",
            "Create FibreLOA",
            "FibreLOA Remap",
            "Create Materials",
        ]
        self.label_attachments = QtWidgets.QLabel(":::::::::::::::::::::::::::::::::::::::::::::: Create zAttachments")
        self.constraint_button = QtWidgets.QPushButton("Create Attachment")
        self.constraint_button.setToolTip(
            "Create Attachment from selected Object \nMake sure that 2 objects (tissue or bone) are selected \nUse the sliding or fixed radio button \nto change th properties of the attachments"
        )
        # Add radio buttons
        self.sliding_radio = QtWidgets.QRadioButton("Sliding")
        self.fixed_radio = QtWidgets.QRadioButton("Fixed")

        # Set the default value
        self.sliding_radio.setChecked(True)

        self.delete_component_button = QtWidgets.QPushButton(
            "Delete Component")
        self.delete_component_button.setToolTip(
            "Delete attributes selected from the \ndropdown menu of a selected objects (mesh)"
        )

        self.component_dropdown = QtWidgets.QComboBox()
        self.component_dropdown.addItems(
            [
                "zAll",
                "zTet",
                "zBone",
                "zTissue",
                "zAttachment",
                "zMaterial",
                "zFiber",
                "zLineOfAction",
                "zRivetToBone",
            ]
        )

        # Components Tab Layout #################################

        self.label_tet_info = QtWidgets.QLabel(" ::::::::::::::::::::::::::::::::::::::: Reduce / Increase zTet size")

        # self.apply_tissue_percentage_button = QtWidgets.QPushButton("Apply Tissue %")
        self.increase_button = QtWidgets.QPushButton(" + ")
        self.reduce_button = QtWidgets.QPushButton(" - ")
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(1)
        self.slider.setMaximum(100)
        self.slider.setSingleStep(1)
        self.slider.setTickInterval(10)
        self.slider.setTickPosition(QtWidgets.QSlider.TicksBelow)

        self.slider_label = QtWidgets.QLabel("Slider Value: 1%")  # Initial text
        self.tissue_label = QtWidgets.QLabel("Tissue")
        self.bones_label = QtWidgets.QLabel("Bones")
        # Connect the slider valueChanged signal to the update_slider_label method
        self.slider.valueChanged.connect(self.update_slider_label)


        self.label_zattach_drive = QtWidgets.QLabel(" :::::::::::::::::::::::::::: Create zAttach by Driver => Driven")
        self.zattach_parent_child_button = QtWidgets.QPushButton(
            "zAttach Parent->Child"
        )
        self.zattach_parent_child_button.setToolTip(
            "Create attachments for any number of even selected objects \nIn each number the odd number is the parent and even \nis the child \nFor example (if 4 tissues are selected , \nfirst would be parent of the second tissue \nand third would be parent of forth tissue) \n --  Bones will be connected automatically on selected tissues"
        )

        self.sliding_radio_par = QtWidgets.QRadioButton("Sliding")
        self.fixed_radio_par = QtWidgets.QRadioButton("Fixed")
        self.sliding_radio_par.setChecked(True)

        self.zattach_all_objects_button = QtWidgets.QPushButton(
            "zAttach All Objects")

        self.create_sets_button = QtWidgets.QPushButton("Create Sets")
        self.create_sets_dropdown = QtWidgets.QComboBox()
        self.create_sets_dropdown.addItems(
            [
                "Set zBone",
                "Set zTissue",
                "Set zFiber",
                "Set zAttachment",
                "Set zRivet",
                "Set zCloth",
                "Set zLoa",
                "Set Bone Mesh",
                "Set Tissue Mesh",
                "Set LOA Curves",
            ]
        )
        self.blendshape = QtWidgets.QPushButton("Create Blendshape")
        self.duplicate = QtWidgets.QPushButton("Create Duplicate")
        self.mirror = QtWidgets.QPushButton("Create Mirror")
        self.mirror_lr = QtWidgets.QPushButton("Mirror L -> R")
        self.left_buttons_widgets = []
        self.right_buttons_widgets = []

        for name in self.left_buttons:
            button = QtWidgets.QPushButton(name)
            self.left_buttons_widgets.append(button)

        for name in self.right_buttons:
            button = QtWidgets.QPushButton(name)
            self.right_buttons_widgets.append(button)


        # New widgets for Refresh and Apply
        self.refresh_button = QtWidgets.QPushButton("Refresh")
        self.dropdown = QtWidgets.QComboBox()
        self.textbox1 = QtWidgets.QDoubleSpinBox()
        self.textbox1.setDecimals(5)
        self.textbox1.setMinimum(0)
        self.textbox1.setMaximum(10)
        self.textbox1.setSingleStep(0.01)
        self.textbox1.setValue(0.05)
        self.textbox2 = QtWidgets.QDoubleSpinBox()
        self.textbox2.setDecimals(5)
        self.textbox2.setMinimum(0)
        self.textbox2.setMaximum(10)
        self.textbox2.setSingleStep(0.01)
        self.textbox2.setValue(1.0)

        self.apply_button = QtWidgets.QPushButton("zProximity Paint Apply")
        self.validate_button = QtWidgets.QPushButton("Validate Scene File")
        self.paint_button = QtWidgets.QPushButton("Paint Weight Tool")
        self.smooth_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        # Set slider properties
        self.smooth_slider.setRange(1, 200)
        self.smooth_slider.setValue(1)
        self.smooth_spin_box = QtWidgets.QSpinBox()
        self.smooth_spin_box.setMaximum(200)
        self.smooth_apply_button = QtWidgets.QPushButton("Apply Paint Smooth")
        self.randomize_clr_button = QtWidgets.QPushButton("Randomize Color")

        # Create widgets for solvers
        self.start_frame_label = QtWidgets.QLabel("Start Frame:")
        self.start_frame_spinbox = QtWidgets.QSpinBox()
        self.start_frame_spinbox.setRange(-1000, 1000)
        self.start_frame_spinbox.setValue(1)

        self.collision_space_label = QtWidgets.QLabel("Collision Space:")
        self.collision_space_lineedit = QtWidgets.QLineEdit()
        self.collision_space_lineedit.setValidator(
            QtGui.QDoubleValidator(0.1, 0.002, 3)
        )
        self.collision_space_lineedit.setText("0.1")

        self.newton_iteration_label = QtWidgets.QLabel("Newton Iterations:")
        self.newton_iteration_spinbox = QtWidgets.QSpinBox()
        self.newton_iteration_spinbox.setRange(1, 100)
        self.newton_iteration_spinbox.setValue(1)

        self.substeps_label = QtWidgets.QLabel("Substeps:")
        self.substeps_spinbox = QtWidgets.QSpinBox()
        self.substeps_spinbox.setRange(1, 10)
        self.substeps_spinbox.setValue(1)

        self.gravity_label = QtWidgets.QLabel("Gravity:")
        self.gravity_spinbox = QtWidgets.QDoubleSpinBox()
        self.gravity_spinbox.setRange(-10.0, 10.0)
        self.gravity_spinbox.setValue(9.78)

        self.collision_checkbox = QtWidgets.QCheckBox("Collision Detection")
        self.collision_checkbox.setChecked(False)

        # solver settings preset
        self.function_combo_box = QtWidgets.QComboBox()
        self.function_combo_box.addItem("Def-Solver Fascia Settings")
        self.function_combo_box.addItem("Def-Solver Settings")
        self.function_combo_box.addItem("Def-Materials Fascia Settings")

        self.update_button = QtWidgets.QPushButton("Update")
        self.complist_dropdown = QtWidgets.QComboBox()
        self.transfer_button = QtWidgets.QPushButton("Transfer Mesh")


        # Create list boxes for listing components
        self.listbox_zattachments = QtWidgets.QListWidget()
        self.listbox_zmaterials = QtWidgets.QListWidget()
        self.listbox_ztet = QtWidgets.QListWidget()
        self.listbox_ztissue = QtWidgets.QListWidget()
        self.listbox_zbone = QtWidgets.QListWidget()  # New list box for zFiber components
        self.listbox_zfiber = QtWidgets.QListWidget()
        self.listbox_zcloth = QtWidgets.QListWidget()
        self.listbox_zloa = QtWidgets.QListWidget()  # New list box for zFiber components

        self.refresh_listboxes_button = QtWidgets.QPushButton("Refresh")
        # Enable the "Refresh" button by default
        self.refresh_listboxes_button.setEnabled(True)
        # Populate list boxes initially
        #self.refresh_comp_listboxes()


    ############# CREATE LAYOUTS


    def create_layout(self):
        main_grid_lay = QtWidgets.QGridLayout()
        # Add the Validate button on top
        main_grid_lay.addWidget(self.validate_button, 1, 0, 1, 2)

        # Creating tabs
        self.main_tab_widget = QtWidgets.QTabWidget()

        tab1_comp_grid_layout = QtWidgets.QGridLayout()

        # layout.addWidget(validate_button, 0, 0, 1, 2, QtCore.Qt.AlignTop | QtCore.Qt.AlignRight)

        # Adding left buttons
        for i, button in enumerate(self.left_buttons_widgets):
            tab1_comp_grid_layout.addWidget(button, i, 0)

        # Adding right buttons
        for i, button in enumerate(self.right_buttons_widgets):
            tab1_comp_grid_layout.addWidget(button, i, 1)

        # Add tab1_layout to the first tab
        tab1_comp_widget = QtWidgets.QWidget()
        tab1_comp_widget.setLayout(tab1_comp_grid_layout)
        self.main_tab_widget.addTab(tab1_comp_widget, "CREATE")

        # Setup TabWidget with mainLay Layout
        main_grid_lay.addWidget(self.main_tab_widget, len(self.left_buttons) + 2, 0, 1, 2)

        # Creating tabs for checkboxes
        tab1_checkboxes_grid_layout = QtWidgets.QGridLayout()

        #Create checkboxes functions
        checkbox_to_function = {
            "zTet": "zSolver1Shape.showTetMeshes",
            "zTissues": self.toggle_zivatissue,
            "zFibers": "zSolver1Shape.showMuscleFibers",
            "zConstraints": "zSolver1Shape.showAttachments",
            "zSstaticStrain": "zSolver1Shape.showAttachments",
            "zSolver": "zSolver1.enable",
            "zCollide": "zSolver1Shape.showCollisions",
        }

        checkboxes_layout = QtWidgets.QGridLayout()
        # checkboxes_layout.setStyleSheet("font-weight: bold; color: darkblue; border: 2px ridge #darkgrey; border-radius: 4px 4px 4px 4px; text-shadow: 1px 1px 2px #000000;")
        checkboxes_layout.setRowMinimumHeight(0, 20)

        for i, (checkbox_name, action) in enumerate(checkbox_to_function.items()):
            checkbox = QtWidgets.QCheckBox(checkbox_name)
            checkbox.setChecked(True)
            # Connect to the class method
            checkbox.stateChanged.connect(
                partial(self.on_checkbox_state_changed, action)
            )
            checkboxes_layout.addWidget(
                checkbox, i // 2, i % 2, QtCore.Qt.AlignTop)

        tab1_checkboxes_grid_layout.addLayout(checkboxes_layout, len(
            self.left_buttons) + 0, 0, 1, 2)
        tab1_checkboxes_spacer_item = QtWidgets.QSpacerItem(
            20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding
        )
        tab1_checkboxes_grid_layout.addItem(tab1_checkboxes_spacer_item, len(self.left_buttons) + 1, 0, 1, 2)
        tab2_comp_widget = QtWidgets.QWidget()
        tab2_comp_widget.setLayout(tab1_checkboxes_grid_layout)
        self.main_tab_widget.addTab(tab2_comp_widget, "SHOW")


        #=============================================================

        # # Creating tabs for checkboxes
        # self.checkboxes_tab_widget = QtWidgets.QTabWidget()
        # self.checkboxes_tab_widget.setStyleSheet("font-weight: bold; color: darkblue; border: 2px ridge #darkgrey; border-radius: 4px 4px 4px 4px; text-shadow: 1px 1px 2px #000000;")

        # # Creating tabs for checkboxes
        # tab1_checkboxes_grid_layout = QtWidgets.QGridLayout()


        # #Create checkboxes functions
        # checkbox_to_function = {
        #     "zTet": "zSolver1Shape.showTetMeshes",
        #     "zTissues": self.toggle_zivatissue,
        #     "zFibers": "zSolver1Shape.showMuscleFibers",
        #     "zConstraints": "zSolver1Shape.showAttachments",
        #     "zSstaticStrain": "zSolver1Shape.showAttachments",
        #     "zSolver": "zSolver1.enable",
        #     "zCollide": "zSolver1Shape.showCollisions",
        # }

        # checkboxes_layout = QtWidgets.QGridLayout()
        # checkboxes_layout.setRowMinimumHeight(0, 20)

        # for i, (checkbox_name, action) in enumerate(checkbox_to_function.items()):
        #     checkbox = QtWidgets.QCheckBox(checkbox_name)
        #     checkbox.setChecked(True)
        #     # Connect to the class method
        #     checkbox.stateChanged.connect(
        #         partial(self.on_checkbox_state_changed, action)
        #     )
        #     checkboxes_layout.addWidget(
        #         checkbox, i // 2, i % 2, QtCore.Qt.AlignTop)

        # tab1_checkboxes_grid_layout.addLayout(checkboxes_layout, len(
        #     self.left_buttons) + 0, 0, 1, 2)

        # tab1_checkboxes_grid_layout.addWidget(self.label_attachments , len(self.left_buttons) + 2 , 0 , 1 , 2)
        # # Add the checkboxes to the comp_tab1_layout
        # tab1_checkboxes_grid_layout.addWidget(self.sliding_radio, len(self.left_buttons) + 3, 0)
        # tab1_checkboxes_grid_layout.addWidget(self.fixed_radio, len(self.left_buttons) + 3, 1)

        # tab1_checkboxes_grid_layout.addWidget(self.constraint_button, len(self.left_buttons) + 4, 0)

        # self.spin_box = QtWidgets.QDoubleSpinBox()
        # self.spin_box.setDecimals(3)  # Set decimals to 3 places
        # self.spin_box.setMinimum(0)
        # self.spin_box.setMaximum(10)
        # self.spin_box.setSingleStep(0.01)
        # self.spin_box.setValue(0.25)  # Set the default value to 0.25

        # tab1_checkboxes_grid_layout.addWidget(self.spin_box, len(self.left_buttons) + 4, 1)


        # # Add tab1_layout to the first tab
        # tab1_checkboxes_widget = QtWidgets.QWidget()
        # tab1_checkboxes_widget.setLayout(tab1_checkboxes_grid_layout)
        # self.checkboxes_tab_widget.addTab(tab1_checkboxes_widget, "VISUAL AND ATTACHMENTS")
        

        # # Setup TabWidget with mainLay Layout
        # main_grid_lay.addWidget(self.checkboxes_tab_widget, len(self.left_buttons) + 3, 0, 1, 2)

        #=============================================================

        # Delete Component in mainLay Layout
        main_grid_lay.addWidget(self.delete_component_button,len(self.left_buttons) + 4, 0)
        main_grid_lay.addWidget(self.component_dropdown, len(self.left_buttons) + 4, 1)

        #============= COMPONENT TAB LAYOUT

        # Creating tabs
        self.tab_widget = QtWidgets.QTabWidget()

        #============= Tab 1
        tab1_layout = QtWidgets.QGridLayout()
        # ... (add other widgets to tab1_layout as needed)
        tab1_layout.addWidget(self.label_attachments , len(self.left_buttons) + 1 , 0 , 1 , 2)
        # Add the checkboxes to the comp_tab1_layout
        tab1_layout.addWidget(self.sliding_radio, len(self.left_buttons) + 2, 0)
        tab1_layout.addWidget(self.fixed_radio, len(self.left_buttons) + 2, 1)
        tab1_layout.addWidget(self.constraint_button, len(self.left_buttons) + 3, 0)

        self.spin_box = QtWidgets.QDoubleSpinBox()
        self.spin_box.setDecimals(3)  # Set decimals to 3 places
        self.spin_box.setMinimum(0)
        self.spin_box.setMaximum(10)
        self.spin_box.setSingleStep(0.01)
        self.spin_box.setValue(0.25)  # Set the default value to 0.25

        tab1_layout.addWidget(self.spin_box, len(self.left_buttons) + 3, 1)
        tab1_layout.addWidget(self.label_tet_info , len(self.left_buttons) + 4, 0, 1, 2)

        # New slider layout and connections
        self.slider_layout = QtWidgets.QHBoxLayout()
        self.slider_layout.addWidget(self.increase_button)
        self.slider_layout.addWidget(self.slider)
        self.slider_layout.addWidget(self.reduce_button)

        # Add the label for the slider
        self.slider_label.setStyleSheet("font-weight: bold; font-size: 12px; color: red; border: 2px ridge #ff0000; border-radius: 100px 10px 10px 10px; filter: drop-shadow(5px 5px 10px #000000);")
        #self.slider_label.setFrameStyle(QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken)
        tab1_layout.addWidget(self.slider_label, len(self.left_buttons) + 5, 0, 1, 2, alignment=QtCore.Qt.AlignHCenter)
        #self.slider_label.setStylesheet("text-transform: capitalize;")
        tab1_layout.addLayout(self.slider_layout, len(self.left_buttons) + 6, 0, 1, 2, alignment=QtCore.Qt.AlignTop)
        tab1_layout.addWidget(self.label_zattach_drive , len(self.left_buttons) + 7, 0, 1, 2)

        # Add three_column_layout and qv_layout to the first tab
        label_column_layout = QtWidgets.QHBoxLayout()
        label_column_layout.addWidget(self.tissue_label, alignment=QtCore.Qt.AlignBottom)
        label_column_layout.addWidget(self.bones_label, alignment=QtCore.Qt.AlignBottom)
        tab1_layout.addLayout(label_column_layout, len(self.left_buttons) + 8, 0, alignment=QtCore.Qt.AlignBottom)

        # Add QHLayout with two spinner boxes
        qh_spinbox_layout = QtWidgets.QHBoxLayout()
        self.spin_box_tissue = QtWidgets.QDoubleSpinBox()
        self.spin_box_tissue.setDecimals(3)
        self.spin_box_tissue.setMinimum(0)
        self.spin_box_tissue.setMaximum(10)
        self.spin_box_tissue.setSingleStep(0.01)
        self.spin_box_tissue.setValue(0.1)
        qh_spinbox_layout.addWidget(self.spin_box_tissue)

        self.spin_box_bone = QtWidgets.QDoubleSpinBox()
        self.spin_box_bone.setDecimals(3)
        self.spin_box_bone.setMinimum(0)
        self.spin_box_bone.setMaximum(10)
        self.spin_box_bone.setSingleStep(0.01)
        self.spin_box_bone.setValue(0.25)
        qh_spinbox_layout.addWidget(self.spin_box_bone)

        tab1_layout.addLayout(qh_spinbox_layout, len(self.left_buttons) + 9, 0, alignment=QtCore.Qt.AlignTop)
        # Add QHLayout with two radio button
        qh_radio_layout = QtWidgets.QHBoxLayout()
        qh_radio_layout.addWidget(self.sliding_radio_par)
        qh_radio_layout.addWidget(self.fixed_radio_par)
        tab1_layout.addLayout(qh_radio_layout, len(self.left_buttons) + 9, 1, alignment=QtCore.Qt.AlignTop)
        tab1_layout.addWidget(self.zattach_parent_child_button, len(self.left_buttons) + 10, 0)

        qv_button_layout = QtWidgets.QVBoxLayout()
        qv_button_layout.addWidget(self.zattach_all_objects_button)
        tab1_layout.addLayout(qv_button_layout, len(self.left_buttons) + 10, 1, alignment=QtCore.Qt.AlignTop)

        # Add Refresh button and dropdown
        tab1_layout.addWidget(self.refresh_button, len(self.left_buttons) + 11, 0)
        tab1_layout.addWidget(self.dropdown, len(self.left_buttons) + 11, 1)

        # Add numeric textboxes and Apply button
        tab1_layout.addWidget(self.textbox1, len(self.left_buttons) + 12, 0)
        tab1_layout.addWidget(self.textbox2, len(self.left_buttons) + 12, 1)
        tab1_layout.addWidget(self.apply_button, len(self.left_buttons) + 13, 0, 1, 2)
        tab1_layout_spacer_item = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        tab1_layout.addItem(tab1_layout_spacer_item, len(self.left_buttons) + 14, 0, 1, 2)

        # Add tab1_layout to the first tab
        tab1_widget = QtWidgets.QWidget()
        tab1_widget.setLayout(tab1_layout)
        self.tab_widget.addTab(tab1_widget, "Edits")

        #============= Tab panel
        tab_panel_grid_layout = QtWidgets.QGridLayout()
        tab_panel_grid_layout.addWidget(self.refresh_listboxes_button , 1 , 0)
        panel_qvlayout = QtWidgets.QVBoxLayout()
        panel_qvlayout.addWidget(self.listbox_zattachments)
        panel_qvlayout.addWidget(self.listbox_zmaterials)
        panel_qvlayout.addWidget(self.listbox_zfiber)
        panel_qvlayout.addWidget(self.listbox_zbone)
        panel_qvlayout.addWidget(self.listbox_zloa)
        panel_qvlayout.addWidget(self.listbox_zcloth)
        panel_qvlayout.addWidget(self.listbox_ztet)
        panel_qvlayout.addWidget(self.listbox_ztissue)
        tab_panel_grid_layout.addLayout(panel_qvlayout , 2 , 0)

        # Add tab2_layout to the second tab
        tab_panel_widget = QtWidgets.QWidget()
        tab_panel_widget.setLayout(tab_panel_grid_layout)
        self.tab_widget.addTab(tab_panel_widget, "Panel")

        #============= Tab 2

        tab2_layout = QtWidgets.QGridLayout()
        # Add create_sets_layout to the second tab
        self.create_sets_layout = QtWidgets.QHBoxLayout()
        self.create_sets_layout.addWidget(self.create_sets_button, alignment=QtCore.Qt.AlignTop)
        self.create_sets_layout.addWidget(self.create_sets_dropdown)
        tab2_layout.addLayout(self.create_sets_layout, 1, 0, 1, 2, alignment=QtCore.Qt.AlignTop)
        tab2_layout.addWidget(self.blendshape, 2, 0)
        tab2_layout.addWidget(self.duplicate, 2, 1)
        tab2_layout.addWidget(self.smooth_slider, 3, 0)
        tab2_layout.addWidget(self.smooth_spin_box, 3, 1)
        tab2_layout.addWidget(self.paint_button, 4, 0)
        tab2_layout.addWidget(self.smooth_apply_button, 4, 1)
        tab2_layout.addWidget(self.randomize_clr_button, 5, 0)
        tab2_layout_spacer_item = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        tab2_layout.addItem(tab2_layout_spacer_item, 6, 0, 1, 2)

        # Add tab2_layout to the second tab
        tab2_widget = QtWidgets.QWidget()
        tab2_widget.setLayout(tab2_layout)
        self.tab_widget.addTab(tab2_widget, "General")

        # Tab 3
        tab3_layout = QtWidgets.QGridLayout()

        self.create_utils_layout = QtWidgets.QHBoxLayout()
        self.create_utils_layout.addWidget(self.mirror_lr)
        self.create_utils_layout.addWidget(self.mirror)
        tab3_layout.addLayout(self.create_utils_layout, 1, 0, 1, 2)
        tab3_layout.addWidget(self.complist_dropdown, 2, 0, 1, 2)
        tab3_layout.addWidget(self.update_button, 3, 0)
        tab3_layout.addWidget(self.transfer_button, 3, 1)
        tab3_layout_spacer_item = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum,QtWidgets.QSizePolicy.Expanding)
        tab3_layout.addItem(tab3_layout_spacer_item, 4, 0, 1, 2)

        # Add tab3_layout to the third tab
        tab3_widget = QtWidgets.QWidget()
        tab3_widget.setLayout(tab3_layout)
        self.tab_widget.addTab(tab3_widget, "Utils")

        # Tab 3
        tab4_layout = QtWidgets.QGridLayout()
        tab4_layout.addWidget(self.collision_checkbox, 0, 0)
        tab4_layout.addWidget(self.start_frame_label, 1, 0)
        tab4_layout.addWidget(self.start_frame_spinbox, 1, 1)
        tab4_layout.addWidget(self.collision_space_label, 2, 0)
        tab4_layout.addWidget(self.collision_space_lineedit, 2, 1)
        tab4_layout.addWidget(self.newton_iteration_label, 3, 0)
        tab4_layout.addWidget(self.newton_iteration_spinbox, 3, 1)
        tab4_layout.addWidget(self.substeps_label, 4, 0)
        tab4_layout.addWidget(self.substeps_spinbox, 4, 1)
        tab4_layout.addWidget(self.gravity_label, 5, 0)
        tab4_layout.addWidget(self.gravity_spinbox, 5, 1)
        tab4_layout.addWidget(self.function_combo_box, 7, 0, 1, 2)

        tab4_layout_spacer_item = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        tab4_layout.addItem(tab4_layout_spacer_item, 8, 0, 1, 2)

        # Add tab3_layout to the third tab
        tab4_widget = QtWidgets.QWidget()
        tab4_widget.setLayout(tab4_layout)
        self.tab_widget.addTab(tab4_widget, "Solver")

        # Setup TabWidget with mainLay Layout
        main_grid_lay.addWidget(self.tab_widget , len(self.left_buttons) + 5, 0, 1, 2)

        ##########################################################################
        # style buttons for ui style
        self.style_dropdown = QtWidgets.QComboBox(self)
        self.style_load_button = QtWidgets.QPushButton("Load Style", self)
        main_grid_lay.addWidget(self.style_dropdown, len(self.left_buttons) + 6, 0)
        main_grid_lay.addWidget(self.style_load_button, len(self.left_buttons) + 6, 1)
        self.style_load_button.clicked.connect(self.load_style)
        ##########################################################################

        #spacer to align everything on top
        spacer_item = QtWidgets.QSpacerItem(20, 50, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        main_grid_lay.addItem(spacer_item, len(self.left_buttons) + 7, 0, 1, 2)
        # main_grid_lay.addLayout(comp_tab1_layout , 2 , 0 , 1 , 2)
        self.setLayout(main_grid_lay)

    ############# CREATE CONNECTIONS 

    def create_connections(self):
        for button in self.left_buttons_widgets + self.right_buttons_widgets:
            button.clicked.connect(self.on_button_click)
        self.constraint_button.clicked.connect(
            lambda: zi.create_ziva_attachment(
                self.spin_box.value(), self.get_radio_value()
            )
        )
        self.delete_component_button.clicked.connect(
            lambda: zi.delete_component_action(
                self.component_dropdown.currentText())
        )
        self.zattach_parent_child_button.clicked.connect(
            lambda: zi.create_zattachments_for_selected(
                self.spin_box_tissue.value(),
                self.spin_box_bone.value(),
                self.get_radio_par_value(),
            )
        )
        self.zattach_all_objects_button.clicked.connect(
            lambda: zi.zattach_all_objects_button_one_time(
                self.spin_box_tissue.value(), self.spin_box_bone.value()
            )
        )
        # self.apply_tissue_percentage_button.clicked.connect(lambda: zi.modify_ztet_size(self.slider.value()))
        self.increase_button.clicked.connect(
            lambda: zi.change_ztet_size(+((self.slider.value())))
        )
        self.reduce_button.clicked.connect(
            lambda: zi.change_ztet_size(-((self.slider.value())))
        )
        self.create_sets_button.clicked.connect(self.create_sets_action)
        # self.create_sets_dropdown.currentIndexChanged.connect(self.on_create_sets_index_changed)
        self.blendshape.clicked.connect(lambda: zi.create_blendshape())
        self.duplicate.clicked.connect(lambda: zi.create_duplicate_clean_mesh())
        self.mirror.clicked.connect(lambda: zi.create_zMirror())
        self.mirror_lr.clicked.connect(lambda: zi.create_zMirror_lr())

        # Connect the clicked signals of radio buttons to the print_radio_values function
        self.sliding_radio.clicked.connect(
            lambda: self.print_radio_values("Sliding"))
        self.fixed_radio.clicked.connect(
            lambda: self.print_radio_values("Fixed"))
        self.sliding_radio_par.clicked.connect(
            lambda: self.print_radio_par_values("Sliding")
        )
        self.fixed_radio_par.clicked.connect(
            lambda: self.print_radio_par_values("Fixed")
        )
        self.refresh_button.clicked.connect(self.refresh_action)
        # Connect dropdown change to a function
        self.dropdown.currentIndexChanged.connect(
            self.select_object_from_dropdown)
        # Connect Apply button to a function
        self.apply_button.clicked.connect(lambda: zi.apply_zpaint_attachments(self.textbox1.value(), self.textbox2.value()))
        self.validate_button.clicked.connect(lambda: valid.run_check_points_ui())
        self.paint_button.clicked.connect(lambda: zi.paint_tool())
        self.smooth_slider.valueChanged.connect(self.update_smooth_spinbox)
        self.smooth_spin_box.valueChanged.connect(self.update_smooth_slider)
        self.smooth_apply_button.clicked.connect(lambda: zi.apply_paint_operation(self.smooth_slider.value())
        )
        self.randomize_clr_button.clicked.connect(lambda: zi.randomize_mesh_colors())

        # connection for solver widgets
        self.start_frame_spinbox.valueChanged.connect(self.update_solver_settings)
        self.collision_space_lineedit.textChanged.connect(self.update_solver_settings)
        self.newton_iteration_spinbox.valueChanged.connect(self.update_solver_settings)
        self.substeps_spinbox.valueChanged.connect(self.update_solver_settings)
        self.gravity_spinbox.valueChanged.connect(self.update_solver_settings)
        self.collision_checkbox.stateChanged.connect(self.update_collision_detection)

        # apply solver settings
        self.function_combo_box.currentIndexChanged.connect(self.apply_selected_function)
        self.complist_dropdown.currentIndexChanged.connect(self.select_comp_from_dropdown)

        self.update_button.clicked.connect(self.populate_comp_dropdown)
        self.transfer_button.clicked.connect(lambda: zi.ziva_cloth_transfer())

        self.refresh_listboxes_button.clicked.connect(self.refresh_comp_listboxes)

        # Connect selection changed signal
        self.listbox_zattachments.itemSelectionChanged.connect(lambda: self.select_component(self.listbox_zattachments))
        self.listbox_zmaterials.itemSelectionChanged.connect(lambda: self.select_component(self.listbox_zmaterials))
        self.listbox_ztet.itemSelectionChanged.connect(lambda: self.select_component(self.listbox_ztet))
        self.listbox_ztissue.itemSelectionChanged.connect(lambda: self.select_component(self.listbox_ztissue))
        self.listbox_zbone.itemSelectionChanged.connect(lambda: self.select_component(self.listbox_zbone))
        self.listbox_zfiber.itemSelectionChanged.connect(lambda: self.select_component(self.listbox_zfiber))
        self.listbox_zcloth.itemSelectionChanged.connect(lambda: self.select_component(self.listbox_zcloth))
        self.listbox_zloa.itemSelectionChanged.connect(lambda: self.select_component(self.listbox_zloa))

        # Initially, hide the additional list boxes
        self.set_additional_listboxes_visibility(False)
        self.populate_style_dropdown()

    def populate_style_dropdown(self):
        path = cmds.internalVar(usd=True)
        directory_path = r'{}z_toolbox/style/'.format(path)
        # List only qss files
        qss_files = [f for f in os.listdir(directory_path) if f.endswith('.qss')]
        # Populate the dropdown with qss files
        self.style_dropdown.addItems(qss_files)

    def load_style(self):
        path = cmds.internalVar(usd=True)
        selected_style = self.style_dropdown.currentText()
        if selected_style:
            style_path = os.path.join(
                r'{}z_toolbox/style/'.format(path), selected_style)
            with open(style_path, "r") as ss:
                self.setStyleSheet(ss.read())

    def set_additional_listboxes_visibility(self, visible):
        for listbox in [self.listbox_zattachments, self.listbox_zmaterials, self.listbox_ztissue, self.listbox_zbone, self.listbox_zfiber, self.listbox_zcloth, self.listbox_zloa]:
            listbox.setVisible(visible)

    def select_component(self, list_box):
        """
        Select the Ziva component in Maya corresponding to the selected item in the list box.
        Args:
            list_box (QtWidgets.QListWidget): The list box containing the selected item.
        """
        # print(list_box)
        selected_items = list_box.selectedItems()
        if not selected_items:
            return  # No item selected
        selected_item = selected_items[0].text()
        cmds.select(selected_item)
        # Clear selection in other list boxes
        other_list_boxes = [box for box in [self.listbox_zattachments, self.listbox_zmaterials, self.listbox_ztet, self.listbox_ztissue, self.listbox_zcloth, self.listbox_zbone, self.listbox_zfiber, self.listbox_zloa] if box != list_box]
        for other_list_box in other_list_boxes:
            other_list_box.clearSelection()

    def populate_list_box(self, list_box, items):
        """
        Populate a QListWidget with the given items.
        Args:
            list_box (QtWidgets.QListWidget): The list box to populate.
            items (list): List of items to add to the list box.
        """
        list_box.addItems(items)

    def refresh_comp_listboxes(self):
        # Clear existing items in list boxes
        self.listbox_zattachments.clear()
        self.listbox_zmaterials.clear()
        self.listbox_ztet.clear()
        self.listbox_ztissue.clear()
        self.listbox_zbone.clear()
        self.listbox_zfiber.clear()
        self.listbox_zcloth.clear()
        #self.listbox_zloa.clear()

        selected_objects = cmds.ls(selection=True)

        # Check if there is exactly one selected object
        if not selected_objects or len(selected_objects) != 1:
            cmds.warning("Please select exactly one object.")
            self.set_additional_listboxes_visibility(False)
            return

        selected_object = selected_objects[0]
        shape_nodes = cmds.listRelatives(selected_object, shapes=True, fullPath=True) or []

        if not shape_nodes:
            cmds.warning(f"No shape nodes found for {selected_object}.")
            return

        # Assuming that the first shape node is the main shape for simplicity
        main_shape_node = shape_nodes[0]

        # Get Ziva components associated with the main shape node
        z_components = zi.get_z_components(main_shape_node)
        print(z_components)

        # Populate list boxes with zComponents
        #self.populate_list_box(self.listbox_zattachments, z_components.get("zAttachment", []))
        #self.populate_list_box(self.listbox_zmaterials, z_components.get("zMaterial", []))
        self.populate_list_box(self.listbox_ztet, z_components.get("zTet", []))
        # self.populate_list_box(self.listbox_ztissue, z_components.get("zTissue", []))
        # self.populate_list_box(self.listbox_zbone, z_components.get("zBone", []))
        # self.populate_list_box(self.listbox_zfiber, z_components.get("zFiber", []))
        # self.populate_list_box(self.listbox_zcloth, z_components.get("zCloth", []))
        # self.populate_list_box(self.listbox_zloa, z_components.get("zLineOfAction", []))

        # Check for additional components and show corresponding list boxes
        additional_components = {
            "zAttachment": self.listbox_zattachments,
            "zMaterial": self.listbox_zmaterials,
            "zTissue": self.listbox_ztissue,
            "zBone": self.listbox_zbone,
            "zFiber": self.listbox_zfiber,
            "zCloth": self.listbox_zcloth,
            #"zLineOfAction": self.listbox_zloa,
        }

        for component_type, listbox in additional_components.items():
            component_nodes = cmds.zQuery(type=component_type)
            print (component_nodes)
            if component_nodes:
                listbox.setVisible(True)
                self.populate_list_box(listbox, component_nodes)
            else:
                listbox.setVisible(False)

    def select_comp_from_dropdown(self):
        # Select the object based on the dropdown value
        selected_attachment = self.complist_dropdown.currentText()
        if selected_attachment:
            cmds.select(selected_attachment)
            print(f"Selected object: {selected_attachment}")

    def populate_comp_dropdown(self):
        # Populate the dropdown with zAttachments from the selected mesh
        attachments_list = zi.ziva_get_mesh_nodes()
        self.complist_dropdown.clear()
        self.complist_dropdown.addItems(attachments_list)

    def apply_selected_function(self):
        selected_function = self.function_combo_box.currentText()
        if selected_function == "Def-Solver Fascia Settings":
            self.default_fascia_settings()
        elif selected_function == "Def-Solver Settings":
            self.default_settings()
        elif selected_function == "Def-Materials Fascia Settings":
            self.default_zcloth_fascia_material()

    def default_fascia_settings(self):
        solver_name = "zSolver1"
        cmds.setAttr("{}.collisionDetection".format(solver_name), 1)
        cmds.setAttr("{}.startFrame".format(solver_name), -20)
        cmds.setAttr("{}.collisionPointSpacing".format(solver_name), 0.003)
        cmds.setAttr("{}.maxNewtonIterations".format(solver_name), 2)
        cmds.setAttr("{}.substeps".format(solver_name), 4)
        cmds.setAttr("{}.gravityY".format(solver_name), 0)
        self.start_frame_spinbox.setValue(-20)
        self.collision_space_lineedit.setText("0.003")
        self.newton_iteration_spinbox.setValue(2)
        self.substeps_spinbox.setValue(4)
        self.gravity_spinbox.setValue(0)
        self.collision_checkbox.setChecked(True)

    def default_settings(self):
        solver_name = "zSolver1"
        cmds.setAttr("{}.collisionDetection".format(solver_name), 0)
        cmds.setAttr("{}.startFrame".format(solver_name), 1)
        cmds.setAttr("{}.collisionPointSpacing".format(solver_name), 0.1)
        cmds.setAttr("{}.maxNewtonIterations".format(solver_name), 5)
        cmds.setAttr("{}.substeps".format(solver_name), 1)
        cmds.setAttr("{}.gravityY".format(solver_name), 0)
        self.start_frame_spinbox.setValue(1)
        self.collision_space_lineedit.setText("0.1")
        self.newton_iteration_spinbox.setValue(5)
        self.substeps_spinbox.setValue(1)
        self.gravity_spinbox.setValue(9.78)
        self.collision_checkbox.setChecked(False)

    def default_zcloth_fascia_material(self):
        selected = cmds.ls(sl=True)
        solver_name = cmds.zQuery(selected[0], type="zMaterial")[0]
        cmds.setAttr("{}.restScale".format(solver_name), 0.9)
        cmds.setAttr("{}.pressure".format(solver_name), 100)
        cmds.setAttr("{}.surfaceTension".format(solver_name), 1)

    def update_solver_settings(self):
        solver_name = "zSolver1"
        start_frame_value = self.start_frame_spinbox.value()
        collision_space_value = float(self.collision_space_lineedit.text())
        newton_iteration_value = self.newton_iteration_spinbox.value()
        substeps_value = self.substeps_spinbox.value()
        gravity_value = self.gravity_spinbox.value()
        cmds.setAttr("{}.startFrame".format(solver_name), start_frame_value)
        cmds.setAttr(
            "{}.collisionPointSpacing".format(
                solver_name), collision_space_value
        )
        cmds.setAttr(
            "{}.maxNewtonIterations".format(
                solver_name), newton_iteration_value
        )
        cmds.setAttr("{}.substeps".format(solver_name), substeps_value)
        cmds.setAttr("{}.gravityY".format(solver_name), gravity_value)

    def update_collision_detection(self, state):
        # This function remains empty for now
        solver_name = "zSolver1"
        collision_detection_value = 1 if self.collision_checkbox.isChecked() else 0
        print("Collision Detection Checkbox Value:", collision_detection_value)
        cmds.setAttr(
            "{}.collisionDetection".format(
                solver_name), collision_detection_value
        )
        pass

    def update_smooth_spinbox(self, value):
        self.smooth_spin_box.setValue(value)

    def update_smooth_slider(self, value):
        self.smooth_slider.setValue(value)

    def get_radio_value(self):
        if self.sliding_radio.isChecked():
            return 2
        elif self.fixed_radio.isChecked():
            return 1
        else:
            return 0

    def get_radio_par_value(self):
        if self.sliding_radio_par.isChecked():
            return 2
        elif self.fixed_radio_par.isChecked():
            return 1
        else:
            return 0

    def print_radio_values(self, value):
        print(f"Selected radio button value: {value}")
        return

    def print_radio_par_values(self, value):
        print(f"Selected radio button value: {value}")
        return

    def on_button_click(self):
        sender_button = self.sender()
        button_text = sender_button.text()

        if button_text == "Create Bones":
            zi.create_ziva_bone()
        elif button_text == "Create Bones_w/BS":
            zi.create_ziva_BS__bone()
        elif button_text == "Create Tissues":
            zi.create_ziva_tissue()
        elif button_text == "Create Fiber":
            zi.create_ziva_fiber()
        elif button_text == "Create LOA":
            zi.create_ziva_line_of_action()
        elif button_text == "Create Rivets":
            zi.create_ziva_rivet_to_bone()
        elif button_text == "Create FibreLOA":
            zi.create_ziva_muscle_loa()
        elif button_text == "FibreLOA Remap":
            zi.create_point_on_curve_and_remap()
        elif button_text == "Create Cloth":
            zi.create_ziva_cloth()
        elif button_text == "Create Materials":
            zi.create_ziva_zmaterials()

    def create_sets_action(self):
        selected_set = self.create_sets_dropdown.currentText()
        index_mapping = {
            "Set zBone": 0,
            "Set zTissue": 1,
            "Set zFiber": 2,
            "Set zAttachment": 3,
            "Set zRivet": 4,
            "Set zCloth": 5,
            "Set zLineOfAction": 6,
            "Set Bone Mesh": 7,
            "Set Tissue Mesh": 8,
            "Set LineOfAction Curves": 9,
        }
        index = index_mapping.get(selected_set)
        if index is not None:
            print(f"index = {index} & selected_set = {selected_set}")
            zi.sets_create_by_index(index)
        else:
            print(f"No function mapped for '{selected_set}'.")

    def update_slider_label(self, value):
        # Update the text of the label with the current slider value
        self.slider_label.setText(f"Slider Value: {value}%")

    def on_checkbox_state_changed(self, action, state):
        # Perform action based on checkbox state
        if callable(action):
            action(state)
        else:
            # Assuming it's an attribute
            cmds.setAttr(action, int(state == QtCore.Qt.Checked))

    def refresh_action(self):
        # Populate the dropdown when the Refresh button is clicked
        self.populate_dropdown()
        print("Refreshing...")

    def populate_dropdown(self):
        # Populate the dropdown with zAttachments from the selected mesh
        attachments_list = zi.get_zattachments_from_selected_mesh()
        self.dropdown.clear()
        self.dropdown.addItems(attachments_list)

    def select_object_from_dropdown(self):
        # Select the object based on the dropdown value
        selected_attachment = self.dropdown.currentText()
        if selected_attachment:
            cmds.select(selected_attachment)
            print(f"Selected object: {selected_attachment}")

    def toggle_zivatissue(self, state):
        zTis = cmds.ls(sl=True)
        for zTis_obj in zTis:
            meshes = cmds.listRelatives(
                zTis_obj, c=True, ad=True, type="mesh") or []
            for mesh in meshes:
                parent_objs = cmds.listRelatives(mesh, p=True) or []
                for parent_obj in parent_objs:
                    zTiss = cmds.zQuery(parent_obj, type="zTissue")
                    if zTiss:
                        cmds.setAttr(
                            zTiss[0] +
                            ".enable", int(state == QtCore.Qt.Checked)
                        )


if __name__ == "__main__":
    path = cmds.internalVar(usd=True)
    try:
        win.close()
        # deleteLater method keeps the window hidden while closing the instance
        # it helps to store the values of the instance in the maya session
        win.deleteLater()
    except:
        pass
    win = Window()
    # win.setStyle(QtWidgets.QSQStyleFactory.create('Cleanlooks'))
    mystyle = "{}z_toolbox/style/mix.qss".format(path)
    # mystyle = "{}z_toolbox/style/macos.qss".format(path)
    with open(mystyle, "r") as ss:
        win.setStyleSheet(ss.read())
    win.show(dockable=True, floating=False, area="right")
