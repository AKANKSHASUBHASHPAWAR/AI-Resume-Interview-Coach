import streamlit as st

def apply_custom_css():
    """
    Applies modern, high-conversion UI styling to the Streamlit app.
    Injects Google Fonts, card styling, gradients, and custom badge components.
    Fully responsive with adaptive dark mode contrast.
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

        /* Global Font & Baseline */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
            letter-spacing: -0.01em;
            font-size: 15px;
        }

        /* Prevent Streamlit Main Container Oversizing & Excessive Top Padding */
        .main .block-container {
            max-width: 1200px !important;
            padding-top: 1.5rem !important;
            padding-bottom: 3rem !important;
            padding-left: 2rem !important;
            padding-right: 2rem !important;
        }

        /* Ensure Sidebar is visible and well-proportioned */
        section[data-testid="stSidebar"] {
            min-width: 310px !important;
            max-width: 360px !important;
        }

        section[data-testid="stSidebar"] .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            padding-left: 1.25rem !important;
            padding-right: 1.25rem !important;
        }

        /* Always show the sidebar expand/collapse chevron control */
        button[data-testid="stSidebarCollapseButton"],
        button[data-testid="stSidebarHeaderChevron"],
        button[data-testid="stSidebarCollapsedControl"],
        [data-testid="stSidebarCollapsedControl"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            z-index: 999999 !important;
        }

        /* Gradient Main Header - Proportional scaling */
        .main-header {
            background: linear-gradient(135deg, #4338ca 0%, #3b82f6 50%, #06b6d4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.1rem;
            font-weight: 800;
            margin-bottom: 0.25rem;
            text-align: center;
            letter-spacing: -0.025em;
            line-height: 1.2;
        }
        
        .sub-header {
            font-size: 0.95rem;
            color: #64748b;
            text-align: center;
            margin-bottom: 1.4rem;
            font-weight: 400;
            max-width: 820px;
            margin-left: auto;
            margin-right: auto;
            line-height: 1.4;
        }

        /* Glassmorphic Info Card */
        .info-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.25rem 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04), 0 2px 4px -2px rgba(0, 0, 0, 0.04);
            margin-bottom: 1.25rem;
            transition: all 0.25s ease;
            color: #1e293b;
        }
        .info-card:hover {
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.04);
            border-color: #cbd5e1;
        }

        /* Candidate Header Card */
        .candidate-hero {
            background: linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%);
            border: 1px solid #dbeafe;
            border-radius: 16px;
            padding: 1.5rem 1.75rem;
            margin-bottom: 1.5rem;
            color: #1e293b;
        }

        /* Candidate Name Highlight */
        .candidate-name {
            color: #2563eb !important;
            background: linear-gradient(135deg, #1d4ed8 0%, #4f46e5 50%, #06b6d4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            display: inline-block;
            letter-spacing: -0.02em;
        }

        /* Step Progression & Connected Navigation */
        .step-tracker-bar {
            display: flex;
            align-items: center;
            justify-content: flex-start;
            flex-wrap: wrap;
            gap: 0.45rem;
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 0.6rem 0.9rem;
            margin-bottom: 1.25rem;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        }

        .step-pill {
            display: inline-flex;
            align-items: center;
            font-size: 0.78rem;
            font-weight: 600;
            padding: 0.35rem 0.75rem;
            border-radius: 9999px;
            color: #64748b;
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            white-space: nowrap;
            transition: all 0.2s ease;
        }

        .step-pill-active {
            color: #ffffff !important;
            background: linear-gradient(135deg, #4f46e5 0%, #2563eb 100%) !important;
            border-color: #4338ca !important;
            box-shadow: 0 4px 8px -1px rgba(79, 70, 229, 0.35);
            font-weight: 700;
        }

        .step-pill-completed {
            color: #059669;
            background: #ecfdf5;
            border-color: #a7f3d0;
        }

        .step-nav-box {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.1rem 1.4rem;
            margin-top: 2.2rem;
            margin-bottom: 1.2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.04);
        }

        /* Categorized Skill Badges */
        .skill-badge {
            display: inline-block;
            background: #e0f2fe;
            color: #0369a1;
            padding: 0.3rem 0.75rem;
            border-radius: 9999px;
            font-size: 0.82rem;
            font-weight: 600;
            margin: 0.25rem 0.2rem;
            border: 1px solid #bae6fd;
            transition: all 0.2s ease;
        }
        .skill-badge:hover {
            background: #bae6fd;
            transform: translateY(-1px);
        }

        .badge-lang {
            background: #ede9fe;
            color: #6d28d9;
            border-color: #ddd6fe;
        }
        .badge-framework {
            background: #e0f2fe;
            color: #0369a1;
            border-color: #bae6fd;
        }
        .badge-cloud {
            background: #fef3c7;
            color: #b45309;
            border-color: #fde68a;
        }
        .badge-data {
            background: #dcfce7;
            color: #15803d;
            border-color: #bbf7d0;
        }
        .badge-ai {
            background: #fce7f3;
            color: #be185d;
            border-color: #fbcfe8;
        }
        .badge-arch {
            background: #f1f5f9;
            color: #475569;
            border-color: #e2e8f0;
        }

        /* Section Titles */
        .section-title {
            font-size: 1.45rem;
            font-weight: 700;
            color: #0f172a;
            border-bottom: 2px solid #f1f5f9;
            padding-bottom: 0.5rem;
            margin-top: 1rem;
            margin-bottom: 1.25rem;
        }

        /* Audit Status Pills */
        .status-pill-pass {
            display: inline-block;
            background: #d1fae5;
            color: #065f46;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 6px;
        }
        .status-pill-warn {
            display: inline-block;
            background: #fef3c7;
            color: #92400e;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 6px;
        }
        .status-pill-critical {
            display: inline-block;
            background: #fee2e2;
            color: #991b1b;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 6px;
        }

        /* Generation Engine Mode Pills */
        .mode-pill-ai {
            display: inline-flex;
            align-items: center;
            background: #ede9fe;
            color: #6d28d9;
            border: 1px solid #ddd6fe;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 3px 9px;
            border-radius: 9999px;
            margin-bottom: 0.5rem;
        }
        .mode-pill-offline {
            display: inline-flex;
            align-items: center;
            background: #fef3c7;
            color: #b45309;
            border: 1px solid #fde68a;
            font-size: 0.75rem;
            font-weight: 700;
            padding: 3px 9px;
            border-radius: 9999px;
            margin-bottom: 0.5rem;
        }

        /* Insights feedback boxes */
        .strength-box {
            border-left: 4px solid #10b981;
            background-color: #f0fdf4;
            padding: 0.85rem 1.1rem;
            margin-bottom: 0.75rem;
            border-radius: 0 10px 10px 0;
            font-size: 0.92rem;
            color: #065f46;
        }
        
        .missing-box {
            border-left: 4px solid #f59e0b;
            background-color: #fffbeb;
            padding: 0.85rem 1.1rem;
            margin-bottom: 0.75rem;
            border-radius: 0 10px 10px 0;
            font-size: 0.92rem;
            color: #92400e;
        }
        
        .tip-box {
            border-left: 4px solid #3b82f6;
            background-color: #eff6ff;
            padding: 0.85rem 1.1rem;
            margin-bottom: 0.75rem;
            border-radius: 0 10px 10px 0;
            font-size: 0.92rem;
            color: #1e40af;
        }

        /* Rewriter Box */
        .rewrite-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 1.2rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            transition: all 0.2s ease;
            color: #1e293b;
        }
        .rewrite-card:hover {
            border-color: #6366f1;
            box-shadow: 0 6px 12px rgba(99, 102, 241, 0.1);
        }

        /* Networking & Outreach Card */
        .outreach-card {
            background: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 14px;
            padding: 1.2rem 1.4rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            color: #1e293b;
        }

        /* STAR Score Box */
        .star-metric-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 0.75rem;
            margin: 1rem 0;
        }
        .star-metric-box {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 0.75rem 0.5rem;
            text-align: center;
            color: #1e293b;
        }

        /* Modern Buttons & Next Button UI Enhancement */
        div.stButton > button {
            border-radius: 10px;
            padding: 0.55rem 1.4rem;
            font-weight: 600;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            letter-spacing: -0.01em;
            border: 1px solid #e2e8f0;
        }

        /* Default Secondary / Action Button */
        div.stButton > button:not([kind="primary"]) {
            background: #ffffff;
            color: #334155;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03);
        }

        div.stButton > button:not([kind="primary"]):hover {
            background: #f8fafc;
            color: #1e293b;
            border-color: #cbd5e1;
            transform: translateY(-1px);
        }

        /* Primary Action Buttons */
        div.stButton > button[kind="primary"],
        button[data-testid="stBaseButton-primary"] {
            background: linear-gradient(135deg, #4f46e5 0%, #3730a3 100%) !important;
            color: #ffffff !important;
            border: none !important;
            font-weight: 700 !important;
            box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
        }

        div.stButton > button[kind="primary"]:hover,
        button[data-testid="stBaseButton-primary"]:hover {
            background: linear-gradient(135deg, #4338ca 0%, #312e81 100%) !important;
            box-shadow: 0 8px 18px rgba(79, 70, 229, 0.45) !important;
            transform: translateY(-2px) !important;
        }

        /* Next Button UI Enhancement - High Energy Gradient, Glowing Border & Hover Scale */
        button[key*="next"],
        button[key*="top_next"],
        button[key*="bottom_next"] {
            background: linear-gradient(135deg, #4f46e5 0%, #06b6d4 100%) !important;
            color: #ffffff !important;
            border: none !important;
            font-weight: 800 !important;
            font-size: 0.95rem !important;
            padding: 0.65rem 1.6rem !important;
            border-radius: 12px !important;
            box-shadow: 0 4px 15px rgba(6, 182, 212, 0.35), 0 2px 6px rgba(79, 70, 229, 0.25) !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        button[key*="next"]:hover,
        button[key*="top_next"]:hover,
        button[key*="bottom_next"]:hover {
            background: linear-gradient(135deg, #4338ca 0%, #0891b2 100%) !important;
            box-shadow: 0 8px 25px rgba(6, 182, 212, 0.55), 0 4px 12px rgba(79, 70, 229, 0.4) !important;
            transform: translateY(-2px) scale(1.02) !important;
        }

        button[key*="next"]:active,
        button[key*="top_next"]:active,
        button[key*="bottom_next"]:active {
            transform: translateY(0) scale(0.98) !important;
        }

        /* Previous Step Button - Sleek Subtle Outline */
        button[key*="prev"],
        button[key*="bottom_prev"] {
            background: #ffffff !important;
            color: #475569 !important;
            border: 1px solid #cbd5e1 !important;
            font-weight: 600 !important;
            border-radius: 12px !important;
            padding: 0.65rem 1.4rem !important;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.03) !important;
        }

        button[key*="prev"]:hover,
        button[key*="bottom_prev"]:hover {
            background: #f8fafc !important;
            color: #1e293b !important;
            border-color: #94a3b8 !important;
            transform: translateY(-1px) !important;
        }

        /* High-Contrast Dark Mode Adjustments */
        @media (prefers-color-scheme: dark) {
            div.stButton > button:not([kind="primary"]) {
                background: #1e293b;
                color: #cbd5e1;
                border-color: #334155;
            }
            div.stButton > button:not([kind="primary"]):hover {
                background: #334155;
                color: #f8fafc;
                border-color: #475569;
            }
            button[key*="prev"],
            button[key*="bottom_prev"] {
                background: #1e293b !important;
                color: #cbd5e1 !important;
                border: 1px solid #475569 !important;
            }
            button[key*="prev"]:hover,
            button[key*="bottom_prev"]:hover {
                background: #334155 !important;
                color: #f8fafc !important;
                border-color: #64748b !important;
            }

            .info-card, .rewrite-card, .outreach-card {
                background: #1e293b;
                border-color: #334155;
                color: #f1f5f9 !important;
            }
            .candidate-hero {
                background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
                border-color: #334155;
                color: #f1f5f9 !important;
            }
            .section-title {
                color: #f8fafc;
                border-bottom-color: #334155;
            }
            .strength-box {
                background-color: #062f21;
                color: #a7f3d0;
            }
            .missing-box {
                background-color: #2d1e05;
                color: #fde68a;
            }
            .tip-box {
                background-color: #0c2040;
                color: #bfdbfe;
            }
            .star-metric-box {
                background: #0f172a;
                border-color: #334155;
                color: #f1f5f9 !important;
            }
            .candidate-name {
                color: #60a5fa !important;
                background: linear-gradient(135deg, #60a5fa 0%, #a5b4fc 50%, #38bdf8 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            .step-tracker-bar {
                background: #1e293b;
                border-color: #334155;
            }
            .step-pill {
                color: #94a3b8;
                background: #0f172a;
                border-color: #334155;
            }
            .step-pill-completed {
                color: #34d399;
                background: #064e3b;
                border-color: #065f46;
            }
            .step-nav-box {
                background: #1e293b;
                border-color: #334155;
            }
            .badge-lang {
                background: #2e1065;
                color: #c4b5fd;
                border-color: #4c1d95;
            }
            .badge-framework {
                background: #082f49;
                color: #7dd3fc;
                border-color: #0369a1;
            }
            .badge-cloud {
                background: #451a03;
                color: #fde68a;
                border-color: #92400e;
            }
            .badge-data {
                background: #052e16;
                color: #86efac;
                border-color: #166534;
            }
            .badge-ai {
                background: #500724;
                color: #f472b6;
                border-color: #9d174d;
            }
            .badge-arch {
                background: #1e293b;
                color: #cbd5e1;
                border-color: #475569;
            }
        }
        </style>
        """,
        unsafe_allow_html=True
    )
