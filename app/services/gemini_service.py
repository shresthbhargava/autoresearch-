"""
Gemini AI Service
Handles text, image, and document processing via Gemini 1.5 Pro
"""

import os
import base64
import json
from typing import Optional
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import traceback
import os

print("GEMINI KEY FOUND:", bool(os.getenv("GEMINI_API_KEY")))
print("KEY PREFIX:", os.getenv("GEMINI_API_KEY", "")[:10])
print("KEY =", os.getenv("GEMINI_API_KEY"))
print("GOOGLE_API_KEY =", os.getenv("GOOGLE_API_KEY"))
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Use gemini-2.5-flash for multimodal support and working free tier quota
model = genai.GenerativeModel(
    model_name="gemini-2.5-flash",
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    }
)

EXTRACT_PROMPT = """You are a business analyst AI. Extract ALL key information from the following input.

Return ONLY valid JSON with this structure:
{{
  "business_name": "string or null",
  "problem_statement": "string",
  "target_users": ["list of user types"],
  "proposed_solution": "string",
  "key_features": ["list of features"],
  "tech_stack": ["list of technologies"],
  "market_size": "string or null",
  "competitors": ["list or empty"],
  "business_model": "string or null",
  "success_metrics": ["list"],
  "risks": ["list"],
  "confidence": 0.0
}}

Set confidence (0-1) based on how much usable information was found.
Input: {content}"""

BRD_PROMPT = """You are a Senior Product Manager 
with 15 years experience writing investor-grade BRDs.

Generate a COMPLETE, SPECIFIC, DETAILED Business 
Requirements Document based ONLY on this data:

{extracted_data}

CRITICAL RULES:
1. Every section must reference the SPECIFIC startup, 
   product, and market from the input data
2. NEVER use generic placeholders like "string" or 
   "list of features" — use REAL specific content
3. SWOT must be specific to THIS startup's market, 
   NOT generic business advice
4. Competitors must be REAL named companies in 
   THIS startup's industry
5. TAM/SAM/SOM must have REAL dollar values with 
   reasoning specific to this market
6. All requirements must reference actual features 
   from the input
7. User stories must use actual user types from input

For TAM/SAM/SOM format EXACTLY like this:
"TAM: $XB (reason). SAM: $XB (reason). SOM: $XM (reason)"

Return ONLY valid JSON. No markdown. No explanation.

JSON structure:
{
  "title": "BRD: [ACTUAL startup name from input]",
  "version": "1.0",
  "date": "2026-06-13",
  "executive_summary": "[3 sentences specific to THIS startup]",
  "problem_statement": {
    "current_situation": "[specific current problem]",
    "pain_points": ["specific pain 1", "specific pain 2", "specific pain 3"],
    "impact": "[specific business/user impact]"
  },
  "objectives": [
    "SMART objective 1 with specific metric",
    "SMART objective 2 with specific metric",
    "SMART objective 3 with specific metric"
  ],
  "scope": {
    "in_scope": ["specific feature 1", "specific feature 2"],
    "out_of_scope": ["specific exclusion 1", "specific exclusion 2"]
  },
  "stakeholders": [
    {"role": "specific role", "responsibility": "specific responsibility"}
  ],
  "functional_requirements": [
    {"id": "FR-001", "requirement": "specific requirement", "priority": "High"}
  ],
  "non_functional_requirements": [
    {"id": "NFR-001", "requirement": "specific NFR", "category": "Performance"}
  ],
  "user_stories": [
    {
      "id": "US-001",
      "as_a": "specific user type",
      "i_want": "specific action",
      "so_that": "specific benefit",
      "acceptance_criteria": ["specific criterion 1", "specific criterion 2"]
    }
  ],
  "technical_architecture": {
    "overview": "specific architecture description",
    "components": ["specific component 1", "specific component 2"],
    "data_flow": "specific data flow description",
    "tech_stack": ["specific tech 1", "specific tech 2"]
  },
  "success_metrics": [
    {"metric": "specific metric", "target": "specific target with number", "measurement": "specific method"}
  ],
  "risks": [
    {"risk": "specific risk", "probability": "High/Medium/Low", "impact": "High/Medium/Low", "mitigation": "specific mitigation"}
  ],
  "timeline": [
    {"phase": "Phase name", "duration": "X weeks", "deliverables": ["specific deliverable"]}
  ],
  "swot": {
    "strengths": [
      "Specific strength unique to THIS startup",
      "Specific competitive advantage",
      "Specific technical or market advantage"
    ],
    "weaknesses": [
      "Specific weakness THIS startup faces",
      "Specific resource or market limitation"
    ],
    "opportunities": [
      "Specific market opportunity for THIS sector",
      "Specific growth vector for THIS product"
    ],
    "threats": [
      "Specific named competitor threat",
      "Specific market or regulatory threat"
    ]
  },
  "competitors": [
    {
      "name": "REAL competitor company name",
      "advantages": "their specific strengths",
      "disadvantages": "their specific weaknesses vs us",
      "risk_level": "High/Medium/Low"
    }
  ],
  "citations": [
    {
      "source_text": "exact quote from user input",
      "confidence": 0.95,
      "mapped_requirement": "which section this supports"
    }
  ],
  "target_market": {
    "title": "Target Market Analysis",
    "content": "TAM: $XB (specific reasoning for THIS market). SAM: $XB (specific serviceable segment). SOM: $XM (realistic Year 1 capture). Primary users: [specific user types]. Geography: [specific markets]."
  },
  "overall_confidence": 0.85
}"""


