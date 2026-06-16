RULES = [

    {
        "keywords": ["SINGULAR MATRIX", "ZERO PIVOT"],
        "issue": "Singular Matrix",
        "cause": "Model is underconstrained or has disconnected DOFs",
        "fix": [
            "Check boundary conditions",
            "Check connectivity",
            "Remove free DOFs"
        ]
    },

    {
        "keywords": [
            "EXCESSIVE PIVOT RATIOS",
            "RIGID-BODY MODES",
            "POTENTIAL MECHANISMS",
            "SINGULAR DOF"
        ],
        "issue": "Numerical Singularity / Mechanism",
        "cause": "Model is underconstrained or contains mechanisms",
        "fix": [
            "Add proper constraints",
            "Check disconnected elements",
            "Verify contacts",
            "Remove rigid body motion"
        ]
    },

    {
        "keywords": [
            "NOT ENOUGH SPACE ON THE DISK",
            "BIOWRT",
            "SCRATCH",
            "STATUS = 112",
            "ERROR 1039 HAS OCCURRED"
        ],
        "issue": "Disk Space Exhausted / Scratch File Failure",
        "cause": (
            "Solver failed to write required scratch/output files due to insufficient "
            "disk space in the working or scratch directory."
        ),
        "fix": [
            "Free disk space on the drive used for scratch files",
            "Check scratch directory location and ensure sufficient space",
            "Redirect scratch files to a larger disk using environment variables",
            "Delete old temporary or unused solver files",
            "Ensure user has write permissions for the directory"
            "Make sure having enough disk space for the solver to write temporary files"
        ]
    }

]