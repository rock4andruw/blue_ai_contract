%%{init: {"theme": "base","themeVariables": {"background": "#050816","primaryColor": "#0b1220","primaryTextColor": "#e6f1ff","primaryBorderColor": "#22d3ee","lineColor": "#5eead4","secondaryColor": "#101a2f","tertiaryColor": "#0f172a","fontFamily": "'Noto Sans TC', 'Microsoft JhengHei', 'PingFang TC', sans-serif","fontSize": "15px"},"flowchart": {"htmlLabels": true,"curve": "basis","nodeSpacing": 60,"rankSpacing": 90}}}%%

flowchart LR

NOW["✅ 現況（已完成）\n規則引擎 + Verification Agent\n+ Layer 3 + MAS 雙重驗證"]

SHORT["🔵 短期（3 個月內）\n• NDA／採購合約類型\n• 合約範本 Playbook\n• Layer 3 法條/先例擴充\n• Teams／SharePoint 整合"]

MID["🟣 中期（6 個月內）\n• 罰款合理性 Insight 分析\n• 歷史修改趨勢追蹤\n• 掃描版 PDF（OCR）"]

LONG["⚫ 長期（12 個月）\n• 週報自動整併月報\n• RBAC 三層權限\n• 跨部門推廣（採購／業務／人資）"]

NOW --> SHORT --> MID --> LONG

classDef done fill:#07131f,stroke:#00e5ff,stroke-width:2px,color:#e6faff;
classDef short fill:#081422,stroke:#38bdf8,stroke-width:2px,color:#eff6ff;
classDef mid fill:#1a0f1f,stroke:#e879f9,stroke-width:2px,color:#fdf4ff;
classDef long fill:#140d22,stroke:#a855f7,stroke-width:2px,color:#f5f3ff;

class NOW done;
class SHORT short;
class MID mid;
class LONG long;