def remap_brd_keys(data: dict) -> dict:
    if not isinstance(data, dict):
        return data
        
    mappings = [
        ("summary", "executive_summary"),
        ("problem", "problem_statement"),
        ("technical_architecture", "tech_architecture"),
        ("timeline", "implementation_timeline"),
        ("risks", "risk_mitigation"),
        ("kpi_metrics", "success_metrics"),
        ("kpis", "success_metrics"),
        ("kpis", "kpi_metrics")
    ]
    
    # Populate both keys to maintain full compatibility with the user requests,
    # backend validations, and frontend render expectations.
    for k1, k2 in mappings:
        val1 = data.get(k1)
        val2 = data.get(k2)
        if val1 and not val2:
            data[k2] = val1
        elif val2 and not val1:
            data[k1] = val2
            
    return data


def generate_fallback_brd(extracted_data: dict) -> dict:
    startup_name = (
        extracted_data.get("startup_name") or 
        extracted_data.get("business_name") or 
        "Startup"
    )
    problem = extracted_data.get("problem_statement", "")
    solution = extracted_data.get("proposed_solution", "")
    features = extracted_data.get("key_features", [])
    users = extracted_data.get("target_users", [])
    tech = extracted_data.get("tech_stack", [])
    competitors_raw = extracted_data.get("competitors", [])
    market_size = extracted_data.get("market_size", "")
    business_model = extracted_data.get("business_model", "")
    risks_raw = extracted_data.get("risks", [])
    metrics_raw = extracted_data.get("success_metrics", [])
    context = extracted_data.get("user_context", "")

    title = f"BRD: {startup_name}"
    
    summary = (
        f"{startup_name} is an innovative platform designed to solve "
        f"{problem[:200] if problem else 'key market challenges'}. "
        f"The solution focuses on {solution[:200] if solution else 'delivering value to target users'} "
        f"targeting {', '.join(users[:2]) if users else 'key user segments'}."
    )

    brd = {
        "title": title,
        "version": "1.0",
        "date": "2026-06-13",
        "executive_summary": summary,
        "problem_statement": {
            "current_situation": problem or f"{startup_name} addresses a critical gap in the market.",
            "pain_points": features[:3] if features else ["Manual processes", "Lack of automation", "Poor user experience"],
            "impact": f"Without {startup_name}, users face significant challenges in {problem[:100] if problem else 'their daily workflows'}."
        },
        "objectives": [
            f"Launch {startup_name} MVP within 3 months with core features",
            f"Acquire first 1,000 users from {', '.join(users[:2]) if users else 'target market'} segment",
            f"Achieve {metrics_raw[0] if metrics_raw else '85%'} user satisfaction score",
            f"Generate first revenue within 6 months via {business_model or 'subscription model'}"
        ],
        "scope": {
            "in_scope": features[:5] if features else [
                "Core product functionality",
                "User authentication and profiles", 
                "Mobile and web application",
                "Basic analytics dashboard"
            ],
            "out_of_scope": [
                "Third-party hardware integrations",
                "Enterprise white-label solutions",
                "Offline-only functionality",
                "International localization (Phase 2)"
            ]
        },
        "stakeholders": [
            {"role": "Product Manager", 
             "responsibility": f"Define and prioritize {startup_name} feature roadmap"},
            {"role": users[0] if users else "End User", 
             "responsibility": "Primary consumer of the product"},
            {"role": "Engineering Lead", 
             "responsibility": "Technical architecture and delivery"},
            {"role": "Business Development", 
             "responsibility": f"Partner acquisition and {business_model or 'revenue'} strategy"}
        ],
        "functional_requirements": [
            {"id": f"FR-00{i+1}", 
             "requirement": f"The system must support {feat}", 
             "priority": "High" if i < 2 else "Medium"}
            for i, feat in enumerate(
                features[:5] if features else [
                    "user registration and authentication",
                    "core feature delivery",
                    "real-time notifications",
                    "data export and reporting"
                ]
            )
        ],
        "non_functional_requirements": [
            {"id": "NFR-001", 
             "requirement": "System must maintain 99.9% uptime SLA", 
             "category": "Reliability"},
            {"id": "NFR-002", 
             "requirement": "API response time under 200ms for 95th percentile", 
             "category": "Performance"},
            {"id": "NFR-003", 
             "requirement": "All user data encrypted at rest using AES-256", 
             "category": "Security"},
            {"id": "NFR-004", 
             "requirement": "System must scale to 100,000 concurrent users", 
             "category": "Scalability"}
        ],
        "user_stories": [
            {
                "id": "US-001",
                "as_a": users[0] if users else "User",
                "i_want": f"to use {features[0] if features else 'the core feature'}",
                "so_that": f"I can {solution[:100] if solution else 'achieve my goal'} efficiently",
                "acceptance_criteria": [
                    "Feature works on mobile and desktop",
                    "Response time under 2 seconds",
                    "Clear success/error feedback"
                ]
            },
            {
                "id": "US-002",
                "as_a": users[1] if len(users) > 1 else "Power User",
                "i_want": f"to access {features[1] if len(features) > 1 else 'advanced features'}",
                "so_that": "I can maximize productivity and ROI",
                "acceptance_criteria": [
                    "Feature accessible within 2 clicks",
                    "Data persists across sessions",
                    "Export functionality available"
                ]
            }
        ],
        "technical_architecture": {
            "overview": f"{startup_name} uses a cloud-native microservices architecture on Google Cloud Platform, ensuring scalability and reliability.",
            "components": tech if tech else [
                "React/Next.js Frontend",
                "FastAPI Backend",
                "PostgreSQL Database",
                "Redis Cache",
                "Google Cloud Run"
            ],
            "data_flow": f"User request → API Gateway → {startup_name} Core Service → Database → Response",
            "tech_stack": tech if tech else [
                "Next.js", "FastAPI", "PostgreSQL", 
                "Redis", "Google Cloud", "Docker"
            ]
        },
        "success_metrics": [
            {"metric": m, 
             "target": "Exceed industry benchmark", 
             "measurement": "Monthly analytics review"}
            for m in (metrics_raw[:3] if metrics_raw else [
                "Monthly Active Users",
                "User Retention Rate",
                "Revenue Growth MoM"
            ])
        ],
        "risks": [
            {
                "risk": r,
                "probability": "Medium",
                "impact": "High",
                "mitigation": f"Proactive monitoring and contingency planning for {r[:50]}"
            }
            for r in (risks_raw[:3] if risks_raw else [
                "Market adoption slower than projected",
                "Technical scalability challenges",
                "Regulatory compliance requirements"
            ])
        ],
        "timeline": [
            {"phase": "Phase 1: Foundation", 
             "duration": "4 weeks", 
             "deliverables": ["Architecture design", "Core infrastructure setup", "Team onboarding"]},
            {"phase": "Phase 2: Core Development", 
             "duration": "8 weeks", 
             "deliverables": ["MVP features built", "API integrations", "Internal testing"]},
            {"phase": "Phase 3: Beta Launch", 
             "duration": "4 weeks", 
             "deliverables": ["Beta user onboarding", "Feedback collection", "Bug fixes"]},
            {"phase": "Phase 4: Public Launch", 
             "duration": "4 weeks", 
             "deliverables": ["Marketing campaign", "Full launch", "KPI monitoring"]}
        ],
        "swot": {
            "strengths": [
                f"First-mover advantage in {problem[:80] if problem else 'target market'}",
                f"Strong technical foundation using {', '.join(tech[:2]) if tech else 'modern tech stack'}",
                f"Clear target market: {', '.join(users[:2]) if users else 'identified user segments'}",
                f"Innovative solution: {solution[:100] if solution else 'unique approach'}"
            ],
            "weaknesses": [
                "Early stage with limited brand recognition",
                "Dependent on initial funding for growth",
                f"Market education needed for {problem[:60] if problem else 'new concept'}",
                "Small team — needs strategic hiring"
            ],
            "opportunities": [
                f"Growing demand for {solution[:80] if solution else 'innovative solutions'}",
                "Partnership opportunities with established players",
                f"Expansion beyond initial {users[0] if users else 'user'} segment",
                "International market expansion in Phase 3"
            ],
            "threats": [
                f"Established competitors: {', '.join(str(c) for c in competitors_raw[:2]) if competitors_raw else 'existing solutions'}",
                "Rapidly changing technology landscape",
                "Economic uncertainty affecting user spending",
                "Potential regulatory changes in the sector"
            ]
        },
        "competitors": [
            {
                "name": str(c),
                "advantages": "Established market presence and user base",
                "disadvantages": f"Lacks the innovation of {startup_name}'s approach",
                "risk_level": "Medium"
            }
            for c in (competitors_raw[:3] if competitors_raw else [
                "Existing Manual Solutions",
                "Generic Platforms",
                "Direct Competitors"
            ])
        ],
        "citations": [
            {
                "source_text": problem[:100] if problem else "User provided context",
                "confidence": 0.90,
                "mapped_requirement": "executive_summary, problem_statement"
            },
            {
                "source_text": solution[:100] if solution else "Proposed solution",
                "confidence": 0.85,
                "mapped_requirement": "objectives, scope, user_stories"
            }
        ],
        "target_market": {
            "title": "Target Market Analysis",
            "content": (
                f"TAM: {market_size or '$10B+'} (Total addressable market for {startup_name}'s sector). "
                f"SAM: Estimated 20-25% of TAM representing serviceable segments "
                f"({', '.join(users[:2]) if users else 'primary user segments'}). "
                f"SOM: Conservative 2-5% capture in Year 1, growing to 10-15% by Year 3. "
                f"Primary focus: {', '.join(users[:3]) if users else 'core user segments'} "
                f"who face challenges with {problem[:100] if problem else 'current solutions'}."
            )
        },
        "overall_confidence": extracted_data.get("confidence", 0.75)
    }

    return remap_brd_keys(brd)


