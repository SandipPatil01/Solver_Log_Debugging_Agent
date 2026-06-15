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
    }

]