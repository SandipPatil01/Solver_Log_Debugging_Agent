# agent/troubleshooting.py

TROUBLESHOOTING_GUIDES = {
    "Numerical Singularity / Mechanism Detected": [
        {
            "title": "Check boundary conditions",
            "instruction": "Open the model and verify that the structure is properly constrained. Make sure rigid body motion is prevented in all required directions.",
            "expected": "The model should not be free to translate or rotate unintentionally."
        },
        {
            "title": "Check for disconnected nodes or elements",
            "instruction": "Inspect the mesh connectivity. Look for nodes not attached to any element or parts that are not connected to the main structure.",
            "expected": "All expected components should be connected correctly."
        },
        {
            "title": "Review contacts or joints",
            "instruction": "If the model uses contact, connectors, or joints, confirm they are defined and active correctly.",
            "expected": "The interaction definitions should prevent unintended free motion."
        },
        {
            "title": "Check for very low or zero stiffness",
            "instruction": "Review material and property definitions. Very low stiffness or missing property values can create mechanism-like behaviour.",
            "expected": "All critical components should have valid stiffness."
        }
    ],

    "Disk Space Exhausted / Scratch File Failure": [
        {
            "title": "Check free disk space",
            "instruction": "Go to the drive where the scratch folder is located and confirm there is enough free space available.",
            "expected": "There should be sufficient free space for temporary solver files."
        },
        {
            "title": "Clean temporary files",
            "instruction": "Delete old scratch, temp, or previous solver output files that are no longer needed.",
            "expected": "Unused files should be removed to recover space."
        },
        {
            "title": "Move scratch folder to a larger drive",
            "instruction": "Change the scratch or working directory to a drive with more available space.",
            "expected": "The new location should have enough capacity for the analysis."
        },
        {
            "title": "Check write permissions",
            "instruction": "Confirm that the user account running the solver has permission to write to the scratch folder.",
            "expected": "The solver should be able to create and update temporary files."
        }
    ],

    "Singular Matrix": [
        {
            "title": "Review constraints",
            "instruction": "Check whether the model has adequate supports and whether free degrees of freedom remain.",
            "expected": "The model should be stable and fully supported as intended."
        },
        {
            "title": "Check connectivity",
            "instruction": "Inspect whether all elements and nodes are connected correctly, especially at interfaces.",
            "expected": "No unintentionally disconnected parts should remain."
        },
        {
            "title": "Check material and property data",
            "instruction": "Verify that all materials and properties are assigned and not zero or invalid.",
            "expected": "Each element should have valid property data."
        }
    ]
}


def get_troubleshooting_steps(issue):
    return TROUBLESHOOTING_GUIDES.get(
        issue,
        [
            {
                "title": "Review solver message",
                "instruction": "Check the exact fatal or warning message and compare it with documented solver behaviour.",
                "expected": "You should identify the closest known issue pattern."
            },
            {
                "title": "Inspect model setup",
                "instruction": "Review boundary conditions, connectivity, materials, and solver settings.",
                "expected": "Any obvious modelling or setup issue should become visible."
            },
            {
                "title": "Escalate with evidence",
                "instruction": "If the issue remains unclear, save the log, input deck, and screenshots, and share them with an expert.",
                "expected": "You will have enough evidence for deeper debugging."
            }
        ]
    )