def parse_dirty_json(s: str) -> dict:
    s = s.strip()
    
    # Strip markdown code fences if present (```json ... ```)
    import re
    s = re.sub(r'```(?:json)?\s*', '', s)
    s = re.sub(r'```', '', s)
    
    # Strip any text before the first { character and after the last } character
    first_brace = s.find('{')
    last_brace = s.rfind('}')
    if first_brace != -1 and last_brace != -1:
        s = s[first_brace:last_brace+1]
    
    try:
        parsed = json.loads(s)
    except json.JSONDecodeError:
        # Clean trailing commas inside lists and dicts
        s_clean = re.sub(r',\s*([\]}])', r'\1', s)
        try:
            parsed = json.loads(s_clean)
        except Exception:
            raise

    return remap_brd_keys(parsed)


async def extract_information(content: str, input_type: str, filename: Optional[str] = None) -> dict:
    """Extract structured information from any input type."""
    try:
        if input_type == "image":
            # Decode base64 image
            image_data = base64.b64decode(content)
            image_part = {
                "mime_type": _get_mime_type(filename or "image.jpg"),
                "data": image_data
            }
            prompt = f"Extract ALL business/startup information from this image. {EXTRACT_PROMPT.format(content='[see image above]')}"
            response = model.generate_content([prompt, image_part])
        elif input_type == "pdf":
            # For PDFs, decode base64 and send as document
            pdf_data = base64.b64decode(content)
            pdf_part = {
                "mime_type": "application/pdf",
                "data": pdf_data
            }
            prompt = EXTRACT_PROMPT.format(content="[see PDF document above]")
            response = model.generate_content([prompt, pdf_part])
        else:
            # Plain text or URL content
            prompt = EXTRACT_PROMPT.format(content=content[:8000])
            response = model.generate_content(prompt)

        raw = response.text.strip()
        print("========== GEMINI RAW ==========")
        print(raw)
        print("================================")        
        return parse_dirty_json(raw)

    except Exception as e:
        # Dynamic fallback — extract key signals from the raw content string
        print(f"[extract_information] Gemini call failed ({e}), using dynamic fallback")
        content_lower = content.lower() if isinstance(content, str) else ""
        # Attempt to pull a startup name from common patterns
        import re as _re
        name_match = _re.search(r'(?:startup|company|app|platform|product)[:\s]+([A-Z][A-Za-z0-9]+)', content)
        extracted_name = name_match.group(1) if name_match else None
        return {
            "business_name": extracted_name,
            "problem_statement": content[:500] if isinstance(content, str) else "",
            "target_users": [],
            "proposed_solution": "",
            "key_features": [],
            "tech_stack": [],
            "market_size": "",
            "competitors": [],
            "business_model": "",
            "success_metrics": [],
            "risks": [],
            "confidence": 0.4,
            "user_context": content[:1000] if isinstance(content, str) else ""
        }


async def generate_brd(extracted_data: dict) -> dict:
    try:
        prompt = BRD_PROMPT.replace(
            "{extracted_data}",
            json.dumps(extracted_data, indent=2)
        )

        response = model.generate_content(prompt)
        raw = response.text.strip()
        return parse_dirty_json(raw)
    
    

    except Exception as e:
        print("===== FULL ERROR =====")
        traceback.print_exc()
        print("======================")
        return generate_fallback_brd(extracted_data)


async def generate_brd_streaming(extracted_data: dict):
    prompt = BRD_PROMPT.replace(
        "{extracted_data}",
        json.dumps(extracted_data, indent=2)
    )

    response = model.generate_content(prompt, stream=True)

    for chunk in response:
        if chunk.text:
            yield chunk.text


def _get_mime_type(filename: str) -> str:
    ext = filename.lower().split(".")[-1]
    return {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "gif": "image/gif",
        "webp": "image/webp",
        "pdf": "application/pdf"
    }.get(ext, "image/jpeg")
